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
2. List existing worktrees to determine next tree number:
   ```bash
   git worktree list
   ```
3. Determine the next available tree number:
   - If no trees exist in `~/devtree/` → use `tree1`
   - If `tree1_*` exists → use `tree2`
   - Always increment from the highest existing number
4. Create the worktree with numbered naming:
   ```bash
   git worktree add ~/devtree/tree[N]_$ARGUMENTS -b feature/$ARGUMENTS
   ```
5. Confirm creation with `git worktree list`
6. Report the assigned port: `4321 + tree_number` (tree1 = 4322, tree2 = 4323, etc.)

### Phase 2: Work

7. Do the work in `~/devtree/tree[N]_$ARGUMENTS`
8. Commit changes atomically as you go (use commit skill)
9. Report back what was created/modified

### Phase 3: Publish (when user says "ready" or "publish")

10. Rebase on latest main:
    ```bash
    cd ~/devtree/tree[N]_$ARGUMENTS
    git fetch origin
    git rebase origin/main
    ```
11. Push and create PR:
    ```bash
    git push -u origin feature/$ARGUMENTS
    gh pr create --title "Add: $ARGUMENTS" --body "New content/feature: $ARGUMENTS"
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
    git worktree remove ~/devtree/tree[N]_$ARGUMENTS
    git branch -d feature/$ARGUMENTS
    ```

## Port Assignment

| Worktree | Port |
| -------- | ---- |
| main     | 4321 |
| tree1_*  | 4322 |
| tree2_*  | 4323 |
| tree3_*  | 4324 |

Pattern: `4321 + tree_number`

## Important Notes

- Dev server runs ONLY in main repo (localhost:4321) by default
- Worktrees are for editing files only, not running servers
- If you need to run a dev server in a worktree, use its assigned port:
  ```bash
  cd ~/devtree/tree1_$ARGUMENTS
  bun run dev --port 4322
  ```
- To preview changes without running a separate server, use temporary merge in main repo:
  ```bash
  git merge feature/$ARGUMENTS --no-commit --no-ff
  # preview at localhost:4321
  git merge --abort
  ```
