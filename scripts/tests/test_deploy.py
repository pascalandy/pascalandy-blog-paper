"""Exercise the deploy CLI with fixture commits and HTTP responses."""

from __future__ import annotations

import json
import os
import unittest
from contextlib import chdir, redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
from unittest.mock import patch

from harness import Sandbox

from scripts import deploy

OTHER_HEAD = "fedcba9876543210fedcba9876543210fedcba98"
DEPLOYED_ASTRO = "9.8.7"
LOCAL_ASTRO = "1.2.3"
PRODUCTION = "https://pascalandy.com/"


class DeployTest(unittest.TestCase):
    def setUp(self) -> None:
        sandbox = Sandbox()
        self.addCleanup(sandbox.close)
        client = sandbox.work.with_name("stale-client")
        sandbox.git(
            "clone",
            "--quiet",
            "--branch",
            "feature",
            "--single-branch",
            str(sandbox.origin),
            str(client),
        )
        sandbox.git("switch", "--quiet", "main")
        (sandbox.work / "package.json").write_text(
            json.dumps({"dependencies": {"astro": DEPLOYED_ASTRO}}), encoding="utf-8"
        )
        sandbox.git("add", "package.json")
        self.head = sandbox.commit("Set the deployed Astro version")
        sandbox.git("push", "--quiet", "origin", "main")
        (client / "package.json").write_text(
            json.dumps({"dependencies": {"astro": LOCAL_ASTRO}}), encoding="utf-8"
        )
        self.preview_head = sandbox.git("rev-parse", "feature")
        self.enterContext(chdir(client))
        self.enterContext(
            patch.dict(
                os.environ,
                sandbox.env,
                clear=True,
                SEVALLA_TOKEN="fixture",
                SEVALLA_STATIC_SITE_ID="fixture",
                SEVALLA_STATIC_SITE_ID_PREVIEW="fixture",
            )
        )
        self.github_tip = self.enterContext(
            patch.object(deploy, "github_tip", wraps=deploy.github_tip)
        )
        self.live_checks = self.enterContext(
            patch.object(deploy, "failures", return_value=[])
        )
        self.enterContext(patch.object(deploy, "POLL_SECONDS", 0))
        self.urlopen = self.enterContext(patch.object(deploy.urllib.request, "urlopen"))

    def responses(self, *payloads: dict[str, str]) -> None:
        self.urlopen.side_effect = [
            BytesIO(json.dumps(payload).encode()) for payload in payloads
        ]

    def run_deploy(
        self, *args: str, target: str = "production"
    ) -> tuple[int, str, str]:
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = deploy.main([target, *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_matching_commit_is_reported_as_deployed(self) -> None:
        self.responses({"id": "build"}, {"status": "success", "commit_sha": self.head})
        code, stdout, stderr = self.run_deploy("--expected-commit", self.head)
        self.assertEqual(code, 0, stderr)
        self.assertIn(f"deployed {self.head} to production\n", stdout)
        self.live_checks.assert_called_once_with(
            PRODUCTION, astro_version=DEPLOYED_ASTRO, expected_commit=self.head
        )
        self.assertEqual(
            [call.args[0].get_method() for call in self.urlopen.call_args_list],
            ["POST", "GET"],
        )

    def test_different_commit_fails_and_names_both_shas(self) -> None:
        self.github_tip.side_effect = [self.head, OTHER_HEAD]
        self.responses({"id": "build"}, {"status": "success", "commit_sha": OTHER_HEAD})
        code, stdout, stderr = self.run_deploy()
        self.assertEqual(code, 1)
        self.assertNotIn("deployed", stdout)
        self.assertEqual(
            stderr, f"error: Sevalla built {OTHER_HEAD}, not {self.head}\n"
        )
        self.live_checks.assert_not_called()

    def test_main_moving_after_checks_refuses_to_start_a_deployment(self) -> None:
        code, stdout, stderr = self.run_deploy("--expected-commit", self.preview_head)
        self.assertEqual((code, stdout), (1, ""))
        self.assertIn(f"GitHub main is at {self.head}", stderr)
        self.assertIn(f"checked commit {self.preview_head}", stderr)
        self.urlopen.assert_not_called()

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
                self.live_checks.assert_not_called()

    def test_dry_run_prints_the_request_without_sending_it(self) -> None:
        code, stdout, stderr = self.run_deploy("--dry-run")
        self.assertEqual(code, 0, stderr)
        self.assertEqual(
            stdout,
            f"Deploying main at {self.head[:7]} to production\n"
            'dry run: POST https://api.sevalla.com/v3/static-sites/fixture/deployments {"branch": "main"}\n',
        )
        self.urlopen.assert_not_called()
        self.live_checks.assert_not_called()

    def test_live_failures_use_the_deployed_manifest_and_fail_the_command(self) -> None:
        self.assertNotEqual(
            deploy.run("git", "cat-file", "-e", self.head).returncode, 0
        )
        self.responses({"id": "build"}, {"status": "success", "commit_sha": self.head})
        diagnostics = [
            f"{PRODUCTION}: expected generator 'Astro v{DEPLOYED_ASTRO}', received 'Astro v{LOCAL_ASTRO}'",
            f"{PRODUCTION}rss.xml: expected HTTP 200, received HTTP 404",
        ]

        def check_live(
            base: str, *, astro_version: str, expected_commit: str
        ) -> list[str]:
            self.assertEqual(self.urlopen.call_count, 2)
            self.assertEqual(self.urlopen.call_args.args[0].get_method(), "GET")
            self.assertEqual(
                (base, astro_version, expected_commit),
                (PRODUCTION, DEPLOYED_ASTRO, self.head),
            )
            return diagnostics

        self.live_checks.side_effect = check_live
        code, stdout, stderr = self.run_deploy()
        self.assertEqual(code, 1)
        self.assertNotIn("deployed", stdout)
        self.assertEqual(stderr.splitlines(), diagnostics)
        self.assertEqual(self.live_checks.call_count, 1)

    def test_no_wait_skips_the_commit_and_live_checks(self) -> None:
        self.responses({"id": "build"})
        code, stdout, stderr = self.run_deploy("--no-wait")
        self.assertEqual((code, stderr), (0, ""))
        self.assertIn(
            "skipped the deployed commit check and live checks (--no-wait)\n", stdout
        )
        self.assertEqual(self.urlopen.call_count, 1)
        self.assertEqual(self.urlopen.call_args.args[0].get_method(), "POST")
        self.live_checks.assert_not_called()

    def test_preview_verifies_the_commit_without_live_checks(self) -> None:
        self.responses(
            {"id": "build"}, {"status": "success", "commit_sha": self.preview_head}
        )
        code, stdout, stderr = self.run_deploy("feature", target="preview")
        self.assertEqual((code, stderr), (0, ""))
        self.assertIn(f"deployed {self.preview_head} to preview\n", stdout)
        self.live_checks.assert_not_called()

    def test_live_check_ignores_local_git_replace_refs(self) -> None:
        fetch = deploy.run("git", "fetch", "--no-write-fetch-head", "origin", self.head)
        self.assertEqual(fetch.returncode, 0, fetch.stderr)
        replace = deploy.run("git", "replace", self.head, self.preview_head)
        self.assertEqual(replace.returncode, 0, replace.stderr)
        self.responses({"id": "build"}, {"status": "success", "commit_sha": self.head})
        code, _, stderr = self.run_deploy()
        self.assertEqual(code, 0, stderr)
        self.live_checks.assert_called_once_with(
            PRODUCTION, astro_version=DEPLOYED_ASTRO, expected_commit=self.head
        )
