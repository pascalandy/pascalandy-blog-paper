#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Image Analysis Script for Ghost to Astro Migration

Analyzes images in og-legacy folder to:
1. Find duplicates by base filename
2. Recommend source image (largest file size) per group
3. Cross-reference with markdown posts to find orphaned images
4. Generate a cleanup report

Usage: uv run scripts/analyze_images.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# --- Configuration ---
OG_LEGACY_DIR = Path("public/og-legacy")
MARKDOWN_DIRS = [Path("to_import"), Path("src/data/blog")]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

# Pattern to strip Ghost suffixes: -1, -2, _o-1, _o-2, etc.
SUFFIX_PATTERN = re.compile(r"(-\d+|_o-\d+)$", re.IGNORECASE)


@dataclass
class ImageFile:
    """Represents a single image file."""

    path: Path
    filename: str
    base_name: str
    extension: str
    size_bytes: int

    @classmethod
    def from_path(cls, path: Path) -> ImageFile:
        stem = path.stem
        # Strip Ghost suffixes to get base name
        base_name = SUFFIX_PATTERN.sub("", stem)
        return cls(
            path=path,
            filename=path.name,
            base_name=base_name,
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
        )


@dataclass
class ImageGroup:
    """A group of images sharing the same base name."""

    base_name: str
    images: list[ImageFile] = field(default_factory=list)

    @property
    def source_image(self) -> ImageFile:
        """Return the largest image as the recommended source."""
        return max(self.images, key=lambda x: x.size_bytes)

    @property
    def duplicates(self) -> list[ImageFile]:
        """Return images that are NOT the source (candidates for removal)."""
        source = self.source_image
        return [img for img in self.images if img.path != source.path]

    @property
    def total_duplicate_size(self) -> int:
        """Total bytes that could be saved by removing duplicates."""
        return sum(img.size_bytes for img in self.duplicates)


@dataclass
class ImageReference:
    """An image reference found in a markdown file."""

    markdown_path: Path
    image_path: str  # The path as written in markdown
    line_number: int


def scan_images(directory: Path) -> list[ImageFile]:
    """Scan directory recursively for image files."""
    images = []
    if not directory.exists():
        return images

    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            # Skip .DS_Store and other hidden files
            if file_path.name.startswith("."):
                continue
            images.append(ImageFile.from_path(file_path))

    return images


def group_images_by_base_name(images: list[ImageFile]) -> dict[str, ImageGroup]:
    """Group images by their base name (with extension for uniqueness)."""
    groups: dict[str, ImageGroup] = {}

    for img in images:
        # Key: base_name + extension (e.g., "photo.jpg" and "photo.png" are different)
        key = f"{img.base_name}{img.extension}"
        if key not in groups:
            groups[key] = ImageGroup(base_name=key)
        groups[key].images.append(img)

    return groups


def extract_image_references(markdown_dirs: list[Path]) -> list[ImageReference]:
    """Extract all image references from markdown files."""
    references = []
    # Match markdown image syntax: ![alt](path) and also HTML <img src="path">
    md_pattern = re.compile(r"!\[.*?\]\(([^)]+)\)")
    html_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')

    for directory in markdown_dirs:
        if not directory.exists():
            continue

        for md_file in directory.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for line_num, line in enumerate(content.splitlines(), 1):
                for match in md_pattern.finditer(line):
                    references.append(
                        ImageReference(
                            markdown_path=md_file,
                            image_path=match.group(1),
                            line_number=line_num,
                        )
                    )
                for match in html_pattern.finditer(line):
                    references.append(
                        ImageReference(
                            markdown_path=md_file,
                            image_path=match.group(1),
                            line_number=line_num,
                        )
                    )

    return references


