#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deploy a branch from GitHub to a Sevalla static site and wait for the build.

Sevalla clones the branch from GitHub and builds it, so only pushed commits
ship. production always deploys main; preview deploys any pushed branch.

Usage:
    just deploy [--dry-run] [--no-wait]
    just deploy-preview [branch] [--dry-run] [--no-wait]

Setup: store a Sevalla API key in the macOS Keychain under the service
sevalla-api-token, or set SEVALLA_TOKEN. The site IDs come from
SEVALLA_STATIC_SITE_ID and SEVALLA_STATIC_SITE_ID_PREVIEW in the environment,
or else from the GitHub repository variables of the same names through gh.

Exit codes: 0 deployed, 1 refused or the deployment failed, 2 bad usage.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

API = "https://api.sevalla.com/v3"
POLL_SECONDS = 5.0
DEADLINE_SECONDS = 30 * 60
FINISHED = {"success": True, "failed": False, "cancelled": False}
KEYCHAIN_SERVICE = "sevalla-api-token"


@dataclass(frozen=True)
class Target:
    site_variable: str
    fixed_branch: str | None


TARGETS = {
    "production": Target("SEVALLA_STATIC_SITE_ID", "main"),
    "preview": Target("SEVALLA_STATIC_SITE_ID_PREVIEW", None),
}


class Refused(Exception):
    """A precondition failed; the message says how to fix it."""


class ApiError(Exception):
    """A Sevalla API call failed; retryable is False for a 4xx answer."""

    def __init__(self, message: str, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True)


def site_id(variable: str) -> str:
    if value := os.environ.get(variable):
        return value
    if shutil.which("gh") is None:
        raise Refused(
            f"{variable} is not set, and gh is missing to read it from GitHub"
        )
    result = run("gh", "variable", "get", variable)
    if result.returncode != 0 or not result.stdout.strip():
        raise Refused(
            f"{variable} is not set, and `gh variable get {variable}` failed: "
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def github_tip(branch: str) -> str:
    """Return the commit GitHub has for branch, the one Sevalla will build."""
    result = run("git", "ls-remote", "--exit-code", "origin", f"refs/heads/{branch}")
    if result.returncode != 0:
        raise Refused(f"{branch} is not on GitHub; run: git push -u origin {branch}")
    return result.stdout.split()[0]


def require_local_matches(branch: str, remote_sha: str) -> None:
    local = run("git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")
    local_sha = local.stdout.strip()
    if local_sha and local_sha != remote_sha:
        raise Refused(
            f"local {branch} is at {local_sha[:7]} but GitHub has {remote_sha[:7]}; "
            "push or pull first so the preview matches your checkout"
        )


def request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "pascalandy-blog-deploy",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace").strip()[:300]
        message = f"HTTP {error.code} {error.reason}" + (
            f": {detail}" if detail else ""
        )
        raise ApiError(message, retryable=error.code >= 500) from None
    except json.JSONDecodeError:
        raise ApiError("the answer was not JSON", retryable=True) from None
    # urllib wraps only request errors in URLError; response errors arrive raw
    except (OSError, http.client.HTTPException) as error:
        raise ApiError(f"could not reach Sevalla: {error}", retryable=True) from None


def wait_for(site: str, deployment: str, token: str) -> int:
    deadline = time.monotonic() + DEADLINE_SECONDS
    last = None
    while time.monotonic() < deadline:
        time.sleep(POLL_SECONDS)
        try:
            status = request(
                "GET", f"/static-sites/{site}/deployments/{deployment}", token
            ).get("status")
        except ApiError as error:
            if not error.retryable:
                print(
                    f"error: status check failed ({error}); "
                    "the deployment may still run on Sevalla",
                    file=sys.stderr,
                )
                return 1
            print(f"status check failed ({error}); retrying", file=sys.stderr)
            continue
        if status != last:
            print(f"deployment {deployment}: {status}")
            last = status
        if status in FINISHED:
            return 0 if FINISHED[status] else 1
    print(
        f"error: deployment {deployment} did not finish in 30 minutes", file=sys.stderr
    )
    return 1


def sevalla_token() -> str:
    """Read the API key from SEVALLA_TOKEN, else from the macOS Keychain."""
    token = os.environ.get("SEVALLA_TOKEN", "")
    if not token and shutil.which("security"):
        token = run(
            "security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"
        ).stdout
    token = token.strip()
    if not token:
        raise Refused(
            "no Sevalla API key; store one with: security add-generic-password "
            f'-s {KEYCHAIN_SERVICE} -a "$USER" -w  (or set SEVALLA_TOKEN)'
        )
    if not token.isprintable():
        raise Refused("the Sevalla API key has a line break or control character")
    return token


def deploy(target_name: str, branch: str | None, dry_run: bool, wait: bool) -> int:
    target = TARGETS[target_name]
    branch = (
        target.fixed_branch
        or branch
        or run("git", "branch", "--show-current").stdout.strip()
    )
    if not branch:
        raise Refused("no branch to deploy; check out a branch or pass one")
    token = sevalla_token()
    site = site_id(target.site_variable)
    sha = github_tip(branch)
    if target.fixed_branch is None:
        require_local_matches(branch, sha)

    print(f"Deploying {branch} at {sha[:7]} to {target_name}")
    if dry_run:
        print(
            f'dry run: POST {API}/static-sites/{site}/deployments {{"branch": "{branch}"}}'
        )
        return 0
    try:
        deployment = request(
            "POST", f"/static-sites/{site}/deployments", token, {"branch": branch}
        )
    except ApiError as error:
        raise Refused(f"Sevalla did not start the deployment: {error}") from None
    deployment_id = deployment.get("id")
    if not deployment_id:
        raise Refused(f"Sevalla answered without a deployment id: {deployment}")
    print(f"deployment {deployment_id}: started")
    return wait_for(site, deployment_id, token) if wait else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts/deploy.py",
        description=__doc__.split("\n\n")[0],
    )
    parser.add_argument("target", choices=TARGETS, help="production deploys main")
    parser.add_argument(
        "branch", nargs="?", help="preview only; defaults to the current branch"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="check the setup, send nothing"
    )
    parser.add_argument(
        "--no-wait", action="store_true", help="return once Sevalla accepts"
    )
    args = parser.parse_args(argv)
    if args.branch and args.target == "production":
        parser.error("production always deploys main; a branch is for preview")
    try:
        return deploy(args.target, args.branch, args.dry_run, not args.no_wait)
    except Refused as refused:
        print(f"error: {refused}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
