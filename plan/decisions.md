# BLOG: Decisions

Plan-structure and technical decisions, newest last. Pascal's product decisions of 2026-11-19 live in [BC §3](00-business-case.md#s3); W01 copies them into the public decision log (`src/data/blog/dev_workflows/decision-log.md`).

## D001: Four waves, with the enablers first

- Date: 2026-11-19
- Trigger: initial decomposition
- Decision: the plan has four waves:
  - W01 foundations: the queue, the docs, verify-blog, the merge and deploy tools, and the invisible code cleanup ([BC §4](00-business-case.md#s4), [BC §7](00-business-case.md#s7), [BC §8](00-business-case.md#s8))
  - W02 reader-release: everything a reader sees, the editorial rules, and the deploy ([BC §5](00-business-case.md#s5), [BC §6](00-business-case.md#s6), [BC §9](00-business-case.md#s9), [BC §10](00-business-case.md#s10))
  - W03 brand-and-reach and W04 upkeep: the later items ([BC §11](00-business-case.md#s11))
- Why: the business case lists seven steps in reader order. The plan keeps step 1 first and moves steps 4 and 5 before steps 2 and 3, for four reasons:
  - The QA agent proves the reader-facing work of W02 with verify-blog. Today two verify-blog recipes fail before their first step (B41), the recipes have no 639 px and 640 px menu check (R18), and the QA machine has no `bun`
  - R5 removes one full `just check` run (about 98 s cold) from each merge. W02 has about 15 merges
  - The W02 deploy needs the commit comparison (B43) and the live check. The worst failure of this project was a production site that served an old build for weeks, and nobody noticed
  - W01 changes nothing that a reader sees, so Pascal's three interventions (two lists, screenshots, the deploy) all fall in W02
- Affects: W01, W02, W03, W04 (new)

## D002: Plan prose in English

- Date: 2026-11-19
- Trigger: technical choice
- Decision: every file in `plan/` is in English, except the business case, which keeps Pascal's French text
- Why: `AGENTS.md` says code, docs and commits are in English, and the GitHub issues get the epic entries and the briefs word for word. One language avoids two copies of each term
- Affects: all plan files

## D003: QA runs on the Mac Mini, in a fresh clone

- Date: 2026-11-19
- Trigger: technical choice
- Decision: the QA machine is the Mac Mini (the fleet QA host). Each QA session clones `pascalandy/pascalandy-blog-paper` into a new scratch folder and tests its default branch. The Mini keeps no permanent clone, so the fleet's `repos.toml` does not change
- Why: a fresh clone tests exactly the default branch and carries no state from an implementer. On 2026-11-19 the Mini had `git`, `gh`, `node` v26.12.1, `uv`, `just` and `fnox`, but no `bun`, no Playwright Chromium and no `agent-browser`. E02-T04 installs what the QA agent needs
- Affects: every QA task, E02-T04

## D004: The planner approved the checkpoint of Procedure A

- Date: 2026-11-19
- Trigger: technical choice (PM delegation)
- Decision: Pascal asked the planner to decide everything it would otherwise wait on him for ("YOU ARE THE BOSS", 2026-11-19). The planner approved step 8 of Procedure A itself and synced the plan to GitHub. Pascal keeps the three interventions of the business case:
  - The two lists: a human task of W02 (R13, R15)
  - The screenshots: Pascal's UAT, after he reads the QA reports of W02
  - The deploy: a human task of W02
- Why: Pascal delegated the decisions explicitly. Each GitHub write is reversible: an issue closes as not planned
- Affects: initial sync

## D005: The live check reads only the public site

- Date: 2026-11-19
- Trigger: technical choice
- Decision: `just verify-live` checks the public site with plain HTTP requests and needs no secret. The comparison of the deployed commit stays in `just deploy`, which already reads the Sevalla token from fnox
- Why: the QA agent, Pascal and any agent can run the live check without the token. The Sevalla deployment record says which commit Sevalla built, and the public site shows that readers get a working build. Neither check proves that the CDN serves the new revision instead of a cached one. A build stamp in the pages would prove it, but it needs a fact that the plan lacks: whether Sevalla's build exposes its commit. It waits for a stale-cache incident
- Affects: E03-T02, E03-T03, E03-T04, E06, E09

## D006: Issue #84 becomes the issue of E03-T01

- Date: 2026-11-19
- Trigger: technical choice
- Decision: the sync rewrites issue #84 as the brief of E03-T01 instead of opening a second issue. Before the rewrite, the planner comments that R5 chose only the merge reuse, and that GitHub keeps the old body in the edit history
- Why: #84 already holds the history of the question. One issue per piece of work keeps SC1
- Affects: E03-T01, #84

## D007: Keep the 90-file cap and name CodeRabbit

- Date: 2026-11-19
- Trigger: technical choice (R7)
- Decision: `AGENTS.md` keeps the rule "a PR has 90 files or fewer" as a review-size rule, and names CodeRabbit as the review bot instead of Greptile
- Why: #99 and #102 show CodeRabbit reviews and no Greptile review. The cap serves review size for Pascal and the bot, so it needs no documented bot limit
- Affects: E01-T01

## D008: What happens to each backlog row

- Date: 2026-11-19
- Trigger: technical choice (R10)
- Decision: each row of `dev_notes/backlog.md` at `cb723c8` gets one fate:
  - A plan task: B2 (E07), B7 (E06), B12 (E05, with R20), B13 (E07), B38 (E04-T03), B39 (E05), B41 (E02-T01), B42 (E05), B43 (E03-T02), #84 (E03-T01), R18 (E02-T03)
  - A new issue without a wave label, filed by E01-T03: R2, R6, B14, B16, B18, B23, B24, B26, B28, B29, B30, B31, B33, B36
  - Closed by E01-T02: #89, #90, #95, #98, #54, #56, #59, #62, #65
  - Removed from the file as done or settled: B1, B3 to B6, B8 to B11, B15, B17, B19 to B22, B25, B27, B32, B34, B35, B37, B40, #87, #92, #94, #97, R1, R3 to R5, R7 to R17, R19
- Why: B23 and B26 are not in [BC §11](00-business-case.md#s11), but they are open work, so they become issues (B26 in W03, B23 in W04). B32 closes because the decision of 2026-10-21 keeps the unified processor. B37 closes because R9 says no Ghost export exists. #95 is done: #108 deleted the playbook that held the stale font example
- Affects: E01-T02, E01-T03, W03, W04

## D009: Deletions and moves count once

- Date: 2026-11-19
- Trigger: technical choice
- Decision: for the task limit of 8 files, a deleted folder counts as one file, and a moved file counts once. The lines of a deleted file do not count toward the limit of about 400 changed lines
- Why: a deletion or a `git mv` needs no review line by line. Without this rule, E02-T03 (it deletes about 2,900 lines of old plans) and E04-T02 would split into PRs that each do almost nothing
- Affects: Limits in `01-project.md`

## D010: Keep `dev_notes/MultiLanguage/`

- Date: 2026-11-19
- Trigger: technical choice (R18)
- Decision: E02-T03 deletes the old browser test plans, `dev_notes/dev-workflow.md` and `dev_notes/ci-flow.mermaid`, and keeps `dev_notes/MultiLanguage/`
- Why: R18 left the multilingual plans to Pascal's preference. They are scratch notes about a bilingual site, they cost nothing, and nothing reads them
- Affects: E02-T03

## D011: The later items are issues first, then waves

- Date: 2026-11-19
- Trigger: initial decomposition
- Decision: E01-T03 files each later item as an issue without a `wave:` label, so it has no deadline. W03 and W04 stay `proposed` and name these items. When a wave review makes W03 or W04 active, each of its tasks that comes from an item filed by E01-T03 takes over that issue: the planner rewrites the issue as the brief and adds the wave label, instead of opening a second issue
- Why: Pascal asked that each later item become an issue without a deadline ([BC §11](00-business-case.md#s11)). The proposed waves keep the order and the reasons
- Affects: E01-T03, W03, W04

## D012: The automatic checks cover `just deploy` when it waits

- Date: 2026-11-19
- Trigger: technical choice (review of the plan)
- Decision: the commit comparison and the live checks run automatically after each production deploy that `just deploy` waits for. Two paths are exceptions: `just deploy --no-wait` prints that it skipped both checks, and after a deploy by the manual CI workflow (`just gh-ci main production`), the playbook says to run `just verify-live`
- Why: the decision log (2026-09-29) makes `just deploy` the way to ship `main`. `--no-wait` returns before the build ends, so it cannot check the result. The CI workflow is a manual fallback with its own Sevalla action; wiring checks into it would add a workflow change for a path that nobody uses today
- Affects: SC8, E03, E03-T04

## D013: Reuse the existing CI baseline and browser verification

- Date: 2026-11-21
- Trigger: review of the active wave against planning version 3.1.0
- Decision: under delegated planning authority, waive a duplicate baseline task. The existing agent guide, justfile, hooks and signoff cover the baseline. Keep the existing check selection.
- Why: `just check --list` reports ten checks. The repository already has a verifier with a launcher, doctor, Playwright driver and feature recipes. A second verifier would test the same site.
- Affects: W01. E02-T03 maintains the existing navigation journey. When W02 changes a reader journey, its briefs must update the affected verify-blog recipe.

## D014: Verify the Mini setup before independent QA

- Date: 2026-11-21
- Trigger: four QA issues required Bun on the Mini but had no issue dependency on its setup
- Decision: each independent QA issue verifies E02-T04. The setup evidence is a successful build on the Mini. E02-QA1 also verifies a real browser launch.
- Why: the ten independent delivery tasks can start now. A reviewer who starts QA before the Mini can build the blog cannot distinguish a setup failure from a product defect.
- Affects: E01 to E04, the native issue dependencies and the QA playbook

## D015: Set the editorial lists from the published articles

- Date: 2026-11-21
- Trigger: Pascal delegated the pending editorial choices
- Decision: E07 and #149 give the English files, the six vacancies and the five featured files. The English choices follow the main article, role description or event announcement. For image-only posts, the title and description supply the language.
- Why: event footers, pasted specifications and external links can outweigh the author’s text in a word count. A fixed list keeps language metadata, listings and search verifiable.
- Affects: E07. This decision replaces the list confirmation in D004. The original November 19 answers remain historical.

## D016: Publish after the reader wave

- Date: 2026-11-21
- Trigger: a human release in W02 would wait for agent work in the same wave
- Decision: W02 covers the preview. W02B covers the authorized production revision and public checks. Keep release issue #151 and its ID, E09, for W02B. This existing issue remains visible while its wave is proposed.
- Why: Pascal needs the finished screenshots and QA reports before he can authorize publication. Keeping that decision after W02 lets agents finish the preview independently.
- Affects: W02, W02B, W03 and W04. The later outlines identify the remaining human inputs. This decision updates the wave order in D001.

## D017: Put deferred work on GitHub during planning

- Date: 2026-11-21
- Trigger: the requested handoff must work from the issues alone
- Decision: the fourteen deferred items now have individual issues (#155–#168), acceptance criteria and prerequisites. The four missing labels exist. E01-T03 reconciles these issues and preserves the Inbox.
- Why: an agent can inspect the scope before a later wave starts. Each later brief reuses the existing issue, which preserves its history.
- Affects: E01-T03, W03 and W04. This decision updates the timing in D008 and D011. B24 supplies the comparison baseline for B30. B28, B29, B30 and B31 use the same dependency files in that order.
