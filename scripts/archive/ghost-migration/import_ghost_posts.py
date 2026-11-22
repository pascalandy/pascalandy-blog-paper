#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
Import Ghost CMS posts into Astro blog.

Plan:
1. Scan all 146 source posts for S3 image references
2. For each image:
   - Check if it exists in src/assets/images/og-legacy/
   - If NOT, copy from to_import/img_to_import/
3. Update image paths in posts to point to og-legacy/

Usage:
    uv run scripts/import_ghost_posts.py <list_file>           # dry run
    uv run scripts/import_ghost_posts.py <list_file> --execute # actually copy

Example:
    uv run scripts/import_ghost_posts.py dashboard_imports/03_medium_confidence.txt
"""

import re
import shutil
import sys
from pathlib import Path


def get_list_file() -> str:
    """Get list file from command line args."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("Usage: uv run scripts/import_ghost_posts.py <list_file> [--execute]")
        print(
            "Example: uv run scripts/import_ghost_posts.py dashboard_imports/03_medium_confidence.txt"
        )
        sys.exit(1)
    return args[0]


# Define the import order - earlier lists take precedence
IMPORT_ORDER = [
    "02_high_confidence.txt",
    "03_medium_confidence.txt",
    "04_needs_review.txt",
    "05_critical.txt",
    "06_major.txt",
    "07_moderate.txt",
    "08_minor.txt",
    "09_word_delta.txt",
]


