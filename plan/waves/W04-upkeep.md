---
id: W04
project: BLOG
status: proposed
label: wave:W04
skill_version: "2.0.0"
---

# W04: upkeep

## Goal

Dependencies stay current with little effort from Pascal, and guards catch silent regressions.

## Exit criteria

- [ ] One dependency agent opens upgrade PRs that can reach a green `signoff`, or a decision says why upgrades stay agent tickets; the decision log matches what runs (SC11)
- [ ] ESLint, TypeScript, Pagefind and satori run their chosen versions, and `just check` passes (SC11)
- [ ] A fixture without `compressHTML` or without the unified processor makes `just check` fail and name the setting (SC11)
- [ ] The iOS steps of verify-blog ran once on the Mac Mini (SC11)

## Scope

- R6: a spike compares Renovate, Dependabot and other agents, and says how their PRs pass `signoff`; the result replaces or confirms the decision "Renovate is the only dependency bot" (2026-09-29)
- B28, then B29: ESLint, eslint-plugin-astro and typescript-eslint together, then TypeScript; B30: Pagefind; B31: satori, with Pascal's review of the OG images
- B33: a guard for `compressHTML` and the unified processor; B24: Pagefind byte differences; B36: the Prettier cache
- B23: `persist-credentials: false` in `claude.yml`, with one live `@claude` run by Pascal
- B18: phone-format QA on the Mac Mini with `agent-browser -p ios`, Xcode and Appium
- Each task of this wave that comes from the backlog takes over the issue that E01-T03 filed, instead of a new issue (D011)
