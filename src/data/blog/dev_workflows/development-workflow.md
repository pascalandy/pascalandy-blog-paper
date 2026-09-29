---
title: "Development Workflow"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "Commands and workflow for developing, testing, and building the blog"
---

# Development Workflow

> Quick reference for all development commands.

## Daily Development

```bash
# Start dev server (hot reload)
bun run lint && bun run format | tspin && bun run build | tspin && bun run dev | tspin

# Preview production build locally
bun run preview
```

## Quality Checks

Run these before committing:

```bash
# Type checking (Astro + TypeScript)
bun astro check

# Linting (ESLint)
bun run lint

# Format check (Prettier)
bun run format:check
# stop on error

# Auto-format all files
bun run format | tspin
```

## Production Build

```bash
# Full build pipeline
bun run build
```

This runs:

1. `astro check` — TypeScript validation
2. `astro build` — Generate static site in `dist/`
3. `pagefind --site dist` — Build search index
4. `cp -r dist/pagefind public/` — Copy search index to public

## Sync Content Collections

```bash
# Regenerate TypeScript types for content
bun run sync
```

Use after modifying `src/content.config.ts` or adding new content fields.

## Command Summary

| Command                | Purpose                          |
| ---------------------- | -------------------------------- |
| `bun run dev`          | Start dev server with hot reload |
| `bun run build`        | Full production build            |
| `bun run preview`      | Preview production build         |
| `bun run sync`         | Sync content collection types    |
| `bun astro check`      | TypeScript type checking         |
| `bun run lint`         | ESLint code linting              |
| `bun run format`       | Auto-format with Prettier        |
| `bun run format:check` | Check formatting without changes |

## Git Hooks (Automated Quality Checks)

Git hooks are configured via [Lefthook](https://github.com/evilmartians/lefthook) to automatically run quality checks.

### Pre-commit (runs on every commit)

1. `bun run format:check` — Verify formatting
2. `bun run lint` — Check for linting errors

### Pre-push (runs before pushing)

1. `bun astro check` — TypeScript validation
2. `bun run build` — Full production build

### Setup

Hooks are installed automatically when you run `bun install` (via the `prepare` script). To manually reinstall:

```bash
bunx lefthook install
```

### Bypassing Hooks (use sparingly)

```bash
# Skip pre-commit hooks
git commit --no-verify -m "message"

# Skip pre-push hooks
git push --no-verify
```

## Merge Gate: Sign Off

GitHub Actions no longer runs on pull requests. Your machine runs the checks, and [gh-signoff](https://github.com/basecamp/gh-signoff) posts the result to GitHub as a green `signoff` commit status. `main` merges a PR only when its head commit carries one.

Push the branch, then run:

```bash
just signoff
```

It refuses in about a second when a tool is missing, the working tree has changes, or HEAD is not pushed. Then it runs `just ci` and `just gitleaks`, and only when both pass does `gh signoff` mark HEAD green. The status belongs to that one commit, so every push needs a new signoff. Leave the checkout alone until it finishes: if HEAD moves during the run, it signs nothing.

| Situation                               | Do                                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------------------- |
| Refused: HEAD not pushed                | `git push`, or `git push -u origin HEAD` for a new branch, then `just signoff`      |
| Refused: uncommitted or untracked files | Commit or remove them, push, then `just signoff`                                    |
| A check failed                          | Fix it, commit, push, then `just signoff`                                           |
| Pushed more commits                     | `just signoff` again                                                                |
| A PR from an agent or Renovate          | `gh pr checkout <number> && just signoff`; auto-merge completes once it is green    |
| Stacked PRs                             | Sign off each layer; a restack changes every head, so sign off each again           |
| A PR from a fork                        | `gh pr checkout <number>`, then `just ci && just gitleaks && gh signoff`            |
| Did this commit get signed off?         | `gh signoff status`                                                                 |
| Merge blocked on `signoff`              | Sign off the PR head, then merge; never merge with `gh pr merge --admin` to skip it |
| Want a run on a clean machine           | `just gh-ci <branch>`, then `gh run watch`                                          |

Agents in Claude Code on the web have no `gh`, so they run `just ci` and report the result; Pascal signs off.

### One-time setup

Install the prerequisites listed in the README, including the gh-signoff extension. Then, once per repository, require signoff to merge into `main`:

```bash
gh signoff install
gh signoff check
```

`gh signoff install` creates the `signoff` ruleset on `main`: it requires the `signoff` status to merge a PR, and it blocks force pushes and deleting `main`. Repository admins bypass it, so a direct push to `main` still works.

## Deploy

Merging no longer deploys. Sevalla builds from GitHub, so push first, then deploy from the terminal:

```bash
# Ship GitHub's main to production and wait for the build
just deploy

# Ship a pushed branch, the current one by default, to the preview site
just deploy-preview
just deploy-preview my-branch

# Check the setup without deploying
just deploy --dry-run
```

`just deploy-preview` refuses a branch that GitHub does not have, or whose local tip differs from GitHub's, so the preview matches your checkout. Add `--no-wait` to return as soon as Sevalla accepts the deployment.

### Setup

Export a Sevalla API key in `~/.zshrc`:

```bash
export SEVALLA_TOKEN="..."
```

The site IDs come from the `SEVALLA_STATIC_SITE_ID` and `SEVALLA_STATIC_SITE_ID_PREVIEW` repository variables through `gh variable get`; export either variable to override it. If you create a new API key, also run `gh secret set SEVALLA_TOKEN` so the manual CI workflow deploys with it.

## GitHub Actions (manual only)

Every workflow runs only when started by hand, except `claude.yml`, which answers `@claude` mentions. GitHub runs a workflow from the branch you name, but it lists a manual workflow only once `main` has it.

| Recipe                      | Workflow         | What it does                                                                             |
| --------------------------- | ---------------- | ---------------------------------------------------------------------------------------- |
| `just gh-ci [ref] [deploy]` | `ci.yml`         | Lint, format check, typecheck, and build; `deploy` is `none`, `preview`, or `production` |
| `just gh-gitleaks [ref]`    | `gitleaks.yml`   | Scan the full git history for secrets                                                    |
| `just gh-labels <pr>`       | `pr-labeler.yml` | Label a PR from the paths it changes, per `.github/labeler.yml`                          |

`ref` defaults to the current branch. `production` deploys only `main` and fails on any other ref. The local equivalents are `just ci`, `just gitleaks`, and `just deploy`.

## Notes

- Build output goes to `dist/` directory
- Search index is generated by Pagefind during build
- The `public/` folder contents are copied as-is to `dist/`
