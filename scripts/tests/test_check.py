"""The verdict rejects unsupported runtimes before running its rows."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check import Failure, check_node


class NodePreflightTests(unittest.TestCase):
    def test_supported_versions(self) -> None:
        for version in ("v22.23.4", "v22.23.5", "v24.0.0"):
            with self.subTest(version=version):
                check_node(">=22.23.4", version, "/example/node")

    def test_unsupported_versions_name_runtime_and_fix(self) -> None:
        for version in ("v22.23.3", "v22.23.4-rc.1", "v24.0.0-rc.1"):
            with self.subTest(version=version):
                with self.assertRaises(Failure) as error:
                    check_node(">=22.23.4", version, "/example/node")
                for detail in (version, "/example/node", ">=22.23.4", "PATH"):
                    self.assertIn(detail, str(error.exception))

    def test_unknown_range_fails_clearly(self) -> None:
        with self.assertRaisesRegex(Failure, "unsupported engines.node range"):
            check_node("^22.23.4", "v22.23.4", "/example/node")
