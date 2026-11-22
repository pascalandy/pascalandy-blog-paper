"""Enumerate when a late wake-up or a late HTTP response changes the live verdict."""

import unittest
from itertools import product
from unittest.mock import patch
from urllib.request import OpenerDirector

import test_verify_live as fixtures


class DeadlineModelTest(unittest.TestCase):
    def test_deadline_boundaries(self) -> None:
        site = fixtures.VerifyLiveTest()
        self.addCleanup(site.doCleanups)
        site.setUp()
        verifier = fixtures.verify_live
        healthy = site.home(fixtures.ASTRO)
        real_open = OpenerDirector.open
        window = 4
        interval = 1

        def trace(budget: int, oversleep: int | None, response_time: int) -> None:
            now = 0
            starts = []
            site.requests.clear()
            site.pages["/"] = healthy if oversleep is None else site.home("0.0.0")

            def wake(seconds: float) -> None:
                nonlocal now
                self.assertIsNotNone(oversleep)
                now += seconds + oversleep
                site.pages["/"] = healthy

            def open_http(opener, request, **kwargs):
                nonlocal now
                starts.append(now)
                response = real_open(opener, request, **kwargs)
                if request.full_url == site.base and site.pages["/"] == healthy:
                    now += response_time
                return response

            with (
                patch.object(verifier, "time") as clock,
                patch.object(verifier, "RETRY_INTERVAL_SECONDS", interval),
                patch.object(OpenerDirector, "open", open_http),
            ):
                clock.monotonic.side_effect = lambda: now
                clock.sleep.side_effect = wake
                errors = verifier.failures(site.base, fixtures.ASTRO, budget)

            start = interval + oversleep if oversleep is not None else 0
            expected_attempts = 1 + int(oversleep is not None and start < budget)
            self.assertEqual(site.requests["/"], expected_attempts)
            limit = budget or verifier.HTTP_TIMEOUT_SECONDS
            self.assertEqual(not errors, start + response_time < limit, errors)
            if budget:
                self.assertTrue(all(tick < budget for tick in starts), starts)

        for late_wake, response_time in product(range(window), range(window + 1)):
            with self.subTest(late_wake=late_wake, response_time=response_time):
                trace(window, late_wake, response_time)

        for budget in (0, window):
            limit = budget or verifier.HTTP_TIMEOUT_SECONDS
            for response_time in (limit - 1, limit, limit + 1):
                with self.subTest(first_pass=budget, response_time=response_time):
                    trace(budget, None, response_time)