def get_already_imported_slugs(base_dir: Path, current_list: str) -> set[str]:
    """Get slugs from lists that come BEFORE the current list in import order."""
    already_imported: set[str] = set()
    dashboard_dir = base_dir / "dashboard_imports"

    current_index = -1
    for i, name in enumerate(IMPORT_ORDER):
        if name == current_list:
            current_index = i
            break

    if current_index <= 0:
        return already_imported  # First list or not found

    # Read all previous lists
    for name in IMPORT_ORDER[:current_index]:
        list_file = dashboard_dir / name
        if list_file.exists():
            with open(list_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        already_imported.add(line)

    return already_imported


# S3 URL pattern: https://s3.amazonaws.com/g00000017_001/2016/May/file.jpg
S3_PATTERN = re.compile(
    r"https?://s3\.amazonaws\.com/g00000017_001/(\d{4})/(\w+)/([^)\s]+)"
)


def find_referenced_images(content: str) -> list[tuple[str, str, str]]:
    """Find all S3 image references. Returns list of (year, month, filename)."""
    return S3_PATTERN.findall(content)


def fix_image_paths(content: str) -> tuple[str, int]:
    """Replace S3 URLs with local paths (flattened without g00000017_001)."""

    def replacer(match: re.Match) -> str:
        year, month, filename = match.groups()
        # Flatten: og-legacy/2016/May/filename.jpg (no g00000017_001)
        return f"../../assets/images/og-legacy/{year}/{month}/{filename}"

    new_content, count = S3_PATTERN.subn(replacer, content)
    return new_content, count


def main() -> None:
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("DRY RUN MODE (use --execute to actually copy files)\n")

    # Paths
    base_dir = Path(__file__).parent.parent
    source_dir = base_dir / "to_import/ghost_bkp/posts_extracted_md"
    dest_dir = base_dir / "src/data/blog"
    list_file = base_dir / get_list_file()

    print(f"List file: {list_file.name}")

    # Image paths (source has g00000017_001, dest is flattened)
    img_source_dir = base_dir / "to_import/img_to_import/g00000017_001"
    img_dest_dir = base_dir / "src/assets/images/og-legacy"

    # Get slugs already imported from previous lists
    already_imported = get_already_imported_slugs(base_dir, list_file.name)
    if already_imported:
        print(f"Excluding {len(already_imported)} slugs from previous lists\n")

    # Read the list of posts to import (excluding already imported)
    posts_to_import: list[str] = []
    skipped_already_imported: list[str] = []
    with open(list_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line in already_imported:
                skipped_already_imported.append(line)
            else:
                posts_to_import.append(line)

    print(f"Found {len(posts_to_import)} posts to import")
    if skipped_already_imported:
        print(f"Skipped {len(skipped_already_imported)} (already in previous lists)\n")
    else:
        print()

    # Step 1: Scan all posts for S3 image references
    print("=== Step 1: Scanning posts for S3 image references ===")
    all_images: set[tuple[str, str, str]] = set()
    post_contents: dict[str, str] = {}

    for slug in posts_to_import:
        source_file = source_dir / f"{slug}.md"
        if source_file.exists():
            content = source_file.read_text(encoding="utf-8")
            post_contents[slug] = content
            images = find_referenced_images(content)
            all_images.update(images)

    print(f"Found {len(all_images)} unique S3 images referenced\n")

    # Step 2: Check which images need to be copied
    print("=== Step 2: Checking image availability ===")
    images_already_exist: list[str] = []
    images_to_copy: list[tuple[Path, Path, str]] = []  # (src, dst, display_name)
    images_missing: list[str] = []

    for year, month, filename in sorted(all_images):
        display_name = f"{year}/{month}/{filename}"

        # Destination: flattened (no g00000017_001)
        dst = img_dest_dir / year / month / filename

        # Source: has g00000017_001 prefix
        src = img_source_dir / year / month / filename

        if dst.exists():
            images_already_exist.append(display_name)
        elif src.exists():
            images_to_copy.append((src, dst, display_name))
        else:
            images_missing.append(display_name)

    print(f"  Already in og-legacy:  {len(images_already_exist)}")
    print(f"  To copy from Ghost:    {len(images_to_copy)}")
    print(f"  Missing (not found):   {len(images_missing)}")

    if images_to_copy:
        print("\n  Images to copy:")
        for _, _, name in images_to_copy:
            print(f"    {name}")

    if images_missing:
        print("\n  WARNING - Missing images (not in Ghost backup):")
        for name in images_missing:
            print(f"    {name}")

    # Step 3: Copy images (if not dry run)
    if not dry_run and images_to_copy:
        print("\n=== Step 3: Copying images ===")
        for src, dst, name in images_to_copy:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Copied: {name}")
        print(f"  Total copied: {len(images_to_copy)}")

    # Step 4: Import posts with fixed paths
    print(f"\n=== {'Step 3' if dry_run else 'Step 4'}: Posts ===")
    would_create = 0
    would_overwrite = 0
    skipped = 0
    total_img_fixes = 0
    errors: list[str] = []

    for slug in posts_to_import:
        source_file = source_dir / f"{slug}.md"
        dest_file = dest_dir / f"{slug}.md"

        if not source_file.exists():
            errors.append(f"Source not found: {slug}.md")
            skipped += 1
            continue

        exists = dest_file.exists()
        content = post_contents.get(slug, source_file.read_text(encoding="utf-8"))
        fixed_content, img_fixes = fix_image_paths(content)
        total_img_fixes += img_fixes

        suffix = f" ({img_fixes} img fixes)" if img_fixes > 0 else ""

        if dry_run:
            action = "would overwrite" if exists else "would create"
            print(f"  {action}: {slug}.md{suffix}")
        else:
            dest_file.write_text(fixed_content, encoding="utf-8")
            action = "overwritten" if exists else "created"
            print(f"  {action}: {slug}.md{suffix}")

        if exists:
            would_overwrite += 1
        else:
            would_create += 1

    # Summary
    print(f"\n=== Summary ===")
    if dry_run:
        print("Would do:")
    else:
        print("Done:")
    print(f"  Posts - Create:       {would_create}")
    print(f"  Posts - Overwrite:    {would_overwrite}")
    print(f"  Posts - Skipped:      {skipped}")
    print(f"  Image path fixes:     {total_img_fixes}")
    print(f"  Images to copy:       {len(images_to_copy)}")
    print(f"  Images already exist: {len(images_already_exist)}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
