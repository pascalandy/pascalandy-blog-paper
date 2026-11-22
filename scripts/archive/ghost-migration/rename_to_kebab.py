#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Rename Images to Kebab-Case

Normalizes image filenames to kebab-case while preserving meaningful numbers.

Rules:
- All lowercase
- Underscores → hyphens
- Remove Ghost timestamps (13-digit numbers like -1467085572429)
- Clean up double/triple hyphens
- Preserve sequence numbers (-01, -02, -032, etc.)
- Preserve event numbers (017-, 025b-, etc.)
- Extension lowercase

Usage:
    uv run scripts/rename_to_kebab.py --dry-run  # Preview changes
    uv run scripts/rename_to_kebab.py            # Apply changes
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# --- Configuration ---
IMAGE_DIR = Path("public/og-legacy")
MARKDOWN_DIRS = [Path("to_import"), Path("src/data/blog")]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Ghost timestamp pattern: 13-digit number at end of filename
GHOST_TIMESTAMP = re.compile(r"-\d{13}$")

# Redundant suffixes to remove (case-insensitive)
REDUNDANT_PATTERNS = [
    r"_Crypto-In-Montreal_par-Pascal-Andy",
    r"_CryptoInMontreal-par-Pascal-Andy",
    r"_par-Pascal-Andy",
]


def to_kebab_case(filename: str) -> str:
    """
    Convert filename to kebab-case while preserving meaningful structure.

    Preserves:
    - Leading numbers (event IDs): 017-, 025b-
    - Trailing numbers (sequence): -02, -032
    - Date prefixes: 2003-09-19-
    """
    name = filename

    # Remove Ghost timestamps (13-digit numbers)
    name = GHOST_TIMESTAMP.sub("", name)

    # Remove redundant patterns
    for pattern in REDUNDANT_PATTERNS:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)

    # Replace underscores with hyphens
    name = name.replace("_", "-")

    # Convert to lowercase
    name = name.lower()

    # Fix common encoding issues
    name = name.replace("montre-al", "montreal")
    name = name.replace("e-conomie", "economie")
    name = name.replace("re-novation", "renovation")

    # Clean up multiple hyphens (but preserve double hyphens in dates like ---02)
    # First, temporarily protect sequence patterns like ---02
    name = re.sub(r"---(\d)", r"__SEQ__\1", name)
    # Then clean up other multiple hyphens
    name = re.sub(r"-{2,}", "-", name)
    # Restore sequence patterns as single hyphen + number
    name = re.sub(r"__SEQ__(\d)", r"-\1", name)

    # Remove leading/trailing hyphens
    name = name.strip("-")

    # Remove trailing hyphen before extension would go
    name = re.sub(r"-$", "", name)

    return name


def get_new_filename(old_name: str) -> str:
    """Generate new kebab-case filename."""
    stem = Path(old_name).stem
    ext = Path(old_name).suffix.lower()

    new_stem = to_kebab_case(stem)

    return f"{new_stem}{ext}"


def find_all_images() -> list[Path]:
    """Find all image files in the image directory."""
    images = []
    if not IMAGE_DIR.exists():
        return images

    for img_path in IMAGE_DIR.rglob("*"):
        if img_path.is_file() and img_path.suffix.lower() in IMAGE_EXTENSIONS:
            if not img_path.name.startswith("."):
                images.append(img_path)

    return sorted(images)


def check_collisions(renames: list[tuple[Path, Path]]) -> list[tuple[Path, Path, Path]]:
    """
    Check for filename collisions after renaming.
    Returns list of (file1, file2, collision_path) tuples.
    """
    collisions = []
    new_paths: dict[Path, Path] = {}

    for old_path, new_path in renames:
        if new_path in new_paths:
            collisions.append((new_paths[new_path], old_path, new_path))
        else:
            new_paths[new_path] = old_path

    return collisions


def find_markdown_references(old_path: Path) -> list[tuple[Path, str]]:
    """Find all markdown files that reference this image."""
    refs = []
    # Build the URL path from the file path
    rel_path = old_path.relative_to(Path("public"))
    url_path = f"/{rel_path}"

    for md_dir in MARKDOWN_DIRS:
        if not md_dir.exists():
            continue
        for md_file in md_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if url_path in content or old_path.name in content:
                    refs.append((md_file, url_path))
            except (OSError, UnicodeDecodeError):
                continue

    return refs


