#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Fix Broken Image References

Scans markdown files for image references and fixes paths to deleted duplicates
by finding the correct source image.

Usage:
    uv run scripts/fix_broken_refs.py --dry-run  # Preview changes
    uv run scripts/fix_broken_refs.py            # Apply changes
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# --- Configuration ---
MARKDOWN_DIRS = [Path("to_import"), Path("src/data/blog")]
IMAGE_DIR = Path("public/og-legacy")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def get_all_images() -> dict[str, Path]:
    """
    Build a lookup of filename (lowercase) -> full path for all images.
    If multiple images have the same filename, keep the one with largest size.
    """
    images: dict[str, Path] = {}
    sizes: dict[str, int] = {}

    if not IMAGE_DIR.exists():
        return images

    for img_path in IMAGE_DIR.rglob("*"):
        if img_path.is_file() and img_path.suffix.lower() in IMAGE_EXTENSIONS:
            filename = img_path.name.lower()
            size = img_path.stat().st_size

            # Keep the largest version if duplicate filenames exist
            if filename not in images or size > sizes[filename]:
                images[filename] = img_path
                sizes[filename] = size

    return images


def extract_image_refs(content: str) -> list[tuple[str, int, int, str]]:
    """
    Extract image references from markdown content.
    Returns list of (full_match, start_pos, end_pos, path).
    """
    refs = []

    # Markdown image: ![alt](path)
    md_pattern = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for match in md_pattern.finditer(content):
        path = match.group(1)
        if "/og-legacy/" in path:
            refs.append((match.group(0), match.start(), match.end(), path))

    return refs


def find_replacement(ref_path: str, images: dict[str, Path]) -> str | None:
    """
    Given a broken reference path, try to find the correct image.
    Returns the new path or None if not found.
    """
    # Extract filename from path
    # e.g., /og-legacy/2017/10/Re-novation-Studio-Transology-032.jpg
    filename = Path(ref_path).name.lower()

    if filename in images:
        # Found a match - build the new path
        img_path = images[filename]
        # Convert to URL path: public/og-legacy/... -> /og-legacy/...
        rel_path = img_path.relative_to(Path("public"))
        return f"/{rel_path}"

    return None


def check_image_exists(ref_path: str) -> bool:
    """Check if the referenced image exists."""
    # /og-legacy/... -> public/og-legacy/...
    if ref_path.startswith("/"):
        file_path = Path("public") / ref_path.lstrip("/")
    else:
        file_path = Path("public") / ref_path

    return file_path.exists()


def process_markdown_file(
    md_path: Path, images: dict[str, Path], dry_run: bool
) -> list[dict]:
    """
    Process a single markdown file, fixing broken image references.
    Returns list of changes made.
    """
    changes = []

    try:
        content = md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"  Warning: Could not read {md_path}: {e}")
        return changes

    refs = extract_image_refs(content)
    new_content = content

    for full_match, start, end, ref_path in reversed(
        refs
    ):  # Reverse to preserve positions
        if check_image_exists(ref_path):
            continue  # Image exists, no fix needed

        # Image doesn't exist - try to find replacement
        replacement = find_replacement(ref_path, images)

        if replacement:
            # Build new match string
            new_match = full_match.replace(ref_path, replacement)
            new_content = new_content[:start] + new_match + new_content[end:]

            changes.append(
                {
                    "file": str(md_path),
                    "old_path": ref_path,
                    "new_path": replacement,
                }
            )
        else:
            changes.append(
                {
                    "file": str(md_path),
                    "old_path": ref_path,
                    "new_path": None,
                    "error": "No replacement found",
                }
            )

    if changes and not dry_run:
        # Only write if there were actual fixes (not just errors)
        fixes = [c for c in changes if c.get("new_path")]
        if fixes:
            md_path.write_text(new_content, encoding="utf-8")

    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix broken image references")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Fix Broken Image References")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN - No changes will be made\n")

    # Build image lookup
    print("Building image index...")
    images = get_all_images()
    print(f"Found {len(images)} unique images\n")

    # Process markdown files
    all_changes = []
    files_processed = 0

    for md_dir in MARKDOWN_DIRS:
        if not md_dir.exists():
            continue

        print(f"Processing {md_dir}/...")
        for md_path in md_dir.rglob("*.md"):
            changes = process_markdown_file(md_path, images, args.dry_run)
            if changes:
                all_changes.extend(changes)
            files_processed += 1

    # Report results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    fixes = [c for c in all_changes if c.get("new_path")]
    errors = [c for c in all_changes if not c.get("new_path")]

    print(f"Files processed: {files_processed}")
    print(f"Broken references found: {len(all_changes)}")
    print(f"Fixed: {len(fixes)}")
    print(f"Could not fix: {len(errors)}")

    if fixes:
        print("\n" + "-" * 60)
        print("FIXES APPLIED:" if not args.dry_run else "FIXES TO APPLY:")
        print("-" * 60)
        for change in fixes:
            print(f"\n  File: {change['file']}")
            print(f"  Old:  {change['old_path']}")
            print(f"  New:  {change['new_path']}")

    if errors:
        print("\n" + "-" * 60)
        print("COULD NOT FIX (image not found):")
        print("-" * 60)
        for change in errors:
            print(f"\n  File: {change['file']}")
            print(f"  Path: {change['old_path']}")

    if args.dry_run and fixes:
        print("\n" + "=" * 60)
        print("Run without --dry-run to apply these fixes")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
