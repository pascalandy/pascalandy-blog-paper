#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run `just ci` and `just gitleaks`, then post a green `signoff` status on the pushed HEAD.

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

CHECKS = (("just", "ci"), ("just", "gitleaks"))


class Refused(Exception):
    """A precondition failed; the message says how to fix it."""


def git(*args: str) -> str:
    result = subprocess.run(("git", *args), capture_output=True, text=True)
    if result.returncode != 0:
        raise Refused(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def require_tools() -> None:
    for tool, fix in (
        ("gh", "install the GitHub CLI: brew install gh"),
        ("gitleaks", "install gitleaks: brew install gitleaks"),
        ("just", "install just: brew install just"),
    ):
        if shutil.which(tool) is None:
            raise Refused(f"{tool} not found; {fix}")
    extensions = subprocess.run(
        ("gh", "extension", "list"), capture_output=True, text=True
    ).stdout
    if "gh-signoff" not in extensions:
        raise Refused(
            "the gh signoff extension is missing; "
            "run: gh extension install basecamp/gh-signoff"
        )


def require_clean_tree() -> None:
    if git("status", "--porcelain"):
        raise Refused(
            "the working tree has uncommitted or untracked files; "
            "commit or stash them, push, then run: just signoff"
        )


def require_pushed_head() -> None:
    try:
        push_ref = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{push}")
    except Refused:
        raise Refused(
            "HEAD has no push branch; run: git push -u origin HEAD. "
            "For a PR from a fork, run: just ci && just gitleaks && gh signoff"
        ) from None
    remote, _, branch = push_ref.partition("/")
    if not is_ancestor("HEAD", push_ref):
        git("fetch", "--quiet", remote, branch)
        if not is_ancestor("HEAD", push_ref):
            raise Refused(f"HEAD is not pushed to {push_ref}; run: git push")


def is_ancestor(commit: str, ref: str) -> bool:
    return (
        subprocess.run(("git", "merge-base", "--is-ancestor", commit, ref)).returncode
        == 0
    )


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
        if subprocess.run(check).returncode != 0:
            print(
                f"error: `{' '.join(check)}` failed; nothing was signed off",
                file=sys.stderr,
            )
            return 1

    if git("rev-parse", "HEAD") != head:
        raise Refused(
            f"HEAD moved from {head[:7]} while the checks ran; run: just signoff"
        )
    return subprocess.run(("gh", "signoff")).returncode


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
