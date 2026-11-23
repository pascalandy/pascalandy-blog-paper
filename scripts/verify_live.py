#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the public blog with read-only HTTP GETs.

Checks cover the homepage language and Astro generator, RSS and its first post,
the sitemap index, the sitemap named in robots.txt, and the 41 legacy event
redirects and their destination articles. With an expected commit, the check
also requires the homepage commit, stylesheets and banner images. Failed checks retry
every ten seconds within a 120-second window.

The verifier requires complete headers and body framing. A response without
Content-Length or chunked encoding ends at a clean EOF from the transport.

The retry window limits when the checker starts another urllib attempt.
A blocking socket read can overrun by its configured timeout (up to ten
seconds). DNS, address fallback, and response parsing inside urllib can take
longer. An attempt already in progress can send its GET after expiry. The
checker checks the deadline when urllib returns control and rejects late results.
"""

from __future__ import annotations

import argparse
import http.client
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urldefrag, urljoin, urlsplit

from event_redirects import EVENT_REDIRECTS, PageMetadata, redirect_problem

DEFAULT_BASE = "https://pascalandy.com/"
PACKAGE_JSON = Path(__file__).resolve().parents[1] / "package.json"
RETRY_WINDOW_SECONDS = 120
RETRY_INTERVAL_SECONDS = 10
HTTP_TIMEOUT_SECONDS = 10
USER_AGENT = "pascalandy-blog-verify-live"
MAX_HTTP_LINE = 65536


class CheckFailed(Exception):
    """A failed HTTP check with its URL and expected and received values."""


def srcset_urls(value: str) -> list[str]:
    return [candidate.split()[0] for candidate in value.split(",") if candidate.strip()]


class HomeMetadata(PageMetadata):
    def __init__(self) -> None:
        super().__init__()
        self.commits: list[str] = []
        self.stylesheets: list[str] = []
        self.banner_webp: list[str] = []
        self.banner_src = ""
        self.banner_srcset: list[str] = []
        self.in_banner = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        super().handle_starttag(tag, attrs)
        if self.inert:
            return
        values = dict(attrs)
        if tag == "meta" and values.get("name") == "build-commit":
            self.commits.append(values.get("content") or "")
        elif (
            tag == "link" and "stylesheet" in (values.get("rel") or "").lower().split()
        ):
            self.stylesheets.append(values.get("href") or "")
        elif tag == "picture" and "data-site-banner" in values:
            self.in_banner = True
        elif self.in_banner and tag == "source" and values.get("type") == "image/webp":
            self.banner_webp.extend(srcset_urls(values.get("srcset") or ""))
        elif self.in_banner and tag == "img":
            self.banner_src = values.get("src") or ""
            self.banner_srcset = srcset_urls(values.get("srcset") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "picture" and not self.inert:
            self.in_banner = False
        super().handle_endtag(tag)


class DirectResponses(urllib.request.HTTPErrorProcessor):
    """Expose the requested URL's status before urllib can follow a redirect."""

    def http_response(
        self, _request: urllib.request.Request, response: http.client.HTTPResponse
    ) -> http.client.HTTPResponse:
        return response

    https_response = http_response


class FramingLines:
    def __init__(self, stream: BinaryIO) -> None:
        self.stream = stream

    def readline(self, size: int = -1) -> bytes:
        line = self.stream.readline(size)
        if not line:
            raise http.client.RemoteDisconnected("EOF inside HTTP framing")
        if len(line) > MAX_HTTP_LINE:
            raise http.client.LineTooLong("HTTP framing line")
        if not line.endswith(b"\r\n"):
            raise http.client.HTTPException("incomplete HTTP framing line")
        return line

    def close(self) -> None:
        self.stream.close()


