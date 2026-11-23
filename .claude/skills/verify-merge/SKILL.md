---
name: verify-merge
description: "Use when changing just merge, signoff timing, PR retargeting, the pinned head, or recovery after a lost merge response."
---

# Verify the merge result

A successful `just merge` must mean that GitHub confirmed the tested head landed on `main`. A PR can change between the last poll and the merge request. Reporting success for another branch can send a maintainer to release changes that never reached `main`.

1. From the repository root, check `git --version` and `uv --version`. The model uses Git with `merge-tree --write-tree` and Python's standard library. The [prerequisites](../../../README.md#prerequisites) cover tool setup. Run the bounded model and its companion Git integration cases:

   ```bash
   uv run --no-project --python 3.11.16 python -m unittest discover -s scripts/tests -p test_merge.py
   ```

   The command must end in `OK`. Every merge in this check goes into a temporary bare Git repository. The manual CI workflow and local signoff run these tests through `just check --only scripts`.

2. On failure, read the reported event, its timing, the merge response, and whether GitHub answered the final read. Compare the command's exit status with the parents of the recorded `main` and `layer-1` commits. A merge on `layer-1` after an early retarget is a defect even when the command reports failure. A late retarget can move `layer-1`: GitHub's match-head guard pins only the head. The command must refuse to report success.

3. When changing the merge protocol, compare [the CLI](../../../scripts/merge.py) with [the model](../../../scripts/tests/test_merge.py) and [the GitHub double](../../../scripts/tests/fake.py). The model crosses the signoff, last eligibility poll, merge request and final read in `merge`, `wait_until_mergeable`, and `land`. Last checked against `94d0086`. Run `git diff 94d0086 -- scripts/merge.py scripts/signoff.py` to see what changed. Advance that revision after verifying the same steps and assumptions, or update the events to match the new protocol. Run the historical failure and the current suite again before accepting an updated model.

## Bound

One open, same-repository PR starts on its tested head and targets `main`. One concurrent actor can retarget it, push another head, close it, or merge that other head. Four traces place the edit during signoff. Thirty place one of the four edits or no edit at submission, combined with a normal response, refusal or lost response and with an available or unavailable final read. An edit caught at the last poll ends that trace before submission.

The verdict compares the CLI status with real Git refs in the fixture. It covers one competing actor and one merge attempt. The GitHub double supplies API decisions and failures. Branch protection on the hosted repository, API consistency and sequences with multiple racing edits need separate evidence.

## Replay the historical failure

On the parent of `537b29b`, the last poll saw `main`, the PR then moved to `layer-1`, and GitHub merged there. The CLI still printed success. To replay it without changing the checkout:

```bash
replay_dir=$(mktemp -d)
mkdir -p "$replay_dir/scripts/tests"
cp scripts/tests/{test_merge,harness,fake}.py "$replay_dir/scripts/tests/"
git show '537b29b^:scripts/merge.py' > "$replay_dir/scripts/merge.py"
git show '537b29b^:scripts/signoff.py' > "$replay_dir/scripts/signoff.py"
uv run --no-project --python 3.11.16 python -m unittest discover \
  -s "$replay_dir/scripts/tests" -p test_merge.py -f -k bounded_merge_races
```

Expect exit 1 for `retarget` at `gh pr merge` with an available final read. A different failure needs investigation before it counts as a replay.
