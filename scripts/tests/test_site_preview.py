"""Replay the two-checkout race in #177 with a real Astro preview."""

import functools
import importlib.util
import io
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout, suppress
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = Path(".claude/skills/verify-blog/scripts")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def launcher(root: Path):
    scripts = root / SCRIPTS
    shutil.copytree(ROOT / SCRIPTS, scripts)
    spec = importlib.util.spec_from_file_location("blog_site", scripts / "site.py")
    assert spec is not None and spec.loader is not None
    site = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site)
    return site


class PreviewTest(unittest.TestCase):
    def test_listener_that_arrives_during_build_is_never_returned(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        site = launcher(root)
        (root / "node_modules").symlink_to(
            ROOT / "node_modules", target_is_directory=True
        )
        (root / "src").mkdir()
        (root / "src/config.ts").write_text(
            'export const SITE = {title: "Fixture blog"}'
        )
        (root / "dist").mkdir()
        (root / "dist/index.html").write_text("<title>Fixture blog</title>our checkout")
        (root / "build.mjs").write_text(
            'await Bun.write("building", "");'
            'for (let i = 0; !(await Bun.file("resume").exists()); i++) {'
            '  if (i >= 200) throw Error("timed out waiting for competing listener");'
            "  await Bun.sleep(50);"
            "}"
        )
        (root / "package.json").write_text(
            json.dumps(
                {
                    "type": "module",
                    "scripts": {
                        "preview": "astro preview",
                        "build:ci": "bun build.mjs",
                    },
                }
            )
        )
        rival = root / "rival"
        rival.mkdir()
        (rival / "index.html").write_text("<title>Fixture blog</title>other checkout")
        handler = functools.partial(QuietHandler, directory=rival)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler, bind_and_activate=False)
        self.addCleanup(server.server_close)
        server.server_bind()
        site.PREVIEW_PORT = server.server_address[1]
        site.PREVIEW = f"http://127.0.0.1:{site.PREVIEW_PORT}"
        site.DEV = "http://127.0.0.1:0"
        stderr = io.StringIO()

        listener = Thread(target=server.serve_forever, daemon=True)

        with (
            redirect_stderr(stderr),
            redirect_stdout(io.StringIO()),
            patch.dict(os.environ, {"ASTRO_TELEMETRY_DISABLED": "1"}),
            patch.object(site, "install"),
        ):
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    launching = pool.submit(site.main, ["up"])
                    deadline = time.monotonic() + 10
                    while not (root / "building").exists():
                        if launching.done() or time.monotonic() >= deadline:
                            self.fail(f"build did not start: {stderr.getvalue()}")
                        time.sleep(0.02)
                    server.server_activate()
                    listener.start()
                    (root / "resume").touch()
                    self.assertEqual(
                        launching.result(timeout=15), 1, "up accepted the rival blog"
                    )
                self.assertIn(str(site.PREVIEW_PORT), stderr.getvalue())
                self.assertFalse(site.STATE.exists())
                self.assertEqual(site.main(["down"]), 0)
                with urlopen(site.PREVIEW, timeout=3) as response:
                    self.assertIn(b"other checkout", response.read())
            finally:
                site.main(["down"])
                if listener.is_alive():
                    server.shutdown()
                server.server_close()

            try:
                self.assertEqual(site.main(["up"]), 0, stderr.getvalue())
                first_state = json.loads(site.STATE.read_text())
                with urlopen(site.PREVIEW, timeout=3) as response:
                    self.assertIn(b"our checkout", response.read())
                self.assertEqual(site.main(["doctor"]), 0)
                self.assertEqual(site.main(["up"]), 0)
                self.assertEqual(json.loads(site.STATE.read_text()), first_state)
            finally:
                self.assertEqual(site.main(["down"]), 0)
            with self.assertRaises(OSError):
                urlopen(site.PREVIEW, timeout=3)

    def test_interrupted_start_can_be_stopped_before_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            site = launcher(Path(folder))
            (site.ROOT / "node_modules").mkdir()
            (site.ROOT / "package.json").write_text('{"scripts":{"build:ci":"true"}}')
            site.PREVIEW_SCRIPT.write_text("setTimeout(() => {}, 12000)")
            shutil.copy2(
                site.PREVIEW_SCRIPT.with_name("site.py"),
                site.PREVIEW_SCRIPT.with_name("site_launcher.py"),
            )
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    (
                        "import site_launcher as s; s.install=lambda:None; s.site_title=lambda:'fixture'; "
                        "s.fetch=lambda *args:None; s.main(['up'])"
                    ),
                ],
                cwd=site.PREVIEW_SCRIPT.parent,
            )
            try:
                deadline = time.monotonic() + 8
                while not site.STATE.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(
                    site.STATE.exists(), "detached preview has no recovery record"
                )
                process.terminate()
                process.wait(timeout=5)
                state = site.load()
                self.assertTrue(site.ours(state))
                site.down()
                self.assertFalse(site.ours(state))
            finally:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=5)
                site.down()

    def test_old_state_stops_only_a_preview_from_its_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = launcher(root / "first")
            second = launcher(root / "second")
            with socket.socket() as available:
                available.bind(("127.0.0.1", 0))
                port = available.getsockname()[1]
            for site in (first, second):
                site.PREVIEW_PORT = port
                site.PREVIEW = f"http://127.0.0.1:{port}"
            (first.ROOT / "node_modules").symlink_to(
                ROOT / "node_modules", target_is_directory=True
            )
            (first.ROOT / "package.json").write_text(
                '{"scripts":{"preview":"astro preview"}}'
            )
            (first.ROOT / "dist").mkdir()
            (first.ROOT / "dist/index.html").write_text("legacy preview")
            preview = subprocess.Popen(
                [
                    "bun",
                    "run",
                    "preview",
                    "--port",
                    str(port),
                    "--host",
                    "127.0.0.1",
                    "--ignore-lock",
                ],
                cwd=first.ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env={**os.environ, "ASTRO_TELEMETRY_DISABLED": "1"},
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 15
                while first.fetch(first.PREVIEW) != "legacy preview":
                    if preview.poll() is not None or time.monotonic() >= deadline:
                        self.fail("legacy preview did not start")
                    time.sleep(0.05)
                for site in (second, first):
                    site.STATE_DIR.mkdir(parents=True)
                    site.STATE.write_text(
                        json.dumps(
                            {
                                "url": site.PREVIEW,
                                "pid": preview.pid,
                                "started": True,
                                "root": str(site.ROOT),
                            }
                        )
                    )
                    self.assertEqual(site.main(["down"]), 0)
                    if site is second:
                        self.assertEqual(first.fetch(first.PREVIEW), "legacy preview")
                preview.wait(timeout=3)
                self.assertIsNone(first.fetch(first.PREVIEW))
            finally:
                with suppress(ProcessLookupError):
                    os.killpg(preview.pid, signal.SIGKILL)
                preview.wait()
