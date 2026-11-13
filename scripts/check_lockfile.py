#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Require one resolved Vite version in Bun's text lockfile."""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def problem(text: str) -> str | None:
    versions = set(
        re.findall(r'^\s*"[^"\n]+":\s*\[\s*"vite@([^"\n]+)"', text, re.MULTILINE)
    )
    if len(versions) != 1:
        found = ", ".join(sorted(versions)) or "none"
        return f"bun.lock must resolve one Vite version; found {found}; run: bun install --force, then just check --only lockfile"
    return None


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("lockfile", type=Path, nargs="?", default=ROOT / "bun.lock")
    args = cli.parse_args()
    try:
        message = problem(args.lockfile.read_text(encoding="utf-8"))
    except OSError as error:
        message = str(error)
    if message:
        print(f"error: {message}", file=sys.stderr)
    return int(bool(message))


if __name__ == "__main__":
    raise SystemExit(main())
