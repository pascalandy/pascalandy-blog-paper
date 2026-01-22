---
title: "Release Please Workflow"
tags:
  - dev-notes
date_created: 2026-01-22
author: Pascal Andy
description: "Automated releases using Release Please with auto-merge"
---

# Release Please Workflow

> Hands-free releases using [Release Please](https://github.com/googleapis/release-please) with auto-merge enabled.

## How It Works

```
PR merged to main
       ↓
Release Please creates/updates Release PR
       ↓
CI passes → Auto-merge kicks in
       ↓
Release PR merges automatically
       ↓
GitHub Release + tag created
```

No manual intervention required after merging your PR.

## Writing Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

| Prefix   | Version Bump          | Example                      |
| -------- | --------------------- | ---------------------------- |
| `feat:`  | Minor (0.1.0 → 0.2.0) | `feat: add dark mode toggle` |
| `fix:`   | Patch (0.1.0 → 0.1.1) | `fix: resolve search crash`  |
| `feat!:` | Major (0.1.0 → 1.0.0) | `feat!: redesign API`        |
| `docs:`  | No release            | `docs: update README`        |
| `chore:` | No release            | `chore: update deps`         |

Breaking changes can also use footer:

```
feat: redesign theme system

BREAKING CHANGE: theme config moved from config.ts to themes.ts
```

## Configuration Files

| File                                   | Purpose                                  |
| -------------------------------------- | ---------------------------------------- |
| `release-please-config.json`           | Release type, changelog path, bump rules |
| `.release-please-manifest.json`        | Tracks current version (updated by bot)  |
| `.github/workflows/release-please.yml` | GitHub Actions workflow                  |

## Manual Commands

Usually not needed, but available if auto-merge is disabled:

```bash
# List pending release PRs
gh pr list --label "autorelease: pending"

# Manually merge a release PR
gh pr merge <PR_NUMBER> --squash

# Enable auto-merge on a release PR
gh pr merge <PR_NUMBER> --auto --squash
```

## Checking Release Status

```bash
# View recent releases
gh release list

# View specific release
gh release view v0.2.0

# View release PR status
gh pr list --label "autorelease: pending"
```

## Troubleshooting

### Release PR not created?

- Commits must use Conventional Commits format
- Only `feat:` and `fix:` trigger releases
- Check workflow ran: Actions → Release Please

### Auto-merge not working?

- Verify "Allow auto-merge" is enabled in repo settings (Settings → General → Pull Requests)
- Check that required CI checks are passing
- The release PR needs all branch protection requirements met

### Wrong version?

The version is tracked in `.release-please-manifest.json`. To reset:

1. Edit `.release-please-manifest.json` with the correct version
2. Edit `package.json` version to match
3. Commit and push

## GitHub Settings Required

For auto-merge to work, ensure this repo setting is enabled:

**Settings → General → Pull Requests → Allow auto-merge**

This setting enables the feature; it doesn't auto-merge everything. Each PR must explicitly enable auto-merge (which our workflow does only for release PRs).
