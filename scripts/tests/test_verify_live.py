"""Verify the live-site command using a local HTTP server."""

from __future__ import annotations

import json
import os
import unittest
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout, suppress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from threading import Thread
from time import monotonic, sleep
from unittest.mock import patch

from scripts import verify_live

PACKAGE = Path(__file__).resolve().parents[2] / "package.json"
ASTRO = json.loads(PACKAGE.read_text(encoding="utf-8"))["dependencies"]["astro"]


class VerifyLiveTest(unittest.TestCase):
    def setUp(self) -> None:
        pages: dict[str, bytes] = {}
        redirects: dict[str, str] = {}
        retry_delays: dict[str, float] = {}
        response_chunks: dict[tuple[str, int], list[bytes]] = {}
        requests: Counter[str] = Counter()

        class Handler(BaseHTTPRequestHandler):
            def write_chunks(self, chunks: list[bytes]) -> None:
                with suppress(ConnectionError):
                    for chunk in chunks:
                        self.wfile.write(chunk)
                        sleep(0.05)

            def do_CONNECT(self) -> None:
                requests[self.path] += 1
                self.write_chunks(
                    [
                        b"HTTP/1.1 200 Connection established\r\n",
                        *([b"X-Fixture: slow\r\n"] * 30),
                        b"\r\n",
                    ]
                )

            def do_GET(self) -> None:
                requests[self.path] += 1
                if requests[self.path] > 1 and self.path in retry_delays:
                    sleep(retry_delays[self.path])
                if chunks := response_chunks.get((self.path, requests[self.path])):
                    self.write_chunks(chunks)
                    return
                if target := redirects.get(self.path):
                    self.send_response(302)
                    self.send_header("Location", target)
                    self.end_headers()
                    return
                body = pages.get(self.path)
                with suppress(ConnectionError):
                    self.send_response(404 if body is None else 200)
                    self.end_headers()
                    if body is not None:
                        self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)

        self.base = f"http://127.0.0.1:{server.server_port}/"
        self.pages = pages
        self.redirects = redirects
        self.retry_delays = retry_delays
        self.response_chunks = response_chunks
        self.requests = requests
        pages.update(
            {
                "/": self.home(ASTRO),
                "/rss.xml": (
                    f"<rss><channel><item><link>{self.base}blog/newest/</link></item>"
                    f"<item><link>{self.base}blog/older/</link></item></channel></rss>"
                ).encode(),
                "/sitemap-index.xml": b"<sitemapindex/>",
                "/robots.txt": f"User-agent: *\nSitemap: {self.base}sitemap-0.xml\n".encode(),
                "/sitemap-0.xml": b"<urlset/>",
                "/blog/newest/": b"Newest post",
            }
        )

    @staticmethod
    def home(version: str) -> bytes:
        return (
            f'<html lang="fr-CA"><head><meta content="Astro v{version}" name="generator">'
            "</head></html>"
        ).encode()

    def run_cli(self) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with (
            patch.object(verify_live, "RETRY_WINDOW_SECONDS", 0),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            code = verify_live.main([self.base])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_good_site_passes(self) -> None:
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(stdout, f"live site OK: 8 checks on {self.base}\n")
        self.assertEqual(set(self.requests), set(self.pages))

    def test_wrong_generator_names_the_expected_and_received_versions(self) -> None:
        self.pages["/"] = self.home("0.0.0")
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stdout), (1, ""))
        self.assertEqual(
            stderr,
            f"{self.base}: expected generator 'Astro v{ASTRO}', received 'Astro v0.0.0'\n",
        )

    def test_rss_404_names_the_feed_and_status(self) -> None:
        del self.pages["/rss.xml"]
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stdout), (1, ""))
        self.assertEqual(
            stderr, f"{self.base}rss.xml: expected HTTP 200, received HTTP 404\n"
        )

    def test_latest_post_404_names_the_post_and_status(self) -> None:
        del self.pages["/blog/newest/"]
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stdout), (1, ""))
        self.assertEqual(
            stderr, f"{self.base}blog/newest/: expected HTTP 200, received HTTP 404\n"
        )

    def test_first_item_must_have_its_own_link(self) -> None:
        self.pages["/rss.xml"] = (
            f"<rss><channel><item><title>Newest</title></item>"
            f"<item><link>{self.base}blog/older/</link></item></channel></rss>"
        ).encode()
        self.pages["/blog/older/"] = b"Older post"
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stdout), (1, ""))
        self.assertEqual(
            stderr,
            f"{self.base}rss.xml: expected first RSS item link, received no link\n",
        )
        self.assertEqual(self.requests["/blog/older/"], 0)

    def test_latest_post_redirect_is_an_http_302_failure(self) -> None:
        for target in (self.base, "ftp://127.0.0.1:0/post"):
            with self.subTest(target=target):
                self.requests.clear()
                self.redirects["/blog/newest/"] = target
                code, stdout, stderr = self.run_cli()
                self.assertEqual((code, stdout), (1, ""))
                self.assertEqual(
                    stderr,
                    f"{self.base}blog/newest/: expected HTTP 200, received HTTP 302\n",
                )
                self.assertEqual(self.requests["/"], 1)

    def test_unknown_rss_encoding_reports_the_feed_as_invalid(self) -> None:
        self.pages["/rss.xml"] = (
            b'<?xml version="1.0" encoding="unsupported-codec"?><rss><channel/></rss>'
        )
        code, stdout, stderr = self.run_cli()
        self.assertEqual((code, stdout), (1, ""))
        self.assertIn(
            f"{self.base}rss.xml: expected RSS XML, received invalid XML", stderr
        )

    def test_malformed_link_reports_its_source(self) -> None:
        for link in (
            "http://[",
            "http://",
            "http://127.0.0.1:bad/post",
            "http://invalid host/post",
        ):
            for path, body in {
                "/rss.xml": f"<rss><channel><item><link>{link}</link></item></channel></rss>",
                "/robots.txt": f"Sitemap: {link}\n",
            }.items():
                with (
                    self.subTest(path=path, link=link),
                    patch.dict(self.pages, {path: body.encode()}),
                ):
                    self.requests.clear()
                    code, stdout, stderr = self.run_cli()
                    self.assertEqual((code, stdout), (1, ""))
                    self.assertEqual(
                        stderr,
                        f"{self.base}{path[1:]}: expected HTTP(S) link, received {link!r}\n",
                    )
                    self.assertEqual(self.requests[path], 1)

    def test_retries_failed_checks_until_they_pass(self) -> None:
        self.pages["/"] = self.home("0.0.0")

        def update_home(_: float) -> None:
            self.pages["/"] = self.home("9.8.7")

        with patch.object(verify_live.time, "sleep", side_effect=update_home):
            errors = verify_live.failures(self.base, astro_version="9.8.7")
        self.assertEqual(errors, [])
        self.assertEqual(self.requests["/"], 2)
        self.assertEqual(self.requests["/rss.xml"], 1)
        self.assertEqual(self.requests["/robots.txt"], 1)

    def test_retry_cannot_wait_past_its_request_budget(self) -> None:
        self.pages["/"] = self.home("0.0.0")
        self.retry_delays["/"] = 1.5

        def update_home(_: float) -> None:
            self.pages["/"] = self.home(ASTRO)

        with (
            patch.object(verify_live, "RETRY_INTERVAL_SECONDS", 0.01),
            patch.object(verify_live.time, "sleep", side_effect=update_home),
        ):
            errors = verify_live.failures(self.base, retry_seconds=0.5)
        self.assertEqual(self.requests["/"], 2)
        self.assertEqual(len(errors), 1)
        self.assertIn(f"{self.base}: expected HTTP 200, received", errors[0])
        self.assertIn("timed out", errors[0].lower())

    def test_retry_rejects_late_headers_or_body(self) -> None:
        self.pages["/"] = self.home("0.0.0")
        body = self.home(ASTRO)
        status = b"HTTP/1.1 200 OK\r\n"
        headers = f"Connection: close\r\nContent-Length: {len(body)}\r\n\r\n".encode()
        streams = {
            "headers": [status, *([b"X-Fixture: slow\r\n"] * 20), headers, body],
            "body": [
                status + headers,
                *(body[i : i + 4] for i in range(0, len(body), 4)),
            ],
        }
        for part, chunks in streams.items():
            with (
                self.subTest(part=part),
                patch.object(verify_live, "RETRY_INTERVAL_SECONDS", 0.01),
            ):
                self.requests.clear()
                self.response_chunks["/", 2] = chunks
                start = monotonic()
                errors = verify_live.failures(self.base, retry_seconds=0.5)
                if part == "body":
                    self.assertLess(monotonic() - start, 0.9)
                self.assertEqual(self.requests["/"], 2)
                expected = "complete HTTP body" if part == "body" else "HTTP 200"
                self.assertEqual(
                    errors,
                    [f"{self.base}: expected {expected}, received request timed out"],
                )

    def test_late_https_proxy_response_is_a_timeout(self) -> None:
        target = "https://127.0.0.1:1/"
        with patch.dict(os.environ, {"https_proxy": self.base}, clear=True):
            errors = verify_live.failures(
                target, astro_version=ASTRO, retry_seconds=0.5
            )
        self.assertEqual(self.requests["127.0.0.1:1"], 1)
        self.assertIn(
            f"{target}: expected HTTP 200, received request timed out", errors
        )

    def test_the_first_pass_uses_the_shared_deadline(self) -> None:
        body = self.home(ASTRO) + b" " * 100
        headers = (
            f"HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: {len(body)}\r\n\r\n"
        ).encode()
        self.response_chunks["/", 1] = [
            headers,
            *(body[i : i + 5] for i in range(0, len(body), 5)),
        ]
        start = monotonic()
        errors = verify_live.failures(self.base, retry_seconds=0.5)
        self.assertLess(monotonic() - start, 0.9)
        self.assertEqual(dict(self.requests), {"/": 1})
        self.assertIn(
            f"{self.base}: expected complete HTTP body, received request timed out",
            errors,
        )

    def test_incomplete_bodies_fail_even_when_the_prefix_is_valid(self) -> None:
        for path, body in self.pages.items():
            response = (
                f"HTTP/1.1 200 OK\r\nConnection: close\r\n"
                f"Content-Length: {len(body) + 10}\r\n\r\n"
            ).encode() + body
            with (
                self.subTest(path=path),
                patch.dict(self.response_chunks, {(path, 1): [response]}),
            ):
                self.requests.clear()
                code, stdout, stderr = self.run_cli()
                self.assertEqual((code, stdout), (1, ""))
                self.assertEqual(
                    stderr,
                    f"{self.base}{path[1:]}: expected complete HTTP body, "
                    "received EOF with 10 bytes missing\n",
                )

    def test_invalid_framing_cannot_make_a_valid_body_prefix_pass(self) -> None:
        for path, body in self.pages.items():
            length = str(len(body)).encode()
            for header in (
                b"Content-Length: abc",
                b"Content-Length: -5",
                b"Content-Length: " + length + b"\r\nContent-Length: 99999",
                b"Transfer-Encoding: gzip, chunked",
                b"Transfer-Encoding: chunked\r\nContent-Length: " + length,
            ):
                response = (
                    b"HTTP/1.1 200 OK\r\nConnection: close\r\n"
                    + header
                    + b"\r\n\r\n"
                    + body
                )
                with (
                    self.subTest(path=path, header=header),
                    patch.dict(self.response_chunks, {(path, 1): [response]}),
                ):
                    self.requests.clear()
                    code, stdout, stderr = self.run_cli()
                    self.assertEqual((code, stdout), (1, ""))
                    self.assertIn(f"{self.base}{path[1:]}: expected", stderr)