def update_markdown_references(old_path: Path, new_path: Path, dry_run: bool) -> int:
    """Update markdown files to reference the new image path."""
    old_rel = old_path.relative_to(Path("public"))
    new_rel = new_path.relative_to(Path("public"))

    old_url = f"/{old_rel}"
    new_url = f"/{new_rel}"

    updates = 0

    for md_dir in MARKDOWN_DIRS:
        if not md_dir.exists():
            continue
        for md_file in md_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if old_url in content:
                    new_content = content.replace(old_url, new_url)
                    if not dry_run:
                        md_file.write_text(new_content, encoding="utf-8")
                    updates += 1
            except (OSError, UnicodeDecodeError):
                continue

    return updates


def main() -> int:
    parser = argparse.ArgumentParser(description="Rename images to kebab-case")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("Rename Images to Kebab-Case")
    print("=" * 70)

    if args.dry_run:
        print("DRY RUN - No changes will be made\n")

    # Find all images
    print("Scanning for images...")
    images = find_all_images()
    print(f"Found {len(images)} images\n")

    if not images:
        print("No images found.")
        return 0

    # Generate rename plan
    print("Generating rename plan...")
    renames: list[tuple[Path, Path, str]] = []  # (old, new, change_type)
    no_change = 0

    for img_path in images:
        old_name = img_path.name
        new_name = get_new_filename(old_name)

        if old_name == new_name:
            no_change += 1
            continue

        new_path = img_path.parent / new_name

        # Categorize the change
        changes = []
        if old_name.lower() != old_name:
            changes.append("lowercase")
        if "_" in old_name:
            changes.append("underscore")
        if GHOST_TIMESTAMP.search(Path(old_name).stem):
            changes.append("timestamp")
        if any(re.search(p, old_name, re.IGNORECASE) for p in REDUNDANT_PATTERNS):
            changes.append("redundant")
        if "---" in old_name or "--" in old_name:
            changes.append("hyphens")

        change_type = ", ".join(changes) if changes else "normalize"
        renames.append((img_path, new_path, change_type))

    print(f"  Files to rename: {len(renames)}")
    print(f"  Files unchanged: {no_change}")

    if not renames:
        print("\nNo files need renaming.")
        return 0

    # Check for collisions
    print("\nChecking for collisions...")
    collisions = check_collisions([(old, new) for old, new, _ in renames])

    if collisions:
        print(f"\n{'=' * 70}")
        print("COLLISION DETECTED - Cannot proceed!")
        print("=" * 70)
        for file1, file2, collision_path in collisions:
            print(f"\n  These files would both become:")
            print(f"    {collision_path.name}")
            print(f"  From:")
            print(f"    1. {file1}")
            print(f"    2. {file2}")
        print("\nPlease resolve collisions manually before running again.")
        return 1

    print("  No collisions detected.")

    # Show detailed preview
    print(f"\n{'=' * 70}")
    print("RENAME PLAN")
    print("=" * 70)

    # Group by change type
    by_type: dict[str, list[tuple[Path, Path]]] = {}
    for old, new, change_type in renames:
        if change_type not in by_type:
            by_type[change_type] = []
        by_type[change_type].append((old, new))

    for change_type, items in sorted(by_type.items()):
        print(f"\n--- {change_type.upper()} ({len(items)} files) ---")
        for old, new in items[:5]:  # Show first 5 of each type
            print(f"  {old.name}")
            print(f"    → {new.name}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total files to rename: {len(renames)}")
    print(f"  Change types:")
    for change_type, items in sorted(by_type.items()):
        print(f"    - {change_type}: {len(items)}")

    if args.dry_run:
        print(f"\n{'=' * 70}")
        print("DRY RUN COMPLETE")
        print("Run without --dry-run to apply these changes")
        print("=" * 70)
        return 0

    # Apply changes
    print(f"\n{'=' * 70}")
    print("APPLYING CHANGES")
    print("=" * 70)

    renamed = 0
    md_updates = 0
    errors = []

    for old_path, new_path, change_type in renames:
        try:
            # Update markdown references first
            updates = update_markdown_references(old_path, new_path, dry_run=False)
            md_updates += updates

            # Rename the file
            old_path.rename(new_path)
            renamed += 1

            print(f"  ✓ {old_path.name} → {new_path.name}")
            if updates:
                print(f"      (updated {updates} markdown files)")

        except Exception as e:
            errors.append((old_path, str(e)))
            print(f"  ✗ {old_path.name}: {e}")

    print(f"\n{'=' * 70}")
    print("RESULTS")
    print("=" * 70)
    print(f"  Files renamed: {renamed}")
    print(f"  Markdown files updated: {md_updates}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for path, error in errors:
            print(f"  - {path}: {error}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
