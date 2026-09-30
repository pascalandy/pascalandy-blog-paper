#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run the CI verdict: every check in CHECKS, in order; success prints nothing."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, TextIO

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "cache" / "check"

Command = tuple[str, ...]

# --quiet keeps uvx's install messages out of the logs; optional local linters
# stay off so every machine agrees
ACTIONLINT: Command = (
    "uvx",
    "--quiet",
    "--from",
    "actionlint-py@1.7.12.25",
    "actionlint",
    "-shellcheck=",
    "-pyflakes=",
)

# The scripts' tests use only the standard library
UNITTEST: Command = (
    "uv",
    "run",
    "--quiet",
    "--no-project",
    "--python",
    ">=3.11",
    "python",
    "-m",
    "unittest",
    "discover",
    "--start-directory",
)


@dataclass(frozen=True)
class Check:
    """A named row whose commands run from the repository root and stop at the first failure."""

    name: str
    commands: tuple[Command, ...]


def row(name: str, *commands: Command) -> Check:
    return Check(name, commands)


def uv_run(script: str, *args: str) -> Command:
    return ("uv", "run", "--quiet", script, *args)


# Slow rows last
CHECKS = [
    row("format", uv_run("scripts/tidy.py", "check")),
    row("lint", uv_run("scripts/tidy.py", "lint")),
    row("workflows", ACTIONLINT),
    # astro sync validates every post against the schema in src/content.config.ts.
    # --force clears the content store: without it, a registry edit in
    # src/tags.ts leaves unchanged posts unvalidated
    row("content", ("bun", "run", "sync", "--force")),
    row("docs", uv_run("scripts/check_docs.py")),
    # The ship scripts against a bare origin and fake tools
    row("scripts", (*UNITTEST, "scripts/tests")),
    row("typecheck", ("bun", "run", "astro", "check")),
    row("build", ("bun", "run", "build:ci")),
]

EPILOG = """\
Each check is one row of CHECKS in scripts/check.py; add a row to add a check.
A failing check does not stop the others. It replays an excerpt of its output
on stderr, keeps the full log in cache/check/NAME.log, and names its rerun.

examples:
  just check
  just check --list -v
  just check --only lint --only format
  just check --only build --verbose

exit codes:
  0    every selected check passed
  1    a check failed
  2    bad usage
  130  interrupted (SIGINT)
  143  terminated (SIGTERM)"""

# Install hints for the programs the rows run
FIXES = {
    "bun": "install Bun (https://bun.sh), then run: just install",
    "uv": "install uv (https://docs.astral.sh/uv/)",
    "uvx": "install uv (https://docs.astral.sh/uv/)",
}

# A log this short is replayed whole; a longer one replays its error lines,
# up to MATCHES of them, then its last TAIL lines
WHOLE = 40
MATCHES = 30
TAIL = 15
# A location such as `src/pages/index.astro:12:5`, not a timestamp such as `02:08:41`
ERROR_LINE = re.compile(
    r"error|fail|fatal|exception|✖|✘|\[warn\]|would reformat|^\s*\S+\.\w+:\d+",
    re.IGNORECASE,
)
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

# How long a stopped check may clean up after SIGTERM before SIGKILL
GRACE = 10.0


class Failure(Exception):
    """An expected failure; the message says what to fix."""


class Interrupted(Exception):
    """SIGINT or SIGTERM arrived; `code` is 130 or 143."""

    def __init__(self, code: int) -> None:
        super().__init__(code)
        self.code = code


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


def parser() -> Parser:
    cli = Parser(
        prog="just check",
        description="Run the CI verdict: the same checks GitHub Actions runs",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument(
        "--only",
        action="append",
        choices=[check.name for check in CHECKS],
        metavar="NAME",
        help="run only this check; repeat for more (see --list)",
    )
    cli.add_argument(
        "--list",
        action="store_true",
        help="print the check names and exit; -v adds their commands on stderr",
    )
    cli.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="stream each command and its output on stderr",
    )
    return cli