def normalize_image_path(ref_path: str) -> str | None:
    """
    Normalize an image reference path to match against og-legacy files.
    Returns the relative path within og-legacy, or None if not an og-legacy ref.
    """
    # Handle various path formats:
    # /content/og-legacy/2017/04/file.jpg
    # ../content/og-legacy/2017/04/file.jpg
    # /og-legacy/2017/04/file.jpg

    # Skip external URLs
    if ref_path.startswith(("http://", "https://", "data:")):
        return None

    # Extract og-legacy path
    patterns = [
        r"/content/og-legacy/(.+)",
        r"\.\./content/og-legacy/(.+)",
        r"/og-legacy/(.+)",
        r"og-legacy/(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, ref_path)
        if match:
            return match.group(1)

    return None


def analyze_usage(
    images: list[ImageFile], references: list[ImageReference]
) -> tuple[set[Path], set[Path], dict[Path, list[ImageReference]]]:
    """
    Analyze which images are used vs orphaned.

    Returns:
        - used_images: Set of image paths that are referenced
        - orphaned_images: Set of image paths that are not referenced
        - usage_map: Map of image path to list of references
    """
    # Build a lookup of normalized filename -> image paths
    filename_to_paths: dict[str, list[Path]] = defaultdict(list)
    for img in images:
        # Index by full relative path and just filename
        rel_path = img.path.relative_to(OG_LEGACY_DIR)
        filename_to_paths[str(rel_path)].append(img.path)
        filename_to_paths[img.filename.lower()].append(img.path)

    used_images: set[Path] = set()
    usage_map: dict[Path, list[ImageReference]] = defaultdict(list)

    for ref in references:
        normalized = normalize_image_path(ref.image_path)
        if normalized is None:
            continue

        # Try to match by full path first, then by filename
        matched_paths = filename_to_paths.get(normalized)
        if not matched_paths:
            # Try just the filename
            filename = Path(normalized).name.lower()
            matched_paths = filename_to_paths.get(filename)

        if matched_paths:
            for path in matched_paths:
                used_images.add(path)
                usage_map[path].append(ref)

    all_image_paths = {img.path for img in images}
    orphaned_images = all_image_paths - used_images

    return used_images, orphaned_images, dict(usage_map)


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def generate_report(
    groups: dict[str, ImageGroup],
    used_images: set[Path],
    orphaned_images: set[Path],
    usage_map: dict[Path, list[ImageReference]],
    images: list[ImageFile],
) -> dict:
    """Generate a comprehensive analysis report."""
    # Find groups with actual duplicates (more than 1 image)
    duplicate_groups = {k: v for k, v in groups.items() if len(v.images) > 1}

    # Calculate statistics
    total_images = len(images)
    total_size = sum(img.size_bytes for img in images)
    total_duplicates = sum(len(g.duplicates) for g in duplicate_groups.values())
    duplicate_size = sum(g.total_duplicate_size for g in duplicate_groups.values())

    report = {
        "summary": {
            "total_images": total_images,
            "total_size": format_size(total_size),
            "total_size_bytes": total_size,
            "duplicate_groups": len(duplicate_groups),
            "total_duplicate_files": total_duplicates,
            "duplicate_size": format_size(duplicate_size),
            "duplicate_size_bytes": duplicate_size,
            "used_images": len(used_images),
            "orphaned_images": len(orphaned_images),
            "potential_savings": format_size(duplicate_size),
        },
        "duplicate_groups": [],
        "orphaned_images": [],
        "cleanup_commands": [],
    }

    # Sort groups by potential savings (descending)
    sorted_groups = sorted(
        duplicate_groups.items(), key=lambda x: x[1].total_duplicate_size, reverse=True
    )

    for base_name, group in sorted_groups:
        source = group.source_image
        group_info = {
            "base_name": base_name,
            "source_image": {
                "path": str(source.path),
                "size": format_size(source.size_bytes),
                "size_bytes": source.size_bytes,
            },
            "duplicates": [
                {
                    "path": str(dup.path),
                    "size": format_size(dup.size_bytes),
                    "size_bytes": dup.size_bytes,
                }
                for dup in group.duplicates
            ],
            "potential_savings": format_size(group.total_duplicate_size),
        }
        report["duplicate_groups"].append(group_info)

        # Generate cleanup commands for duplicates
        for dup in group.duplicates:
            report["cleanup_commands"].append(f'rm "{dup.path}"')

    # List orphaned images (sorted by size, largest first)
    orphaned_list = sorted(
        [img for img in images if img.path in orphaned_images],
        key=lambda x: x.size_bytes,
        reverse=True,
    )

    for img in orphaned_list:
        report["orphaned_images"].append(
            {
                "path": str(img.path),
                "size": format_size(img.size_bytes),
                "size_bytes": img.size_bytes,
            }
        )
        report["cleanup_commands"].append(f'rm "{img.path}"')

    return report


def main() -> int:
    """Main entry point."""
    print("=" * 60)
    print("Image Analysis for Ghost to Astro Migration")
    print("=" * 60)

    # Scan images
    print(f"\nScanning images in {OG_LEGACY_DIR}...")
    images = scan_images(OG_LEGACY_DIR)
    print(f"Found {len(images)} images")

    if not images:
        print("No images found. Check the OG_LEGACY_DIR path.")
        return 1

    # Group by base name
    print("\nGrouping images by base filename...")
    groups = group_images_by_base_name(images)
    duplicate_groups = {k: v for k, v in groups.items() if len(v.images) > 1}
    print(f"Found {len(duplicate_groups)} groups with duplicates")

    # Extract markdown references
    print(f"\nScanning markdown files in {MARKDOWN_DIRS}...")
    references = extract_image_references(MARKDOWN_DIRS)
    print(f"Found {len(references)} image references")

    # Analyze usage
    print("\nAnalyzing image usage...")
    used_images, orphaned_images, usage_map = analyze_usage(images, references)
    print(f"Used images: {len(used_images)}")
    print(f"Orphaned images: {len(orphaned_images)}")

    # Generate report
    print("\nGenerating report...")
    report = generate_report(groups, used_images, orphaned_images, usage_map, images)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = report["summary"]
    print(f"Total images:         {summary['total_images']}")
    print(f"Total size:           {summary['total_size']}")
    print(f"Duplicate groups:     {summary['duplicate_groups']}")
    print(f"Duplicate files:      {summary['total_duplicate_files']}")
    print(f"Duplicate size:       {summary['duplicate_size']}")
    print(f"Used images:          {summary['used_images']}")
    print(f"Orphaned images:      {summary['orphaned_images']}")
    print(f"Potential savings:    {summary['potential_savings']}")

    # Save full report
    report_path = Path("image_analysis_report.json")
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to: {report_path}")

    # Print top 10 duplicate groups
    if report["duplicate_groups"]:
        print("\n" + "=" * 60)
        print("TOP 10 DUPLICATE GROUPS (by potential savings)")
        print("=" * 60)
        for i, group in enumerate(report["duplicate_groups"][:10], 1):
            print(f"\n{i}. {group['base_name']}")
            print(f"   Source: {group['source_image']['path']}")
            print(f"   Source size: {group['source_image']['size']}")
            print(f"   Duplicates: {len(group['duplicates'])}")
            print(f"   Potential savings: {group['potential_savings']}")

    # Print sample orphaned images
    if report["orphaned_images"]:
        print("\n" + "=" * 60)
        print("SAMPLE ORPHANED IMAGES (top 10 by size)")
        print("=" * 60)
        for img in report["orphaned_images"][:10]:
            print(f"  {img['path']} ({img['size']})")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Review the full report in image_analysis_report.json")
    print(
        "2. The report includes 'cleanup_commands' - shell commands to delete duplicates"
    )
    print("3. Before deleting, verify the source images are correct")
    print("4. Update markdown files to reference the source images")

    return 0


if __name__ == "__main__":
    sys.exit(main())
