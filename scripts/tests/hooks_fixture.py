"""Author and verifier worktrees with real Bun and project-installed Lefthook."""

import json
import os
import shutil
import subprocess
from pathlib import Path

from harness import SCRIPTS, Sandbox


def hook_worktrees(sandbox: Sandbox, *, build_fixture: bool = False) -> Path:
    root = SCRIPTS.parent
    author = sandbox.work
    verifier = author.parent / "verifier"
    manifest = json.loads((root / "package.json").read_text())
    package = {"name": "fixture", "scripts": manifest["scripts"]}
    if build_fixture:
        package = manifest
        package["scripts"]["build:ci"] = "astro build"
        shutil.copy2(root / "bun.lock", author)
        sandbox.git("add", "bun.lock")
    (author / "package.json").write_text(json.dumps(package))
    (author / ".gitignore").write_text("tools/\nnode_modules/\n")
    shutil.copy2(root / "lefthook.yml", author)
    shutil.copy2(root / "justfile", author)
    bun = shutil.which("bun")
    assert bun is not None, "install Bun to run the worktree hook tests"
    sandbox.git("add", ".gitignore", "package.json", "lefthook.yml", "justfile")
    sandbox.git("commit", "-qm", "authoring hooks")
    sandbox.git("push", "--quiet")
    sandbox.git("switch", "--quiet", "--detach")
    sandbox.git("worktree", "add", "--quiet", str(verifier), "feature")
    sandbox.work = verifier

    lefthook = subprocess.check_output(
        [bun, "-p", "require('lefthook/get-exe').getExePath()"], cwd=root, text=True
    ).strip()
    for checkout in (author, verifier):
        tools = checkout / "tools"
        tools.mkdir()
        (tools / "bun").symlink_to(bun)
        shutil.copy2(lefthook, tools)
    path = sandbox.env["PATH"]
    sandbox.env["PATH"] = f"{author / 'tools'}{os.pathsep}{path}"
    subprocess.run(
        [shutil.which("just"), "install"],
        cwd=author,
        env=sandbox.env,
        capture_output=True,
        check=True,
    )
    sandbox.env["PATH"] = f"{verifier / 'tools'}{os.pathsep}{path}"
    return author / ".git" / "hooks"


def installed_hooks(folder: Path) -> dict[str, tuple[int, bytes]]:
    for name in ("pre-commit", "pre-push"):
        assert os.access(folder / name, os.X_OK), f"author setup did not install {name}"
    return {
        hook.name: (hook.stat().st_mode, hook.read_bytes())
        for hook in folder.iterdir()
        if hook.is_file() and hook.suffix != ".sample"
    }
