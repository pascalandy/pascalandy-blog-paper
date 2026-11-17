"""verify-blog's site.py installs dependencies without touching shared git hooks (#92).

A throwaway clone gets a linked worktree holding site.py. A fake `bun` on PATH
behaves like Bun with this repository's package.json: an install runs the
`prepare` script, which rewrites the hooks every worktree shares, unless it is
given --ignore-scripts.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / ".claude/skills/verify-blog/scripts/site.py"

FAKE_BUN = """#!/bin/sh
echo "$*" >> "$BUN_LOG"
case "$1" in
install)
  mkdir -p node_modules
  case " $* " in
  *" --ignore-scripts "*) ;;
  *) echo "# lefthook fallback: $PWD" > "$(git rev-parse --git-common-dir)/hooks/pre-commit" ;;
  esac ;;
-e) echo "Fixture blog" ;;
*) exit 1 ;;
esac
"""


def digest(hooks: Path) -> str:
    files = sorted(path for path in hooks.iterdir() if path.is_file())
    return hashlib.sha256(
        b"".join(path.name.encode() + path.read_bytes() for path in files)
    ).hexdigest()


class SiteInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        base = Path(folder.name)
        clone = base / "clone"
        clone.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(
            GIT_CONFIG_GLOBAL=str(base / "gitconfig"),
            GIT_CONFIG_NOSYSTEM="1",
            BUN_LOG=str(base / "bun.log"),
        )
        self.git(clone, "init", "-q", "-b", "main")
        self.git(clone, "config", "user.email", "test@example.com")
        self.git(clone, "config", "user.name", "Test")
        self.git(clone, "commit", "-q", "--allow-empty", "-m", "start")
        common = self.git(
            clone, "rev-parse", "--path-format=absolute", "--git-common-dir"
        )
        self.hooks = Path(common) / "hooks"
        (self.hooks / "pre-commit").write_text("# authoring hook\n", encoding="utf-8")
        self.worktree = base / "worktree"
        self.git(clone, "worktree", "add", "-q", "--detach", str(self.worktree))
        script = self.worktree / ".claude/skills/verify-blog/scripts/site.py"
        script.parent.mkdir(parents=True)
        shutil.copy2(SITE, script)
        self.script = script
        fakes = base / "bin"
        fakes.mkdir()
        (fakes / "bun").write_text(FAKE_BUN, encoding="utf-8")
        (fakes / "bun").chmod(0o755)
        self.env["PATH"] = f"{fakes}{os.pathsep}{os.environ['PATH']}"
        self.log = Path(self.env["BUN_LOG"])

    def git(self, cwd: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def run_in_worktree(self, *command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self.worktree,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def test_fake_install_with_scripts_rewrites_shared_hooks(self) -> None:
        before = digest(self.hooks)
        self.run_in_worktree("bun", "install", "--frozen-lockfile")
        self.assertNotEqual(digest(self.hooks), before)

    def test_up_installs_without_scripts_and_keeps_shared_hooks(self) -> None:
        before = digest(self.hooks)
        result = self.run_in_worktree(sys.executable, str(self.script), "up")
        installs = [
            line
            for line in self.log.read_text().splitlines()
            if line.startswith("install")
        ]
        self.assertTrue(installs, result.stderr)
        for line in installs:
            self.assertEqual(line, "install --frozen-lockfile --ignore-scripts")
        self.assertTrue((self.worktree / "node_modules").is_dir())
        self.assertEqual(digest(self.hooks), before)


if __name__ == "__main__":
    unittest.main()
