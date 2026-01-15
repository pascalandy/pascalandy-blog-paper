#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Normalize blog post tags to kebab-case multi-line format.

Converts:
    tags: ["Personnel", "Du Fond Des Tripes"]
To:
    tags:
      - personnel
      - du-fond-des-tripes

Rules:
    - Lowercase all characters
    - Replace spaces with hyphens
    - Replace underscores with hyphens
    - Collapse multiple hyphens to single
    - Trim leading/trailing hyphens

Usage:
    uv run scripts/normalize-tags.py --dry-run     # Preview changes
    uv run scripts/normalize-tags.py               # Execute conversion
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


BLOG_DIR = Path("src/data/blog")


def to_kebab_case(tag: str) -> str:
    """Convert a tag to kebab-case."""
    result = tag.lower()
    result = result.replace(" ", "-")
    result = result.replace("_", "-")
    result = re.sub(r"-{2,}", "-", result)
    result = result.strip("-")
    return result


def extract_frontmatter(content: str) -> tuple[dict | None, str, str]:
    """Extract YAML frontmatter, return (frontmatter, raw_yaml, body)."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None, "", content
    try:
        raw_yaml = match.group(1)
        frontmatter = yaml.safe_load(raw_yaml)
        body = match.group(2)
        return frontmatter, raw_yaml, body
    except yaml.YAMLError:
        return None, "", content


def rebuild_frontmatter(raw_yaml: str, new_tags: list[str]) -> str:
    """
    Replace the tags in raw YAML with multi-line kebab-case format.
    Preserves all other frontmatter exactly as-is.
    """
    lines = raw_yaml.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for inline array: tags: ["x", "y"]
        if re.match(r"^\s*tags:\s*\[", line):
            # Replace with multi-line format
            result_lines.append("tags:")
            for tag in new_tags:
                result_lines.append(f"  - {tag}")
            i += 1
            continue

        # Check for multi-line tags start: tags:
        if re.match(r"^\s*tags:\s*$", line):
            result_lines.append("tags:")
            for tag in new_tags:
                result_lines.append(f"  - {tag}")
            i += 1
            # Skip existing tag items
            while i < len(lines) and re.match(r"^\s+-\s+", lines[i]):
                i += 1
            continue

        result_lines.append(line)
        i += 1

    return "\n".join(result_lines)


def process_file(file_path: Path, dry_run: bool) -> tuple[bool, str]:
    """Process a single markdown file. Returns (changed, message)."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Error reading: {e}"

    frontmatter, raw_yaml, body = extract_frontmatter(content)

    if frontmatter is None:
        return False, "No valid frontmatter"

    if "tags" not in frontmatter:
        return False, "No tags field"

    tags = frontmatter["tags"]
    if not isinstance(tags, list):
        return False, f"Tags not a list: {type(tags)}"

    # Convert tags to kebab-case
    new_tags = [to_kebab_case(tag) for tag in tags]

    # Check if inline format or tags need case conversion
    has_inline = bool(re.search(r"tags:\s*\[", raw_yaml))
    tags_changed = tags != new_tags

    if not has_inline and not tags_changed:
        return False, "Already normalized"

    # Rebuild frontmatter with new tags
    new_yaml = rebuild_frontmatter(raw_yaml, new_tags)
    new_content = f"---\n{new_yaml}\n---\n{body}"

    changes = []
    if has_inline:
        changes.append("inline→multiline")
    if tags_changed:
        old_str = ", ".join(tags)
        new_str = ", ".join(new_tags)
        changes.append(f"case: {old_str} → {new_str}")

    if dry_run:
        return True, f"Would fix: {'; '.join(changes)}"

    try:
        file_path.write_text(new_content, encoding="utf-8")
        return True, f"Fixed: {'; '.join(changes)}"
    except Exception as e:
        return False, f"Error writing: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize tags to kebab-case multi-line format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    args = parser.parse_args()

    if not BLOG_DIR.exists():
        print(f"Error: Blog directory not found: {BLOG_DIR}", file=sys.stderr)
        return 1

    md_files = list(BLOG_DIR.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found in {BLOG_DIR}", file=sys.stderr)
        return 1

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(md_files)} files...")
    print()

    changed = 0
    unchanged = 0
    errors = []

    for file_path in sorted(md_files):
        was_changed, message = process_file(file_path, args.dry_run)

        if was_changed:
            changed += 1
            rel_path = file_path.relative_to(BLOG_DIR)
            print(f"  [CHG] {rel_path}: {message}")
        elif "Error" in message or "No valid" in message:
            errors.append((file_path, message))
        else:
            unchanged += 1

    print()
    print("=" * 60)
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Changed:   {changed}")
    print(f"  Unchanged: {unchanged}")
    print(f"  Errors:    {len(errors)}")

    if errors:
        print()
        print("Files with errors:")
        for path, msg in errors[:10]:
            print(f"  - {path.name}: {msg}")

    if args.dry_run and changed > 0:
        print()
        print("Run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
