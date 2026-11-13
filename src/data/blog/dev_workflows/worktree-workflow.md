---
title: "git worktree workflow"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "Understanding this git worktree workflow"
---

Use one worktree per repository under `~/projects/.worktrees/<repo>-<branch>/`. The clone under `~/projects/` stays on its existing branch. Read its files, but edit only the worktree.

## Create a worktree

Start from the remote default branch, or the base agreed with the coordinator. These commands use `feature/blue-sky` as an example:

```bash
repo="$HOME/projects/pascalandy-blog-paper"
worktree="$HOME/projects/.worktrees/pascalandy-blog-paper-feature-blue-sky"
git -C "$repo" fetch origin
base=$(git -C "$repo" symbolic-ref refs/remotes/origin/HEAD)
git -C "$repo" worktree add "$worktree" -b feature/blue-sky "$base"
```

Read the worktree's `AGENTS.md` and any instructions nested under the files you edit. Install its dependencies without changing shared git hooks:

```bash
cd "$worktree"
bun install --frozen-lockfile --ignore-scripts
just overview
```

Use an explicit working directory or `git -C "$worktree"` for every command. A T3 thread can stay bound to the projects directory after the worktree exists.

## Verify the work

Run `just check`. For browser proof, follow the verify-blog skill. It reuses a matching dev server or starts its own production preview. Pascal's server on port 4320 stays untouched. Do not merge a branch temporarily into the clone to preview it.

## Open a pull request

Fetch the base before opening the PR. Rebase unpublished work onto that base. A stacked PR uses the branch below it, not `main`.

```bash
git -C "$worktree" fetch origin
git -C "$worktree" rebase origin/main
git -C "$worktree" push -u origin feature/blue-sky
gh -R pascalandy/pascalandy-blog-paper pr create --base main
```

Open the PR ready. Report its URL and head SHA. Agents run `just check` and `just signoff-check`. Pascal reviews and signs off. An agent runs `just merge` only when Pascal explicitly authorizes that merge. Deployment needs separate authorization.

## Remove a merged worktree

Confirm that the PR merged and that the worktree has no uncommitted work or running preview. Then remove that worktree and its merged local branch:

```bash
git -C "$repo" worktree remove "$worktree"
git -C "$repo" branch -d feature/blue-sky
```

Leave the clone's branch and working files alone.
