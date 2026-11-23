#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Launch, check, or stop the blog instance a verification run drives."""

from __future__ import annotations

import argparse
import fcntl
import itertools
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from threading import current_thread, main_thread
from typing import Any, NoReturn
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[4]
STATE_DIR = ROOT / "cache" / "verify-blog"
STATE = STATE_DIR / "server.json"
DEV = "http://localhost:4320"
PREVIEW_PORT = 4330
PREVIEW = f"http://127.0.0.1:{PREVIEW_PORT}"
PREVIEW_SCRIPT = Path(__file__).with_name("preview.mjs").resolve()
READY_TIMEOUT = 60.0
# While its toolbar is on, Astro's dev server marks elements with the absolute
# path of their source file, which names the checkout it serves
SOURCE_FILE = re.compile(r'data-astro-source-file="([^"]+)"')
# What a build reads. Deleting or renaming a file changes its folder's time, so
# folders count as well as files
INPUTS = ("src", "public", "astro.config.ts", "package.json", "bun.lock")
# package.json's prepare script runs `lefthook install`, which rewrites the hooks
# every worktree of the clone shares, so a verifier installs without scripts (#92)
INSTALL = ("bun", "install", "--frozen-lockfile", "--ignore-scripts")

EPILOG = """\
actions:
  up      reuse Pascal's dev server on :4320 when it answers, unless its pages
          name source files in another checkout (Astro marks them while its
          dev toolbar is on); otherwise serve a build on :4330, rebuilt once a
          build input (src/, public/, astro.config.ts, package.json, bun.lock)
          changes; print the base URL. Before it builds, and whenever
          node_modules/ is missing, it installs the locked dependencies with
          bun install --frozen-lockfile --ignore-scripts, which leaves the git
          hooks shared by every worktree as they are
  doctor  read-only: which instance, whether it answers as the blog, and whether
          it is current; exit 1 when it is not worth driving
  down    stop the preview this run started, once its command confirms it,
          and nothing else

It never starts the dev server. The state lives in cache/verify-blog/server.json
with this checkout's path, so a state copied from another checkout is ignored;
down leaves every other file in cache/verify-blog/, the evidence, in place.

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


def require_bun() -> None:
    if shutil.which("bun") is None:
        raise Failure("bun not found on PATH; install Bun (https://bun.sh)")


def install() -> None:
    """Install the locked dependencies without lifecycle scripts."""
    require_bun()
    result = subprocess.run(
        INSTALL, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print(result.stdout + result.stderr, file=sys.stderr, end="")
        raise Failure(f"{' '.join(INSTALL)} failed; fix the lockfile, then rerun up")


def site_title() -> str:
    """SITE.title, read from src/config.ts through Bun, never copied."""
    require_bun()
    result = subprocess.run(
        ["bun", "-e", 'console.log((await import("./src/config.ts")).SITE.title)'],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise Failure(
            f"could not read SITE.title from src/config.ts; run: {' '.join(INSTALL)}"
        )
    return result.stdout.strip()


def fetch(url: str, instance: str | None = None) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if instance and response.headers.get("X-Verify-Blog-Instance") != instance:
                return None
            return response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def is_blog(body: str | None, title: str) -> bool:
    match = re.search(r"<title>(.*?)</title>", body or "", re.DOTALL)
    return bool(match and title in match.group(1))


def elsewhere(body: str | None) -> str | None:
    """A source file of the page when none sits in this checkout, else None.

    None also when the page carries no source marks: the checkout is unknown."""
    files = [Path(name) for name in SOURCE_FILE.findall(body or "")]
    if not files or any(name.is_relative_to(ROOT) for name in files):
        return None
    return str(files[0])


def changed(state: dict[str, Any]) -> str | None:
    """Why this run's build is out of date, or None while it is current."""
    if not (ROOT / "dist" / "index.html").exists():
        return "the build is gone"
    built = state.get("built") or 0
    for name in INPUTS:
        top = ROOT / name
        for path in (top, *top.rglob("*")) if top.is_dir() else (top,):
            if path.exists() and path.stat().st_mtime > built:
                name = f"{path.relative_to(ROOT)}{'/' if path.is_dir() else ''}"
                return f"{name} changed after the build"
    return None


def load() -> dict[str, Any] | None:
    """This checkout's recorded instance; a state copied from another is ignored."""
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return state if state.get("root") == str(ROOT) else None


def save(
    url: str,
    pid: int | None = None,
    built: float | None = None,
    instance: str | None = None,
) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state = {"url": url, "started": pid is not None, "pid": pid, "root": str(ROOT)}
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({**state, "built": built, "instance": instance}), encoding="utf-8"
    )
    temporary.replace(STATE)


