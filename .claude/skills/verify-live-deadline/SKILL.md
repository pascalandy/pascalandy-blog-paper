---
name: verify-live-deadline
description: Use when changing the live verifier's request timeout, retry window, retry scheduling, or acceptance of a late HTTP response.
---

# Verify the live-check deadline

A correct response that arrives at or after the deadline must fail the live check. Otherwise a deployment can report success after its verification window expired.

1. From the repository root, run the bounded check with [uv](../../../README.md#prerequisites):

   ```sh
   uv run --no-project --python 3.11.16 python -m unittest discover -s scripts/tests -p test_live_deadline_model.py
   ```

   Expect `OK`. CI and local signoff run this test in the `scripts` row of `just check`.

2. Read a failing subtest in clock ticks. The retry model starts with an incorrect homepage at tick zero. The home page recovers during the one-tick sleep. The scheduler can wake zero through three ticks late. A successful HTTP response can take zero through four ticks to return. These 20 combinations cover a four-tick window. Six first-pass cases finish just before, exactly at, or just after the deadline, with either a positive window or retries disabled. With retries disabled, each request gets its own timeout.

3. Compare the observed homepage request count and verdict with [the model](../../../scripts/tests/test_live_deadline_model.py). A wake at the deadline must start zero additional HTTP attempts. A response must return before the deadline to count. The fixture serves real loopback HTTP. The simulated time advances at sleep and when urllib returns the healthy homepage headers. DNS, socket timing, streaming and response framing have separate [transport tests](../../../scripts/tests/test_verify_live.py).

4. `SiteRequests.get` in [the verifier](../../../scripts/verify_live.py) applies the request and window deadlines. `verify` chooses which checks to retry. Last checked against `94d0086`. Run `git diff 94d0086 -- scripts/verify_live.py` when either changes. If the contract changes, update the clock model, rerun the boundary and transport tests, then advance the recorded revision.

## Replay the old verdict

The parent of `1f73bdf` could accept a successful retry after its window expired. Run the historical verifier and its own loopback fixture in a temporary directory:

```sh
replay_dir=$(mktemp -d)
mkdir -p "$replay_dir/scripts/tests"
cp scripts/tests/test_live_deadline_model.py "$replay_dir/scripts/tests/"
git show '1f73bdf^:scripts/verify_live.py' > "$replay_dir/scripts/verify_live.py"
git show '1f73bdf^:scripts/tests/test_verify_live.py' > "$replay_dir/scripts/tests/test_verify_live.py"
git show '1f73bdf^:package.json' > "$replay_dir/package.json"
(cd "$replay_dir" && uv run --no-project --python 3.11.16 python -m unittest discover -s scripts/tests -p test_live_deadline_model.py -f)
```

Expect exit 1. With a one-tick sleep and a three-tick response, the historical verifier returned success at tick four. The window had expired.
