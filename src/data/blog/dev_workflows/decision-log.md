---
title: "Decision Log"
tags:
  - dev-notes
date_created: 2026-09-29
author: Pascal Andy
description: "Settled decisions about how this blog is built, one dated line each"
---

# Decision Log

> One dated line per settled decision, newest first, linked to where it was decided. Read the link before proposing to change a decision.

- 2026-09-29 · GitHub workflows run only by hand; a green `signoff` status from Pascal's `just signoff` gates merges into `main`, and `just deploy` ships `main` from the terminal ([#75](https://github.com/pascalandy/pascalandy-blog-paper/pull/75), [#76](https://github.com/pascalandy/pascalandy-blog-paper/pull/76), [#77](https://github.com/pascalandy/pascalandy-blog-paper/pull/77), [#78](https://github.com/pascalandy/pascalandy-blog-paper/pull/78))
- 2026-09-29 · UI proof runs through the verify-blog skill: it reuses Pascal's dev server on :4320, else previews a build on :4330, and never starts the dev server ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#74](https://github.com/pascalandy/pascalandy-blog-paper/pull/74))
- 2026-09-29 · Sessions start with `just overview`, computed from the source files, instead of exploring them ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#74](https://github.com/pascalandy/pascalandy-blog-paper/pull/74))
- 2026-09-29 · `AGENTS.md` is a router of at most 150 lines; `CLAUDE.md` and `GEMINI.md` stay symlinks to it ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · Posts are in Québec French; code, docs, and commits are in English ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · Commits follow Pascal's [commit skill](https://github.com/pascalandy/skills/tree/main/skills/commit); `dev_notes/` commits say `update dev_notes` ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · Playbooks stay public in `src/data/blog/dev_workflows/`; moving them to `/docs` is backlog ticket B10 ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · Renovate is the only dependency bot ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · Astro answers come from the Astro docs MCP server, with [llms-small.txt](https://docs.astro.build/llms-small.txt) as the fallback ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70), [#73](https://github.com/pascalandy/pascalandy-blog-paper/pull/73))
- 2026-09-29 · The frontmatter schema is strict, and every tag must be registered in `src/tags.ts` ([#72](https://github.com/pascalandy/pascalandy-blog-paper/pull/72))
- 2026-09-29 · `type`, not `interface`, outside declaration files ([#72](https://github.com/pascalandy/pascalandy-blog-paper/pull/72))
- 2026-09-29 · `just check` is the one verdict, and CI runs exactly it: silent on success, a failing row names its rerun ([#71](https://github.com/pascalandy/pascalandy-blog-paper/pull/71))
- 2026-09-29 · Checks are rows in `scripts/check.py`; scripts are Python run by uv, with stdlib argparse and no copied CLI helpers ([#71](https://github.com/pascalandy/pascalandy-blog-paper/pull/71))
- 2026-09-29 · Commits run gitleaks, formatting with re-staging, lint, and the content check; pushes run the verdict ([#71](https://github.com/pascalandy/pascalandy-blog-paper/pull/71))
- 2026-09-28 · Make the repo agent-native in 4 stacked milestones: one verdict, invariants, a truthful map, a computed overview ([#70](https://github.com/pascalandy/pascalandy-blog-paper/issues/70))
