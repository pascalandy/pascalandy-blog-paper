#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Launch, check, or stop the blog instance a verification run drives."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parents[4]
STATE_DIR = ROOT / "cache" / "verify-blog"
STATE = STATE_DIR / "server.json"
DEV = "http://localhost:4320"
PREVIEW_PORT = 4330
PREVIEW = f"http://127.0.0.1:{PREVIEW_PORT}"
READY_TIMEOUT = 60.0

EPILOG = """\
actions:
  up      reuse Pascal's dev server on :4320 when it answers; otherwise build the
          site and serve the build on :4330; print the base URL
  doctor  read-only: which instance, whether it answers as the blog, whether the
          build is older than src/; exit 1 when it is not worth driving
  down    stop the preview this run started, and nothing else

It never starts the dev server. The state lives in cache/verify-blog/server.json,
and down leaves every other file in cache/verify-blog/, the evidence, in place.

examples:
  uv run .claude/skills/verify-blog/scripts/site.py up
  uv run .claude/skills/verify-blog/scripts/site.py doctor
  uv run .claude/skills/verify-blog/scripts/site.py down

exit codes:
  0    success
  1    failure, or doctor found the instance not worth driving
  2    bad usage
  130  interrupted (SIGINT)"""


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


class Failure(Exception):
    """An expected failure; the message says what to fix."""


def site_title() -> str:
    """SITE.title, read from src/config.ts through Bun, never copied."""
    result = subprocess.run(
        ["bun", "-e", 'console.log((await import("./src/config.ts")).SITE.title)'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise Failure("could not read SITE.title from src/config.ts; run: just install")
    return result.stdout.strip()


def fetch(url: str) -> str | None:
    """The page body when the URL answers 200, else None."""
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def is_blog(body: str | None, title: str) -> bool:
    match = re.search(r"<title>(.*?)</title>", body or "", re.DOTALL)
    return bool(match and title in match.group(1))


def load() -> dict[str, Any] | None:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def up() -> str:
    title = site_title()
    state = load()
    if state and is_blog(fetch(state["url"] + "/"), title):
        return state["url"]
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if is_blog(fetch(DEV + "/"), title):
        STATE.write_text(json.dumps({"url": DEV, "started": False}), encoding="utf-8")
        return DEV
    if fetch(PREVIEW + "/") is not None:
        raise Failure(
            f"another process serves {PREVIEW}; stop it or free port {PREVIEW_PORT}, then rerun up"
        )
    log = STATE_DIR / "build.log"
    with log.open("w", encoding="utf-8") as output:
        built = subprocess.run(
            ["bun", "run", "build:ci"],
            cwd=ROOT,
            stdout=output,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if built.returncode != 0:
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
        print("\n".join(tail), file=sys.stderr)
        raise Failure(f"the build failed (log: {log}); run: just check --only build")
    with (STATE_DIR / "preview.log").open("w", encoding="utf-8") as output:
        preview = subprocess.Popen(
            [
                "bun",
                "run",
                "preview",
                "--port",
                str(PREVIEW_PORT),
                "--host",
                "127.0.0.1",
            ],
            cwd=ROOT,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    STATE.write_text(
        json.dumps({"url": PREVIEW, "started": True, "pid": preview.pid}),
        encoding="utf-8",
    )
    deadline = time.monotonic() + READY_TIMEOUT
    while time.monotonic() < deadline:
        if is_blog(fetch(PREVIEW + "/"), title):
            return PREVIEW
        if preview.poll() is not None:
            break
        time.sleep(0.5)
    down()
    raise Failure(
        f"the preview did not answer within {READY_TIMEOUT:g}s; "
        f"read {STATE_DIR / 'preview.log'}, then rerun up"
    )


def doctor() -> tuple[bool, str]:
    state = load()
    if state is None:
        return False, "no instance recorded; run: site.py up"
    title = site_title()
    lines = [f"url: {state['url']}"]
    healthy = is_blog(fetch(state["url"] + "/"), title)
    lines.append(f"answers as {title!r}: {'yes' if healthy else 'no'}")
    if state["started"]:
        running = alive(state["pid"])
        healthy = healthy and running
        lines.append(
            f"instance: preview started by this run, pid {state['pid']} "
            f"{'running' if running else 'gone'}"
        )
        built = ROOT / "dist" / "index.html"
        newest = max(
            path.stat().st_mtime for path in (ROOT / "src").rglob("*") if path.is_file()
        )
        if built.exists() and built.stat().st_mtime < newest:
            lines.append("warning: src/ changed after the build; run down, then up")
    else:
        lines.append("instance: Pascal's dev server, reused; this run never stops it")
    return healthy, "\n".join(lines)


def down() -> str:
    state = load()
    if state and state.get("started") and alive(state["pid"]):
        try:
            os.killpg(state["pid"], signal.SIGTERM)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and alive(state["pid"]):
                time.sleep(0.2)
            if alive(state["pid"]):
                os.killpg(state["pid"], signal.SIGKILL)
        except ProcessLookupError:
            pass
    STATE.unlink(missing_ok=True)
    return ""


def main(argv: list[str] | None = None) -> int:
    cli = Parser(
        prog="site.py",
        description="Launch, check, or stop the blog instance a verification run drives",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument(
        "action", choices=["up", "doctor", "down"], help="up, doctor, or down"
    )
    args = cli.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.action == "doctor":
            healthy, report = doctor()
            print(report)
            return 0 if healthy else 1
        output = up() if args.action == "up" else down()
    except Failure as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    if output:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
