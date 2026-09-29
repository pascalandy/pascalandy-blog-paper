#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install, run `just ci` and `just gitleaks`, then post a green `signoff` on the pushed HEAD.

The status is the merge gate for pull requests into main. It belongs to one
commit, so every push needs a new signoff.

Usage:
    just signoff
    uv run scripts/signoff.py --help

Exit codes: 0 signed off, 1 refused or a check failed, 2 bad usage.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Callable

# The install runs first so a dependency bump is checked against its own lockfile
CHECKS = (
    ("bun", "install", "--frozen-lockfile"),
    ("just", "ci"),
    ("just", "gitleaks"),
)
FORK_HINT = (
    "For a PR from a fork, read its whole diff first, since the checks run its code, "
    "then run: bun install --frozen-lockfile && just ci && just gitleaks && gh signoff"
)


class Refused(Exception):
    """A precondition failed; the message says how to fix it."""


def git(*args: str) -> str:
    result = subprocess.run(("git", *args), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise Refused(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def succeeds(*command: str) -> bool:
    return subprocess.run(command, capture_output=True, check=False).returncode == 0


def require_tools() -> None:
    for tool, fix in (
        ("bun", "install Bun: brew install bun"),
        ("gh", "install the GitHub CLI: brew install gh"),
        ("gitleaks", "install gitleaks: brew install gitleaks"),
        ("just", "install just: brew install just"),
    ):
        if shutil.which(tool) is None:
            raise Refused(f"{tool} not found; {fix}")
    extensions = subprocess.run(
        ("gh", "extension", "list"), capture_output=True, text=True, check=False
    ).stdout
    if "gh-signoff" not in extensions:
        raise Refused(
            "the gh signoff extension is missing; "
            "run: gh extension install basecamp/gh-signoff"
        )
    if not succeeds("gh", "auth", "status", "--hostname", "github.com"):
        raise Refused("gh is not signed in to github.com; run: gh auth login")
    if not succeeds("git", "config", "user.name"):
        raise Refused(
            'git user.name is not set; run: git config --global user.name "..."'
        )


def require_clean_tree() -> None:
    if git("status", "--porcelain", "--untracked-files=all"):
        raise Refused(
            "the working tree has uncommitted or untracked files; "
            "commit or stash them, push, then run: just signoff"
        )


def require_pushed_head() -> None:
    """Require HEAD to be exactly the tip GitHub has for this branch's upstream."""
    branch = subprocess.run(
        ("git", "symbolic-ref", "--quiet", "--short", "HEAD"),
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not branch:
        raise Refused(
            "HEAD is detached; check out the PR branch, then run: just signoff"
        )
    # The upstream names the remote branch exactly; git push -u and gh pr checkout
    # both set it
    remote, _, remote_ref = git(
        "for-each-ref",
        "--format=%(upstream:remotename)%09%(upstream:remoteref)",
        f"refs/heads/{branch}",
    ).partition("\t")
    if not remote or not remote_ref:
        raise Refused(
            f"{branch} has no upstream; run: git push -u origin HEAD. {FORK_HINT}"
        )
    git("fetch", "--quiet", remote, remote_ref)
    head, tip = git("rev-parse", "HEAD"), git("rev-parse", "FETCH_HEAD")
    if head == tip:
        return
    shown = remote_ref.removeprefix("refs/heads/")
    if succeeds("git", "merge-base", "--is-ancestor", head, tip):
        raise Refused(f"GitHub has newer commits on {remote}/{shown}; run: git pull")
    raise Refused(f"HEAD is not pushed to {remote}/{shown}; run: git push")


PRECONDITIONS: tuple[Callable[[], None], ...] = (
    require_tools,
    require_clean_tree,
    require_pushed_head,
)


def signoff() -> int:
    for precondition in PRECONDITIONS:
        precondition()
    head = git("rev-parse", "HEAD")

    for check in CHECKS:
        if subprocess.run(check, check=False).returncode != 0:
            print(
                f"error: `{' '.join(check)}` failed; nothing was signed off",
                file=sys.stderr,
            )
            return 1

    if git("rev-parse", "HEAD") != head:
        raise Refused(
            f"HEAD moved from {head[:7]} while the checks ran; run: just signoff"
        )
    return subprocess.run(("gh", "signoff"), check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="just signoff",
        description=__doc__.split("\n\n")[0],
    )
    parser.parse_args()
    try:
        return signoff()
    except Refused as refused:
        print(f"error: {refused}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
