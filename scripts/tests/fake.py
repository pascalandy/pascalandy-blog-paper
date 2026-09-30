"""Stand in for gh, bun, just, and gitleaks in the ship-script tests.

Run as `fake.py PROGRAM ARGS...`. Each call appends its argv and GH_REPO to the
calls in the JSON state named by FAKE_STATE, then answers from that state:
gh from the commit statuses it records, and every other program by running its
hook and failing when it is listed in `failing`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args), capture_output=True, text=True, check=True
    ).stdout.strip()


def gh(state: dict, args: list[str]) -> int:
    if args[:2] == ["auth", "status"]:
        if state["signed_in"]:
            return 0
        print("You are not logged into any GitHub hosts", file=sys.stderr)
        return 1
    if args[:2] == ["extension", "list"]:
        print("gh signoff\tbasecamp/gh-signoff\tv0.4.1")
        return 0
    if args == ["signoff"]:
        sha = git("rev-parse", "HEAD")
        state["statuses"][sha] = "success"
        print(f"✓ Signed off on {sha}")
        return 0
    print(f"fake gh does not support: {' '.join(args)}", file=sys.stderr)
    return 2


def program(state: dict, argv: list[str]) -> int:
    command = " ".join(argv)
    if hook := state["hooks"].get(command):
        subprocess.run(hook, shell=True, check=True)
    return 1 if command in state["failing"] else 0


def main() -> int:
    path = Path(os.environ["FAKE_STATE"])
    state = json.loads(path.read_text(encoding="utf-8"))
    argv = sys.argv[1:]
    state["calls"].append({"argv": argv, "repo": os.environ.get("GH_REPO")})
    code = gh(state, argv[1:]) if argv[0] == "gh" else program(state, argv)
    path.write_text(json.dumps(state), encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
