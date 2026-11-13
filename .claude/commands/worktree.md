---
description: Create a worktree under ~/projects/.worktrees from the remote default branch
---

Use `$ARGUMENTS` as the branch topic. Follow [the worktree workflow](../../src/data/blog/dev_workflows/worktree-workflow.md).

1. Fetch the remote and resolve `origin/HEAD`, unless the coordinator supplied a base
2. Create `~/projects/.worktrees/pascalandy-blog-paper-<branch>/` from that base, with a new branch
3. Read the worktree's `AGENTS.md` and nested instructions before editing
4. Install dependencies with `bun install --frozen-lockfile --ignore-scripts`, then run `just overview`
5. Report the worktree path and branch; target every later command at that worktree

The clone stays on its existing branch. Use verify-blog for a preview. Open a ready PR when publication is authorized. Merge and deployment follow the repository's explicit authorization gates.
