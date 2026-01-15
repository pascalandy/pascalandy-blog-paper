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

## Starting 3 New Posts

```bash
# From your main repo
cd ~/Documents/github_local/pascalandy-blog-paper

# Create 3 worktrees for 3 posts
git worktree add ~/devtree/blue-sky feature/blue-sky -b
git worktree add ~/devtree/green-field feature/green-field -b
git worktree add ~/devtree/yellow-sun feature/yellow-sun -b
```

You now have:

```
~/devtree/
├── blue-sky/        # feature/blue-sky
├── green-field/     # feature/green-field
└── yellow-sun/      # feature/yellow-sun

~/Documents/github_local/
└── pascalandy-blog-paper/   # main branch (run dev server here)
```

---

## Daily Workflow

**Working on posts:**

```bash
# Open each in separate VS Code windows
code ~/devtree/blue-sky
code ~/devtree/green-field
code ~/devtree/yellow-sun
```

**Committing as you go:**

```bash
cd ~/devtree/blue-sky
git add .
git commit -m "fix typos in blue-sky"

# ... later that day ...
git add .
git commit -m "rewrite intro section"
```

---

## Dev Server and Previewing Posts

**No port conflicts.** You only run the dev server once, in your main repo.

The worktrees at `~/devtree/` are just for **editing files**. You don't run a server there.

```
~/Documents/github_local/pascalandy-blog-paper/   # main branch
└── runs dev server at localhost:4321

~/devtree/blue-sky/        # just edit files here
~/devtree/green-field/     # just edit files here
~/devtree/yellow-sun/      # just edit files here
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

---

## Publishing Blue Sky (First Post)

```bash
# 1. Go to the worktree
cd ~/devtree/blue-sky

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
git worktree remove ~/devtree/blue-sky
git branch -d feature/blue-sky
```

---

## Publishing Green Field (Second Post, Days Later)

```bash
# 1. Go to the worktree
cd ~/devtree/green-field

# 2. Rebase on latest main (which now includes blue-sky)
git fetch origin
git rebase origin/main

# 3. Push and create PR
git push -u origin feature/green-field
gh pr create --title "Add post: Green Field" --body "New blog post about green field"

# 4. Wait for PR to be approved and merged on GitHub...

# 5. Update local main
cd ~/Documents/github_local/pascalandy-blog-paper
git pull origin main

# 6. Clean up
git worktree remove ~/devtree/green-field
git branch -d feature/green-field
```

---

## Publishing Yellow Sun (Third Post, Weeks Later)

```bash
# 1. Go to the worktree
cd ~/devtree/yellow-sun

# 2. Rebase on latest main
git fetch origin
git rebase origin/main

# 3. Push and create PR
git push -u origin feature/yellow-sun
gh pr create --title "Add post: Yellow Sun" --body "New blog post about yellow sun"

# 4. Wait for PR to be approved and merged on GitHub...

# 5. Update local main
cd ~/Documents/github_local/pascalandy-blog-paper
git pull origin main

# 6. Clean up
git worktree remove ~/devtree/yellow-sun
git branch -d feature/yellow-sun
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
git worktree remove ~/devtree/blue-sky

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
