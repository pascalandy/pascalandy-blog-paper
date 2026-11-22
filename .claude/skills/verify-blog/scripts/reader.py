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


def check_menu(page: Page, opened: bool, narrow: bool) -> None:
    button = page.locator("#menu-btn")
    panel = page.locator("#menu-items")
    link = panel.locator('a[href="/blog/"]')
    if narrow:
        expect(button).to_be_visible()
        expect(button).to_have_attribute("aria-expanded", str(opened).lower())
        panel.evaluate("""panel => {
            for (const animation of panel.getAnimations()) {
                if (animation instanceof CSSTransition && animation.transitionProperty === "opacity")
                    animation.finish();
            }
        }""")
    else:
        expect(button).to_be_hidden()
    if opened or not narrow:
        expect(panel).to_have_css("opacity", "1")
        expect(link).to_be_visible()
        link.click(trial=True)
    else:
        expect(link).to_be_hidden()
        expect(panel).to_have_css("opacity", "0")


def check_layout(page: Page, width: int) -> None:
    sizes = page.evaluate("""() => {
        const root = document.documentElement;
        return [root.clientWidth, root.scrollWidth];
    }""")
    viewport, content = sizes
    if viewport != width:
        raise ValueError(
            f"expected a {width}px layout viewport, got {viewport}px; check the viewport meta tag"
        )
    if content > viewport:
        raise ValueError(
            f"page overflows horizontally by {content - viewport} CSS pixels"
        )
    if not page.locator("main > :first-child").evaluate("""element => {
        const box = element.getBoundingClientRect();
        return box.left > 0 && box.right < document.documentElement.clientWidth;
    }"""):
        raise ValueError("main content needs a visible inset on both sides")
    if not page.locator("#article iframe").evaluate_all("""frames => frames.every(frame => {
        const box = frame.getBoundingClientRect();
        let left = 0, right = document.documentElement.clientWidth;
        for (let parent = frame.parentElement; parent; parent = parent.parentElement) {
            if (parent.tagName === "ARTICLE" || getComputedStyle(parent).overflowX !== "visible") {
                const bounds = parent.getBoundingClientRect();
                left = Math.max(left, bounds.left + parent.clientLeft);
                right = Math.min(right, bounds.left + parent.clientLeft + parent.clientWidth);
            }
        }
        return box.width > 0 && box.left >= left - 0.5 && box.right <= right + 0.5;
    })"""):
        raise ValueError(
            "embedded video is clipped or extends outside the article or viewport"
        )


def background_luminance(page: Page, theme: str) -> float:
    expect(page.locator("html")).to_have_attribute("data-theme", theme)
    colors = page.evaluate("""() => {
        const sample = document.createElement("span");
        sample.style.cssText = "color:var(--foreground);background-color:var(--background)";
        document.documentElement.append(sample);
        const style = getComputedStyle(sample);
        const colors = [style.color, style.backgroundColor];
        sample.remove();
        return colors;
    }""")
    body = page.locator("body")
    expect(body).to_have_css("color", colors[0])
    expect(body).to_have_css("background-color", colors[1])
    return body.evaluate("""body => {
        const canvas = document.createElement("canvas");
        canvas.width = canvas.height = 1;
        const context = canvas.getContext("2d");
        context.fillStyle = getComputedStyle(body).backgroundColor;
        context.fillRect(0, 0, 1, 1);
        const [r, g, b] = Array.from(context.getImageData(0, 0, 1, 1).data, channel => {
            const v = channel / 255;
            return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }""")


def matrix(base: str, evidence: Path | None) -> int:
    count = 0
    with sync_playwright() as playwright, browse.launch_chromium(playwright) as browser:
        for width, height in VIEWPORTS:
            narrow = width < 640
            phone = (width, height) in ((375, 667), (667, 375))
            light_backgrounds: dict[str, float] = {}
            for theme in ("light", "dark"):
                for label, (path, landmark) in PAGES.items():
                    with browser.new_page(
                        viewport={"width": width, "height": height},
                        color_scheme=theme,
                        is_mobile=phone,
                        has_touch=phone,
                        locale="fr-CA",
                    ) as page:
                        page.route(
                            "https://www.youtube.com/embed/**",
                            lambda route: route.fulfill(
                                content_type="text/html", body=""
                            ),
                        )
                        case = f"{label}-{width}x{height}-{theme}-closed"
                        try:
                            response = page.goto(base + path)
                            if response is None or response.status != 200:
                                raise ValueError(f"expected HTTP 200 from {path}")
                            expect(page.locator(landmark).first).to_be_visible()
                            luminance = background_luminance(page, theme)
                            if theme == "light":
                                light_backgrounds[label] = luminance
                            elif luminance >= light_backgrounds[label]:
                                raise ValueError(
                                    "dark background must paint darker than the light background"
                                )
                            page.evaluate("document.fonts.ready")
                            for opened in (False, True) if narrow else (False,):
                                if opened:
                                    case = f"{label}-{width}x{height}-{theme}-open"
                                    page.locator("#menu-btn").click()
                                check_layout(page, width)
                                check_menu(page, opened, narrow)
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
                            if narrow:
                                page.locator("#menu-btn").click()
                                check_menu(page, False, narrow)
                        except (Error, ValueError, AssertionError) as error:
                            raise ValueError(f"{case} on {path}: {error}") from error
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
