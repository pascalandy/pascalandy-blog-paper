#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check image references in source, including drafts, and find unused images."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
# Keep these legacy copies under R17 because external links may use their URLs (issue #182).
RETAINED_PUBLIC_IMAGES = {
    "public/og-legacy/2017/11/rsvp-2.jpg",
    "public/og-legacy/2019/01/026-cryptoinmontreal-1.jpg",
    "public/og-legacy/2019/02/027b-cryptoinmontreal.jpg",
    "public/og-legacy/2019/04/029b-cryptoinmontreal.jpg",
    "public/og-legacy/2019/05/031-cryptoinmontreal.jpg",
}
IMAGES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".avif",
    ".svg",
    ".ico",
    ".bmp",
    ".tif",
    ".tiff",
}
SOURCES = {".md", ".mdx", ".astro", ".ts", ".tsx", ".js", ".jsx", ".css"}


def image_references(source: Path) -> set[str]:
    text = source.read_text(encoding="utf-8")
    if source.suffix in {".md", ".mdx"}:
        text = re.sub(r"(?m)^\s*(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\s*\1\s*$", "", text)
        values = re.findall(r"\]\(\s*<?([^\s)>]+)", text)
        values += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*<?([^\s>]+)", text)
        frontmatter = re.match(r"\A---\n([\s\S]*?)\n---", text)
        if frontmatter:
            values += re.findall(
                r"(?m)^ogImage:\s*['\"]?([^'\"\n]+)", frontmatter.group(1)
            )
    else:
        text = re.sub(r"(?m)^\s*//.*$", "", text)
        text = re.sub(r"<!--[\s\S]*?-->", "", text)
        values = re.findall(r"""["'`]([^"'`\n]+)["'`]""", text)
    values += re.findall(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", text)
    values += re.findall(r"""url\(\s*["']?([^\s)'";]+)""", text)
    return {
        value.strip()
        for value in values
        if Path(urlsplit(value.strip()).path).suffix.lower() in IMAGES
        and not re.search(r"[{}<>]", value)
    }


def inspect(root: Path) -> tuple[list[str], list[str]]:
    root = root.resolve()
    public = root / "public"
    referenced: set[Path] = set()
    missing: set[str] = set()
    for source in sorted((root / "src").rglob("*")):
        if not source.is_file() or source.suffix not in SOURCES:
            continue
        for reference in image_references(source):
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc:
                continue
            target = unquote(parsed.path)
            if target.startswith("@/"):
                path = root / "src" / target[2:]
            elif target.startswith("/"):
                path = public / target.lstrip("/")
            elif target.startswith("."):
                path = source.parent / target
            else:
                path = public / target
            path = path.resolve()
            if not path.is_file():
                generated = root / "src/pages" / target.lstrip("/")
                if target.startswith("/") and any(
                    Path(str(generated) + suffix).is_file() for suffix in (".ts", ".js")
                ):
                    continue
                missing.add(f"{source.relative_to(root)}: missing image {reference}")
            referenced.add(path)
    pagefind = public / "pagefind"
    retained = {root / name for name in RETAINED_PUBLIC_IMAGES}
    orphans = sorted(
        path.relative_to(root).as_posix()
        for directory in (root / "src/assets/images", public)
        for path in directory.rglob("*")
        if not path.is_relative_to(pagefind)
        and path.suffix.lower() in IMAGES
        and path not in retained
        and path.is_file()
        and path.resolve() not in referenced
    )
    return sorted(missing), orphans


def problems(root: Path) -> list[str]:
    missing, orphans = inspect(root)
    return missing + [f"unreferenced image: {name}" for name in orphans]


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(
        "--list-orphans",
        action="store_true",
        help="print the unreferenced image paths",
    )
    args = cli.parse_args()
    if args.list_orphans:
        missing, orphans = inspect(ROOT)
        print("\n".join(orphans))
        errors = missing
    else:
        errors = problems(ROOT)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            "error: fix image references or remove unused images, then run: just check --only images",
            file=sys.stderr,
        )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
