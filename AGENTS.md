# pascalandy-blog-paper

Pascal Andy's blog, [pascalandy.com/blog](https://pascalandy.com/blog/): Astro 5, TypeScript strict, Tailwind v4, Pagefind, Bun. It began as a fork of AstroPaper. `CLAUDE.md` and `GEMINI.md` are symlinks to this file, so every agent reads the same contract.

## First moves

1. Run `just` to list the recipes, and `just check --list` to list the checks
2. Read only the route below that matches your task
3. Before you report done, run `just check`: it prints nothing when every check passes, and a failure prints `NAME failed; rerun: just check --only NAME`

## Trust map

When sources disagree, trust them in this order:

1. Code and config: `src/`, `astro.config.ts`, `justfile`, `scripts/`, `lefthook.yml`, `.github/workflows/`
2. The output of `just check`
3. This contract, then the playbooks in `src/data/blog/dev_workflows/`
4. The [decision log](src/data/blog/dev_workflows/decision-log.md), for why things are the way they are
5. `dev_notes/`: Pascal's scratchpad, never authoritative and often stale

## Judgment rules

- Posts are in Québec French; code, docs, and commits are in English
- Pascal runs the dev server on port 4320; agents start it only when he asks
- Never hardcode colors: use the theme variables from `src/config.ts`
- Prefer a check over a sentence: when a rule matters, add a row to `scripts/check.py` or a constraint to `src/content.config.ts`
- Do not re-propose a settled decision; read its line in the decision log first
- Keep scope: a defect outside the task becomes a ticket in `dev_notes/backlog.md`, not a drive-by fix
- Code conventions that no tool enforces: imports go external, then `@/`, then relative, then types; components are PascalCase, utils camelCase, constants SCREAMING_SNAKE; Tailwind conditionals use `class:list`; `app-layout` is the container utility

## Routes: read on demand

| Task                      | Read                                                                                                                                    |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Write or edit a post      | `src/content.config.ts` (schema), `src/tags.ts` (tag registry), [frontmatter schema](src/data/blog/dev_workflows/frontmatter-schema.md) |
| Tags and their visibility | [tag visibility](src/data/blog/dev_workflows/tag-visibility-system.md)                                                                  |
| Images in posts           | [image paths](src/data/blog/dev_workflows/image_path.md)                                                                                |
| Theme and colors          | [theme system](src/data/blog/dev_workflows/shadcn-theme-system.md)                                                                      |
| Mermaid diagrams          | [Mermaid](src/data/blog/dev_workflows/using-mermaid.md)                                                                                 |
| Recipes, hooks, CI        | [development workflow](src/data/blog/dev_workflows/development-workflow.md)                                                             |
| Parallel work             | [worktrees](src/data/blog/dev_workflows/worktree-workflow.md), or the [`/worktree`](.claude/commands/worktree.md) command               |
| Dependencies              | [updating dependencies](src/data/blog/dev_workflows/how-to-update-dependencies.md), [`renovate.json`](renovate.json)                    |
| Astro APIs                | the `astro-docs` MCP server in `.mcp.json`; fallback https://docs.astro.build/llms-small.txt                                            |
| Pick work                 | `dev_notes/backlog.md`                                                                                                                  |
| Check the UI in a browser | Browser checks, below                                                                                                                   |

## Browser checks

- Drive the site with `agent-browser` (run `agent-browser --help`); Pascal's dev server answers on http://localhost:4320/
- Keep the viewport at most 1920×1920: larger crashes the browser
- Shrink each screenshot before reading it: `magick mogrify -resize '1920x1920>' -quality 70 FILE`

## Git and pull requests

- Commits follow Pascal's [commit skill](https://github.com/pascalandy/skills/tree/main/skills/commit): one logical change per commit, and a subject that needs "and" means two commits
- Commit files under `dev_notes/` with the message `update dev_notes`
- Never skip hooks with `--no-verify` unless Pascal says so
- Keep a PR under 96 files, since Greptile skips larger ones: past 90, push a subset, get the review, then push the rest
- Split large work into stacked PRs, each based on the branch below it
- Fill the PR template: summary, evidence, and what you could not confirm

## Gotchas

- Drafts never build, dev included. A future `date_created` keeps a post out of listings and RSS until 15 minutes before, but its page still builds
- A post may use only the frontmatter keys in `src/content.config.ts` and the tags in `src/tags.ts`; `just check --only content` names any other
- A `_` prefix removes a file from the collection; a `_` folder stays in it but drops out of the URL
- Folder names are slugified in URLs: `dev_workflows/` publishes at `/blog/dev-workflows/`
- Posts that share a `date_created` can swap places between builds (backlog B9)
- ruff formats Python code blocks inside Markdown by default; `ruff.toml` limits it to `*.py`
- The build fetches Google Fonts for OG images; `cache/` keeps them, with the optimized images, between builds
- The playbooks are public blog posts: write them for readers

## Leave a trace

Before you finish, record what the next session needs:

- A gotcha you hit: a line in Gotchas above
- A decision Pascal settles: a dated line in the decision log, linked to its PR
- Work you defer: a ticket in `dev_notes/backlog.md`
- A new workflow: a playbook in `src/data/blog/dev_workflows/`
