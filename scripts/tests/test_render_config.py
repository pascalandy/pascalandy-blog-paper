"""The effective Astro configuration preserves spaces and published heading links."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless((ROOT / "node_modules").is_dir(), "run: just install")
class RenderingConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        (self.root / "node_modules").symlink_to(ROOT / "node_modules")
        self.pages = self.root / "src/pages"
        self.pages.mkdir(parents=True)

    def astro(self, command: str, settings: str) -> subprocess.CompletedProcess[str]:
        project = json.dumps(str(ROOT / "astro.config.ts"))
        (self.root / "astro.config.mjs").write_text(
            f"import config from {project};\n{settings}\n", encoding="utf-8"
        )
        return subprocess.run(
            [str(ROOT / "node_modules/.bin/astro"), command],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    def check_missing(self, setting: str, fix: str) -> None:
        run = self.astro("sync", f"delete config.{setting};\nexport default config;")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn(fix, run.stdout + run.stderr)

    def test_missing_compression_names_the_fix(self) -> None:
        self.check_missing("compressHTML", "set compressHTML: true")

    def test_missing_processor_names_the_fix(self) -> None:
        self.check_missing("markdown.processor", "set markdown.processor to unified")

    def test_inline_words_stay_separate(self) -> None:
        subprocess.run(
            ["git", "init", "--quiet"], cwd=self.root, env=self.env, check=True
        )
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Render fixture",
                "-c",
                "user.email=render-fixture@example.invalid",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--quiet",
                "--allow-empty",
                "-m",
                "Initialize render fixture",
            ],
            cwd=self.root,
            env=self.env,
            check=True,
        )
        (self.pages / "index.astro").write_text(
            "<p><em>Bonjour</em>\n<strong>Pascal</strong></p>", encoding="utf-8"
        )
        run = self.astro(
            "build",
            "export default { ...config, redirects: {}, fonts: [] };",
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        dist = self.root / "dist"
        self.assertRegex((dist / "index.html").read_text(), r"</em>\s+<strong>")
