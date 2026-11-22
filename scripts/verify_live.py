#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the public blog with read-only HTTP GETs."""

from __future__ import annotations

import argparse
import http.client
import json
import socket
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from contextlib import suppress
from functools import partial
from html.parser import HTMLParser
from pathlib import Path
from threading import Event, Timer
from urllib.parse import urljoin, urlsplit

DEFAULT_BASE = "https://pascalandy.com/"
PACKAGE_JSON = Path(__file__).resolve().parents[1] / "package.json"
RETRY_WINDOW_SECONDS = 120
RETRY_INTERVAL_SECONDS = 10
HTTP_TIMEOUT_SECONDS = 10
USER_AGENT = "pascalandy-blog-verify-live"


class CheckFailed(Exception):
    """A failed HTTP check with its URL and expected and received values."""


class DirectResponses(urllib.request.HTTPErrorProcessor):
    """Expose the requested URL's status before urllib can follow a redirect."""

    def http_response(
        self, _request: urllib.request.Request, response: http.client.HTTPResponse
    ) -> http.client.HTTPResponse:
        return response

    https_response = http_response


def retry_opener(
    connected: Callable[[socket.socket | None], None],
) -> urllib.request.OpenerDirector:
    class Connection(http.client.HTTPConnection):
        def connect(self) -> None:
            super().connect()
            connected(self.sock)

    class SecureConnection(http.client.HTTPSConnection):
        def connect(self) -> None:
            super().connect()
            connected(self.sock)

    class TrackSocket(urllib.request.HTTPSHandler, urllib.request.HTTPHandler):
        def http_open(
            self, request: urllib.request.Request
        ) -> http.client.HTTPResponse:
            return self.do_open(Connection, request)

        def https_open(
            self, request: urllib.request.Request
        ) -> http.client.HTTPResponse:
            return self.do_open(SecureConnection, request, context=self._context)

    return urllib.request.build_opener(DirectResponses(), TrackSocket())


class SiteRequests:
    def __init__(self) -> None:
        self.opener = urllib.request.build_opener(DirectResponses())
        self.retry_deadline: float | None = None

    def get(self, url: str, *, read_body: bool = False) -> bytes:
        if self.retry_deadline is None:
            return self.read(self.opener, url, read_body, HTTP_TIMEOUT_SECONDS)
        now = time.monotonic()
        if self.retry_deadline <= now:
            raise CheckFailed(problem(url, "HTTP 200", "retry window elapsed"))
        deadline = min(self.retry_deadline, now + HTTP_TIMEOUT_SECONDS)
        timed_out = CheckFailed(problem(url, "HTTP 200", "retry timed out"))
        expired = Event()
        active_socket: socket.socket | None = None

        def interrupt() -> None:
            expired.set()
            if active_socket is not None:
                with suppress(OSError):
                    socket.socket.shutdown(active_socket, socket.SHUT_RDWR)

        def connected(sock: socket.socket | None) -> None:
            nonlocal active_socket
            active_socket = sock
            if expired.is_set() or time.monotonic() >= deadline:
                interrupt()

        opener = retry_opener(connected)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise timed_out
        # Socket timeouts bound idle reads. Shut down the connection when the
        # absolute deadline expires, even if the server keeps sending bytes.
        timer = Timer(remaining, interrupt)
        timer.start()
        try:
            try:
                body = self.read(opener, url, read_body, remaining)
            except CheckFailed:
                if not expired.is_set() and time.monotonic() < deadline:
                    raise
                raise timed_out from None
            if expired.is_set() or time.monotonic() >= deadline:
                raise timed_out
            return body
        finally:
            timer.cancel()
            timer.join()

    @staticmethod
    def read(
        opener: urllib.request.OpenerDirector, url: str, read_body: bool, timeout: float
    ) -> bytes:
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT}, method="GET"
            )
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200:
                    raise CheckFailed(
                        problem(url, "HTTP 200", f"HTTP {response.status}")
                    )
                return response.read() if read_body else b""
        except (OSError, ValueError, http.client.HTTPException) as error:
            raise CheckFailed(problem(url, "HTTP 200", str(error))) from None


class HomeMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.language: str | None = None
        self.generator: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        elif tag == "meta" and (values.get("name") or "").lower() == "generator":
            self.generator = values.get("content")


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


def check_home(requests: SiteRequests, url: str, astro_version: str) -> list[str]:
    metadata = HomeMetadata()
    metadata.feed(requests.get(url, read_body=True).decode("utf-8", errors="replace"))
    generator = f"Astro v{astro_version}"
    return [
        problem(url, f"{field} {expected!r}", f"{received!r}")
        for field, expected, received in (
            ("HTML language", "fr-CA", metadata.language),
            ("generator", generator, metadata.generator),
        )
        if expected != received
    ]


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
    base: str, astro_version: str | None, retry_seconds: float
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
    requests = SiteRequests()
    checks = [
        (3, partial(check_home, requests, base, astro_version)),
        (2, partial(check_rss, requests, urljoin(base, "rss.xml"))),
        (1, partial(check_status, requests, urljoin(base, "sitemap-index.xml"))),
        (2, partial(check_robots, requests, urljoin(base, "robots.txt"))),
    ]
    count = sum(size for size, _ in checks)
    pending = [check for _, check in checks]
    deadline = time.monotonic() + retry_seconds
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
        requests.retry_deadline = deadline
        time.sleep(RETRY_INTERVAL_SECONDS)


def failures(
    base: str,
    astro_version: str | None = None,
    retry_seconds: float = RETRY_WINDOW_SECONDS,
) -> list[str]:
    """Return errors for the live site after retrying the checks that fail."""
    _, messages = verify(base, astro_version, retry_seconds)
    return messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="just verify-live", description=__doc__)
    parser.add_argument("base", nargs="?", default=DEFAULT_BASE)
    args = parser.parse_args(argv)
    try:
        count, messages = verify(args.base, None, RETRY_WINDOW_SECONDS)
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
