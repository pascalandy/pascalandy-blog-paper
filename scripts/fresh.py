#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Clear generated output while keeping downloaded fonts and browser evidence."""

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def targets(root: Path) -> list[Path]:
    paths = [root / "dist", root / ".astro", root / "public/pagefind"]
    cache = root / "cache"
    if cache.is_symlink():
        raise OSError("cache is a symlink; use a worktree-local cache")
    if cache.is_dir():
        paths.extend(
            sorted(
                path
                for path in cache.iterdir()
                if path.name not in {"fonts", "verify-blog"}
            )
        )
    return [path for path in paths if path.exists() or path.is_symlink()]


def clear(root: Path, dry_run: bool = False) -> list[Path]:
    paths = targets(root)
    if not dry_run:
        for path in paths:
            if path.is_symlink() or path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
    return paths


def main() -> int:
    cli = argparse.ArgumentParser(
        description=__doc__, epilog="Example: just fresh --dry-run"
    )
    cli.add_argument(
        "--dry-run", action="store_true", help="list paths without deleting them"
    )
    args = cli.parse_args()
    try:
        paths = clear(ROOT, args.dry_run)
    except OSError as error:
        print(
            f"error: fresh failed: {error}; stop the build, then rerun: just fresh",
            file=sys.stderr,
        )
        return 1
    if args.dry_run:
        for path in paths:
            print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