class CompleteResponse(http.client.HTTPResponse):
    """Require complete framing where http.client otherwise accepts an EOF."""

    def begin(self) -> None:
        if self.headers is not None:
            return
        stream = self.fp
        if stream is None:
            raise http.client.RemoteDisconnected("response stream closed")
        self.fp = FramingLines(stream)
        try:
            super().begin()
        finally:
            if self.fp is not None:
                self.fp = stream

    def validate_framing(self) -> None:
        lengths = {
            value.strip() for value in self.headers.get_all("Content-Length", [])
        }
        encodings = self.headers.get_all("Transfer-Encoding", [])
        if encodings and (
            len(encodings) != 1 or not self.chunked or lengths or self.version != 11
        ):
            raise http.client.HTTPException(
                "unsupported or conflicting Transfer-Encoding"
            )
        if lengths and (
            len(lengths) > 1
            or self.length is None
            or any(not (value.isascii() and value.isdecimal()) for value in lengths)
        ):
            raise http.client.HTTPException("invalid or conflicting Content-Length")
        if self.headers.defects:
            raise http.client.HTTPException("malformed HTTP headers")

    def _read_next_chunk_size(self) -> int:
        line = FramingLines(self.fp).readline(MAX_HTTP_LINE + 1)
        size, extension, _ = line[:-2].partition(b";")
        if extension:
            size = size.rstrip(b" \t")
        if not re.fullmatch(rb"[0-9a-fA-F]+", size):
            raise http.client.HTTPException("invalid HTTP chunk size")
        return int(size, 16)

    def _get_chunk_left(self) -> int | None:
        if self.chunk_left == 0:
            if self._safe_read(2) != b"\r\n":
                raise http.client.HTTPException("invalid HTTP chunk separator")
            self.chunk_left = None
        return super()._get_chunk_left()

    def _read_and_discard_trailer(self) -> None:
        trailers = http.client.parse_headers(FramingLines(self.fp))
        if trailers.defects:
            raise http.client.HTTPException("malformed HTTP trailers")

    def read1(self, n: int = -1) -> bytes:
        chunk = super().read1(n)
        if not chunk and n != 0 and self.length:
            raise http.client.HTTPException(f"EOF with {self.length} bytes missing")
        return chunk


class CompleteHTTPHandler(urllib.request.HTTPSHandler, urllib.request.HTTPHandler):
    class HTTPConnection(http.client.HTTPConnection):
        response_class = CompleteResponse

    class HTTPSConnection(http.client.HTTPSConnection):
        response_class = CompleteResponse

    def http_open(self, request: urllib.request.Request) -> CompleteResponse:
        return self.do_open(self.HTTPConnection, request)

    def https_open(self, request: urllib.request.Request) -> CompleteResponse:
        return self.do_open(self.HTTPSConnection, request, context=self._context)


class SiteRequests:
    def __init__(self, deadline: float | None) -> None:
        self.deadline = deadline
        self.opener = urllib.request.build_opener(
            DirectResponses(), CompleteHTTPHandler()
        )

    def get(
        self,
        url: str,
        *,
        read_body: bool = False,
        html: bool = False,
        media_type: str | None = None,
    ) -> bytes:
        now = time.monotonic()
        deadline = now + HTTP_TIMEOUT_SECONDS
        expected = "HTTP 200"
        if self.deadline is not None:
            if self.deadline <= now:
                raise CheckFailed(problem(url, expected, "verification window elapsed"))
            deadline = min(self.deadline, deadline)

        def remaining() -> float:
            seconds = deadline - time.monotonic()
            if seconds <= 0:
                raise CheckFailed(problem(url, expected, "request timed out")) from None
            return seconds

        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT}, method="GET"
            )
            with self.opener.open(request, timeout=remaining()) as response:
                remaining()
                if response.status != 200:
                    raise CheckFailed(problem(url, expected, f"HTTP {response.status}"))
                if html and "Refresh" in response.headers:
                    raise CheckFailed(
                        problem(url, "inline HTML", "unexpected HTTP Refresh")
                    )
                required_type = "text/html" if html else media_type
                if (
                    required_type is not None
                    and response.headers.get_content_type() != required_type
                ):
                    raise CheckFailed(
                        problem(
                            url,
                            required_type,
                            str(response.headers.get("Content-Type")),
                        )
                    )
                if html and response.headers.get_content_disposition() not in (
                    None,
                    "inline",
                ):
                    raise CheckFailed(
                        problem(
                            url,
                            "inline HTML",
                            str(response.headers.get("Content-Disposition")),
                        )
                    )
                expected = "complete HTTP body"
                response.validate_framing()
                body = bytearray()
                while True:
                    remaining()
                    chunk = response.read1(64 * 1024)
                    if not chunk:
                        remaining()
                        return bytes(body)
                    if read_body:
                        body.extend(chunk)
        except (OSError, ValueError, http.client.HTTPException) as error:
            remaining()
            raise CheckFailed(problem(url, expected, str(error))) from None


