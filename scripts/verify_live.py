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
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from functools import partial
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

DEFAULT_BASE = "https://pascalandy.com/"
PACKAGE_JSON = Path(__file__).resolve().parents[1] / "package.json"
RETRY_WINDOW_SECONDS = 120
RETRY_INTERVAL_SECONDS = 10
HTTP_TIMEOUT_SECONDS = 10
USER_AGENT = "pascalandy-blog-verify-live"


class CheckFailed(Exception):
    """A failed HTTP check with its URL and expected and received values."""


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


def get(url: str, *, read_body: bool = False) -> bytes:
    try:
        if urlsplit(url).scheme not in {"http", "https"}:
            raise CheckFailed(problem(url, "HTTP(S) URL", "unsupported scheme"))
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT}, method="GET"
        )
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise CheckFailed(problem(url, "HTTP 200", f"HTTP {response.status}"))
            return response.read() if read_body else b""
    except urllib.error.HTTPError as error:
        error.close()
        raise CheckFailed(problem(url, "HTTP 200", f"HTTP {error.code}")) from None
    except (OSError, ValueError, http.client.HTTPException) as error:
        raise CheckFailed(problem(url, "HTTP 200", str(error))) from None


def check_home(url: str, astro_version: str) -> list[str]:
    metadata = HomeMetadata()
    metadata.feed(get(url, read_body=True).decode("utf-8", errors="replace"))
    generator = f"Astro v{astro_version}"
    return [
        problem(url, f"{field} {expected!r}", f"{received!r}")
        for field, expected, received in (
            ("HTML language", "fr-CA", metadata.language),
            ("generator", generator, metadata.generator),
        )
        if expected != received
    ]


def check_rss(url: str) -> list[str]:
    body = get(url, read_body=True)
    try:
        link = (ET.fromstring(body).findtext("./channel/item/link") or "").strip()
    except ET.ParseError:
        raise CheckFailed(problem(url, "RSS XML", "invalid XML")) from None
    if not link:
        raise CheckFailed(problem(url, "first RSS item link", "no link"))
    return check_status(urljoin(url, link))


def check_robots(url: str) -> list[str]:
    robots = get(url, read_body=True).decode("utf-8", errors="replace")
    for line in robots.splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "sitemap" and value.strip():
            return check_status(urljoin(url, value.strip()))
    raise CheckFailed(problem(url, "Sitemap directive with a URL", "no Sitemap URL"))


def check_status(url: str) -> list[str]:
    get(url)
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
    checks = [
        (3, partial(check_home, base, astro_version)),
        (2, partial(check_rss, urljoin(base, "rss.xml"))),
        (1, partial(check_status, urljoin(base, "sitemap-index.xml"))),
        (2, partial(check_robots, urljoin(base, "robots.txt"))),
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
        time.sleep(RETRY_INTERVAL_SECONDS)


def failures(
    base: str, astro_version: str | None = None, retry_seconds: float = 120
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
