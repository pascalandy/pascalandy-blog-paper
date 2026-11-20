---
id: W02
project: BLOG
status: planned
label: wave:W02
skill_version: "2.0.0"
---

# W02: reader-release

## Goal

Readers get a readable, fully French blog with working old links and the right posts, and production serves it.

## Exit criteria

- [ ] In both themes, the text and link colors reach their contrast thresholds, a `just check` row proves it, and no listed English interface string remains (SC3)
- [ ] Each of the 41 old `/blog/cryptoinmontreal-NN/` URLs leads to its `/blog/cim-NN/` page, in `dist/` and on production (SC4)
- [ ] Each post on Pascal's confirmed lists carries `lang: en` or the `void` tag, and the home page shows the 5 featured posts (SC5)
- [ ] `src/data/blog/dev_workflows/editorial-rules.md` states each editorial rule and names its check (SC9)
- [ ] Production serves the final `main`: `just deploy` reports the matching commit, and `just verify-live` passes (SC10)

## Epics

### E05: Every page reads clearly, in French, in both themes → #147

- Traces: [BC §5](../00-business-case.md#s5), SC3
- Problem (CMO): In the light theme, the orange `primary` (`oklch(0.6171 0.1375 39.0427)`, `src/config.ts:129`) reads at 3.70:1 on the cream background (`src/config.ts:123`). Titles and list links of 18 px and 20 px need 4.5:1. The tag counts read at 1.96:1, and the prose link underline at 1.39:1 (`src/styles/typography.css:31`); Pascal's Inbox also asks for a thinner underline in the primary color (B12). The dark theme passes at 4.86:1. Some interface strings are still in English: the footer's `All Right Reserved`, the home page's `Featured` heading, the code block buttons `Copy` and `Copied`, the social link titles (`on X`, `RSS Feed`) and the 404 page title `404 Not Found` (B42). The post `cryptoinmontreal-photo.md` closes two image links with `))`, so a stray `)` shows after each gallery image (B39).
- Outcome (FMO): The light theme's `primary` is at lightness 0.56 (4.69:1, R20 option B), and the tag counts and the prose link underline reach their thresholds, with a thinner underline in `--primary`. A `just check` row computes the contrast of the theme colors in both themes and fails under the threshold. Each listed string is in Québec French, and a check rejects them in `dist/`. The gallery shows no stray `)`. The QA report carries screenshots of both themes at desktop and phone widths, for Pascal's review.

### E06: Old URLs reach their new pages → #148

- Traces: [BC §5](../00-business-case.md#s5), SC4
- Problem (CMO): Commit `d6b2d99` renamed 41 posts from `/blog/cryptoinmontreal-NN/` to `/blog/cim-NN/` with no redirect, so each old URL answers 404, including links from other sites and from search engines (B7). `astro.config.ts` has no `redirects` key.
- Outcome (FMO): `astro.config.ts` gives Astro `redirects` for the 41 pairs, so the static build emits one redirect page for each old URL (R3). A `just check` row reads `dist/` and fails when an old URL has no redirect page, or when its target is not an existing `/blog/cim-NN/` page. `just verify-live` also requests the 41 old URLs and requires each to lead to its new page.

### E07: The blog roll shows the chosen posts, each in its language → #149

- Traces: [BC §6](../00-business-case.md#s6), SC5
- Problem (CMO): The site default is `fr-CA` since #106, and the schema accepts an optional `lang` key, but no post sets `lang: en`. About 30 English posts and the 9 English playbooks of `src/data/blog/dev_workflows/` thus render `<html lang="fr-CA">`, so browsers and Pagefind treat them as French (B2, R13). Job ads from 2015 sit in the blog roll (R15). No post is featured, so the home page has no featured section (B13).
- Outcome (FMO): Pascal confirms two candidate lists on a human task: the English posts and the job ads. Each English post on the list sets `lang: en`, and `check_html.py` already verifies its `<html lang>`. Each job ad on the list gets the `void` tag, which keeps its page and its URL but removes it from the blog roll and RSS. The 5 posts of Pascal's shortlist set `featured: true` and show on the home page: `lekt-le-lecteur`, `pourquoi-se-donner-la-peine-decrire`, `pourquoi-jaime-vous-tutoyer`, `le-multitache-une-legende-urbaine-qui-a-trop-dure` and `comment-reprendre-le-dessus-quand-le-rythme-accelere`.

### E08: The editorial rules are on one page, and each rule names its check → #150

- Traces: [BC §9](../00-business-case.md#s9), SC9
- Problem (CMO): The editorial rules are spread over `src/content.config.ts`, `src/data/blog/dev_workflows/tag-visibility-system.md`, `frontmatter-schema.md` and the gotchas of `AGENTS.md`: `void`, drafts (they never build), future dates (out of listings and RSS until 15 minutes before), featured posts, the language and the redirects. No page says which check enforces each rule, so Pascal and the agents learn a rule only when a check fails.
- Outcome (FMO): `src/data/blog/dev_workflows/editorial-rules.md`, a public playbook in English, states each rule, what the reader sees, and the `just check` row or schema rule that enforces it. A rule that has no check gets one. `AGENTS.md` routes to the page.

### E09: Production serves the finished blog → #151

- Traces: [BC §10](../00-business-case.md#s10), SC10
- Problem (CMO): Production serves `main` at `cb723c8` (2026-11-19). The work of W01 and W02 is not public until Pascal says "déploie".
- Outcome (FMO): After Pascal's go, `just deploy` ships `main`, reports the matching commit, and passes `just verify-live`, including the 41 old URLs. The deploy task waits for passing verdicts of the QA tasks of E05, E06, E07 and E08, because a deploy follows them (blocking QA). A final QA task checks the public site.
