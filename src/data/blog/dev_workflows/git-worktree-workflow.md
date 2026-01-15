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

1. **List existing worktrees:**

   ```bash
   git worktree list
   ```

2. **Determine next tree number:**
   - If no trees exist in `~/devtree/` → use `tree1`
   - If `tree1_*` and `tree2_*` exist → use `tree3`
   - Always increment from the highest existing number

3. **Create the worktree:**

   ```bash
   git worktree add ~/devtree/tree[N]_[feature_name] -b feature/[feature_name]
   ```

4. **Assign port for dev server (if needed):**
   - Main repo: port 4321 (default)
   - tree1: port 4322
   - tree2: port 4323
   - tree3: port 4324
   - Pattern: `4321 + tree_number`

### Example: First Tree

User: "Create a new tree for blue-sky"

```bash
# Agent runs:
git worktree list
# Output shows only main repo, no trees in ~/devtree/

# Agent creates:
git worktree add ~/devtree/tree1_blue-sky -b feature/blue-sky
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
```

---

## Directory Structure

After creating 3 worktrees:

```
~/devtree/
├── tree1_blue-sky/      # feature/blue-sky     (port 4322 if running server)
├── tree2_green-field/   # feature/green-field  (port 4323 if running server)
└── tree3_yellow-sun/    # feature/yellow-sun   (port 4324 if running server)

~/Documents/github_local/
└── pascalandy-blog-paper/   # main branch (port 4321)
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
└── runs dev server at localhost:4321

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

# Preview at localhost:4321 (server already running)

# When done previewing, abort the merge
git merge --abort
```

Your main repo stays on `main`, server keeps running, you just temporarily pull in the changes to preview them.

**Alternative:** Run dev server directly in a worktree on its assigned port:

```bash
cd ~/devtree/tree1_blue-sky
bun run dev --port 4322
```

---

## Publishing a Post

```bash
# 1. Go to the worktree
cd ~/devtree/tree1_blue-sky

# 2. Make sure you're up to date with main
git fetch origin
git rebase origin/main

# 3. Push and create PR
git push -u origin feature/blue-sky
gh pr create --title "Add post: Blue Sky" --body "New blog post about blue sky"

# 4. Wait for PR to be approved and merged on GitHub...

# 5. Update your local main
cd ~/Documents/github_local/pascalandy-blog-paper
git pull origin main

# 6. Clean up the worktree
git worktree remove ~/devtree/tree1_blue-sky
git branch -d feature/blue-sky
```

---

## Your Git History After All 3 Posts

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
| Port: `4321 + tree_number`       | No conflicts between worktrees      |