def ours(state: dict[str, Any]) -> bool:
    """Whether the recorded process still runs this run's preview.

    A process ID outlives its process and can be reused, so its command decides."""
    try:
        if os.getpgid(state["pid"]) != state["pid"]:
            return False
    except (ProcessLookupError, PermissionError):
        return False
    try:
        result = subprocess.run(
            ["ps", "-ww", "-o", "args=", "-p", str(state["pid"])],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        raise Failure(
            f"ps not found, so pid {state['pid']} can't be confirmed as the preview; "
            "install ps, or stop the preview yourself"
        ) from None
    if instance := state.get("instance"):
        return result.stdout.rstrip().endswith(
            f" {PREVIEW_SCRIPT} {PREVIEW_PORT} {instance}"
        )
    # Older state has no instance ID. Identical Bun commands run in other worktrees.
    if not result.stdout.rstrip().endswith(
        f"run preview --port {PREVIEW_PORT} --host 127.0.0.1 --ignore-lock"
    ):
        return False
    if sys.platform.startswith("linux"):
        try:
            return Path(f"/proc/{state['pid']}/cwd").readlink() == ROOT
        except OSError:
            return False
    if not shutil.which("lsof"):
        return False
    cwd = subprocess.run(
        ["lsof", "-a", "-p", str(state["pid"]), "-d", "cwd", "-Fn"],
        capture_output=True,
        text=True,
        check=False,
    )
    return f"n{ROOT}" in cwd.stdout.splitlines()


@contextmanager
def record_before_interrupt():
    """Finish publishing the detached child's ownership before delivering a stop."""
    if current_thread() is not main_thread():
        yield
        return
    pending = []

    def defer(signum, _frame):
        pending.append(signum)

    previous = {}
    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous[signum] = signal.signal(signum, defer)
        yield
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)
        for signum in pending:
            signal.raise_signal(signum)


def up() -> str:
    if not (ROOT / "node_modules").is_dir():
        install()
    title = site_title()
    state = load()
    started = bool(state and state["started"])
    body = fetch(DEV + "/")
    if is_blog(body, title) and elsewhere(body) is None:
        if started:
            down()
        save(DEV)
        return DEV
    current = (
        started and state.get("instance") and ours(state) and changed(state) is None
    )
    if current and is_blog(fetch(PREVIEW + "/", state["instance"]), title):
        return PREVIEW
    if started:
        down()
    if fetch(PREVIEW + "/") is not None:
        raise Failure(
            f"another process serves {PREVIEW}; stop it or free port {PREVIEW_PORT}, then rerun up"
        )
    # bun.lock may have changed since node_modules/ was installed
    install()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
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
    finished = time.time()
    instance = uuid4().hex
    with (
        record_before_interrupt(),
        (STATE_DIR / "preview.log").open("w", encoding="utf-8") as output,
    ):
        preview = subprocess.Popen(
            ["node", str(PREVIEW_SCRIPT), str(PREVIEW_PORT), instance],
            cwd=ROOT,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            save(PREVIEW, preview.pid, finished, instance)
        except BaseException:
            preview.kill()
            preview.wait()
            raise
    try:
        deadline = time.monotonic() + READY_TIMEOUT
        while preview.poll() is None and time.monotonic() < deadline:
            if is_blog(fetch(PREVIEW + "/", instance), title):
                return PREVIEW
            time.sleep(0.2)
        raise Failure(
            f"this preview could not serve {PREVIEW}; check port {PREVIEW_PORT} "
            f"and {STATE_DIR / 'preview.log'}, then rerun up"
        )
    except BaseException:
        if preview.poll() is None:
            preview.kill()
        preview.wait()
        STATE.unlink(missing_ok=True)
        raise


def doctor() -> tuple[bool, str]:
    state = load()
    if state is None:
        return False, "no instance recorded for this checkout; run: site.py up"
    title = site_title()
    instance = state.get("instance") if state["started"] else None
    body = fetch(state["url"] + "/", instance)
    healthy = is_blog(body, title) and (not state["started"] or bool(instance))
    lines = [
        f"url: {state['url']}",
        f"answers as {title!r}: {'yes' if healthy else 'no'}",
    ]
    if state["started"]:
        running, reason = ours(state), changed(state)
        lines.append(
            f"instance: preview started by this run, pid {state['pid']} "
            f"{'running' if running else 'gone'}"
        )
        if reason:
            lines.append(f"stale: {reason}; run: site.py up")
        healthy = healthy and running and reason is None
    else:
        lines.append("instance: Pascal's dev server, reused; this run never stops it")
        other = elsewhere(body)
        if other:
            lines.append(f"serves another checkout, such as {other}; run: site.py up")
        healthy = healthy and other is None
    return healthy, "\n".join(lines)


def down() -> str:
    state = load()
    if state and state["started"] and ours(state):
        try:
            os.killpg(state["pid"], signal.SIGTERM)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and ours(state):
                time.sleep(0.2)
            if ours(state):
                os.killpg(state["pid"], signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
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
    argv = sys.argv[1:] if argv is None else argv
    if {"-h", "--help"} & set(itertools.takewhile(lambda arg: arg != "--", argv)):
        cli.print_help()
        return 0
    args = cli.parse_args(argv)
    try:
        if args.action == "doctor":
            healthy, report = doctor()
            print(report)
            return 0 if healthy else 1
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with (STATE_DIR / "server.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
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
