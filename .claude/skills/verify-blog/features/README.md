# Blog verification map

This directory is the maintained source for verifying what a reader sees on Pascal Andy's blog. Read this index before driving the site, then follow the matching feature file.

## Baseline preconditions

- `site.py up` printed the base URL, and `site.py doctor` exits 0; the steps call it `$URL`
- Pascal's dev server on :4320 is reused as is; otherwise the preview on :4330 serves a fresh build
- Posts, tags, and counts come from `just overview --json`; do not hardcode them from memory
- Never drive an instance that neither this run started nor Pascal's dev server provides

## Driving conventions

- Start each recipe from the page it names, in a fresh tab, with no stored theme
- Prefer ids, ARIA roles and names, and route paths over CSS classes or position
- The page chrome is in French and English: nav labels are `tags`, `à propos`, and `search`; post navigation says `Previous` and `Next`
- Run agent-browser commands as written; the fallback bullet gives the same proof with `browse.py`

## Proof and skip reporting

- Capture the action and the resulting state, not only the final screen
- UI proof is a screenshot plus an accessibility snapshot, saved under `cache/verify-blog/$RUN/FEATURE/`
- A state change, such as the theme, needs the before and the after
- Record the feature, the entry point, and the instance used with every artifact
- Report an unreachable path with the command tried and the unmet precondition; never report it as verified through another path

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing what the reader sees. It then has exactly four H2 sections, in this order:

1. `Sub-features`: short IDs, one line each
2. `How to get to it (user POV)`: every reader entry point
3. `Driving it with agent-browser`: `Preconditions:`, then labeled bullets that pair each reader action with an exact command and its observable result, ending with a `browse.py` fallback
4. `Gotchas`: traps that waste or invalidate a run

## Features

- [Home](home.md): the landing page with Pascal's introduction and the featured posts
- [Post](post.md): one article, its tags, and the previous and next links
- [Tags](tags.md): the tag list, one tag's posts, and hidden tags
- [Search](search.md): full-text search through Pagefind, with the query in the URL
- [Navigation](navigation.md): the header links, the mobile menu, and blog pagination
- [Theme](theme.md): the light and dark toggle and its persistence
