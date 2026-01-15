---
description: Create a new git worktree for parallel development (posts, features)
---

## Arguments

- `$ARGUMENTS` = feature name (e.g., "blue-sky", "new-login-page")

## Instructions

Follow the workflow documented in:
`src/data/blog/dev_workflows/git-worktree-workflow.md`

Execute the **"Agent Instructions: Creating a New Worktree"** section with `$ARGUMENTS` as the feature name.

## Phases

| Phase     | Trigger                              |
| --------- | ------------------------------------ |
| Setup     | Default (on command invocation)      |
| Work      | After setup completes                |
| Publish   | User says "ready" or "publish"       |
| Cleanup   | After PR is merged                   |
