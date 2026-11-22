"""Exercise browse.py's scroll step and viewport option through the CLI.

The page is served locally and driven through the real CLI. Without the
Chromium build browse.py pins, the cases skip with its install command.
"""

import json
import subprocess
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BROWSE = ROOT / ".claude/skills/verify-blog/scripts/browse.py"

# Smooth scrolling as on the site, a target far below the fold, and a link
# target so a click would navigate away
PAGE = """<!doctype html>
<html style="scroll-behavior: smooth"><head><title>Scroll fixture</title></head>
<body><h1>Top</h1><div style="height: 4000px"></div>
<ul><li><a id="far" href="/elsewhere/">Far row</a></li></ul>
<div style="height: 4000px"></div></body></html>
"""

IN_VIEW = (
    "eval:(() => { const box = document.querySelector('#far').getBoundingClientRect();"
    " return box.top >= 0 && box.bottom <= innerHeight; })()"
)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_: object) -> None:
        pass


class BrowseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.folder = tempfile.TemporaryDirectory()
        site = Path(cls.folder.name) / "site"
        site.mkdir()
        (site / "index.html").write_text(PAGE, encoding="utf-8")
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(Quiet, directory=str(site))
        )
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.folder.cleanup()

    def invoke(self, name: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        out = Path(self.folder.name) / name
        return subprocess.run(
            [
                "uv",
                "run",
                "--quiet",
                str(BROWSE),
                self.url,
                "--out",
                str(out),
                *arguments,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )

    def browse(self, name: str, *arguments: str) -> tuple[int, str, dict]:
        result = self.invoke(name, *arguments)
        if "Chromium did not start" in result.stderr:
            self.skipTest(result.stderr.strip())
        out = Path(self.folder.name) / name
        self.assertTrue((out / "screenshot.png").is_file(), result.stderr)
        state = json.loads((out / "state.json").read_text(encoding="utf-8"))
        return result.returncode, result.stderr, state

    def test_target_starts_below_the_fold(self) -> None:
        code, errors, state = self.browse("plain", "--step", IN_VIEW)
        self.assertEqual(code, 0, errors)
        self.assertEqual(state["evaluations"][0]["result"], False)

    def test_scroll_brings_target_into_view_without_navigating(self) -> None:
        code, errors, state = self.browse(
            "scroll", "--step", "scroll:#far", "--step", IN_VIEW
        )
        self.assertEqual(code, 0, errors)
        self.assertEqual(state["evaluations"][0]["result"], True)
        self.assertEqual(state["url"], self.url)
        self.assertIsNone(state["failure"])

    def test_missing_selector_fails_with_its_name(self) -> None:
        code, errors, state = self.browse("missing", "--step", "scroll:#nowhere")
        self.assertEqual(code, 1)
        self.assertEqual(state["failure"], "scroll: no element matches #nowhere")
        self.assertIn("scroll: no element matches #nowhere", errors)

    def test_scroll_needs_a_selector(self) -> None:
        result = self.invoke("invalid-step", "--step", "scroll:")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid step 'scroll:'", result.stderr)

    def test_viewport_sets_browser_dimensions(self) -> None:
        code, errors, state = self.browse(
            "viewport",
            "--viewport",
            "639x900",
            "--step",
            "eval:window.innerWidth",
            "--step",
            "eval:window.innerHeight",
        )
        self.assertEqual(code, 0, errors)
        self.assertEqual(
            [entry["result"] for entry in state["evaluations"]], [639, 900]
        )

    def test_invalid_viewport_reports_one_error_line(self) -> None:
        for arguments in (
            ("--viewport", "10x10"),
            ("--viewport", "639x900", "--device", "iphone"),
        ):
            with self.subTest(arguments=arguments):
                result = self.invoke("invalid-viewport", *arguments)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(len(result.stderr.splitlines()), 1, result.stderr)
                self.assertIn("--viewport", result.stderr)


if __name__ == "__main__":
    unittest.main()
