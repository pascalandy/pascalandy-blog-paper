---
id: W01
project: BLOG
status: active
label: wave:W01
skill_version: "3.1.0"
executor: agent
---

# W01: foundations

## Goal

All open work is in one labeled queue, the docs state the decisions of 2026-11-19, the QA machine runs every verify-blog recipe, each merge and each deploy proves itself, and the code has no dead feature.

## Exit criteria

- [ ] Each open issue of the repository has a `wave:` label or a `3-pty:*` label, `dev_notes/backlog.md` holds only the Inbox, and each ID of the old backlog has a recorded fate (SC1)
- [ ] A comment on #103 records each answer of 2026-11-19, the decision log has a dated line for each lasting decision with a link to that comment, and `AGENTS.md` states the rules that these decisions change (SC2)
- [ ] On the Mac Mini, a fresh clone passes `just check`, and each verify-blog recipe fallback exits 0, including the menu checks at 639 px and 640 px (SC7)
- [ ] `just verify-live` exits 0 against production, and tests prove three things: `just merge` skips the checks only for a head that already carries a green signoff, `just deploy` fails when Sevalla built another commit, and a production deploy that `just deploy` waits for runs the live checks and fails when they fail (SC8)
- [ ] `rg -n 'EditPost|editPost|hideEditPost' src` prints nothing, the five Ghost scripts are only under `scripts/archive/ghost-migration/`, and `just check --only images` fails on an unreferenced image in `public/` (SC6)

## Epics

### E01: All open work is in one labeled GitHub queue → #126

- Traces: [BC §3](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s3), [BC §4](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s4), SC1, SC2, FR-01, FR-02, FR-14
- Executor: agent
- Problem (CMO): Work lives in two places. `dev_notes/backlog.md` has a ticket table (B1 to B43 and issue rows) and a table of calls (R1 to R19). Before the planning issues existed, nine of the ten open issues had a recorded resolution. `AGENTS.md` sends agents to `dev_notes/backlog.md` and names Greptile as the review bot. The audit issue has no summary of Pascal's answers of 2026-11-19, and the decision log has no line for them. Thus an agent that starts today reads old rules and can propose a settled decision again.
- Outcome (FMO): Each open piece of work is an open, labeled issue of this repository, and `dev_notes/backlog.md` holds only Pascal's Inbox. `AGENTS.md` sends agents to the GitHub issues and to `plan/01-project.md`. A comment on #103 records each answer of 2026-11-19. The decision log has one line for each lasting decision, and each line links that comment.

#### E01-T01: Record the decisions of 2026-11-19 in AGENTS.md and the decision log → #130

- Kind: chore · Executor: agent · State: todo
- Today:
  - Pascal answered the calls R1 to R20 of issue #103 on 2026-11-19. The audit issue has no summary of the answers: #103 is closed, and its last comment only points to a private card
  - `AGENTS.md` sends work to `dev_notes/backlog.md` at line 29 ("a defect outside the task becomes a ticket in `dev_notes/backlog.md`"), line 45 (the route "Pick work") and line 92 ("Work you defer"). `.github/PULL_REQUEST_TEMPLATE.md:10` also names `dev_notes/backlog.md`
  - `AGENTS.md:54` says "Keep a PR under 96 files, since Greptile skips larger ones". PRs #99 and #102 show CodeRabbit reviews and no Greptile review
  - The last AVIF gotcha of `AGENTS.md` says "other items' order is tracked in issue #89". E01-T02 closes #89 as not planned (R8)
  - `src/data/blog/dev_workflows/decision-log.md` has no line dated 2026-11-19. Its rule is one dated line per decision, newest first, with a link to the place of the decision
- After:
  - A comment on #103 gives the dated answers below and links the current plan. A separate dated sentence records the delegated lists in #149
  - `AGENTS.md` sends work and deferred defects to the open GitHub issues of this repository, and its route "Pick work" names the GitHub issues and `plan/01-project.md`. The PR template names a GitHub issue instead of `dev_notes/backlog.md`
  - `AGENTS.md` names CodeRabbit as the review bot and keeps the rule "a PR has 90 files or fewer" (D007)
  - The AVIF gotcha records the scope of the existing check. R8 retires #89 because the blog ships no AVIF images
  - The decision log has 14 new lines dated 2026-11-19, one for each decision of the second table. Each line links the #103 comment
