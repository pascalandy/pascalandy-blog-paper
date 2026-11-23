"""Signoff in a linked worktree must preserve the author's executable Git hooks."""

import unittest

from harness import Sandbox
from hooks_fixture import hook_worktrees, installed_hooks


class SignoffHooksTest(unittest.TestCase):
    def test_signoff_preserves_the_authoring_worktrees_hooks(self) -> None:
        sandbox = Sandbox()
        self.addCleanup(sandbox.close)
        hooks = hook_worktrees(sandbox)
        before = installed_hooks(hooks)
        result = sandbox.run("signoff.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(sandbox.load()["statuses"], {sandbox.head(): "success"})
        self.assertEqual(installed_hooks(hooks), before)
