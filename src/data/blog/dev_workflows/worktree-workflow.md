---
title: "git worktree workflow"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "understadning this git worktree workflow"
---

# Complete Worktree Workflow for Blog Posts

## One-Time Setup

```bash
mkdir ~/devtree
```

---

## Agent Instructions: Creating a New Worktree

When user says "create a new tree" for feature `[feature_name]`:

### Phase 1: Setup (default on command invocation)

1. **Ensure `~/devtree/` exists**

2. **List existing worktrees:**

   ```bash
   git worktree list
   ```

3. **Determine next tree number:**
   - If no trees exist in `~/devtree/` → use `tree1`
   - If `tree1_*` and `tree2_*` exist → use `tree3`
   - Always increment from the highest existing number

4. **Create the worktree:**

   ```bash
   git worktree add ~/devtree/tree[N]_[feature_name] -b feature/[feature_name]
   ```

5. **Copy dependencies from main repo** (saves reinstall time):

   ```bash
   cp -r ~/Documents/github_local/pascalandy-blog-paper/node_modules ~/devtree/tree[N]_[feature_name]/
   cp -r ~/Documents/github_local/pascalandy-blog-paper/.astro ~/devtree/tree[N]_[feature_name]/ 2>/dev/null || true
   ```

6. **Confirm and report:**
   - Run `git worktree list` to confirm
   - Report assigned port: `4320 + tree_number` (tree1=4321, tree2=4322, etc.)

### Phase 2: Work (after setup completes)

7. Do the work in `~/devtree/tree[N]_[feature_name]`
8. Commit changes atomically as you go
9. Report back what was created/modified

### Phase 3: Publish (when user says "ready" or "publish")

10. Rebase on latest main:

    ```bash
    cd ~/devtree/tree[N]_[feature_name]
    git fetch origin
    git rebase origin/main
    ```

11. Push and create PR:

    ```bash
    git push -u origin feature/[feature_name]
    gh pr create --title "Add: [feature_name]" --body "New content/feature: [feature_name]"
    ```

12. Report PR URL to user

### Phase 4: Cleanup (after PR is merged)

13. Update local main:

    ```bash
    cd ~/Documents/github_local/pascalandy-blog-paper
    git pull origin main
    ```

14. Remove worktree and branch:
    ```bash
    git worktree remove ~/devtree/tree[N]_[feature_name]
    git branch -d feature/[feature_name]
    ```

### Port Assignment

| Worktree  | Port |
| --------- | ---- |
| main      | 4320 |
| tree1\_\* | 4321 |
| tree2\_\* | 4322 |
| tree3\_\* | 4323 |

Pattern: `4320 + tree_number`

### Example: First Tree

User: "Create a new tree for blue-sky"

```bash
# Agent runs:
git worktree list
# Output shows only main repo, no trees in ~/devtree/

# Agent creates:
git worktree add ~/devtree/tree1_blue-sky -b feature/blue-sky

# Agent copies dependencies (no reinstall needed):
cp -r ~/Documents/github_local/pascalandy-blog-paper/node_modules ~/devtree/tree1_blue-sky/
cp -r ~/Documents/github_local/pascalandy-blog-paper/.astro ~/devtree/tree1_blue-sky/ 2>/dev/null || true
```

### Example: Third Tree

User: "Create a new tree for yellow-sun"

```bash
# Agent runs:
git worktree list
# Output shows:
# ~/Documents/github_local/pascalandy-blog-paper  main
# ~/devtree/tree1_blue-sky                        feature/blue-sky
# ~/devtree/tree2_green-field                     feature/green-field

# Agent creates:
git worktree add ~/devtree/tree3_yellow-sun -b feature/yellow-sun

# Agent copies dependencies:
cp -r ~/Documents/github_local/pascalandy-blog-paper/node_modules ~/devtree/tree3_yellow-sun/
cp -r ~/Documents/github_local/pascalandy-blog-paper/.astro ~/devtree/tree3_yellow-sun/ 2>/dev/null || true
```

---

## Directory Structure

After creating 3 worktrees:

```
~/devtree/
├── tree1_blue-sky/      # feature/blue-sky     (port 4321 if running server)
├── tree2_green-field/   # feature/green-field  (port 4322 if running server)
└── tree3_yellow-sun/    # feature/yellow-sun   (port 4323 if running server)

~/Documents/github_local/
└── pascalandy-blog-paper/   # main branch (port 4320)
```

---

## Daily Workflow

**Working on posts:**

```bash
# Open each in separate VS Code windows
code ~/devtree/tree1_blue-sky
code ~/devtree/tree2_green-field
code ~/devtree/tree3_yellow-sun
```

**Committing as you go:**

```bash
cd ~/devtree/tree1_blue-sky
git add .
git commit -m "fix typos in blue-sky"

# ... later that day ...
git add .
git commit -m "rewrite intro section"
```

---

## Dev Server and Previewing Posts

**Default approach:** Run dev server only in main repo.

The worktrees at `~/devtree/` are just for **editing files**. You don't run a server there.

```
~/Documents/github_local/pascalandy-blog-paper/   # main branch
└── runs dev server at localhost:4320

~/devtree/tree1_blue-sky/      # just edit files here
~/devtree/tree2_green-field/   # just edit files here
~/devtree/tree3_yellow-sun/    # just edit files here
```

**To preview a post before publishing:**

```bash
# In your main repo (where dev server is running)
cd ~/Documents/github_local/pascalandy-blog-paper

# Temporarily merge the branch (without committing)
git merge feature/blue-sky --no-commit --no-ff

# Preview at localhost:4320 (server already running)

# When done previewing, abort the merge
git merge --abort
```

Your main repo stays on `main`, server keeps running, you just temporarily pull in the changes to preview them.

**Alternative:** Run dev server directly in a worktree on its assigned port:

```bash
cd ~/devtree/tree1_blue-sky
bun run dev --port 4321
```

---

## Git History After Merging Posts

```
main: A---B---C---D (blue-sky merged)---E (green-field merged)---F (yellow-sun merged)
```

Clean. Linear. Each post merged one after another.

---

## Useful Commands

```bash
# List all worktrees
git worktree list

# Remove a worktree after merging
git worktree remove ~/devtree/tree1_blue-sky

# Clean up if you manually deleted a worktree folder
git worktree prune

# See all branches
git branch -a
```

---

## Key Rules

| Rule                             | Why                                 |
| -------------------------------- | ----------------------------------- |
| Always rebase before pushing     | Keeps commits on top, clean history |
| One post = one branch = one PR   | Clean separation                    |
| Merge via GitHub PR, not locally | PR gives you CI checks, review      |
| Delete worktree after merge      | Prevents stale folders piling up    |
| Never commit to main directly    | All changes go through PRs          |
| Naming: `tree[N]_[feature]`      | Auto-increment, predictable ports   |
| Port: `4320 + tree_number`       | No conflicts between worktrees      |
| Copy node_modules on creation    | Skip reinstall, ready to run        |

---

## Dependency Management

**On worktree creation:** Dependencies are copied from main repo automatically.

**When to re-sync dependencies:**

If `package.json` changes in main (new packages added), re-copy to worktrees:

```bash
# From main repo after pulling changes with new dependencies
bun install
cp -r ~/Documents/github_local/pascalandy-blog-paper/node_modules ~/devtree/tree1_[feature]/
```

**What gets copied:**

| Item           | Purpose                      |
| -------------- | ---------------------------- |
| `node_modules` | All installed packages       |
| `.astro`       | Astro build cache (optional) |

**Not copied (regenerated as needed):**

- `dist/` - build output
- `.vercel/` - deployment cache
