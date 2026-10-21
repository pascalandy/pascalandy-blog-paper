---
title: How to update dependencies
author: Pascal Andy
date_created: 2023-07-20
tags:
  - dev-notes
description: How to update project dependencies using bun and npm-check-updates.
---

Updating dependencies can be tedious, but neglecting them is not a good idea. Here's how to update dependencies efficiently using bun.

## Updating Package Dependencies

The recommended way is using [npm-check-updates](https://www.npmjs.com/package/npm-check-updates). With bun, you don't need to install it globally - just use `bunx`:

```bash
# Check all available updates
bunx npm-check-updates
```

### Update by severity

**Patch updates** (safe, bug fixes only):

```bash
bunx npm-check-updates -u --target patch
bun install
```

**Minor updates** (new features, usually safe):

```bash
bunx npm-check-updates -i --target minor
bun install
```

**Major updates** (breaking changes, be careful):

```bash
bunx npm-check-updates -i
bun install
```

For major updates, always read the release notes before updating.

### Interactive mode

Use `-i` flag to select which packages to update:

```bash
bunx npm-check-updates -i
```

If no more packages to update, you're done.

## Prove the build output

For an upgrade that must leave the published site unchanged, build the old and new commits in separate worktrees. Use the same `cache/fonts/` files in both. Google Fonts can return different font files to two fresh builds, which would change the generated images even if the code is identical.

Run the comparison from the new worktree:

```bash
just parity /absolute/old/dist /absolute/new/dist --json /absolute/parity.json
```

The command exits 0 with `IDENTICAL` when routes, page content, images, feeds, search postings, and assets match. Read the JSON report for any material finding. If the upgrade intentionally changes output, record each accepted finding's exact fingerprint and its reason in a ledger, then rerun with `--accept /absolute/ledger.json`. A later change gets a different fingerprint and must be reviewed again.

Capture the browser matrix when the upgrade can change rendering or navigation:

```bash
just shots capture /absolute/old/dist --out /absolute/old-shots --port 4391
just shots capture /absolute/new/dist --out /absolute/new-shots --port 4392
just shots diff /absolute/old-shots /absolute/new-shots --json /absolute/shots.json
```

The diff report gives a changed-pixel ratio for each of the 44 shots and identifies the selected image files where pixels changed. Use ports 4391 to 4399; port 4320 belongs to the developer's server.
