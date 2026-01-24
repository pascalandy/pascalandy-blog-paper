# Project Preferences

## Browser, esign/Style
- the user will ask you to test something on the website, like:
  - http://localhost:4320/
  - http://localhost:4320/blog/lhorizon-cest-toi
  - http://localhost:4320/tags
- run` agent-browser --help` to see avail cmd, go!

**Rules**:
- Max viewport: 1920X1920 (prevents crash)
- resize_page before screenshots
  - magick mogrify -resize '1920x1920>' -quality 70 {filename}

## Make Targets
- `make qa` pre-commit | `make ci` fast check | `make build` | `make lint` | `make format`

## To test this app
- Spawn @charlie → tell it: "run: make qa"

## Git
Atomic commits only. "and" in msg = split it.
- `git status` + `git diff --stat`
- Group by purpose, not filetype
- Separate commits per logical change

For files under `dev_notes`, simply commit with -m "update dev_notes". This is my scratchpad.

### PR File Limit
Max 96 files per PR (Greptile skips review above this).

**When exceeding 90 files** (common with bulk content updates):
1. Stage only a subset of files (< 90) for initial PR
2. Push, wait for CI + Greptile review
3. Once approved, commit remaining files
4. Push again (Greptile already reviewed the logic)

Example: 110 content files changed → push 80 first, get review, then push remaining 30.

## Stack
- Astro 5 | TS strict | Tailwind v4 | Pagefind

## Astro Docs
- Index: docs.astro.build/llms-small.txt

## Architecture
```
astro.config.ts → src/config.ts + content.config + src/constants
                         ↓
              src/layouts/ (SEO, themes, transitions)
                         ↓
         src/pages/ + src/components/ + src/utils/
```

## Routes
`/` home | `/blog/[...page]` list | `/blog/[...slug]/` post | `/tags/[tag]/` filter | `/search/` | `/rss.xml`

## Post Visibility
- Drafts: dev only | Scheduled: visible after pubDatetime-15min

## Dev Cmds
- USER runs dev server, not agent (if not ask)

## Code Style
- TS strict, `@/*` alias, `type` not interface
- Imports: external → @/ → relative → type
- Prettier: semicolons, double quotes, 2 spaces, 80 chars
- ESLint: no console.log
- Names: Components=PascalCase | utils=camelCase | CONSTANTS=SCREAMING_SNAKE

## Tailwind
- `class:list` for conditionals
- Never hardcode colors → use theme vars
- `app-layout` = container util

## Themes
`src/config.ts` THEMES/ACTIVE_THEME | 19 OKLCH vars per mode | shadcn compatible

## Content
Posts: `src/data/blog/` | Zod validated | `_` prefix = ignored | subdirs preserved in URL

## Dev Workflow Docs
Documentation for development workflows is published publicly on the blog:
`src/data/blog/dev_workflows/`

Includes: development commands, git hooks, worktrees, themes, etc.

When adding or updating a workflow, document it there.

---

