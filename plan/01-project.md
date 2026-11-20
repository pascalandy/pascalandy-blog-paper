# BLOG: Project

Rolling-wave plan that finishes the 2026-11 audit of pascalandy.com/blog. The planner is the only actor that edits `plan/`, always in a `plan:` commit. Plan prose is in English because this repository keeps its docs in English (`AGENTS.md`, D002); the business case stays in French, as Pascal wrote it.

## Summary

- Objective: apply every decision of 2026-11-19, fix what readers still see, make each merge and each deploy prove itself, then ship the result to production ([BC §1](00-business-case.md#s1))
- Stakeholders:
  - Pascal: author, PM, the only person who merges or deploys without an agent, and the only person who does UAT
  - Readers of pascalandy.com/blog, mostly French speakers
  - The next agent that works in this repository: it needs one queue, true docs and tools that work
- Success criteria:
  - SC1: one queue. Every open piece of work is a labeled GitHub issue of this repository, and `dev_notes/backlog.md` holds only Pascal's Inbox ([BC §4](00-business-case.md#s4), R10)
  - SC2: a comment on #103 records each answer of 2026-11-19, the decision log has a line for each lasting decision, and `AGENTS.md` states the rules that these decisions change ([BC §3](00-business-case.md#s3), [BC §4](00-business-case.md#s4))
  - SC3: readers see a readable interface, fully in Québec French, with no stray characters: light-theme text reaches 4.5:1 contrast ([BC §5](00-business-case.md#s5): R20, B42, B39)
  - SC4: the 41 old `/blog/cryptoinmontreal-NN/` URLs reach their `/blog/cim-NN/` pages ([BC §5](00-business-case.md#s5): R3)
  - SC5: each post carries its language, job ads leave the blog roll, and the home page features 5 posts ([BC §6](00-business-case.md#s6): R13, R15, B13)
  - SC6: the code holds no disabled feature, no unused script outside an archive, and no unreferenced file in `public/` ([BC §7](00-business-case.md#s7): R16, R9, B38)
  - SC7: every verify-blog recipe runs on a fresh preview, including the 639 px and 640 px menu breakpoint ([BC §7](00-business-case.md#s7) R18, [BC §8](00-business-case.md#s8) B41)
  - SC8: `just merge` checks each commit once, `just deploy` fails when Sevalla built another commit, and a live check runs after each production deploy that `just deploy` waits for ([BC §8](00-business-case.md#s8): R5, B43). `--no-wait` and the manual CI deploy are exceptions (D012)
  - SC9: one page states the editorial rules, and each rule names the check that enforces it ([BC §9](00-business-case.md#s9))
  - SC10: production serves the final `main`, and the live check passes ([BC §10](00-business-case.md#s10))
  - SC11: the later items are tracked as issues, then planned in a wave: `www` keeps the path, a sharp logo, a dependency agent, Star Academy, phone QA on the Mac, library upgrades and small tooling ([BC §11](00-business-case.md#s11))
- Constraints:
  - A PR merges into `main` only with a green `signoff` status on its head, through `just merge` or `gh stack merge` (`AGENTS.md`, decision log 2026-09-29)
  - Agents deploy only when Pascal asks (`AGENTS.md`)
  - Posts are in Québec French; code, docs and commits are in English
  - A PR has 90 files or fewer (`AGENTS.md`, D007)
  - W01 starts after this plan lands on `main` (PR #152): E01-T01 cites `plan/01-project.md` in `AGENTS.md`, and the docs check resolves that path only on the default branch
- Out of scope:
  - om1's Node version: it belongs to the `dotfiles` repository (R4, [BC §12](00-business-case.md#s12))
  - Duplicate images (R17), the 28 uncertain Ghost dates (B37, R9), redirects for old Ghost root URLs (not decided on 2026-11-19)
  - An email sign-up form (B15), Graphite (B17), moving the playbooks to `/docs` (B10)
- Source: [Business case](00-business-case.md) · Agent file: [AGENTS.md](../AGENTS.md) · Decisions: [decisions.md](decisions.md)
- QA machine: Mac Mini (`m4mini`, SSH `assistant@m4mini.donkey-arcturus.ts.net`). Each QA session works in a fresh clone in a scratch folder (D003)

## Open questions

1. Which posts are in English? → asked to PM in W02: a human task confirms the candidate list before the `lang: en` task runs (R13)
2. Which posts are job ads? → asked to PM in W02, in the same human task (R15)
3. Can a static Sevalla site answer real 301s for the 41 old URLs? → resolved by R3: Astro `redirects`, checked by `just check`. A static build emits a redirect page for each old URL, so no host rule is needed
4. What file limit does CodeRabbit apply? → resolved D007: keep the 90-file cap as a review-size rule and name CodeRabbit
5. Where does QA run, and what does the QA machine lack? → resolved D003: the Mac Mini, in a fresh clone; it lacks `bun` and the Playwright Chromium, so E02-T04 installs them
6. Does the live check need the Sevalla token? → resolved D005: no. `just verify-live` reads only the public site; the commit comparison stays in `just deploy`
7. Do the later items get a deadline? → resolved D011: no. They become issues without a wave label, and the proposed waves W03 and W04 order them

## Limits

- Task: one module or ≤ 8 files, ≤ ~400 changed lines, ≤ 5 acceptance items, no open decision. A deleted folder counts as one file, a moved file counts once, and the lines of a deleted file do not count toward the line limit (D009)
- QA: intermediate QA when an epic has > 5 tasks or spans > 2 batches; ≤ 8 QA scenarios per QA task
- Recalibrated: never (set at the initial decomposition, 2026-11-19)

Next IDs: E10, D013

## Waves

| ID | Name | Goal | Status | File |
|---|---|---|---|---|
| W01 | foundations | One queue, true docs, QA tools that run on the QA machine, a delivery loop that proves itself, and no dead code | active | [W01](waves/W01-foundations.md) |
| W02 | reader-release | Readers get a readable, fully French blog with working old links and the right posts, and production serves it | planned | [W02](waves/W02-reader-release.md) |
| W03 | brand-and-reach | Every entry point and the brand look finished: `www` links keep their path, the header shows a sharp logo, and images have French alt text | proposed | [W03](waves/W03-brand-and-reach.md) |
| W04 | upkeep | Dependencies stay current with little effort from Pascal, and guards catch silent regressions | proposed | [W04](waves/W04-upkeep.md) |
