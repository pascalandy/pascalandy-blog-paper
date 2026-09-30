"""`just signoff` against a bare origin and fake tools: what it signs, and when it refuses."""

from __future__ import annotations

import unittest

from harness import Sandbox

CHECKS = ["bun install --frozen-lockfile", "just ci", "just gitleaks"]


class SignoffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sandbox = Sandbox()
        self.addCleanup(self.sandbox.close)

    def signoff(self) -> tuple[int, str]:
        result = self.sandbox.run("signoff.py")
        return result.returncode, result.stderr

    def test_signs_off_the_pushed_head_after_every_check(self) -> None:
        head = self.sandbox.head()
        code, _ = self.signoff()
        self.assertEqual(code, 0)
        self.assertEqual(self.sandbox.checks_run(), CHECKS)
        self.assertEqual(self.sandbox.load()["statuses"], {head: "success"})

    def test_a_failing_check_signs_nothing(self) -> None:
        self.sandbox.update(failing=["just ci"])
        code, stderr = self.signoff()
        self.assertEqual(code, 1)
        self.assertIn("`just ci` failed; nothing was signed off", stderr)
        self.assertEqual(self.sandbox.checks_run(), CHECKS[:2])
        self.assertEqual(self.sandbox.load()["statuses"], {})

    def test_refuses_untracked_files_and_leaves_them(self) -> None:
        notes = self.sandbox.work / ".napkin" / "notes.md"
        notes.parent.mkdir()
        notes.write_text("draft\n", encoding="utf-8")
        code, stderr = self.signoff()
        self.assertEqual(code, 1)
        self.assertIn("uncommitted or untracked files", stderr)
        self.assertEqual(self.sandbox.checks_run(), [])
        self.assertEqual(notes.read_text(encoding="utf-8"), "draft\n")

    def test_refuses_a_head_github_does_not_have(self) -> None:
        self.sandbox.commit("local only")
        code, stderr = self.signoff()
        self.assertEqual(code, 1)
        self.assertIn("HEAD is not pushed to origin/feature; run: git push", stderr)
        self.assertEqual(self.sandbox.checks_run(), [])

    def test_refuses_when_github_has_newer_commits(self) -> None:
        self.sandbox.commit("pushed from elsewhere")
        self.sandbox.git("push", "--quiet")
        self.sandbox.git("reset", "--quiet", "--hard", "HEAD~1")
        code, stderr = self.signoff()
        self.assertEqual(code, 1)
        self.assertIn("GitHub has newer commits on origin/feature", stderr)

    def test_signs_nothing_when_head_moves_during_the_checks(self) -> None:
        self.sandbox.update(hooks={"just ci": "git commit -q --allow-empty -m moved"})
        code, stderr = self.signoff()
        self.assertEqual(code, 1)
        self.assertIn("while the checks ran", stderr)
        self.assertEqual(self.sandbox.load()["statuses"], {})


if __name__ == "__main__":
    unittest.main()
