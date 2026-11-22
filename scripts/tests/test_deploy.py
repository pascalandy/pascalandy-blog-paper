"""Exercise the deploy CLI with fixture commits and HTTP responses."""

from __future__ import annotations

import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
from unittest.mock import patch

from scripts import deploy

HEAD = "0123456789abcdef0123456789abcdef01234567"
OTHER_HEAD = "fedcba9876543210fedcba9876543210fedcba98"


class DeployTest(unittest.TestCase):
    def setUp(self) -> None:
        self.enterContext(
            patch.dict(
                os.environ, SEVALLA_TOKEN="fixture", SEVALLA_STATIC_SITE_ID="fixture"
            )
        )
        self.github_tip = self.enterContext(
            patch.object(deploy, "github_tip", return_value=HEAD)
        )
        self.enterContext(patch.object(deploy, "POLL_SECONDS", 0))
        self.urlopen = self.enterContext(patch.object(deploy.urllib.request, "urlopen"))

    def responses(self, *payloads: dict[str, str]) -> None:
        self.urlopen.side_effect = [
            BytesIO(json.dumps(payload).encode()) for payload in payloads
        ]

    def run_deploy(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = deploy.main(["production", *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_matching_commit_is_reported_as_deployed(self) -> None:
        self.responses({"id": "build"}, {"status": "success", "commit_sha": HEAD})
        code, stdout, stderr = self.run_deploy()
        self.assertEqual(code, 0, stderr)
        self.assertIn(f"deployed {HEAD} to production\n", stdout)
        self.assertEqual(
            [call.args[0].get_method() for call in self.urlopen.call_args_list],
            ["POST", "GET"],
        )

    def test_different_commit_fails_and_names_both_shas(self) -> None:
        self.github_tip.side_effect = [HEAD, OTHER_HEAD]
        self.responses({"id": "build"}, {"status": "success", "commit_sha": OTHER_HEAD})
        code, stdout, stderr = self.run_deploy()
        self.assertEqual(code, 1)
        self.assertNotIn("deployed", stdout)
        self.assertEqual(stderr, f"error: Sevalla built {OTHER_HEAD}, not {HEAD}\n")

    def test_success_without_a_commit_fails(self) -> None:
        for fields in ({}, {"commit_sha": ""}):
            with self.subTest(fields=fields):
                self.responses({"id": "build"}, {"status": "success", **fields})
                code, stdout, stderr = self.run_deploy()
                self.assertEqual(code, 1)
                self.assertNotIn("deployed", stdout)
                self.assertEqual(
                    stderr, "error: Sevalla did not report the deployed commit\n"
                )

    def test_dry_run_prints_the_request_without_sending_it(self) -> None:
        code, stdout, stderr = self.run_deploy("--dry-run")
        self.assertEqual(code, 0, stderr)
        self.assertEqual(
            stdout,
            f"Deploying main at {HEAD[:7]} to production\n"
            'dry run: POST https://api.sevalla.com/v3/static-sites/fixture/deployments {"branch": "main"}\n',
        )
        self.urlopen.assert_not_called()
