#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a command; in an interactive terminal with tspin installed, pipe its output through tspin."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import NoReturn

EPILOG = """\
Outside a terminal, without tspin, or with NO_COLOR set or TERM=dumb, the
command runs unchanged, so no recipe needs tspin in CI or an agent sandbox.

examples:
  uv run scripts/pretty.py bun run dev --port 4320
  uv run scripts/pretty.py bun run build

exit codes:
  the command's own exit code, and:
  2    bad usage
  127  the command was not found
  130  interrupted (SIGINT)"""


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


def pretty() -> str | None:
    """The tspin path when output should be pretty-printed, else None."""
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return None
    if os.environ.get("TERM") == "dumb":
        return None
    return shutil.which("tspin")


def main(argv: list[str] | None = None) -> int:
    cli = Parser(
        prog="pretty.py",
        description="Run a command; in an interactive terminal with tspin installed, "
        "pipe its output through tspin",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument("command", nargs=argparse.REMAINDER, help="the command to run")
    args = cli.parse_args(sys.argv[1:] if argv is None else argv)
    if not args.command:
        cli.error("missing the command to run")
    tspin = pretty()
    try:
        if tspin is None:
            os.execvp(args.command[0], args.command)
        with subprocess.Popen(args.command, stdout=subprocess.PIPE) as producer:
            with subprocess.Popen([tspin], stdin=producer.stdout) as printer:
                assert producer.stdout is not None
                producer.stdout.close()
                printer.wait()
            return producer.wait()
    except FileNotFoundError:
        print(f"error: {args.command[0]} not found on PATH", file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