- Answers for the #103 comment:

  | ID | Answer of 2026-11-19 |
  |---|---|
  | R1 | Done: production serves `main` at `cb723c8` |
  | R2 | Later: install the latest official Cloudflare CLI, then fix the `www` rule that drops the path |
  | R3 | The 41 old URLs redirect through Astro `redirects`, checked by `just check` |
  | R4 | Outside this repository: om1's Node version belongs to `dotfiles` |
  | R5 | `just merge` reuses a green `signoff` status on the same commit (#84) |
  | R6 | Later: find which agent keeps dependencies current, and how its PRs pass `signoff` |
  | R7 | `AGENTS.md` names CodeRabbit instead of Greptile |
  | R8 | Close #89 and #90 while no AVIF ships |
  | R9 | Archive the five Ghost scripts in `scripts/archive/ghost-migration/`. No Ghost export exists, so the 28 dates of B37 stay |
  | R10 | GitHub issues are the one queue, labeled per label-for-issues. `dev_notes/backlog.md` keeps only the Inbox |
  | R11 | Close the five release post-mortems and delete the `autorelease` labels |
  | R12 | Done: 20 dead branches deleted after a `git bundle` backup |
  | R13 | English posts set `lang: en`. Pascal confirms the list |
  | R14 | Same answer as B10: the playbooks stay public |
  | R15 | Old job ads get the `void` tag. Pascal confirms the list |
  | R16 | Remove the disabled "Edit page" link from AstroPaper |
  | R17 | Do nothing about duplicate images |
  | R18 | Add the 639 px and 640 px menu checks to verify-blog, then delete the old test plans |
  | R19 | B13: feature 5 posts. B14, B16 and B18: later. B15 and B17: closed |
  | R20 | Option B: the light theme keeps its orange `primary`, at lightness 0.56 |
  | B10 | Closed: the playbooks stay public |
  | B15 | Closed: no email sign-up form |
  | B17 | Closed: stacks use `gh stack`, not Graphite |
  | B37 | Closed: the 28 uncertain dates stay as they are |
  | B38 | Delete the 5 unreferenced files of `public/og-legacy/`, and make the image check cover `public/` |

- Decision lines for the decision log, each dated 2026-11-19:
  1. GitHub issues of this repository are the one work queue, labeled per label-for-issues; `dev_notes/backlog.md` keeps only Pascal's Inbox, and `plan/` holds the rolling-wave plan (R10)
  2. The light theme keeps its orange `primary`, darkened from lightness 0.6171 to 0.56, for 4.5:1 contrast on the background (R20, option B)
  3. The 41 old `/blog/cryptoinmontreal-NN/` URLs redirect to `/blog/cim-NN/` through Astro `redirects`, checked by `just check` (R3)
  4. English posts set `lang: en`, after Pascal confirms the list (R13)
  5. Old job ads get the `void` tag, after Pascal confirms the list (R15)
  6. The home page features 5 posts (B13)
  7. The playbooks stay public (B10), the blog has no email sign-up form (B15), and stacks use `gh stack`, not Graphite (B17)
  8. The five Ghost migration scripts move to `scripts/archive/ghost-migration/`; no Ghost export exists, so the 28 uncertain dates of B37 stay (R9)
  9. `just merge` reuses a green `signoff` status on the same commit instead of running the checks again (R5, #84)
  10. The 5 unreferenced files of `public/og-legacy/` are deleted, and the image check covers `public/` (B38)
  11. The disabled "Edit page" link from AstroPaper is removed (R16)
  12. CodeRabbit reviews PRs, and a PR keeps 90 files or fewer (R7)
  13. #89 and #90 close while no AVIF ships; the five release post-mortems close, and the `autorelease` labels are deleted (R8, R11)
  14. Duplicate images stay; the repository does not deduplicate them (R17)
- Traces: [BC §3](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s3), [BC §4](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s4), SC2, D007
- Contract: none
- Acceptance:
  - [ ] `gh issue view 103 --comments` shows one new comment with each row of the answers table
  - [ ] `rg -n 'backlog\.md|Greptile' AGENTS.md .github/PULL_REQUEST_TEMPLATE.md` prints nothing, and the route "Pick work" of `AGENTS.md` names the GitHub issues and `plan/01-project.md`
  - [ ] `rg -c '^- 2026-11-19' src/data/blog/dev_workflows/decision-log.md` prints 14, and each of these lines links the #103 comment
  - [ ] `wc -l < AGENTS.md` prints 150 or less (decision log, 2026-09-29: `AGENTS.md` is a router of at most 150 lines)
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: `dev_notes/backlog.md` (E01-T03), the issue closures (E01-T02), the merge text of `AGENTS.md` (E03-T01), the verify-blog files (E02)
- Blocked by: none
- Unblocks: E01-QA1 (#139), E03-T01 (#84)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E01-T01",
  "blocked_by": [],
  "needs": [
    {
      "what": "gh signed in with write access to the repository",
      "check": "gh api repos/pascalandy/pascalandy-blog-paper --jq '.permissions.push' | rg -x true"
    },
    {
      "what": "The plan is on the default branch (PR #152 merged), so the docs check resolves `plan/01-project.md`",
      "check": "gh api repos/pascalandy/pascalandy-blog-paper/contents/plan/01-project.md --silent"
    }
  ],
  "touches": [
    "AGENTS.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "src/data/blog/dev_workflows/decision-log.md"
  ]
}
```

#### E01-T02: Close the settled issues and the retired labels → #131

- Kind: chore · Executor: agent · State: todo
- Today:
  - Before the initial plan, ten issues were open. #84 stays open, because the plan sync made it the issue of E03-T01 (D006). The other 9 are settled:

    | Issue | Close reason | Evidence for the closing comment |
    |---|---|---|
    | #98 | completed | Fixed by #109: `just check --only lockfile` rejects a second Vite version in `bun.lock` |
    | #95 | completed | Fixed by #108, which deleted `src/data/blog/dev_workflows/_how-to-configure-astropaper-theme.md`, the file that held the stale font example |
    | #89, #90 | not planned | R8 of 2026-11-19: no AVIF ships since #102; the AVIF parser of `scripts/parity.py` stays |
    | #54, #56, #59, #62, #65 | completed | R11 of 2026-11-19: release records of February, kept as history |

  - The labels `autorelease: pending` and `autorelease: tagged` remain from release-please, which the repository no longer uses
- Risk: verify the two exact label names before deletion. Deletion removes the label from historical issues.
- After: the 9 issues are closed with the reason of the table and a comment that gives its evidence. The 2 labels are deleted
- Traces: [BC §4](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s4), SC1, D008
- Contract: none
- Acceptance:
  - [ ] `gh issue list --state open --limit 200 --json number --jq '.[].number'` lists none of 54, 56, 59, 62, 65, 89, 90, 95 and 98
  - [ ] `gh issue view 89 --json stateReason --jq .stateReason` prints `NOT_PLANNED`, and so does the same command for 90; for 98 it prints `COMPLETED`
  - [ ] Each of the 9 issues has a closing comment with its evidence from the table
  - [ ] `gh label list --limit 200 --json name --jq '.[].name' | rg autorelease` prints nothing
- Verify: `gh issue list --state open --limit 200` and `just check`
- Out of scope: #84 (E03-T01), each label other than the two `autorelease` labels, the deferred queue (#132)
- Blocked by: none
- Unblocks: E01-QA1 (#139)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E01-T02",
  "blocked_by": [],
  "needs": [
    {
      "what": "gh signed in with write access to the repository",
      "check": "gh api repos/pascalandy/pascalandy-blog-paper --jq '.permissions.push' | rg -x true"
    }
  ],
  "touches": []
}
```

#### E01-T03: Reconcile the GitHub backlog and preserve the Inbox → #132

- Kind: chore · Executor: agent · State: todo
- Today: GitHub now has the fourteen deferred issues below. The source at `cb723c8:dev_notes/backlog.md` still has the ticket tables and Pascal’s Inbox.
- After: the issues own the work. The current backlog retains its frontmatter, a short route to GitHub and the original Inbox.
- Rationale: preserving the Inbox protects unpublished ideas. Removing the copied ticket tables prevents contradictory status updates.
- Expected queue:
  - [R2 · #155](https://github.com/pascalandy/pascalandy-blog-paper/issues/155): www.pascalandy.com drops the path when it redirects. Labels: `2-type:bug`, `3-pty:p2`, `1-needs-triage`
  - [R6 · #156](https://github.com/pascalandy/pascalandy-blog-paper/issues/156): Choose the agent that keeps dependencies current. Labels: `2-type:task`, `3-pty:p2`, `1-needs-triage`
  - [B14 · #157](https://github.com/pascalandy/pascalandy-blog-paper/issues/157): Redraw the egg-chair logo as an SVG for the header. Labels: `2-type:feature`, `3-pty:p2`, `1-needs-triage`
  - [B16 · #158](https://github.com/pascalandy/pascalandy-blog-paper/issues/158): Add the Star Academy content. Labels: `2-type:feature`, `3-pty:p2`, `1-needs-triage`
  - [B18 · #159](https://github.com/pascalandy/pascalandy-blog-paper/issues/159): Run phone-format QA on a Mac. Labels: `2-type:task`, `3-pty:p2`, `1-needs-triage`
  - [B23 · #160](https://github.com/pascalandy/pascalandy-blog-paper/issues/160): Stop persisting the checkout token in claude.yml. Labels: `2-type:task`, `3-pty:p3`, `1-needs-triage`
  - [B24 · #161](https://github.com/pascalandy/pascalandy-blog-paper/issues/161): Prove or explain Pagefind byte differences between builds. Labels: `2-type:task`, `3-pty:p3`, `1-ready-for-agent`
  - [B26 · #162](https://github.com/pascalandy/pascalandy-blog-paper/issues/162): Give informative images French alt text. Labels: `2-type:feature`, `3-pty:p2`, `1-needs-triage`
  - [B28 · #163](https://github.com/pascalandy/pascalandy-blog-paper/issues/163): Upgrade ESLint, eslint-plugin-astro and typescript-eslint together. Labels: `2-type:task`, `3-pty:p3`, `1-ready-for-agent`
  - [B29 · #164](https://github.com/pascalandy/pascalandy-blog-paper/issues/164): Upgrade TypeScript after the ESLint upgrade. Labels: `2-type:task`, `3-pty:p3`, `1-ready-for-agent`
  - [B30 · #165](https://github.com/pascalandy/pascalandy-blog-paper/issues/165): Upgrade pagefind and @pagefind/default-ui together. Labels: `2-type:task`, `3-pty:p3`, `1-ready-for-agent`
  - [B31 · #166](https://github.com/pascalandy/pascalandy-blog-paper/issues/166): Upgrade satori from 0.18. Labels: `2-type:task`, `3-pty:p3`, `1-needs-triage`
  - [B33 · #167](https://github.com/pascalandy/pascalandy-blog-paper/issues/167): Guard compressHTML and the unified Markdown processor. Labels: `2-type:task`, `3-pty:p3`, `1-ready-for-agent`
  - [B36 · #168](https://github.com/pascalandy/pascalandy-blog-paper/issues/168): Keep Prettier uncached until a cache test exists. Labels: `2-type:task`, `3-pty:p3`, `1-needs-triage`
- The four labels added during planning use the canonical metadata:
  - `1-needs-info` (`d4a72c`): Specific information is missing from the issue
  - `3-pty:p0` (`d95757`): Emergency requiring immediate attention, such as active exploitation or a major outage
  - `3-pty:p1` (`db8b40`): High priority; takes precedence over ordinary planned work
  - `3-pty:p3` (`8b949e`): Low-priority work that can wait
- The backlog header points to GitHub and `plan/01-project.md`. The index in `dev_notes/README.md` describes the Inbox.
- Traces: [BC §4](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s4), [BC §11](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s11), SC1, SC11, D008, D011
- Contract: none
- Acceptance:
  - [ ] For each linked issue, verify its title, labels and acceptance criteria. Each backlog ID has one open issue and no wave label
  - [ ] The native prerequisites are #135 for #159, #163 for #164, #161 and #164 for #165, and #165 for #166
  - [ ] `rg -n '^\| (B|R)[0-9]+|^\| #' dev_notes/backlog.md` prints nothing, and `diff <(git show cb723c8:dev_notes/backlog.md | sed -n '/^## Inbox/,$p') <(sed -n '/^## Inbox/,$p' dev_notes/backlog.md)` prints nothing
  - [ ] `gh label list --limit 200 --json name,color,description` contains the four labels above, with their exact colors and descriptions
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: issue closures (E01-T02), `AGENTS.md` (E01-T01), the legacy labels such as `bug` or `enhancement`, and the work inside the fourteen linked issues
- Blocked by: none
- Unblocks: E01-QA1 (#139), E02-T03 (#140)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E01-T03",
  "blocked_by": [],
  "needs": [
    {
      "what": "gh signed in with write access to the repository",
      "check": "gh api repos/pascalandy/pascalandy-blog-paper --jq '.permissions.push' | rg -x true"
    }
  ],
  "touches": [
    "dev_notes/backlog.md",
    "dev_notes/README.md"
  ]
}
```

#### E01-QA1: QA: All open work is in one labeled GitHub queue → #139

- Kind: qa · Executor: QA agent on the QA machine · State: todo · Verdict: —
- Context: E01 moves all open work into labeled GitHub issues of this repository, and records the decisions of 2026-11-19 in `AGENTS.md`, in the decision log and on #103. The user is the next agent: it must find its work and the reason for each settled decision without `dev_notes/backlog.md`.
- Traces: [BC §3](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s3), [BC §4](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s4), SC1, SC2, FR-01, FR-02, FR-14, NFR-01
- Expected disposition of the old queue:
  - Existing work: B2 and B13 belong to #149. B7 belongs to #148. B12, B39 and B42 belong to #147. B38 belongs to #138, B41 to #133 and B43 to #143. R18 belongs to #140. R5 remains #84
  - Later issues: R2, R6, B14, B16, B18, B23, B24, B26, B28, B29, B30, B31, B33 and B36
  - Closed tickets: #95 and #98 have fixes. Five post-mortems (#54, #56, #59, #62, #65) are complete. #89 and #90 close as not planned
  - For the other rows, the issue history, the decision comment on #103, or the cited change must show the outcome. The 28 unsupported Ghost dates stay as published
- Setup: in a fresh clone in a scratch folder on the Mini, run `bun install --frozen-lockfile --ignore-scripts` before any `just` command (D003)
- QA scenarios (≤ 8):
  - [ ] FR-01, FR-14: No ticket is lost: for each ID in the tables of `git show cb723c8:dev_notes/backlog.md`, match it to the disposition below and find the evidence: an open issue (`gh issue list --state all --search "<ID> in:title"`), a brief in `plan/waves/` (`rg -n '<ID>' plan/waves`), a closed issue, a merged PR that its old row cites, a direct check of the behavior on the default branch (for B20: `sitemap()` in `astro.config.ts`), or a line dated 2026-11-19 in the decision log → each ID has evidence
  - [ ] FR-01: `gh issue list --state open --limit 200 --json number,title,labels` → each open issue has one `wave:` label or one `3-pty:*` label, and one `1-*` label or the `4-epic` label
  - [ ] FR-01: Follow the route "Pick work" of `AGENTS.md` → the GitHub queue includes #130 and the project summary lists W01
  - [ ] FR-02: Open the link of each line dated 2026-11-19 in the decision log → it opens the #103 comment, and the comment gives the same answer
  - [ ] FR-01: `gh issue view <n> --json state,stateReason` for 54, 56, 59, 62, 65, 89, 90, 95 and 98 → #89 and #90 are not planned. The other seven are complete, and `gh label list --limit 200 | rg autorelease` prints nothing
  - [ ] FR-01: `sed -n '/^## Inbox/,$p' dev_notes/backlog.md` → the Inbox text equals the text at `cb723c8`, and the file has no ticket table
  - [ ] NFR-01: In the fresh Mini checkout, run `just check`. The installed Bun builds the tested revision.
- Also check: each acceptance item of E01-T01, E01-T02 and E01-T03 still passes on the default branch; `just check` passes in a fresh clone.
- Output: Record the tested commit, independent Mini session, commands, actual results and verdict on this issue. Link each finding.
- Blocked by: E01-T01 (#130), E01-T02 (#131), E01-T03 (#132), E02-T04 (#135)
- Unblocks: no task in W01. The verdict informs the wave review
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E01-QA1",
  "verifies": [
    "E01-T01",
    "E01-T02",
    "E01-T03",
    "E02-T04"
  ],
  "needs": [
    {
      "what": "The plan is on the default branch (PR #152 merged)",
      "check": "gh api repos/pascalandy/pascalandy-blog-paper/contents/plan/decisions.md --silent"
    },
    {
      "what": "The session runs on the Mac Mini",
      "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"
    },
    {
      "what": "gh signed in on the QA machine",
      "check": "gh auth status"
    },
    {
      "what": "bun on the QA machine (E02-T04)",
      "check": "command -v bun"
    }
  ]
}
```

### E02: verify-blog runs every recipe on a fresh preview, also on the QA machine → #127

- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC7, FR-03, NFR-01
- Executor: agent
- Problem (CMO): The QA agent and Pascal prove the reader-facing changes with the verify-blog skill. Twelve recipe URLs in `features/post.md`, `search.md`, `tags.md` and `theme.md` have no trailing slash before their query string or end. The site uses `trailingSlash: "always"`, so the preview answers 404, and the post and search fallbacks fail before their first step (B41). No recipe checks the mobile menu at 639 px and 640 px, where the menu button hides. Only old plans in `dev_notes/e2e_browser_tests/` check it (R18). The navigation recipe also clicks `a[href="/blog"]`, a link that the header does not emit. `browse.py` has only two viewports. The QA machine has no `bun` and no Playwright Chromium, so it cannot build or drive the blog.
- Outcome (FMO): The path part of each recipe URL, before any query string, ends with `/`, and a test fails on a URL without it. `browse.py` captures at a chosen viewport, from 200 to 1920 pixels a side. The navigation recipe checks the menu at 639 px and 640 px, and the old plans are gone. On the Mac Mini, a fresh clone passes `just check` and runs each recipe fallback.

#### E02-T01: Add the trailing slash to each verify-blog recipe URL → #133

- Kind: fix · Executor: agent · State: todo
- Today:
  - `astro.config.ts:19` sets `trailingSlash: "always"`, so the preview answers 404 for a page path without the final `/`
  - These recipe URLs in `.claude/skills/verify-blog/features/` have no final `/`: `tags.md:25` `$URL/tags`, `tags.md:27` `$URL/tags/technologie`, `tags.md:28` `$URL/tags/void`, `tags.md:30` `$URL/tags`, `theme.md:26` `$URL/tags`, `post.md:16` `$URL/blog/lhorizon-cest-toi`, `post.md:25` `$URL/blog/lhorizon-cest-toi`, `post.md:29` `$URL/blog/dev-workflows/using-mermaid`, `post.md:32` `$URL/blog/lhorizon-cest-toi`, `search.md:15` `$URL/search?q=QUERY` (the preview drops the query before it checks the slash, so this URL also answers 404), `search.md:24` `$URL/search`, `search.md:30` `$URL/search`
  - `search.md:36` says "Search indexes French text as English until backlog B2 sets the page language". This sentence is false since #106 set `SITE.lang` to `fr-CA`
  - No test reads `features/*.md`. The `docs` row (`scripts/check_docs.py`) skips site routes
- After:
  - The path part of each `$URL/` URL in `features/*.md`, before any query string, ends with `/` or a file extension
  - `search.md` states the language that `dist/pagefind/pagefind-entry.json` reports after a build, instead of the old B2 sentence
  - A new test, `scripts/tests/test_verify_blog_features.py`, fails and names the file and the line of each `$URL/` URL whose path part, before any query string, has no final `/` and no file extension. The `scripts` row runs it
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC7
- Contract: none
- Acceptance:
  - [ ] `just check --only scripts` passes, and the new test fails when one recipe URL of a scratch copy loses its final `/`
  - [ ] After `uv run .claude/skills/verify-blog/scripts/site.py up`, `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/blog/lhorizon-cest-toi/" --out /tmp/b41-post` exits 0, and its `network.json` shows status 200 for the page
  - [ ] The same `browse.py` command on `"$URL/search/"` exits 0 with status 200 for the page
  - [ ] `rg -n 'backlog' .claude/skills/verify-blog/` prints nothing
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: new recipes, the menu breakpoint checks (E02-T03), `browse.py` (E02-T02)
- Blocked by: none
- Unblocks: E02-QA1 (#142)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E02-T01",
  "blocked_by": [],
  "needs": [],
  "touches": [
    ".claude/skills/verify-blog/features/post.md",
    ".claude/skills/verify-blog/features/search.md",
    ".claude/skills/verify-blog/features/tags.md",
    ".claude/skills/verify-blog/features/theme.md",
    "scripts/tests/test_verify_blog_features.py"
  ]
}
```

#### E02-T02: Let browse.py capture at a chosen viewport size → #134

- Kind: feature · Executor: agent · State: todo
- Today:
  - `browse.py` accepts `--device desktop|iphone` (`.claude/skills/verify-blog/scripts/browse.py:202-207`). `desktop` is `VIEWPORTS = {"desktop": {"width": 1440, "height": 900}}` (line 59), and `iphone` is Playwright's "iPhone 15" (line 251)
  - No flag sets an exact width. The menu breakpoint check of E02-T03 needs 639 px and 640 px in the Playwright fallback, because the QA machine has no agent-browser
- After:
  - `--viewport WIDTHxHEIGHT`, such as `--viewport 639x900`, sets the Chromium viewport and replaces the desktop default
  - `--viewport` together with `--device iphone` is a usage error
  - The paragraph about the Playwright fallback in `.claude/skills/verify-blog/SKILL.md` documents the flag
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC7
- Contract: `browse.py URL --out DIR [--viewport WIDTHxHEIGHT]`. WIDTH and HEIGHT are integers from 200 to 1920, the largest capture that `browse.py` saves. A bad value, or `--viewport` with `--device iphone`, exits 2 with one error line on stderr
- Acceptance:
  - [ ] A new test in `scripts/tests/test_browse.py` drives a local page with `--viewport 639x900 --step 'eval:window.innerWidth'`, and the saved evaluation is 639
  - [ ] Tests show that `--viewport 10x10`, and `--viewport 639x900 --device iphone`, each exit 2 with one line on stderr
  - [ ] `uv run .claude/skills/verify-blog/scripts/browse.py --help` lists `--viewport`
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: new `browse.py` actions, the navigation recipe (E02-T03), agent-browser
- Blocked by: none
- Unblocks: E02-T03 (#140), E02-QA1 (#142)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E02-T02",
  "blocked_by": [],
  "needs": [{"what": "The Chromium build of Playwright 1.56 launches; the browse.py tests skip without it", "check": "uv run --quiet --with playwright==1.56.0 python -c \"from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.chromium.launch().close(); p.stop()\""}],
  "touches": [
    ".claude/skills/verify-blog/scripts/browse.py",
    "scripts/tests/test_browse.py",
    ".claude/skills/verify-blog/SKILL.md"
  ]
}
```

#### E02-T03: Check the mobile menu at 639 px and 640 px, then delete the old browser plans → #140

- Kind: chore · Executor: agent · State: todo
- Today:
  - `features/navigation.md` checks the menu only at 390 × 844 (line 28, agent-browser) and with `--device iphone` (line 30, `browse.py` fallback)
  - `src/components/Header.astro:66` gives `#menu-btn` the class `sm:hidden`. Tailwind's `sm` breakpoint is 640 px, so the button shows below 640 px and hides from 640 px
  - `dev_notes/e2e_browser_tests/v2/e2e_matrix.yaml` checks these widths (lines 26-33, combinations 4 to 6, failure rules F2 and F3)
  - `navigation.md:26` runs `agent-browser click 'a[href="/blog"]'`, but `Header.astro:90` emits `href="/blog/"`, so the click finds no link
  - `dev_notes/dev-workflow.md` and `dev_notes/ci-flow.mermaid` predate `just check`. `dev_notes/README.md` lists them and the old plans. No tracked file outside `dev_notes/` cites these paths
- After:
  - `navigation.md` has a sub-feature `nav-breakpoint`. At 639 × 900, `#menu-btn` shows, and a click on it shows the links. At 640 × 900, `#menu-btn` is hidden, and the header links show. Each step has an agent-browser form (`agent-browser set viewport 639 900`) and a `browse.py --viewport` fallback
  - Use the existing `maintain-verification-skill` checklist to update the navigation journey. Both browser drivers must prove the same menu behavior
  - The blog-roll step clicks `a[href="/blog/"]`
  - These paths are deleted: `dev_notes/e2e_browser_tests/` (6 files), `dev_notes/dev-workflow.md` and `dev_notes/ci-flow.mermaid`. `dev_notes/README.md` no longer lists them
  - `dev_notes/MultiLanguage/` stays (D010)
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC7, D010
- Contract: none
- Acceptance:
  - [ ] The `nav-breakpoint` fallback at `--viewport 639x900` with `--step 'eval:getComputedStyle(document.querySelector("#menu-btn")).display'` saves a value other than `none`, and at `--viewport 640x900` it saves `none`
  - [ ] On a fresh preview, `browse.py "$URL/" --out <dir> --step 'click:a[href="/blog/"]'` exits 0, and its evidence shows the `/blog/` page
  - [ ] `test ! -e dev_notes/e2e_browser_tests && test ! -e dev_notes/dev-workflow.md && test ! -e dev_notes/ci-flow.mermaid` exits 0
  - [ ] `rg -n 'e2e_browser_tests|ci-flow|dev-workflow\.md' --hidden -g '!.git' -g '!plan/**'` prints nothing
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: `dev_notes/MultiLanguage/`, other recipes, a change to `Header.astro`
- Blocked by: E02-T02 (#134), E01-T03 (#132)
- Unblocks: E02-QA1 (#142)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E02-T03",
  "blocked_by": [
    {"id": "E02-T02", "why": "contract: it defines `browse.py --viewport`, which the fallback steps use"},
    {"id": "E01-T03", "why": "both tasks change `dev_notes/README.md`"}
  ],
  "needs": [],
  "touches": [
    ".claude/skills/verify-blog/features/navigation.md",
    "dev_notes/e2e_browser_tests/**",
    "dev_notes/dev-workflow.md",
    "dev_notes/ci-flow.mermaid",
    "dev_notes/README.md"
  ]
}
```

#### E02-T04: Make the Mac Mini ready to build and drive the blog → #135

- Kind: chore · Executor: agent · State: todo
- Today:
  - The QA machine is the Mac Mini. The fleet registry gives its SSH address. Each QA session works in a fresh clone in a scratch folder (D003)
  - On 2026-11-19 the Mini had `git`, `gh`, `node` v26.12.1 (it satisfies `engines.node` `>=22.23.4`), `uv`, `just` and `fnox`
  - On 2026-11-19 the Mini had no `bun` (`package.json` sets `packageManager` to `bun@1.3.4`), no Playwright Chromium for `browse.py`, no agent-browser and no clone of this repository
- After:
  - `bun` 1.3.x is installed
  - The Chromium build of Playwright 1.56 is installed: `uv run --with playwright==1.56.0 python -m playwright install chromium`
  - In a fresh clone in a scratch folder, `just check` passes, and verify-blog builds a preview and captures the home page
  - Reuse an installed tool that passes its probe. A cached Chromium folder alone cannot prove the browser launches
  - A comment on this issue gives each install command, each version and the `just check` result, so that a QA session can repeat the setup
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC7, D003
- Contract: none
- Acceptance:
  - [ ] On the Mini, `bun --version` prints a 1.3.x version, and in the scratch clone `bun install --frozen-lockfile --ignore-scripts` exits 0 with `git status --porcelain` empty after it
  - [ ] In the scratch clone, `just check` exits 0
  - [ ] `uv run .claude/skills/verify-blog/scripts/site.py up` prints a base URL, `browse.py "$URL/" --out <dir>` exits 0 and writes `screenshot.png`, and `site.py down` stops the preview
  - [ ] This issue has a comment with each required install command, each version and the `just check` result
- Verify: `just check` in the scratch clone on the Mini
- Out of scope: agent-browser and the iOS Simulator (B18, W04), a permanent clone, a change to the fleet's `repos.toml` (D003)
- Blocked by: none
- Unblocks: E01-QA1 (#139), E02-QA1 (#142), E03-QA1 (#144), E03-QA2 (#146), E04-QA1 (#141). The later iOS check (#159) uses this setup
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E02-T04",
  "blocked_by": [],
  "needs": [
    {"what": "The session runs on the Mac Mini", "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"},
    {"what": "gh signed in on the Mini", "check": "gh auth status"}
  ],
  "touches": []
}
```

#### E02-QA1: QA: verify-blog runs every recipe on a fresh preview, also on the QA machine → #142

- Kind: qa · Executor: QA agent on the QA machine · State: todo · Verdict: —
- Context: E02 makes the verify-blog recipes work on a fresh preview, adds the menu checks at 639 px and 640 px, and prepares the Mac Mini. The user is the next QA agent or agent: it proves a reader-facing change in a browser without a fix to the tool first.
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC7, NFR-01, FR-03
- Setup: in a fresh clone in a scratch folder on the Mini, run `bun install --frozen-lockfile --ignore-scripts` before any `just` command (D003)
- QA scenarios (≤ 8):
  - [ ] NFR-01: In a fresh clone in a scratch folder on the Mini, `just check` exits 0
  - [ ] FR-03: On a fresh preview (`uv run .claude/skills/verify-blog/scripts/site.py up`), run the `browse.py` fallback of each feature file: `home`, `navigation`, `post`, `search`, `tags` and `theme` → each call exits 0, and no `network.json` has status 404 for its page
  - [ ] FR-03: Run `nav-breakpoint` at 639 × 900 and at 640 × 900 → `#menu-btn` shows at 639 and is hidden at 640; at 639, a click on it shows the links
  - [ ] FR-03: In the scratch clone, remove the final `/` from one `$URL/tags/` in `tags.md` → `just check --only scripts` fails and names `tags.md` and the line; then restore the file with `git checkout -- .claude/skills/verify-blog/features/tags.md`
  - [ ] FR-03: `browse.py "$URL/" --out <dir> --viewport 639x900 --device iphone` → exits 2 with one error line
  - [ ] FR-03: `ls dev_notes` → no `e2e_browser_tests`, `dev-workflow.md` or `ci-flow.mermaid`, and `dev_notes/README.md` does not list them
- Also check: each acceptance item of E02-T01, E02-T02, E02-T03 and E02-T04 still passes on the default branch; `just check` passes.
- Output: Record the tested commit, independent Mini session, commands, actual results and verdict on this issue. Link each finding.
- Blocked by: E02-T01 (#133), E02-T02 (#134), E02-T03 (#140), E02-T04 (#135)
- Unblocks: no task in W01. The verdict informs the wave review
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E02-QA1",
  "verifies": ["E02-T01", "E02-T02", "E02-T03", "E02-T04"],
  "needs": [
    {"what": "The session runs on the Mac Mini", "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"},
    {"what": "gh signed in on the QA machine", "check": "gh auth status"},
    {"what": "bun on the QA machine (E02-T04)", "check": "command -v bun"}
  ]
}
```

### E03: Each merge and each deploy proves itself → #128

- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, FR-04, FR-05, FR-06
- Executor: agent
- Problem (CMO): One commit runs the full `just check` up to three times: at the push, at `just signoff` and at `just merge`, about 98 s each on a cold cache (#84). `just deploy` reports success when the Sevalla build finishes, but it never reads which commit Sevalla built. Nothing checks the public site after a deploy. Production served a build of 2026-10-22 for weeks, until a manual curl on 2026-11-19 found it.
- Outcome (FMO): `just merge` skips the checks when the PR head already carries a green signoff, and runs them otherwise. `just deploy` exits 1 when the deployed commit differs from the commit it printed. `just verify-live` checks the public site with no secret, and `just deploy` runs the same checks after each production deploy that it waits for. `just deploy --no-wait` says that it skipped both checks, and the playbook says to run `just verify-live` after a deploy by the manual CI workflow.

#### E03-T01: Let just merge reuse a green signoff on the same commit → #84

- Kind: feature · Executor: agent · State: todo
- Today:
  - `scripts/merge.py:260-261` prints `PR #N: checking <sha> before the merge` and calls `sign(repo, sha)` with no condition
  - `sign()` (`scripts/signoff.py:201-218`) runs `bun install --frozen-lockfile`, `just ci` and `just gitleaks`, then `gh signoff --commit <sha>`
  - `merge.py:95-98` already parses the PR's `statusCheckRollup` into `signed_off` (context `signoff`, state `SUCCESS`). But `merge()` reads `signed_off` only in `wait_until_mergeable`, after `sign()`
  - The pre-push hook also runs `just check`. Thus one commit runs the full check three times, about 98 s each on a cold cache (#84)
  - No test in `scripts/tests/test_merge.py` sets a status before the merge. The fake `gh` (`scripts/tests/fake.py`) gives a PR `signed_off` when `state["statuses"][<head>]` is `"success"`
  - pascalandy/skills#260 has a reference `signed_off()` for the same change
- After:
  - After the refusals and `pushed_head()`, `merge()` reads the PR. When the PR head equals the pushed head and it already carries a green `signoff`, `merge()` prints `PR #N: <sha> already carries a green signoff; skipping the checks`, then goes to `wait_until_mergeable`. Otherwise it calls `sign(repo, sha)` as before
  - The other steps do not change
  - The "Merge" section of `src/data/blog/dev_workflows/development-workflow.md` (step 2 at line 104, and line 120) and the section "Merge and deploy" of `AGENTS.md` say that `just merge` skips the checks when the head already carries a green signoff
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, D006
- Contract: none. The command line of `just merge` does not change
- Acceptance:
  - [ ] A new test in `scripts/tests/test_merge.py` sets `statuses[<head>] = "success"` before `just merge`; then `checks_run()` is empty, and the PR merges at that head
  - [ ] A new test sets a green status on the parent commit of the head only; then the three checks run, and the PR merges
  - [ ] `just check --only scripts` passes, and the 18 tests of `test_merge.py` that exist today are not changed
  - [ ] The development workflow and agent guide describe reuse on the exact head and the checks required on a different head
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: the pre-push check and the checks scoped by path of #84 option (a), because they change the decision "pushes run the verdict" (decision log, 2026-09-29); a change to `just signoff`
- Blocked by: E01-T01 (#130)
- Unblocks: E03-T02 (#143), E03-QA1 (#144), E03-QA2 (#146)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-T01",
  "blocked_by": [{"id": "E01-T01", "why": "both tasks change `AGENTS.md`"}],
  "needs": [],
  "touches": [
    "scripts/merge.py",
    "scripts/tests/test_merge.py",
    "src/data/blog/dev_workflows/development-workflow.md",
    "AGENTS.md"
  ]
}
```

#### E03-T02: Make just deploy fail when Sevalla built another commit → #143

- Kind: feature · Executor: agent · State: todo
- Today:
  - `scripts/deploy.py` gets the commit with `git ls-remote --exit-code origin refs/heads/<branch>` (`github_tip`, line 211) and prints `Deploying <branch> at <sha> to <target>` (line 215)
  - It sends `POST /static-sites/{site}/deployments` with `{"branch": branch}` (lines 222-224). Then `wait_for` (lines 136-163) polls `GET /static-sites/{site}/deployments/{deployment}` every 5 s, for at most 30 minutes, and reads only `status`
  - It exits 0 on `success`, prints no final line, and never reads `commit_sha`
  - Sevalla's v3 API accepts only `branch` for a static site, and builds the branch tip when the build starts (B22, #122). Thus a push between the print and the build ships a different commit, and nothing notices it (B43)
  - No test covers `deploy.py`, and no fake Sevalla exists
- After:
  - When the deployment reaches `success`, `deploy.py` reads `commit_sha` from the deployment that `wait_for` already reads
  - Equal to the printed commit: it prints `deployed <sha> to <target>` and exits 0
  - Different: it prints `error: Sevalla built <commit_sha>, not <sha>`, with both full SHAs, and exits 1
  - Missing or empty: it prints `error: Sevalla did not report the deployed commit` and exits 1
  - This applies to the production and preview targets. `--dry-run` does not change. `--no-wait` prints that it did not check the commit
  - The "Deploy" section of `development-workflow.md` (lines 122-160) says that `just deploy` fails when the deployed commit differs
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, D005
- Contract: Sevalla `GET https://api.sevalla.com/v3/static-sites/{site_id}/deployments/{deployment_id}` returns `status` and `commit_sha` (operation `getStaticSiteDeploymentV3`; B43 read the OpenAPI file on 2026-11-16). The 200 JSON response has top-level `status` and `commit_sha` fields. The public schema was checked on 2026-11-21
- Acceptance:
  - [ ] A new `scripts/tests/test_deploy.py` uses a fake Sevalla: a deployment that ends at `success` with the printed commit exits 0 and prints `deployed`; a different `commit_sha` exits 1, and the error names both SHAs; a missing `commit_sha` exits 1
  - [ ] `SEVALLA_TOKEN=fixture SEVALLA_STATIC_SITE_ID=fixture just deploy --dry-run` prints the same `Deploying main at …` and `dry run: POST …` lines as before, and exits 0. The dry run sends no request to Sevalla
  - [ ] The Deploy section of `development-workflow.md` names both the matching and mismatched commit results
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: the live site checks (E03-T03, E03-T04), the deploy jobs of `.github/workflows/ci.yml`
- Blocked by: E03-T01 (#84)
- Unblocks: E03-T04 (#153), E03-QA2 (#146)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-T02",
  "blocked_by": [
    {
      "id": "E03-T01",
      "why": "both tasks change `development-workflow.md`"
    }
  ],
  "needs": [
    {
      "what": "The deployment response includes the commit",
      "check": "curl -fsS https://api.sevalla.com/v3/openapi.json | jq -e '.paths[\"/static-sites/{id}/deployments/{deployment_id}\"].get.responses[\"200\"].content[\"application/json\"].schema.properties | has(\"commit_sha\") and has(\"status\")' >/dev/null"
    }
  ],
  "touches": [
    "scripts/deploy.py",
    "scripts/tests/test_deploy.py",
    "src/data/blog/dev_workflows/development-workflow.md"
  ]
}
```

#### E03-T03: Add just verify-live to check the public site → #145

- Kind: feature · Executor: agent · State: todo
- Today:
  - No script requests the public site: `scripts/` has no request to `pascalandy.com`, and `urllib` serves only the Sevalla API in `deploy.py`
  - On 2026-11-19 a manual curl found that production served a build of 2026-10-22. The curl checked the generator `Astro v7.4.8`, `lang="fr-CA"`, a French date, and status 200 for RSS and the sitemap
  - `src/layouts/Layout.astro:86` emits `<meta name="generator" content={Astro.generator} />`, and `package.json:24` pins `"astro": "7.4.8"`
  - `SITE.website` is `https://pascalandy.com/` (`src/config.ts:4`). The site serves `/rss.xml` and `/sitemap-index.xml`, and `/robots.txt` names the sitemap
- After:
  - `scripts/verify_live.py` and the recipe `just verify-live [BASE]`, in the `ship` group. `BASE` defaults to `https://pascalandy.com/`. The script uses stdlib `urllib` and checks:
    1. `BASE` answers 200, with `<html lang="fr-CA">` and `<meta name="generator" content="Astro v<astro version of package.json>">`
    2. `rss.xml` and `sitemap-index.xml` answer 200, and `robots.txt` answers 200 with a `Sitemap:` URL that answers 200
    3. The `<link>` of the first `<item>` of `rss.xml` answers 200
  - Each failed check prints one line with the URL, the expected value and the received value. The script tries the failed checks again every 10 s, for at most 120 s, because the CDN can serve old pages for a short time. Then it exits 1
  - On success, it prints `live site OK: <N> checks on <BASE>` and exits 0
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, D005
- Contract: `just verify-live [BASE]` exits 0 with one summary line, or exits 1 with one line for each failed check. `scripts/verify_live.py` also gives `failures(base, astro_version=None, retry_seconds=120) -> list[str]`, which returns those lines and an empty list on success. Without `astro_version`, it reads the version from the `package.json` of the checkout. E03-T04 calls this function, and E06 (W02) adds the 41 old URLs to its checks
- Acceptance:
  - [ ] `just verify-live` exits 0 against `https://pascalandy.com/` and prints `live site OK: <N> checks on https://pascalandy.com/`
  - [ ] `scripts/tests/test_verify_live.py` serves fixture sites with a local `http.server`: a good site exits 0; a wrong generator version, a 404 `rss.xml` and a 404 newest post each exit 1, with a line that names the URL, the expected value and the received value. The tests set the retry window to 0
  - [ ] `just --list` shows `verify-live` in the `ship` group
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: the call from `just deploy` and the playbook text (E03-T04), the 41 old URLs (E06), checks of the preview site, any check that needs a secret (D005)
- Blocked by: none
- Unblocks: E03-T04 (#153), E03-QA2 (#146)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-T03",
  "blocked_by": [],
  "needs": [{"what": "The public site answers", "check": "curl -sfI https://pascalandy.com/ -o /dev/null"}],
  "touches": [
    "scripts/verify_live.py",
    "scripts/tests/test_verify_live.py",
    "justfile"
  ]
}
```

#### E03-T04: Run the live checks after each production deploy → #153

- Kind: feature · Executor: agent · State: todo
- Today:
  - After E03-T02, `just deploy` compares the deployed commit with the printed commit, prints `deployed <sha> to <target>` and exits 0 on a match
  - After E03-T03, `scripts/verify_live.py` gives `failures(base, astro_version=None, retry_seconds=120)`, and `just verify-live` exists
  - `deploy.py` deploys GitHub's `main`, which can differ from the local checkout, so the local `package.json` can name another Astro version
  - Nothing runs the live checks after a deploy. `just deploy --no-wait` returns as soon as Sevalla accepts the deployment, and the manual CI workflow (`just gh-ci main production`) deploys through its own Sevalla action
- After:
  - After a waited production deployment reports `success` with a matching commit, `deploy.py` calls `failures()` on `SITE.website`, with the Astro version of `package.json` at the deployed commit. It prints each returned line and exits 1 when the list is not empty
  - `just deploy --no-wait` prints that it skipped the commit check and the live checks
  - The "Deploy" section of `development-workflow.md` documents `just verify-live`, says that `just deploy` runs it, and says to run `just verify-live` after a deploy by the manual CI workflow
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, D005, D012
- Contract: none. It uses the contract of E03-T03
- Acceptance:
  - [ ] A test in `scripts/tests/test_deploy.py` shows that `deploy.py production` calls the live checks after a matching `success`, with the Astro version of the deployed commit even when the local `package.json` differs, and exits 1 when they return a failure
  - [ ] A test shows that a commit mismatch exits 1 before the live checks run
  - [ ] A test shows that `--no-wait` prints the skip line and runs no check
  - [ ] The Deploy section of `development-workflow.md` documents automatic live checks, the no-wait exception and the manual CI fallback
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: the CI deploy jobs of `.github/workflows/ci.yml`, live checks of the preview site
- Blocked by: E03-T02 (#143), E03-T03 (#145)
- Unblocks: E03-QA2 (#146)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-T04",
  "blocked_by": [
    {"id": "E03-T02", "why": "both tasks change `deploy.py`, `test_deploy.py` and `development-workflow.md`"},
    {"id": "E03-T03", "why": "contract: it defines `failures()` in `scripts/verify_live.py`"}
  ],
  "needs": [],
  "touches": [
    "scripts/deploy.py",
    "scripts/tests/test_deploy.py",
    "src/data/blog/dev_workflows/development-workflow.md"
  ]
}
```

#### E03-QA1: QA: just merge reuses a green signoff → #144

- Kind: qa · Executor: QA agent on the QA machine · State: todo · Verdict: —
- Context: This intermediate check covers the first result a maintainer can use: `just merge` no longer runs the full checks again on a head that already carries a green signoff. The user is the agent or Pascal that merges a PR.
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, FR-04, NFR-01
- Setup: in a fresh clone in a scratch folder on the Mini, run `bun install --frozen-lockfile --ignore-scripts` before any `just` command (D003)
- QA scenarios (≤ 8):
  - [ ] FR-04: In a fresh clone on the Mini, `just check --only scripts` → the tests of `test_merge.py` pass, including the two new tests of E03-T01
  - [ ] FR-04: Read `merge()` in `scripts/merge.py` → the checks are skipped only when the green `signoff` is on exactly the pushed head; every refusal still runs before the skip
  - [ ] FR-04: Read the "Merge" section of `development-workflow.md` and the section "Merge and deploy" of `AGENTS.md` → both describe the skip, and neither says that `just merge` always runs the checks
  - [ ] NFR-01: In the fresh Mini checkout, run `just check`. The installed Bun builds the tested revision.
- Also check: each acceptance item of E03-T01 still passes on the default branch; `just check` passes.
- Output: Record the tested commit, independent Mini session, commands, actual results and verdict on this issue. Link each finding.
- Blocked by: E03-T01 (#84), E02-T04 (#135)
- Unblocks: no task in W01. The verdict informs the wave review
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-QA1",
  "verifies": [
    "E03-T01",
    "E02-T04"
  ],
  "needs": [
    {
      "what": "The session runs on the Mac Mini",
      "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"
    },
    {
      "what": "gh signed in on the QA machine",
      "check": "gh auth status"
    },
    {
      "what": "bun on the QA machine (E02-T04)",
      "check": "command -v bun"
    }
  ]
}
```

#### E03-QA2: QA: Each merge and each deploy proves itself → #146

- Kind: qa · Executor: QA agent on the QA machine · State: todo · Verdict: —
- Context: E03 removes the repeated full check from `just merge`, makes `just deploy` compare the deployed commit, and adds `just verify-live`, which `just deploy` also runs. The user is Pascal or the agent that merges and deploys: a wrong deploy must fail loudly, and a merge must not wait for checks that already passed.
- Traces: [BC §8](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s8), SC8, FR-04, FR-05, FR-06, NFR-01
- Setup: in a fresh clone in a scratch folder on the Mini, run `bun install --frozen-lockfile --ignore-scripts` before any `just` command (D003)
- QA scenarios (≤ 8):
  - [ ] FR-04, FR-05: In a fresh clone on the Mini, `just check --only scripts` → the new tests of `test_merge.py`, `test_deploy.py` and `test_verify_live.py` pass
  - [ ] FR-04: Read `merge()` in `scripts/merge.py` → the skip needs a green `signoff` on exactly the pushed head, and the test with a green parent commit runs the three checks
  - [ ] FR-06: `just verify-live` → exits 0 and prints `live site OK: <N> checks on https://pascalandy.com/`
  - [ ] FR-06: `just verify-live https://pascalandy.com/nope/` → exits 1 in at most 3 minutes, and names each failed URL with the expected and received values
  - [ ] FR-04, FR-06: Read the "Merge" and "Deploy" sections of `development-workflow.md` → they describe the signoff reuse, the commit comparison and `just verify-live`, and each `just` recipe that they name is in `just --list`
  - [ ] FR-05, FR-06: Read `deploy.py` → after a production `success`, it compares the commit first, then runs the live checks, and each failure exits 1
  - [ ] NFR-01: In the fresh Mini checkout, run `just check`. The installed Bun builds the tested revision.
- Also check: each acceptance item of E03-T01, E03-T02, E03-T03 and E03-T04 still passes on the default branch; `just check` passes.
- Output: Record the tested commit, independent Mini session, commands, actual results and verdict on this issue. Link each finding.
- Blocked by: E03-T01 (#84), E03-T02 (#143), E03-T03 (#145), E03-T04 (#153), E02-T04 (#135)
- Unblocks: no task in W01. The verdict informs the wave review
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E03-QA2",
  "verifies": [
    "E03-T01",
    "E03-T02",
    "E03-T03",
    "E03-T04",
    "E02-T04"
  ],
  "needs": [
    {
      "what": "The session runs on the Mac Mini",
      "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"
    },
    {
      "what": "gh signed in on the QA machine",
      "check": "gh auth status"
    },
    {
      "what": "bun on the QA machine (E02-T04)",
      "check": "command -v bun"
    }
  ]
}
```

### E04: The repository holds no dead feature, no stray script and no orphan public file → #129

- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC6, FR-07, FR-08
- Executor: agent
- Problem (CMO): The disabled "Edit page" link from AstroPaper is still mounted on each post, and it points to the upstream AstroPaper repository. Five Ghost migration scripts sit in `scripts/` with no caller, and `ruff.toml` excludes them one by one. Five files in `public/og-legacy/` (780 KB) ship to production with no reference, because the image check looks for orphans only under `src/assets/images`.
- Outcome (FMO): No code, config, schema key or doc of the "Edit page" link remains. The Ghost scripts live in `scripts/archive/ghost-migration/` with a README that says why they stay. `public/` holds only referenced images, and `just check --only images` fails on a new unreferenced image under `public/`.

#### E04-T01: Remove the disabled "Edit page" link → #136

- Kind: chore · Executor: agent · State: todo
- Today:
  - `src/components/EditPost.astro` (29 lines) builds `href` from `SITE.editPost.url` and the post's `filePath`, and renders a link with `IconEdit` and `SITE.editPost.text`
  - `src/config.ts:13-17` sets `editPost: { enabled: false, text: "Edit page", url: "https://github.com/satnaing/astro-paper/edit/main/" }`
  - `src/layouts/PostDetails.astro:10` imports the component, and lines 115-118 mount it with a `|` separator. Both stay hidden while `enabled` is `false`
  - `src/content.config.ts:44` accepts `hideEditPost`, and `src/data/blog/dev_workflows/frontmatter-schema.md:33` and `:72` document it. No post sets it
  - `src/assets/icons/IconEdit.svg` has no other user
- After: `EditPost.astro`, `IconEdit.svg`, `SITE.editPost`, the import, the mount and its separator, the schema key `hideEditPost` and its two lines of doc are gone. No built page changes, except the playbook `/blog/dev-workflows/frontmatter-schema/`, which loses its two `hideEditPost` lines. The shared stylesheet loses the Tailwind rules that only `EditPost.astro` used, such as `.justify-baseline`, so its file name changes in each page
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC6
- Contract: none. The frontmatter schema loses the key `hideEditPost`, which no post uses
- Acceptance:
  - [ ] `rg -n 'EditPost|editPost|hideEditPost|IconEdit' src scripts .claude` prints nothing
  - [ ] `just parity` between fresh builds of the commit before the change and the commit with it reports only the page `/blog/dev-workflows/frontmatter-schema/`, the shared stylesheet with its new file name in each page, and what they derive, such as Pagefind entries. A diff of the two emitted stylesheets shows only removed rules that `EditPost.astro` used
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: other AstroPaper leftovers, a visible change to the post layout
- Blocked by: none
- Unblocks: E04-QA1 (#141)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E04-T01",
  "blocked_by": [],
  "needs": [],
  "touches": [
    "src/components/EditPost.astro",
    "src/assets/icons/IconEdit.svg",
    "src/config.ts",
    "src/layouts/PostDetails.astro",
    "src/content.config.ts",
    "src/data/blog/dev_workflows/frontmatter-schema.md"
  ]
}
```

#### E04-T02: Archive the five Ghost migration scripts → #137

- Kind: chore · Executor: agent · State: todo
- Today:
  - `scripts/analyze_images.py`, `scripts/convert_frontmatter.py`, `scripts/import_ghost_posts.py`, `scripts/normalize-tags.py` and `scripts/rename_to_kebab.py` have no caller: no recipe, hook, workflow or other file names them
  - `ruff.toml:6-13` excludes each of the five, under the comment "Ghost migration and content-maintenance helpers that predate the CLI contract"
  - `scripts/archive/` does not exist. R9 (2026-11-19) says to archive them, not to delete them, and says that no Ghost export exists
- After:
  - The five scripts are in `scripts/archive/ghost-migration/`, moved with `git mv` so that `git log --follow` keeps their history
  - `scripts/archive/ghost-migration/README.md` says what each script did, that no recipe runs them, that nobody maintains them, and why they stay (R9)
  - `ruff.toml` excludes `scripts/archive/` with one entry instead of five
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC6, D009
- Contract: none
- Acceptance:
  - [ ] `ls scripts/archive/ghost-migration/` lists the five scripts and `README.md`, and `ls scripts/` lists none of the five
  - [ ] `git log --follow --oneline -- scripts/archive/ghost-migration/import_ghost_posts.py` shows commits from before the move
  - [ ] `rg -n 'import_ghost_posts|convert_frontmatter|rename_to_kebab|normalize-tags|analyze_images' -g '!scripts/archive/**' -g '!plan/**'` prints nothing
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: a fix or a test of the archived scripts, a Ghost import
- Blocked by: none
- Unblocks: E04-QA1 (#141)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E04-T02",
  "blocked_by": [],
  "needs": [],
  "touches": [
    "scripts/analyze_images.py",
    "scripts/convert_frontmatter.py",
    "scripts/import_ghost_posts.py",
    "scripts/normalize-tags.py",
    "scripts/rename_to_kebab.py",
    "scripts/archive/**",
    "ruff.toml"
  ]
}
```

#### E04-T03: Delete the five orphan files of public/, and make the image check cover public/ → #138

- Kind: chore · Executor: agent · State: todo
- Today:
  - `public/` has 19 tracked files: `favicon.png` (`src/layouts/Layout.astro:83`), `pascalandy_banner.jpg` (`src/config.ts:9`, `ogImage`) and 17 files in `public/og-legacy/`. The `cim-NN` posts reference 12 of the 17 with `/og-legacy/…` paths
  - These 5 files have no reference and ship to production (780 KB): `public/og-legacy/2017/11/gault.jpg`, `public/og-legacy/2019/01/025b-cryptoinmontreal.jpg`, `public/og-legacy/2019/03/028a-cryptoinmontreal.jpg`, `public/og-legacy/2019/05/CIM-logo-general.jpg`, `public/og-legacy/2019/11/038b-cryptoinmontreal.jpg`
  - `scripts/check_images.py` scans each source file under `src/` and resolves `/x` and bare paths into `public/`, but looks for orphans only under `src/assets/images`. Its tests are in `scripts/tests/test_images.py`
  - The build copies `dist/pagefind` into `public/pagefind/`, so that folder holds generated files that no source references
- After:
  - The 5 files are deleted
  - `check_images.py` also reports `unreferenced image: public/<path>` for an image under `public/` that no source references. It skips `public/pagefind/`
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC6
- Contract: none
- Acceptance:
  - [ ] None of the 5 paths exists: `for f in 2017/11/gault.jpg 2019/01/025b-cryptoinmontreal.jpg 2019/03/028a-cryptoinmontreal.jpg 2019/05/CIM-logo-general.jpg 2019/11/038b-cryptoinmontreal.jpg; do test ! -e "public/og-legacy/$f" || echo "$f"; done` prints nothing
  - [ ] New tests in `test_images.py`: an unreferenced image in a fixture `public/` fails with `unreferenced image: public/…`; an image referenced by `/x.jpg` from a post, an image referenced by a bare name in a `.ts` file, and a file in `public/pagefind/` pass
  - [ ] `just check --only images` exits 0
  - [ ] `just check` exits 0
- Verify: `just check`
- Out of scope: non-image files in `public/`, duplicate images (R17)
- Blocked by: none
- Unblocks: E04-QA1 (#141)
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E04-T03",
  "blocked_by": [],
  "needs": [],
  "touches": [
    "public/og-legacy/2017/11/gault.jpg",
    "public/og-legacy/2019/01/025b-cryptoinmontreal.jpg",
    "public/og-legacy/2019/03/028a-cryptoinmontreal.jpg",
    "public/og-legacy/2019/05/CIM-logo-general.jpg",
    "public/og-legacy/2019/11/038b-cryptoinmontreal.jpg",
    "scripts/check_images.py",
    "scripts/tests/test_images.py"
  ]
}
```

#### E04-QA1: QA: The repository holds no dead feature, no stray script and no orphan public file → #141

- Kind: qa · Executor: QA agent on the QA machine · State: todo · Verdict: —
- Context: E04 removes the disabled "Edit page" link, archives the Ghost scripts, deletes the orphan files of `public/` and extends the image check to `public/`. The user is the next agent: it must not maintain or reuse code that the site does not run, and a new orphan file must fail the checks.
- Traces: [BC §7](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s7), SC6, FR-07, FR-08, NFR-01
- Setup: in a fresh clone in a scratch folder on the Mini, run `bun install --frozen-lockfile --ignore-scripts` before any `just` command (D003)
- QA scenarios (≤ 8):
  - [ ] FR-07, FR-08: In a fresh clone on the Mini, `just build` → `rg -l 'satnaing/astro-paper/edit/' dist` prints nothing (the decision log may still name the removed link), and `fd 'gault|025b-|028a-|CIM-logo-general|038b-' dist/og-legacy` prints nothing
  - [ ] FR-07: Add `hideEditPost: true` to one post of the scratch clone → `just check --only content` fails and names the key; then restore the post with `git checkout -- <post>`
  - [ ] FR-08: Copy a JPEG to `public/og-legacy/qa-orphan.jpg` → `just check --only images` fails with `unreferenced image: public/og-legacy/qa-orphan.jpg`; delete the file → the check passes
  - [ ] FR-08: `fd -e jpg . public/og-legacy | wc -l` → prints 12, and `just check --only images` passes
  - [ ] FR-07: Read `scripts/archive/ghost-migration/README.md` → it says what each script did, why the scripts stay (R9), and that no recipe runs them; `just lint` passes
  - [ ] FR-07: `git log --follow --oneline -- scripts/archive/ghost-migration/import_ghost_posts.py` → shows commits from before the move, and `just check` exits 0 in the same clone
  - [ ] NFR-01: In the fresh Mini checkout, run `just check`. The installed Bun builds the tested revision.
- Also check: each acceptance item of E04-T01, E04-T02 and E04-T03 still passes on the default branch; `just check` passes.
- Output: Record the tested commit, independent Mini session, commands, actual results and verdict on this issue. Link each finding.
- Blocked by: E04-T01 (#136), E04-T02 (#137), E04-T03 (#138), E02-T04 (#135)
- Unblocks: no task in W01. The verdict informs the wave review
- Ready review: planner, 2026-11-21, brief and dependencies checked

```json
{
  "id": "E04-QA1",
  "verifies": [
    "E04-T01",
    "E04-T02",
    "E04-T03",
    "E02-T04"
  ],
  "needs": [
    {
      "what": "The session runs on the Mac Mini",
      "check": "hostname | tr '[:upper:]' '[:lower:]' | grep -q m4mini"
    },
    {
      "what": "gh signed in on the QA machine",
      "check": "gh auth status"
    },
    {
      "what": "bun on the QA machine (E02-T04)",
      "check": "command -v bun"
    }
  ]
}
```

## Discoveries

## Changes since original plan

D017 moves deferred issue creation into this planning update. D013 records the existing CI and browser checks. D014 makes the Mini setup a prerequisite of independent QA. Each brief lists its immediate successors.

## Learnings