def wants_help(argv: list[str]) -> bool:
    """Whether -h or --help comes before `--`, alone or in a bundle such as -vh."""
    for arg in argv:
        if arg == "--":
            return False
        if arg == "--help" or re.fullmatch(r"-[vh]*h[vh]*", arg):
            return True
    return False


def interrupt(number: int, _frame: object) -> None:
    """Turn SIGINT or SIGTERM into Interrupted; a repeat is ignored while cleanup runs."""
    for each in (signal.SIGINT, signal.SIGTERM):
        signal.signal(each, signal.SIG_IGN)
    raise Interrupted(128 + number)


def preflight(selected: list[Check]) -> None:
    programs = {command[0] for check in selected for command in check.commands}
    for program in sorted(programs):
        if shutil.which(program) is None:
            fix = FIXES.get(program, f"install {program}")
            raise Failure(f"{program} not found on PATH; {fix}")
    if "bun" in programs and not (ROOT / "node_modules").is_dir():
        raise Failure("dependencies are not installed; run: just install")


def stop(process: subprocess.Popen[str]) -> None:
    """SIGTERM a child, then SIGKILL it after GRACE seconds."""
    process.terminate()
    try:
        process.wait(timeout=GRACE)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def execute(command: Command, log: TextIO, verbose: bool) -> tuple[int, list[str]]:
    """Run one command; its output goes to the log and, when verbose, to stderr.

    Returns the exit code and the output lines."""
    output: list[str] = []
    with subprocess.Popen(
        command,
        cwd=ROOT,
        env={**os.environ, "NO_COLOR": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    ) as process:
        try:
            assert process.stdout is not None
            for line in process.stdout:
                output.append(line)
                log.write(line)
                if verbose:
                    sys.stderr.write(line)
            return process.wait(), output
        except BaseException:
            stop(process)
            raise


def excerpt(output: list[str], log_path: Path) -> list[str]:
    """The lines worth replaying from a failing command's output, bounded."""
    lines = [ANSI.sub("", line.rstrip("\n")) for line in output]
    if len(lines) <= WHOLE:
        return lines
    tail = len(lines) - TAIL
    errors = [line for line in lines[:tail] if ERROR_LINE.search(line)][:MATCHES]
    skipped = tail - len(errors)
    where = log_path.relative_to(ROOT)
    return [*errors, f"[... {skipped} more lines in {where} ...]", *lines[tail:]]


def passes(check: Check, verbose: bool) -> bool:
    """Run one check; a failure replays a bounded excerpt of its output on stderr."""
    LOGS.mkdir(parents=True, exist_ok=True)
    log_path = LOGS / f"{check.name}.log"
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as log:
        for command in check.commands:
            header = f"==> {check.name}: {shlex.join(command)}"
            log.write(f"{header}\n")
            if verbose:
                print(header, file=sys.stderr)
            code, output = execute(command, log, verbose)
            if code == 0:
                continue
            if not verbose:
                print(header, file=sys.stderr)
                for line in excerpt(output, log_path):
                    print(line, file=sys.stderr)
            print(
                f"error: {check.name} failed; rerun: just check --only {check.name}",
                file=sys.stderr,
            )
            return False
    if verbose:
        elapsed = time.monotonic() - started
        print(f"==> {check.name}: passed in {elapsed:.1f}s", file=sys.stderr)
    return True


def verdict(args: argparse.Namespace) -> int:
    selected = [check for check in CHECKS if not args.only or check.name in args.only]
    if args.list:
        for check in selected:
            print(check.name)
            if args.verbose:
                for command in check.commands:
                    print(f"{check.name}: {shlex.join(command)}", file=sys.stderr)
        return 0
    preflight(selected)
    failed = [check.name for check in selected if not passes(check, args.verbose)]
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cli = parser()
    if wants_help(argv):
        cli.print_help()
        return 0
    args = cli.parse_args(argv)
    for number in (signal.SIGINT, signal.SIGTERM):
        signal.signal(number, interrupt)
    try:
        return verdict(args)
    except Failure as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 1
    except Interrupted as stopped:
        print("interrupted" if stopped.code == 130 else "terminated", file=sys.stderr)
        return stopped.code
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
