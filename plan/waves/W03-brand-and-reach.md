---
id: W03
project: BLOG
status: proposed
label: wave:W03
skill_version: "3.1.0"
executor: human
---

# W03: brand-and-reach

## Goal

Every entry point and the brand look finished: `www` links keep their path, the header shows a sharp logo, images have French alt text, and the Star Academy content is public.

## Exit criteria

- [ ] A `www.pascalandy.com` URL with a path and a query answers 301 to the same path and query on `pascalandy.com` (SC11)
- [ ] The header shows the egg-chair logo as an SVG that follows the theme, and Pascal approves it (SC11)
- [ ] Informative images have French alt text, and `just check` fails on a new empty alt that no allowlist names (SC11)
- [ ] The Star Academy content builds, and production serves it after a deploy that Pascal authorizes (SC11)

## Scope

- [R2 · #155](https://github.com/pascalandy/pascalandy-blog-paper/issues/155): install the latest official Cloudflare CLI, then fix the `www` rule that drops the path
- [B14 · #157](https://github.com/pascalandy/pascalandy-blog-paper/issues/157): the header already renders `IconPascalAndy.svg`, a trace of the pixelated `logo-chaise-dark-long.png` (at `f7b76ab`); Pascal approves a redrawn egg chair, or keeps the current SVG
- [B26 · #162](https://github.com/pascalandy/pascalandy-blog-paper/issues/162): French alt text for the 194 empty alts in 43 files, an allowlist for decorative images, and a content check (D008)
- [B16 · #158](https://github.com/pascalandy/pascalandy-blog-paper/issues/158): the Star Academy content; Pascal gives it, and a distinct story gets a Québec French post. A correction to the 2013 reunion story keeps its URL
- A deploy at the end of the wave, on Pascal's go, so that the content and the logo are public
- Each later brief uses its existing issue (D017)

## Changes since original plan

D017 links the existing issues. D016 records the human inputs. Pascal supplies the Star Academy material and reviews the logo. A production rule or publication also needs authorization.
