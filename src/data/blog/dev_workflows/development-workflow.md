---
title: "Development Workflow"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "Commands and workflow for developing, testing, and building the blog"
---

# Development Workflow

> Run `just` to list the recipes: the commands first, then the checks. This page explains how they fit together.

## Verify

`just check` runs the same checks as CI, in the same order. It prints nothing when they all pass. A failing check prints an excerpt of its output, then the command that reruns only that check:

```text
error: content failed; rerun: just check --only content
```

The full output of each check stays in `cache/check/`.

- `just check --list` names the checks; add `-v` to see their commands
- `just check --only content` validates every post against the schema; repeat `--only` to run several checks
- `just check -v` streams the output of every command
- `just qa` formats the repo, then runs `just check`

Without Just installed, run any recipe through uv: `uvx --from rust-just just check`.

## Git Hooks

`just install` installs the dependencies, and [Lefthook](https://lefthook.dev) installs the hooks listed in `lefthook.yml`.

Before each commit:

1. gitleaks scans the staged changes for secrets
2. The staged files are formatted, and the fixes are staged again
3. The staged code is linted
4. When a post, the tag registry, or the schema is staged, the `content` check runs

Before each push, `just check` runs.

Skip a hook only when you must: `git commit --no-verify` or `git push --no-verify`.

## CI

GitHub Actions runs `just check` in a single `check` job, on every pull request whatever its base branch, and on every push to `main` that can change the site. Deploys wait for it.

Claude Code on the web runs `.claude/hooks/session-start.sh` when a session starts: it installs uv, Just, gitleaks, and the dependencies with their hooks.

## Preview Deployment

Deploy a preview build to Sevalla on demand using PR labels.

### How it works

1. Create a PR — CI runs `just check` but **no deploy**
2. Add `preview` label — triggers deployment to Sevalla preview instance
3. Push more commits — continues deploying (label persists)
4. Remove label — stops future preview deploys

### Commands

```bash
# Add preview label to current branch's PR
gh pr edit --add-label "preview"

# Add preview label by PR number
gh pr edit 123 --add-label "preview"

# Create PR with preview label
gh pr create --title "Your title" --label "preview"

# Remove preview label
gh pr edit --remove-label "preview"
```

### AI Assistant Prompt

```
Add the preview label to this PR
```

Or if no PR exists:

```
Create a PR with the preview label
```

## Notes

- Build output goes to `dist/`
- Pagefind builds the search index during the build
- The `public/` folder contents are copied as-is to `dist/`
