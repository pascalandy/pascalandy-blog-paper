"""The lockfile row catches a second resolved Vite, not peer version ranges."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_lockfile.py"


class LockfileTests(unittest.TestCase):
    def test_duplicate_vite_versions_fail_with_both_versions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            lock = Path(temporary) / "bun.lock"
            lock.write_text("""{
  "packages": {
    "vite": ["vite@8.3.7", "", {}],
    "astro/vite": ["vite@7.3.0", "", {}],
  },
}""")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(lock)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("8.3.7", result.stderr)
            self.assertIn("7.3.0", result.stderr)
            lock.write_text("""{
  "packages": {
    "vite": ["vite@8.3.7", "", {}],
    "other": ["other@1", "", {"peerDependencies": {"vite": "^7 || ^8"}}],
  },
}""")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(lock)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
