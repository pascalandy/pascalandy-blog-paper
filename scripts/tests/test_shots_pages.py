"""Check pages-file errors through the shots CLI."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / ".claude/skills/verify-blog/scripts/shots.py"


class ShotsPagesCommandTest(unittest.TestCase):
    def test_pages_rejects_unsafe_labels_and_nonroot_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            dist = folder / "dist"
            dist.mkdir()
            (dist / "index.html").write_text("<!doctype html><title>Fixture</title>")
            pages = folder / "pages.json"
            for label, mapping, message in (
                (
                    "traversal-label",
                    {"../escaped": "/blog/photo/"},
                    "unsafe route label",
                ),
                ("relative-route", {"photo": "blog/photo/"}, "site root"),
                ("foreign-route", {"photo": "//evil.example/photo/"}, "site root"),
            ):
                with self.subTest(label=label):
                    pages.write_text(json.dumps(mapping))
                    output = folder / label
                    result = subprocess.run(
                        [
                            "uv",
                            "run",
                            "--quiet",
                            str(SHOTS),
                            "capture",
                            str(dist),
                            "--out",
                            str(output),
                            "--port",
                            "4399",
                            "--pages",
                            str(pages),
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn(message, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertFalse(output.exists())
            self.assertFalse((folder / "escaped").exists())

    def test_pages_file_requires_route_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            dist = folder / "dist"
            dist.mkdir()
            (dist / "index.html").write_text("<!doctype html><title>Fixture</title>")
            pages = folder / "pages.json"
            pages.write_text("[]")
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "--quiet",
                    str(SHOTS),
                    "capture",
                    str(dist),
                    "--out",
                    str(folder / "shots"),
                    "--port",
                    "4399",
                    "--pages",
                    str(pages),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("--pages must map route labels", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
