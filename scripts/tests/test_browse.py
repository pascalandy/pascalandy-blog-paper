"""browse.py's scroll step brings a target into the capture without clicking it (#87).

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


class ScrollStepTests(unittest.TestCase):
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

    def browse(self, name: str, *steps: str) -> tuple[int, str, dict]:
        out = Path(self.folder.name) / name
        command = ["uv", "run", "--quiet", str(BROWSE), self.url, "--out", str(out)]
        for step in steps:
            command += ["--step", step]
        result = subprocess.run(
            command, capture_output=True, text=True, check=False, timeout=180
        )
        if "Chromium did not start" in result.stderr:
            self.skipTest(result.stderr.strip())
        self.assertTrue((out / "screenshot.png").is_file(), result.stderr)
        state = json.loads((out / "state.json").read_text(encoding="utf-8"))
        return result.returncode, result.stderr, state

    def test_target_starts_below_the_fold(self) -> None:
        code, errors, state = self.browse("plain", IN_VIEW)
        self.assertEqual(code, 0, errors)
        self.assertEqual(state["evaluations"][0]["result"], False)

    def test_scroll_brings_target_into_view_without_navigating(self) -> None:
        code, errors, state = self.browse("scroll", "scroll:#far", IN_VIEW)
        self.assertEqual(code, 0, errors)
        self.assertEqual(state["evaluations"][0]["result"], True)
        self.assertEqual(state["url"], self.url)
        self.assertIsNone(state["failure"])

    def test_missing_selector_fails_with_its_name(self) -> None:
        code, errors, state = self.browse("missing", "scroll:#nowhere")
        self.assertEqual(code, 1)
        self.assertEqual(state["failure"], "scroll: no element matches #nowhere")
        self.assertIn("scroll: no element matches #nowhere", errors)

    def test_scroll_needs_a_selector(self) -> None:
        result = subprocess.run(
            ["uv", "run", "--quiet", str(BROWSE), self.url, "--out", "unused"]
            + ["--step", "scroll:"],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid step 'scroll:'", result.stderr)


if __name__ == "__main__":
    unittest.main()
