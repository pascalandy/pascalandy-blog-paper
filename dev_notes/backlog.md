---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# Backlog

This file remains the queue under issue #103's default for R10. Agents pick an `open` ticket whose dependencies are met. `appended` means implemented in an open PR, awaiting review and merge. It does not mean shipped. `needs Pascal` names a decision or action below. The Inbox stays verbatim.

| ID | Status | Ticket | Done when |
| --- | --- | --- | --- |
| B1 | appended | French calendar dates in [#106](https://github.com/pascalandy/pascalandy-blog-paper/pull/106) | `just check --only build` verifies displayed dates against source frontmatter |
| B2 | needs Pascal | Default fr-CA and per-post lang key in [#106](https://github.com/pascalandy/pascalandy-blog-paper/pull/106); English post list waits on R13 | Confirm the English list, then set `lang: en` on those posts; `just check --only build` checks HTML language and locale |
| B3 | appended | Root RSS discovery and robots sitemap in [#105](https://github.com/pascalandy/pascalandy-blog-paper/pull/105) | `just check --only build` follows same-origin link and robots Sitemap targets into dist |
| B4 | appended | Post-only JSON-LD in [#105](https://github.com/pascalandy/pascalandy-blog-paper/pull/105) | `just check --only build` rejects non-post BlogPosting or a missing ISO publication date |
| B5 | appended | Open Graph type and locale in [#106](https://github.com/pascalandy/pascalandy-blog-paper/pull/106) | `just check --only build` requires exactly one correct og:type and og:locale per page |
| B6 | appended | Conditional html class in [#105](https://github.com/pascalandy/pascalandy-blog-paper/pull/105) | `just check --only build` rejects the class token false |
| B7 | needs Pascal | 41 old cryptoinmontreal-NN URLs return 404; pairs come from commit d6b2d99 | R3 chooses redirects; after deployment, curl all 41 pairs and require 301 to their /blog/cim-NN/ pages |
| B8 | needs Pascal | Orphan removal in [#111](https://github.com/pascalandy/pascalandy-blog-paper/pull/111), [#112](https://github.com/pascalandy/pascalandy-blog-paper/pull/112), [#113](https://github.com/pascalandy/pascalandy-blog-paper/pull/113); import exclusion waits on R9 | `just check --only images` rejects missing references and new orphans; R9 asks whether Ghost imports will run again |
| B9 | done | Posts that share a `date_created` have no stable order, so builds can reorder them ([#86](https://github.com/pascalandy/pascalandy-blog-paper/pull/86)) | `getSortedPosts` breaks ties by ascending ID; three fresh builds preserve the same order |
| B10 | needs Pascal | Moving public playbooks to /docs conflicts with the 2026-09-29 decision | R14 asks whether Pascal wants to reverse that decision or close this ticket; default keeps the public routes |
| B11 | appended | SEO findings covered by [#105](https://github.com/pascalandy/pascalandy-blog-paper/pull/105) and [#106](https://github.com/pascalandy/pascalandy-blog-paper/pull/106) | HTML build row verifies metadata and discovery; deployed confirmation waits on R1 |
| B12 | open | Prose links have thin muted underlines; primary color remains | Prose links underline in --primary at rest and on hover; verify-blog captures both themes |
| B13 | needs Pascal | Feature the 5 best posts: 0 are featured; Pascal rereads the shortlist in the Inbox first | 5 posts have `featured: true`; waits on R19 |
| B14 | needs Pascal | Default header image: a brand image with no text | Pascal picks the image, and it replaces the current header; waits on R19 |
| B15 | needs Pascal | "Rester en contact": an email sign-up form | Pascal decides on the form and its copy; waits on R19 |
| B16 | needs Pascal | "star ac est un projet": a post, a page, or a tag? | Pascal chooses the format; waits on R19 |
| B17 | needs Pascal | Graphite (git stacking): evaluate or adopt? | Pascal decides; waits on R19 |
| B18 | needs Pascal | Mobile checks through `agent-browser -p ios`: the verify-blog skill (#70, M4) documents them | The skill's desktop and iOS agent-browser steps run once on the Mac; waits on R19 |
| B22 | open | deploy.py reads a SHA but sends a branch to Sevalla | A fake-provider test proves a later push cannot change the deployed SHA; if Sevalla cannot deploy a SHA, record that limitation and close |
| B23 | open | claude.yml checkout v7 persists the token under RUNNER_TEMP, not .git/config | Set persist-credentials: false and have Pascal trigger one live @claude run, or explain the token requirement in claude.yml |
| B24 | open | Pagefind byte nondeterminism is unproven; parity maps document numbers to URLs | Three fresh builds of identical input have byte-identical dist/pagefind, or link an upstream issue explaining the remaining difference |
| B25 | appended | Deterministic tie order documented in [#108](https://github.com/pascalandy/pascalandy-blog-paper/pull/108) | `just overview --help` and verify-blog post guidance state ascending ID order; the stale-order phrase sweep returns no matches |
| B26 | open | 194 empty-alt images across 43 files, including drafts | Informative images get French alt; decorative images keep empty alt in an allowlist; a content check rejects new unlisted empty alt; ask Pascal about unclear images |
| B27 | appended | Unused back button and storage removed in [#107](https://github.com/pascalandy/pascalandy-blog-paper/pull/107) | The P4 source-symbol sweep returns no matches and its parity receipt explains removal of data attributes and scripts |
| B28 | open | Upgrade ESLint, eslint-plugin-astro, and typescript-eslint together | Drop the redundant @typescript-eslint/parser dependency; `just check` passes with the selected supported versions |
| B29 | open | Upgrade TypeScript after B28 | Choose the newest TypeScript accepted by @astrojs/check; `bun run astro check` reports 0 errors and `just check` passes |
| B30 | open | Upgrade pagefind and @pagefind/default-ui together | The indexed count matches and five fixed queries keep their top results, recorded in the PR; `just check` passes |
| B31 | open | Upgrade satori from 0.18 | Pascal approves before-and-after OG images for three posts and the site card; `just check` passes |
| B32 | needs Pascal | Changing Markdown processors conflicts with the 2026-10-21 decision to keep unified | Pascal decides whether to reopen that decision; otherwise close this ticket |
| B33 | open | No check guards compressHTML or the unified Markdown processor | Removing either setting in a fixture makes `just check` fail with a message naming it |
| B34 | appended | One resolved Vite version guarded in [#109](https://github.com/pascalandy/pascalandy-blog-paper/pull/109); same ticket as #98 | `just check --only lockfile` fails on a lockfile fixture with a second Vite version and names both |
| B35 | appended | Lockfile-keyed CI cache in [#110](https://github.com/pascalandy/pascalandy-blog-paper/pull/110) and fresh comparison guidance in [#109](https://github.com/pascalandy/pascalandy-blog-paper/pull/109) | CI cache key includes bun.lock without broad restore fallback; `just fresh` removes optimized images while preserving fonts and evidence |
| B19 | done | Astro docs MCP server | `.mcp.json` configures `astro-docs` (#70, M3) |
| B20 | done | Sitemap integration | `@astrojs/sitemap` runs in `astro.config.ts` |
| B21 | done | Remove the "Share this post on" block from posts | 0 posts contain it |
| #84 | needs Pascal | Full checks run at push, signoff, and merge | R5 decides whether merge may reuse green signoff on an unchanged SHA; test_merge.py must prove that condition |
| #87 | open | verify-blog has no scroll action | browse.py scrolls a selector into view before capture and a behavior test covers the action |
| #89, #90 | needs Pascal | AVIF parser follow-ups target output the build no longer emits | R8 decides whether to close them as not planned while no AVIF ships; keep the existing parser |
| #92 | open | verify-blog installation can replace hooks in the shared git directory | Install with --ignore-scripts in worktrees; hashes of shared .git/hooks before and after match |
| #94 | open | No invalid-post fixture proves strict schema rejection | A fixture post with an unknown key makes `just check --only content` fail and name the key |
| #97 | open | Tailwind scans the repository beyond src | Constrain scanning to src and run `just parity`; each change is either absent or individually explained |
| #98 | appended | Duplicate of B34, implemented in [#109](https://github.com/pascalandy/pascalandy-blog-paper/pull/109) | The lockfile check rejects two resolved Vite versions |
| #54, #56, #59, #62, #65 | needs Pascal | Release post-mortem records and retired autorelease labels remain | R11 decides which unchecked items deserve tickets before closing records and deleting labels |
| B36 | open | A Prettier content-cache experiment admitted a malformed file when size and mtime stayed unchanged; the uncached command rejected the same file | Keep the formatter uncached until a real CLI test rejects same-size, same-mtime edits with the cache enabled; any future cache also invalidates on plugin lockfile and Tailwind CSS inputs. Reproduction: `/tmp/poteto-blog-phase1/perf/cache-repro.json` |

## Calls awaiting Pascal

No Part 2 decision was answered by the implementation agent. Each row preserves the current state until Pascal decides.

| ID | Finding or question | Done when |
| --- | --- | --- |
| R1 | Production still runs older Astro and banner output | Pascal authorizes and runs a production deploy; curl the deployed generator, RSS discovery, robots sitemap, dates, and OG metadata afterward |
| R2 | www redirects drop path and query | Pascal chooses the host rule change; curl www with a post path and query and require both preserved |
| R3 | Old Ghost and cryptoinmontreal URLs return 404 | Pascal chooses host 301 rules or a repository redirect approach; B7 then verifies the 41 known pairs |
| R4 | om1 system Node shadows mise | Pascal chooses a dotfiles or package change; a non-interactive shell resolves Node satisfying package.json |
| R5 | Merge runs a third full check | Pascal decides whether green signoff on the same SHA may skip that run; #84 then supplies the behavior test |
| R6 | Renovate has no PR history or dashboard | Pascal chooses app installation or removal of config with a superseding decision-log entry; keep the current decision until then |
| R7 | AGENTS.md names Greptile but current reviews are CodeRabbit | Pascal chooses a documented size rule or removal of the reason; this stack keeps the explicit 90-file cap |
| R8 | AVIF follow-ups have no current emitted AVIF | Pascal decides whether #89 and #90 stay open; no parser removal is implied |
| R9 | Five Ghost migration helpers have no caller | Pascal says whether future Ghost imports are needed; delete unused helpers or implement the header exclusion accordingly |
| R10 | Backlog and GitHub are overlapping queues | Pascal chooses one queue; without an answer this file stays canonical, as AGENTS.md requires |
| R11 | Release records and autorelease labels remain | Pascal chooses which #54 and #59 items to keep as tickets before closing the records |
| R12 | Four remote branches are obsolete or hold old proposals | Pascal authorizes any deletions after a git bundle backup; no remote branch was deleted by this program |
| R13 | English posts need explicit lang markers | Propose a list for Pascal to confirm before setting lang: en; the default remains fr-CA |
| R14 | English playbooks are public and indexed by decision | Pascal decides whether to retain that decision and close B10, or explicitly reverse it |
| R15 | Old job ads, sale posts, and CIM events remain public | Pascal chooses any void tagging; preserve existing URLs unless a separate removal is authorized |
| R16 | Four unmounted features were deleted under this program go | The P4 deletion is implemented; Pascal decides separately whether to remove the mounted but disabled EditPost feature |
| R17 | Referenced duplicate image files remain | The plan skips deduplication; keep references unchanged unless Pascal requests a separate effort |
| R18 | Old browser plans include 639 px and 640 px menu cases | Pascal decides which notes to retain; add those widths to verify-blog before deleting the old plans |
| R19 | Editorial and product choices B13 to B18 remain | Pascal chooses featured posts, header artwork, email form, Star ac format, Graphite scope, and a Mac iOS verification run |

## Inbox

Pascal's raw notes, verbatim.

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Liens: soulignement trop épais → amincir + utiliser couleur primaire

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Choisir mes 5 meilleurs posts, les relire, les mettre en avant
- http://localhost:4320/blog/lekt-le-lecteur/
- http://localhost:4320/blog/pourquoi-se-donner-la-peine-decrire/?
- http://localhost:4320/blog/pourquoi-jaime-vous-tutoyer/
- http://localhost:4320/blog/le-multitache-une-legende-urbaine-qui-a-trop-dure/
- http://localhost:4320/blog/comment-reprendre-le-dessus-quand-le-rythme-accelere/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

𝚊𝚐𝚎𝚗𝚝-𝚋𝚛𝚘𝚠𝚜𝚎𝚛 -𝚙 𝚒𝚘𝚜 𝚘𝚙𝚎𝚗

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Sitemap Astro + mini audit SEO
Tu as deux items "sitemap" + "SEO ?". C'est un levier net pour l'indexation. On peut:

Ajouter l'intégration sitemap Astro
Faire un mini‑audit (meta tags, canonical, og/twitter, robots, schema)

Supprimer "Share this post on"
Nettoyage simple et répétitif. Je peux identifier tous les posts concernés et retirer le bloc.

Nettoyage des assets non utilisés
Ça évite d'embarquer du poids mort. On peut lister les assets non référencés et exclure le pattern pascalandy-com_header*.

Header image par défaut
Changement plus "branding". Tu as un besoin clair: image seule, cohérente avec la marque. On peut définir une direction visuelle et produire/choisir l'image.

Mettre en avant 5 meilleurs posts
Impact éditorial fort mais demande ton choix. Je peux préparer une shortlist basée sur tags/engagement si tu veux.

Items à clarifier

"star ac est un projet" → c'est un contenu à écrire, une page à créer, ou un tag à structurer ?
"Graphite (git stacking)" → tu veux évaluer l'outil ou l'adopter dans le workflow ?
"Rester en contact par courriel" → tu veux un nouveau composant form + copy ?
Dis-moi quel lot tu veux attaquer en premier, et si tu veux que j'enchaîne directement avec une implémentation.

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Graphite (git stacking) — graphite.com
https://graphite.com

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Rester en contact 
par courriel : faire une nouvelle forme

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

star ac est un projet

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

mettre à jour l'image header par défault

En ce moment, ça ne fait pas de sens de la conserver puisque mon logo, c'est la chaise avec le mot Pascal Indi écrit. et ensuite de ça on a l'image d'une main en nature et ensuite j'ai un autre texte qui crée le blog de Pascal Indy, l'homme et les relations technologiques. donc je ne veux pas de texte là-dedans Je veux seulement une image qui... on produit une image de marque de mon blog. 

attention à : La génération pas de casque... celle née avant 1990

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Add MCP, maybe ? 
MCP Astro AI — docs.astro.build/en/guides/build-with-ai/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Some posts have a section at the end called : "Share this post on:"
So first identify this post and then delete this part. 

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Double check if there are assets (src/assets) that exists that are not linked to any posts. 

example:
Would copy: dev_to_import/images_to_Import/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg
-> src/assets/images/og-legacy/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg

so exclude the  
do not copy these pics with this pattern "pascalandy-com_header\*"

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

https://docs.astro.build/en/guides/integrations-guide/sitemap/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

SEO — 0o0o quoi exactement? audit? meta tags? schema?

Ajouter sitemap Astro

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

