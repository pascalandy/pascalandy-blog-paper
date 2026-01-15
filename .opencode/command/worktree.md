---
description: Create a new git worktree for parallel development (posts, features)
---

## Arguments

- `$ARGUMENTS` = feature name (e.g., "blue-sky", "new-login-page")

## Workflow Reference

Read and follow: `src/data/blog/dev_workflows/git-worktree-workflow.md`

## Task

### Phase 1: Setup

1. Ensure `~/devtree/` directory exists
2. From the main repo, create the worktree:
   ```bash
   git worktree add ~/devtree/$ARGUMENTS feature/$ARGUMENTS -b
   ```
3. Confirm creation with `git worktree list`

### Phase 2: Work

4. Do the work in `~/devtree/$ARGUMENTS`
5. Commit changes atomically as you go (use commit skill)
6. Report back what was created/modified

### Phase 3: Publish (when user says "ready" or "publish")

7. Rebase on latest main:
   ```bash
   cd ~/devtree/$ARGUMENTS
   git fetch origin
   git rebase origin/main
   ```
8. Push and create PR:
   ```bash
   git push -u origin feature/$ARGUMENTS
   gh pr create --title "Add: $ARGUMENTS" --body "New content/feature: $ARGUMENTS"
   ```
9. Report PR URL to user

### Phase 4: Cleanup (after PR is merged)

10. Update local main:
    ```bash
    cd ~/Documents/github_local/pascalandy-blog-paper
    git pull origin main
    ```
11. Remove worktree and branch:
    ```bash
    git worktree remove ~/devtree/$ARGUMENTS
    git branch -d feature/$ARGUMENTS
    ```

## Important Notes

- Dev server runs ONLY in main repo (localhost:4321)
- Worktrees are for editing files only, not running servers
- To preview changes, use temporary merge in main repo:
  ```bash
  git merge feature/$ARGUMENTS --no-commit --no-ff
  # preview at localhost:4321
  git merge --abort
  ```
