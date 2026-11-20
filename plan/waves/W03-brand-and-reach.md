---
id: W03
project: BLOG
status: proposed
label: wave:W03
skill_version: "2.0.0"
---

# W03: brand-and-reach

## Goal

Every entry point and the brand look finished: `www` links keep their path, the header shows a sharp logo, images have French alt text, and the Star Academy content is public.

## Exit criteria

- [ ] A `www.pascalandy.com` URL with a path and a query answers 301 to the same path and query on `pascalandy.com` (SC11)
- [ ] The header shows the egg-chair logo as an SVG that follows the theme, and Pascal approves it (SC11)
- [ ] Informative images have French alt text, and `just check` fails on a new empty alt that no allowlist names (SC11)

## Scope

- R2: install the latest official Cloudflare CLI, then fix the `www` rule that drops the path (issue filed by E01-T03)
- B14: redraw `logo-chaise-dark-long.png` (600 × 135 px, pixelated) as an SVG with `currentColor`, and put it in the header (issue)
- B26: French alt text for the 194 empty alts in 43 files, an allowlist for decorative images, and a content check (issue, D008)
- B16: the Star Academy content; Pascal gives it, and the planner sets the format when the wave becomes `planned` (issue)
- Each task of this wave takes over the issue that E01-T03 filed, instead of a new issue (D011)