def problem(url: str, expected: str, received: str) -> str:
    return f"{url}: expected {expected}, received {received}"


def http_link(source: str, link: str) -> str:
    try:
        if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in link):
            raise ValueError("link contains whitespace or a control character")
        original = urlsplit(link)
        if (original.scheme or link.startswith("//")) and not original.hostname:
            raise ValueError("absolute link has no host")
        target = urljoin(source, link)
        parts = urlsplit(target)
        if (
            parts.scheme not in {"http", "https"}
            or not parts.hostname
            or parts.port == 0
        ):
            raise ValueError("invalid HTTP(S) target")
    except ValueError:
        raise CheckFailed(problem(source, "HTTP(S) link", repr(link))) from None
    return target


def check_home_assets(
    requests: SiteRequests, url: str, metadata: HomeMetadata
) -> list[str]:
    if metadata.has_base or metadata.directives:
        return [problem(url, "homepage with same-origin assets", "base or refresh tag")]
    errors = []
    asset_groups = (
        ("linked stylesheet", metadata.stylesheets, "text/css", 1),
        ("responsive WebP banner srcset", metadata.banner_webp, "image/webp", 2),
        ("responsive JPEG banner srcset", metadata.banner_srcset, "image/jpeg", 2),
        ("linked banner fallback", [metadata.banner_src], "image/jpeg", 1),
    )
    origin = urlsplit(url)
    checked_assets = set()
    for label, links, media_type, minimum in asset_groups:
        if not links or not all(links):
            errors.append(problem(url, label, "missing URL"))
            continue
        targets = set()
        for link in links:
            try:
                target, _ = urldefrag(http_link(url, link))
                parts = urlsplit(target)
                if (parts.scheme, parts.netloc) != (origin.scheme, origin.netloc):
                    raise CheckFailed(
                        problem(url, f"same-origin {label}", repr(target))
                    )
                targets.add(target)
                asset = (target, media_type)
                if asset in checked_assets:
                    continue
                checked_assets.add(asset)
                if not requests.get(target, read_body=True, media_type=media_type):
                    raise CheckFailed(
                        problem(target, f"nonempty {media_type}", "empty body")
                    )
            except CheckFailed as error:
                errors.append(str(error))
        if len(targets) < minimum:
            errors.append(
                problem(
                    url,
                    f"{label} with at least {minimum} distinct URLs",
                    str(len(targets)),
                )
            )
    return errors


def check_home(
    requests: SiteRequests, url: str, astro_version: str, expected_commit: str | None
) -> list[str]:
    metadata = HomeMetadata()
    metadata.feed(
        requests.get(url, read_body=True, html=expected_commit is not None).decode(
            "utf-8", errors="replace"
        )
    )
    metadata.close()
    generator = f"Astro v{astro_version}"
    errors = [
        problem(url, f"{field} {expected!r}", f"{received!r}")
        for field, expected, received in (
            ("HTML language", "fr-CA", metadata.language),
            ("generator", generator, metadata.generator),
        )
        if expected != received
    ]
    if expected_commit is not None:
        if metadata.commits != [expected_commit]:
            errors.append(
                problem(url, f"build commit {expected_commit}", repr(metadata.commits))
            )
        errors.extend(check_home_assets(requests, url, metadata))
    return errors


def check_rss(requests: SiteRequests, url: str) -> list[str]:
    body = requests.get(url, read_body=True)
    try:
        item = ET.fromstring(body).find("./channel/item")
    except (ET.ParseError, LookupError, ValueError) as error:
        raise CheckFailed(problem(url, "RSS XML", f"invalid XML ({error})")) from None
    link = "" if item is None else (item.findtext("link") or "").strip()
    if not link:
        raise CheckFailed(problem(url, "first RSS item link", "no link"))
    return check_status(requests, http_link(url, link))


