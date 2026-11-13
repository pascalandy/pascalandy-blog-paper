"""The verdict rejects unsupported runtimes before running its rows."""

import os
import signal
import subprocess
import sys
import tempfile
import time
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


DRIVER = """
import sys, pathlib
sys.path.insert(0, {scripts!r})
import check
check.LOGS = pathlib.Path({logs!r})
check.preflight = lambda selected: None
python = sys.executable
check.CHECKS = [check.row(name, (python, "-c", code)) for name, code in {rows!r}]
check.SERIAL = {serial!r}
raise SystemExit(check.main({argv!r}))
"""


class RunnerTests(unittest.TestCase):
    def start(
        self,
        rows: list[tuple[str, str]],
        serial: tuple[str, ...] = (),
        argv: tuple[str, ...] = (),
    ) -> subprocess.Popen[str]:
        self.logs = tempfile.TemporaryDirectory()
        self.addCleanup(self.logs.cleanup)
        driver = DRIVER.format(
            scripts=str(Path(__file__).resolve().parents[1]),
            logs=self.logs.name,
            rows=rows,
            serial=serial,
            argv=list(argv),
        )
        return subprocess.Popen(
            [sys.executable, "-c", driver],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_passing_checks_print_nothing(self) -> None:
        process = self.start([("first", "pass"), ("second", "pass")])
        output, errors = process.communicate(timeout=30)
        self.assertEqual((process.returncode, output, errors), (0, "", ""))

    def test_failures_replay_in_row_order_whichever_finishes_first(self) -> None:
        slow = "import time; time.sleep(0.5); print('slow output'); raise SystemExit(1)"
        fast = "print('fast output'); raise SystemExit(1)"
        process = self.start([("slow", slow), ("passing", "pass"), ("fast", fast)])
        _, errors = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 1)
        lines = [line for line in errors.splitlines() if not line.startswith("==>")]
        self.assertEqual(
            lines,
            [
                "slow output",
                "error: slow failed; rerun: just check --only slow",
                "fast output",
                "error: fast failed; rerun: just check --only fast",
            ],
        )

    def test_independent_rows_run_side_by_side(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:

            def meets(mine: str, other: str) -> str:
                return (
                    "import pathlib, time; "
                    f"pathlib.Path({temporary!r}, {mine!r}).touch(); "
                    "end = time.monotonic() + 10\n"
                    f"while not pathlib.Path({temporary!r}, {other!r}).exists():\n"
                    "    if time.monotonic() > end: raise SystemExit(1)\n"
                    "    time.sleep(0.01)"
                )

            process = self.start(
                [("left", meets("left", "right")), ("right", meets("right", "left"))]
            )
            _, errors = process.communicate(timeout=30)
            self.assertEqual((process.returncode, errors), (0, ""))

    def test_serial_rows_wait_for_the_row_before_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = str(Path(temporary) / "built")
            writes = f"import time, pathlib; time.sleep(0.5); pathlib.Path({marker!r}).touch()"
            reads = f"import pathlib; raise SystemExit(not pathlib.Path({marker!r}).exists())"
            process = self.start(
                [("writes", writes), ("reads", reads)], serial=("writes", "reads")
            )
            _, errors = process.communicate(timeout=30)
            self.assertEqual((process.returncode, errors), (0, ""))

    def test_sigterm_stops_the_running_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pids = Path(temporary)
            sleeps = (
                "import os, pathlib, time; "
                f"pathlib.Path({str(pids)!r}, str(os.getpid())).touch(); time.sleep(60)"
            )
            process = self.start(
                [("free", sleeps), ("lane", sleeps), ("later", "pass")],
                serial=("lane", "later"),
            )
            deadline = time.monotonic() + 20
            while len(list(pids.iterdir())) < 2 and time.monotonic() < deadline:
                time.sleep(0.05)
            children = [int(path.name) for path in pids.iterdir()]
            self.assertEqual(len(children), 2)
            process.send_signal(signal.SIGTERM)
            _, errors = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 143)
            self.assertEqual(errors, "terminated\n")
            for child in children:
                with self.assertRaises(ProcessLookupError):
                    os.kill(child, 0)
