#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check emitted CSS needed by older Safari versions."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKDROP_FILTER = "backdrop" + "-filter"
WEBKIT_BACKDROP_FILTER = "-webkit-" + BACKDROP_FILTER
SELECTORS = (
    ".backdrop-blur-sm",
    ".backdrop-blur-lg",
    r".md\:backdrop-blur-lg",
)


class MenuOverlayParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.classes: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id") == "menu-overlay":
            self.classes = (values.get("class") or "").split()


def check(dist: Path) -> list[str]:
    files = list((dist / "_astro").glob("Footer.*.css"))
    if len(files) != 1:
        return [
            f"expected one Footer CSS file in {dist / '_astro'}, found {len(files)}"
        ]

    css = files[0].read_text(encoding="utf-8")
    errors = []
    for selector in SELECTORS:
        rules = re.findall(re.escape(selector) + r"\s*\{([^{}]*)\}", css)
        if len(rules) != 1:
            errors.append(
                f"{selector}: expected one rule in {files[0]}, found {len(rules)}"
            )
            continue
        names = [part.partition(":")[0].strip() for part in rules[0].split(";")]
        for property_name in (WEBKIT_BACKDROP_FILTER, BACKDROP_FILTER):
            count = names.count(property_name)
            if count != 1:
                errors.append(
                    f"{selector}: expected one {property_name} declaration, found {count}"
                )

    transition_pattern = r"(?:^|[;{])\s*transition-property\s*:[^;}]*" + re.escape(
        WEBKIT_BACKDROP_FILTER
    )
    if not re.search(transition_pattern, css):
        errors.append(f"transition-property lost {WEBKIT_BACKDROP_FILTER}")

    min_width = len(re.findall(r"\(\s*min-width\s*:", css))
    range_width = len(re.findall(r"\(\s*width\s*>=", css))
    if min_width != 11 or range_width != 0:
        errors.append(
            f"media breakpoints: expected 11 min-width and 0 width>=, found {min_width} and {range_width}"
        )

    home = dist / "index.html"
    if not home.is_file():
        errors.append(f"missing built home page: {home}")
    else:
        parser = MenuOverlayParser()
        parser.feed(home.read_text(encoding="utf-8"))
        if parser.classes is None or "backdrop-blur-sm" not in parser.classes:
            errors.append(
                "#menu-overlay on the built home page must use backdrop-blur-sm"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    errors = check(args.dist)
    if errors:
        print("CSS compatibility check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