def check_robots(requests: SiteRequests, url: str) -> list[str]:
    robots = requests.get(url, read_body=True).decode("utf-8", errors="replace")
    for line in robots.splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "sitemap" and value.strip():
            return check_status(requests, http_link(url, value.strip()))
    raise CheckFailed(problem(url, "Sitemap directive with a URL", "no Sitemap URL"))


def check_event(
    requests: SiteRequests, base: str, route: str, target: str
) -> list[str]:
    url = urljoin(base, route)
    html = requests.get(url, read_body=True, html=True).decode(
        "utf-8", errors="replace"
    )
    if error := redirect_problem(html, target):
        return [f"{url}: {error}"]
    article = urljoin(base, target)
    metadata = PageMetadata()
    metadata.feed(
        requests.get(article, read_body=True, html=True).decode(
            "utf-8", errors="replace"
        )
    )
    if (
        len(metadata.canonicals) != 1
        or not metadata.canonicals[0]
        or urlsplit(http_link(article, metadata.canonicals[0])).path != target
    ):
        return [problem(article, f"canonical path {target}", repr(metadata.canonicals))]
    if not metadata.indexed or not metadata.article_text or metadata.directives:
        return [
            problem(article, "a published article", "redirect or missing article body")
        ]
    return []


def check_status(requests: SiteRequests, url: str) -> list[str]:
    requests.get(url)
    return []


def astro_from_package(source: str) -> str:
    try:
        version = json.loads(source)["dependencies"]["astro"]
    except (KeyError, TypeError):
        raise ValueError("package.json lacks dependencies.astro") from None
    if not isinstance(version, str) or not version.strip():
        raise ValueError("package.json has an empty or invalid Astro version")
    return version


def verify(
    base: str,
    astro_version: str | None,
    retry_seconds: float,
    *,
    expected_commit: str | None = None,
) -> tuple[int, list[str]]:
    if astro_version is None:
        try:
            astro_version = astro_from_package(PACKAGE_JSON.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            return 0, [problem(base, "Astro version from package.json", str(error))]

    base = base.rstrip("/") + "/"
    try:
        base = http_link(base, base)
    except CheckFailed as error:
        return 0, [str(error)]
    deadline = time.monotonic() + retry_seconds
    requests = SiteRequests(deadline if retry_seconds > 0 else None)
    checks = [
        (
            3 if expected_commit is None else 6,
            partial(check_home, requests, base, astro_version, expected_commit),
        ),
        (2, partial(check_rss, requests, urljoin(base, "rss.xml"))),
        (1, partial(check_status, requests, urljoin(base, "sitemap-index.xml"))),
        (2, partial(check_robots, requests, urljoin(base, "robots.txt"))),
    ]
    checks.extend(
        (2, partial(check_event, requests, base, route, target))
        for route, target in EVENT_REDIRECTS.items()
    )
    count = sum(size for size, _ in checks)
    pending = [check for _, check in checks]
    while True:
        failed = []
        messages = []
        for check in pending:
            try:
                errors = check()
            except CheckFailed as error:
                errors = [str(error)]
            if errors:
                failed.append(check)
                messages.extend(errors)
        if not failed or time.monotonic() + RETRY_INTERVAL_SECONDS >= deadline:
            return count, messages
        pending = failed
        time.sleep(RETRY_INTERVAL_SECONDS)


def failures(
    base: str,
    astro_version: str | None = None,
    retry_seconds: float = RETRY_WINDOW_SECONDS,
    *,
    expected_commit: str | None = None,
) -> list[str]:
    """Return errors for the live site after retrying the checks that fail."""
    _, messages = verify(
        base, astro_version, retry_seconds, expected_commit=expected_commit
    )
    return messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="just verify-live", description=__doc__)
    parser.add_argument("base", nargs="?", default=DEFAULT_BASE)
    parser.add_argument(
        "--expected-commit",
        help="require a full build commit and working homepage assets",
    )
    args = parser.parse_args(argv)
    try:
        count, messages = verify(
            args.base, None, RETRY_WINDOW_SECONDS, expected_commit=args.expected_commit
        )
    except KeyboardInterrupt:
        return 130
    if messages:
        for message in messages:
            print(message, file=sys.stderr)
        return 1
    print(f"live site OK: {count} checks on {args.base}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
