#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Format or lint files: Prettier and ESLint for the site, ruff for Python."""

from __future__ import annotations

import argparse
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent

# --quiet keeps uvx from drawing a progress spinner in the hooks
RUFF = ("uvx", "--quiet", "ruff@0.16.9")
PRETTIER = (
    "bun",
    "x",
    "prettier",
    "--log-level=warn",
    "--ignore-unknown",
    "--no-error-on-unmatched-pattern",
)
ESLINT = ("bun", "x", "eslint", "--no-warn-ignored")
ESLINT_SUFFIXES = {
    ".astro",
    ".cjs",
    ".cts",
    ".js",
    ".jsx",
    ".mjs",
    ".mts",
    ".ts",
    ".tsx",
}

# What to run next when an action fails
FIXES = {
    "format": "fix the errors above, then rerun: just format",
    "check": "run: just format",
    "lint": "fix the problems above, then rerun: just lint",
}

EPILOG = """\
actions:
  format  rewrite files in place
  check   change nothing; exit 1 when a file needs formatting
  lint    report lint problems

Without FILE, the action covers the whole repository. Prettier skips the paths
in .prettierignore, ESLint the ignores in eslint.config.js, and ruff follows
ruff.toml. Tool output goes to stderr.

examples:
  just format
  just format src/config.ts scripts/check.py
  just lint src/pages/index.astro
  uv run scripts/tidy.py check

exit codes:
  0    success
  1    a tool reported a problem
  2    bad usage
  130  interrupted (SIGINT)
  143  terminated (SIGTERM)"""

Run = tuple[str, tuple[str, ...]]


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


class Terminated(Exception):
    """SIGTERM arrived."""


def parser() -> Parser:
    cli = Parser(
        prog="tidy.py",
        description="Format or lint files: Prettier and ESLint for the site, ruff for Python",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument("action", choices=list(FIXES), help="format, check, or lint")
    cli.add_argument("files", nargs="*", metavar="FILE", help="files to cover")
    return cli


def wants_help(argv: list[str]) -> bool:
    """Whether -h or --help comes before `--`, where options end."""
    for arg in argv:
        if arg == "--":
            return False
        if arg in ("-h", "--help"):
            return True
    return False


def runs(action: str, files: list[str]) -> list[Run]:
    """The named tool runs that cover FILES, or the whole repository without them."""
    python = [name for name in files if name.endswith(".py")]
    site = [name for name in files if not name.endswith(".py")]
    everything = not files
    planned: list[Run] = []
    if action == "lint":
        lintable = [name for name in site if Path(name).suffix in ESLINT_SUFFIXES]
        if everything or lintable:
            planned.append(("eslint", (*ESLINT, *(lintable or ["."]))))
        if everything or python:
            ruff = (*RUFF, "check", "--quiet", "--output-format=concise")
            planned.append(("ruff", (*ruff, *(python or ["."]))))
        return planned
    if everything or site:
        mode = "--write" if action == "format" else "--check"
        planned.append(("prettier", (*PRETTIER, mode, *(site or ["."]))))
    if everything or python:
        check = ("--check",) if action == "check" else ()
        ruff = (*RUFF, "format", "--quiet", *check)
        planned.append(("ruff", (*ruff, *(python or ["."]))))
    return planned


def missing(planned: list[Run]) -> str:
    """What to install before the planned runs can start, or "" when nothing is missing."""
    programs = {command[0] for _, command in planned}
    if "bun" in programs and shutil.which("bun") is None:
        return "bun not found on PATH; install Bun (https://bun.sh), then run: just install"
    if "bun" in programs and not (ROOT / "node_modules").is_dir():
        return "dependencies are not installed; run: just install"
    if "uvx" in programs and shutil.which("uvx") is None:
        return "uvx not found on PATH; install uv (https://docs.astral.sh/uv/)"
    return ""


def terminate(_number: int, _frame: object) -> None:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    raise Terminated


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cli = parser()
    if wants_help(argv):
        cli.print_help()
        return 0
    args = cli.parse_args(argv)
    planned = runs(args.action, args.files)
    problem = missing(planned)
    if problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    signal.signal(signal.SIGTERM, terminate)
    try:
        # Every tool runs, so one failure does not hide another
        failed = [
            name
            for name, command in planned
            if subprocess.run(
                command, cwd=ROOT, stdout=sys.stderr, check=False
            ).returncode
        ]
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    except Terminated:
        print("terminated", file=sys.stderr)
        return 143
    if failed:
        print(
            f"error: {', '.join(failed)} failed; {FIXES[args.action]}", file=sys.stderr
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
