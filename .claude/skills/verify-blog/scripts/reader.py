#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.56.0"]
# ///
"""Exercise the reader matrix against a built copy of the blog."""

from __future__ import annotations

import argparse
import functools
import http.server
import sys
import threading
from pathlib import Path

import browse
from playwright.sync_api import Error, Page, expect, sync_playwright

VIEWPORTS = (
    (375, 667),
    (667, 375),
    (639, 900),
    (640, 900),
    (768, 1024),
    (1024, 768),
    (1440, 900),
)
PAGES = {
    "home": ("/", "#hero"),
    "blog": ("/blog/", "main a[href^='/blog/']"),
    "post": ("/blog/cim-06/", "#article iframe"),
    "tags": ("/tags/", "main a[href^='/tags/']"),
    "search": ("/search/", ".pagefind-ui__search-input"),
}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def check_layout(page: Page, opened: bool, mobile: bool) -> None:
    button = page.locator("#menu-btn")
    link = page.locator('#menu-items a[href="/blog/"]')
    if mobile:
        expect(button).to_be_visible()
        expect(button).to_have_attribute("aria-expanded", str(opened).lower())
    else:
        expect(button).to_be_hidden()
    if opened or not mobile:
        expect(link).to_be_visible()
        link.click(trial=True)
    else:
        expect(link).to_be_hidden()

    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    if overflow > 0:
        raise ValueError(f"page overflows horizontally by {overflow} CSS pixels")
    for frame in page.locator("#article iframe").all():
        if not frame.evaluate("""frame => {
            const box = frame.getBoundingClientRect(), article = frame.closest("article").getBoundingClientRect();
            return box.width > 0 && box.left >= article.left - 1 && box.right <= article.right + 1;
        }"""):
            raise ValueError(
                "embedded video extends outside the article; check its responsive width"
            )


def matrix(base: str, evidence: Path | None) -> int:
    count = 0
    with sync_playwright() as playwright, browse.launch_chromium(playwright) as browser:
        for width, height in VIEWPORTS:
            mobile = width < 640
            for theme in ("light", "dark"):
                with browser.new_context(
                    viewport={"width": width, "height": height},
                    color_scheme=theme,
                    locale="fr-CA",
                ) as context:
                    context.route(
                        "https://www.youtube.com/embed/**",
                        lambda route: route.fulfill(content_type="text/html", body=""),
                    )
                    for label, (path, landmark) in PAGES.items():
                        with context.new_page() as page:
                            page.set_default_timeout(5000)
                            case = f"{label}-{width}x{height}-{theme}-closed"
                            try:
                                response = page.goto(base + path)
                                if response is None or response.status != 200:
                                    raise ValueError(f"expected HTTP 200 from {path}")
                                expect(page.locator(landmark).first).to_be_visible()
                                expect(page.locator("html")).to_have_attribute(
                                    "data-theme", theme
                                )
                                page.evaluate("document.fonts.ready")
                                for opened in (False, True) if mobile else (False,):
                                    if opened:
                                        case = f"{label}-{width}x{height}-{theme}-open"
                                        page.locator("#menu-btn").click()
                                    check_layout(page, opened, mobile)
                                    if evidence:
                                        page.screenshot(
                                            path=evidence / f"{case}.png",
                                            animations="disabled",
                                        )
                                        (evidence / f"{case}.txt").write_text(
                                            page.locator("body").aria_snapshot() + "\n",
                                            encoding="utf-8",
                                        )
                                    count += 1
                            except (Error, ValueError, AssertionError) as error:
                                raise ValueError(
                                    f"{case} on {path}: {error}"
                                ) from error
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dist", type=Path, help="production build containing the Pagefind index"
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        help="empty directory for each case's screenshot and accessibility tree",
    )
    args = parser.parse_args()
    try:
        if not (args.dist / "pagefind/pagefind.js").is_file():
            raise ValueError(f"{args.dist} has no Pagefind index; build the blog first")
        if args.evidence:
            args.evidence.mkdir(parents=True, exist_ok=True)
            if any(args.evidence.iterdir()):
                raise ValueError(f"use an empty evidence directory: {args.evidence}")
        handler = functools.partial(QuietHandler, directory=args.dist.resolve())
        with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                count = matrix(f"http://127.0.0.1:{server.server_port}", args.evidence)
            finally:
                server.shutdown()
                thread.join()
        print(f"{count} reader matrix cases passed")
        return 0
    except (OSError, ValueError, Error, AssertionError) as error:
        print(f"reader QA failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
