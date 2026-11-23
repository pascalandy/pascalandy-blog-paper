"""A cold verify-blog preview preserves the shared Git hooks reported in #92."""

import importlib.util
import io
import json
import os
import shutil
import socket
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from urllib.request import urlopen

from harness import SCRIPTS, Sandbox
from hooks_fixture import hook_worktrees, installed_hooks

VERIFY_SCRIPTS = ".claude/skills/verify-blog/scripts"


class SiteInstallTests(unittest.TestCase):
    def test_cold_preview_installs_dependencies_and_keeps_shared_hooks(self) -> None:
        sandbox = Sandbox()
        self.addCleanup(sandbox.close)
        hooks = hook_worktrees(sandbox, build_fixture=True)
        before = installed_hooks(hooks)
        work = sandbox.work
        scripts = work / VERIFY_SCRIPTS
        shutil.copytree(SCRIPTS.parent / VERIFY_SCRIPTS, scripts)
        pages = work / "src" / "pages"
        pages.mkdir(parents=True)
        (pages / "index.astro").write_text(
            '---\nimport { SITE } from "../config";\n---\n<title>{SITE.title}</title>'
        )
        (work / "src/config.ts").write_text(
            'import pkg from "astro/package.json";\n'
            'export const SITE = { title: pkg.name + " hook fixture" };'
        )
        spec = importlib.util.spec_from_file_location("blog_site", scripts / "site.py")
        assert spec is not None and spec.loader is not None
        site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(site)
        with socket.socket() as available:
            available.bind(("127.0.0.1", 0))
            site.PREVIEW_PORT = available.getsockname()[1]
        site.PREVIEW = f"http://127.0.0.1:{site.PREVIEW_PORT}"
        site.DEV = "http://127.0.0.1:0"

        stderr = io.StringIO()
        with (
            patch.dict(
                os.environ, {**sandbox.env, "ASTRO_TELEMETRY_DISABLED": "1"}, clear=True
            ),
            redirect_stderr(stderr),
            redirect_stdout(io.StringIO()),
        ):
            try:
                self.assertFalse((work / "node_modules").exists())
                self.assertEqual(site.main(["up"]), 0, stderr.getvalue())
                with urlopen(site.PREVIEW, timeout=3) as response:
                    self.assertIn(b"<title>astro hook fixture</title>", response.read())
                self.assertEqual(installed_hooks(hooks), before)
                self.assertEqual(sandbox.git("diff", "--", "bun.lock"), "")
            finally:
                site.main(["down"])

            # A stale manifest must fail without rewriting the committed lockfile.
            manifest = work / "package.json"
            package = json.loads(manifest.read_text())
            del package["dependencies"]["astro"]
            manifest.write_text(json.dumps(package))
            with self.assertRaises(site.Failure):
                site.install()
            self.assertEqual(sandbox.git("diff", "--", "bun.lock"), "")
