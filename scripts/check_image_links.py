#!/usr/bin/env uv run python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Image Link Checker for AstroPaper Blog

Validates that all local image references in markdown files point to
existing files. Reports all broken links and exits with error code 1
if any are found.

Usage:
    uv run scripts/check_image_links.py
    uv run scripts/check_image_links.py --verbose
    uv run scripts/check_image_links.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
MARKDOWN_DIR = PROJECT_ROOT / "src" / "data" / "blog"
PUBLIC_DIR = PROJECT_ROOT / "public"
ASSETS_DIR = PROJECT_ROOT / "src" / "assets"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}


@dataclass
class ImageReference:
    """An image reference found in a markdown file."""

    markdown_path: Path
    image_path: str
    line_number: int
    is_external: bool


@dataclass
class BrokenLink:
    """A broken image link."""

    markdown_path: Path
    image_path: str
    line_number: int
    reason: str


def fct_is_external_url(path: str) -> bool:
    """Check if a path is an external URL."""
    return path.startswith(("http://", "https://", "data:", "//"))


def fct_extract_image_references(markdown_dir: Path) -> list[ImageReference]:
    """Extract all image references from markdown files."""
    references: list[ImageReference] = []

    # Match markdown image syntax: ![alt](path)
    md_pattern = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
    # Match HTML img tags: <img src="path">
    html_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)

    if not markdown_dir.exists():
        return references

    for md_file in markdown_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)
            continue

        for line_num, line in enumerate(content.splitlines(), 1):
            # Find markdown image syntax
            for match in md_pattern.finditer(line):
                image_path = match.group(1)
                references.append(
                    ImageReference(
                        markdown_path=md_file,
                        image_path=image_path,
                        line_number=line_num,
                        is_external=fct_is_external_url(image_path),
                    )
                )

            # Find HTML img tags
            for match in html_pattern.finditer(line):
                image_path = match.group(1)
                references.append(
                    ImageReference(
                        markdown_path=md_file,
                        image_path=image_path,
                        line_number=line_num,
                        is_external=fct_is_external_url(image_path),
                    )
                )

    return references


def fct_resolve_local_path(image_path: str, markdown_file: Path) -> Path | None:
    """
    Resolve a local image path to an absolute filesystem path.

    Handles:
    - Absolute paths starting with / (relative to public/)
    - Paths with @/ prefix (src/assets/)
    - Relative paths like ../../assets/ (relative to markdown file)

    Args:
        image_path: The image path as written in markdown
        markdown_file: The markdown file containing the reference

    Returns None if the path format is not recognized.
    """
    # Decode URL-encoded characters
    decoded_path = unquote(image_path)

    # Remove any query string or fragment
    parsed = urlparse(decoded_path)
    clean_path = parsed.path

    # Handle @/ prefix (Astro alias for src/)
    if clean_path.startswith("@/"):
        return PROJECT_ROOT / "src" / clean_path[2:]

    # Handle absolute paths (relative to public/)
    if clean_path.startswith("/"):
        return PUBLIC_DIR / clean_path[1:]

    # Handle relative paths (relative to the markdown file's directory)
    md_dir = markdown_file.parent
    resolved = (md_dir / clean_path).resolve()
    return resolved


def fct_check_image_exists(ref: ImageReference) -> BrokenLink | None:
    """
    Check if a local image reference points to an existing file.

    Returns a BrokenLink if the image doesn't exist, None otherwise.
    """
    resolved_path = fct_resolve_local_path(ref.image_path, ref.markdown_path)

    if resolved_path is None:
        return BrokenLink(
            markdown_path=ref.markdown_path,
            image_path=ref.image_path,
            line_number=ref.line_number,
            reason="Could not resolve path",
        )

    if not resolved_path.exists():
        return BrokenLink(
            markdown_path=ref.markdown_path,
            image_path=ref.image_path,
            line_number=ref.line_number,
            reason=f"File not found: {resolved_path}",
        )

    if not resolved_path.is_file():
        return BrokenLink(
            markdown_path=ref.markdown_path,
            image_path=ref.image_path,
            line_number=ref.line_number,
            reason=f"Path is not a file: {resolved_path}",
        )

    return None


def fct_format_relative_path(path: Path) -> str:
    """Format a path relative to project root for display."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check that all local image references in markdown files exist.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run scripts/check_image_links.py
    uv run scripts/check_image_links.py --verbose
        """,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show all checked images, not just broken ones",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="check_image_links 1.0.0",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Image Link Checker")
    print("=" * 60)

    # Extract all image references
    print(f"\nScanning markdown files in {fct_format_relative_path(MARKDOWN_DIR)}...")
    references = fct_extract_image_references(MARKDOWN_DIR)

    if not references:
        print("No image references found.")
        return 0

    # Separate local and external references
    local_refs = [r for r in references if not r.is_external]
    external_refs = [r for r in references if r.is_external]

    print(f"Found {len(references)} image references:")
    print(f"  - Local: {len(local_refs)}")
    print(f"  - External (skipped): {len(external_refs)}")

    if not local_refs:
        print("\nNo local images to check.")
        return 0

    # Check each local reference
    print("\nChecking local image references...")
    broken_links: list[BrokenLink] = []

    for ref in local_refs:
        broken = fct_check_image_exists(ref)
        if broken:
            broken_links.append(broken)
        elif args.verbose:
            rel_path = fct_format_relative_path(ref.markdown_path)
            print(f"  OK: {rel_path}:{ref.line_number} -> {ref.image_path}")

    # Report results
    print("\n" + "=" * 60)

    if not broken_links:
        print("SUCCESS: All local image references are valid!")
        print("=" * 60)
        return 0

    print(f"FAILED: Found {len(broken_links)} broken image link(s)")
    print("=" * 60)

    # Group by file for cleaner output
    broken_by_file: dict[Path, list[BrokenLink]] = {}
    for broken in broken_links:
        if broken.markdown_path not in broken_by_file:
            broken_by_file[broken.markdown_path] = []
        broken_by_file[broken.markdown_path].append(broken)

    for md_path, links in sorted(broken_by_file.items()):
        rel_path = fct_format_relative_path(md_path)
        print(f"\n{rel_path}:")
        for link in sorted(links, key=lambda x: x.line_number):
            print(f"  Line {link.line_number}: {link.image_path}")
            print(f"    -> {link.reason}")

    print("\n" + "=" * 60)
    print("Fix the broken links above and run again.")
    print("=" * 60)

    return 1


if __name__ == "__main__":
    sys.exit(main())
