---
id: W04
project: BLOG
status: proposed
label: wave:W04
skill_version: "3.1.0"
executor: human
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

- [R6 · #156](https://github.com/pascalandy/pascalandy-blog-paper/issues/156): a spike compares Renovate, Dependabot and other agents, and says how their PRs pass `signoff`; the result replaces or confirms the decision "Renovate is the only dependency bot" (2026-09-29)
- [B28 · #163](https://github.com/pascalandy/pascalandy-blog-paper/issues/163), then [B29 · #164](https://github.com/pascalandy/pascalandy-blog-paper/issues/164): ESLint, eslint-plugin-astro and typescript-eslint together, then TypeScript; [B30 · #165](https://github.com/pascalandy/pascalandy-blog-paper/issues/165): Pagefind; [B31 · #166](https://github.com/pascalandy/pascalandy-blog-paper/issues/166): satori, with Pascal's review of the OG images
- [B33 · #167](https://github.com/pascalandy/pascalandy-blog-paper/issues/167): a guard for `compressHTML` and the unified processor; [B24 · #161](https://github.com/pascalandy/pascalandy-blog-paper/issues/161): Pagefind byte differences; [B36 · #168](https://github.com/pascalandy/pascalandy-blog-paper/issues/168): the Prettier cache
- [B23 · #160](https://github.com/pascalandy/pascalandy-blog-paper/issues/160): `persist-credentials: false` in `claude.yml`, with one live `@claude` run by Pascal
- [B18 · #159](https://github.com/pascalandy/pascalandy-blog-paper/issues/159): phone-format QA on the Mac Mini with `agent-browser -p ios`, Xcode and Appium
- Each later brief uses its existing issue (D017)

## Changes since original plan

D017 links the existing issues. D016 records the human inputs. Pascal reviews the social images and triggers the live Claude workflow. The dependency study and local fixtures can run independently of those actions.
