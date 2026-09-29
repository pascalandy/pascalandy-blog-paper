---
title: "Development Workflow"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "Commands and workflow for developing, testing, and building the blog"
---

# Development Workflow

> Run `just` to list the recipes: the commands first, then the checks, shipping, and the GitHub workflows. This page explains how they fit together.

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

The staged hook and `just gitleaks` use Gitleaks's built-in rules. They ignore configuration and ignore files from the checked-out branch.

Skip a hook only when you must: `git commit --no-verify` or `git push --no-verify`.

## CI

The CI workflow runs `just check` in a single `check` job, only when started by hand with `just gh-ci`; see [GitHub Actions](#github-actions-manual-only) below. Its deploys wait for the check.

Claude Code on the web runs `.claude/hooks/session-start.sh` when a session starts: it installs uv, Just, gitleaks, and the dependencies with their hooks.

## Merge Gate: Sign Off

CI no longer runs on pull requests. Your machine runs the checks, and [gh-signoff](https://github.com/basecamp/gh-signoff) posts the result to GitHub as a green `signoff` commit status. Once the one-time setup below is done, `main` merges a PR only when its head commit carries one. Repository admins can bypass that rule, so the gate holds only if nobody bypasses it.

Push the branch, then run:

```bash
just signoff
```

It refuses in about a second when a tool is missing, `gh` is signed out, the working tree has changes, or HEAD is not exactly the commit GitHub has for the branch. Then it runs `bun install --frozen-lockfile`, `just ci`, and `just gitleaks`, and only when all three pass does `gh signoff` mark HEAD green. The install step means a dependency bump is built with its new packages, and a `package.json` change without its `bun.lock` fails. The status belongs to that one commit, so every push needs a new signoff. Leave the checkout alone until it finishes: if HEAD moves during the run, it signs nothing.

| Situation                               | Do                                                                                                                                                                                     |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Refused: HEAD not pushed                | `git push`, or `git push -u origin HEAD` for a new branch, then `just signoff`                                                                                                         |
| Refused: GitHub has newer commits       | `git pull`, then `just signoff`                                                                                                                                                        |
| Refused: uncommitted or untracked files | Commit or remove them, push, then `just signoff`                                                                                                                                       |
| A check failed                          | Fix it, commit, push, then `just signoff`                                                                                                                                              |
| Pushed more commits                     | `just signoff` again                                                                                                                                                                   |
| A PR from an agent or Renovate          | `gh pr checkout <number> && just signoff`; Renovate's automerge PRs then merge by themselves                                                                                           |
| Stacked PRs                             | Sign off each layer; a restack changes every head, so sign off each again                                                                                                              |
| A PR from a fork                        | Read the whole diff first, since the checks run its code on your machine; then `gh pr checkout <number>` and `bun install --frozen-lockfile && just ci && just gitleaks && gh signoff` |
| Did this commit get signed off?         | `gh signoff status`                                                                                                                                                                    |
| Merge blocked on `signoff`              | Sign off the PR head, then merge; never merge with `gh pr merge --admin` to skip it                                                                                                    |
| Want a run on a clean machine           | `just gh-ci <branch>`, then `gh run watch`                                                                                                                                             |

Agents run `just ci` and report the result; Pascal signs off. Claude Code on the web has no `gh`, and agents never sign off, merge, or deploy unless Pascal asks.

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

`just deploy-preview` refuses a branch that GitHub does not have, or a local branch whose last commit differs from GitHub's. Uncommitted changes never ship. Add `--no-wait` to return as soon as Sevalla accepts the deployment.

Each PR was signed off on its own, so two PRs can pass separately and still clash once both are on `main`. After several merges, run `just ci` on an up-to-date `main`, or `just gh-ci main`, before `just deploy`.

### Setup

The Sevalla API key is available through chezmoi's keyring on all three machines. Pass it to one deploy command:

```bash
SEVALLA_TOKEN="$(chezmoi secret keyring get --service=SEVALLA_API_KEY --user=api_key)" just deploy
```

Use the same prefix with `just deploy-preview` or `just deploy --dry-run`. The deploy script also reads the macOS Keychain when `SEVALLA_TOKEN` is unset. Keep the token out of shell startup files: every command, including a checked-out PR's scripts, would inherit it.

The site IDs come from the `SEVALLA_STATIC_SITE_ID` and `SEVALLA_STATIC_SITE_ID_PREVIEW` repository variables through `gh variable get`; export either variable to override it. If you create a new API key, also run `gh secret set SEVALLA_TOKEN` so the manual CI workflow deploys with it.

The CI production job uses GitHub's `production` Environment, which permits deployments only from `main`. The Sevalla token remains a repository secret shared with the preview job; separate production and preview tokens are needed to restrict credential access by branch.

## GitHub Actions (manual only)

Every workflow runs only when started by hand, except `claude.yml`, which answers `@claude` mentions. GitHub runs a workflow from the branch you name, but it lists a manual workflow only once `main` has it.

| Recipe                      | Workflow         | What it does                                                                                      |
| --------------------------- | ---------------- | ------------------------------------------------------------------------------------------------- |
| `just gh-ci [ref] [deploy]` | `ci.yml`         | `just check`, the same verdict as on your machine; `deploy` is `none`, `preview`, or `production` |
| `just gh-gitleaks [ref]`    | `gitleaks.yml`   | Scan the full git history for secrets                                                             |
| `just gh-labels <pr>`       | `pr-labeler.yml` | Label a PR from the paths it changes, per `.github/labeler.yml`                                   |

`ref` defaults to the current branch. `production` deploys only `main` and fails on any other ref. The local equivalents are `just ci`, `just gitleaks`, and `just deploy`.

## Notes

- Build output goes to `dist/`
- Pagefind builds the search index during the build
- The `public/` folder contents are copied as-is to `dist/`
