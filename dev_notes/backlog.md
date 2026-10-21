---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# Backlog

Agents pick the first `open` ticket; each fix ships with its own check. Triage adds or updates a ticket and leaves the Inbox untouched: it keeps Pascal's raw notes verbatim.

| ID | Status | Ticket | Done when |
| --- | --- | --- | --- |
| B1 | open | Post dates render a day early and in English | Dates match `date_created`, in Québec French; a check fails on a shifted or English date |
| B2 | open | `<html lang="en">`, so search indexes the French posts as English | French pages declare `fr-CA`, English posts `en`; a check asserts it |
| B3 | open | The RSS autodiscovery URL and the robots.txt sitemap URL return 404 | Both URLs resolve on the built site; a check follows them |
| B4 | open | Non-post pages emit BlogPosting JSON-LD with `datePublished: "undefined"` | Only posts emit BlogPosting, with a real date; a check validates the JSON-LD |
| B5 | open | No `og:type` or `og:locale` | Posts emit `og:type` `article`, other pages `website`, all with `og:locale`; a check asserts them |
| B6 | open | `<html class="false">` | The attribute is gone; a check asserts it |
| B7 | open | 41 renamed `cim` URLs lack redirects | Each old URL redirects to its new one; a check covers the list |
| B8 | open | 178 of 531 images are unreferenced; skip `pascalandy-com_header*` on import | Each orphan is deleted or kept on purpose; a check fails on a new orphan |
| B9 | done | Posts that share a `date_created` have no stable order, so builds can reorder them ([#86](https://github.com/pascalandy/pascalandy-blog-paper/pull/86)) | `getSortedPosts` breaks ties by ascending ID; three fresh builds preserve the same order |
| B10 | open | Move the playbooks from `src/data/blog/dev_workflows/` to `/docs` | Playbooks live in `/docs`, the docs check and the contract follow, and old URLs redirect or are unpublished |
| B11 | open | SEO audit: meta tags, canonical, og and twitter, robots, schema | Each finding is fixed or ticketed; B2 to B6 cover part of it |
| B12 | half done | Thinner link underline in the primary color: thinner is done, the color is not | Links underline thin, in `--primary` |
| B13 | needs Pascal | Feature the 5 best posts: 0 are featured; Pascal rereads the shortlist in the Inbox first | 5 posts have `featured: true` |
| B14 | needs Pascal | Default header image: a brand image with no text | Pascal picks the image, and it replaces the current header |
| B15 | needs Pascal | "Rester en contact": an email sign-up form | Pascal decides on the form and its copy |
| B16 | needs Pascal | "star ac est un projet": a post, a page, or a tag? | Pascal chooses the format |
| B17 | needs Pascal | Graphite (git stacking): evaluate or adopt? | Pascal decides |
| B18 | needs Pascal | Mobile checks through `agent-browser -p ios`: the verify-blog skill (#70, M4) documents them | The skill's desktop and iOS agent-browser steps run once on the Mac |
| B22 | open | Production deploys `branch: main`, not the commit `check` tested: a push that lands while a check runs can go live under the earlier green result | Production ships only a commit that passed `check`; a probe with two quick pushes shows it |
| B23 | open | The `@claude` workflow's checkout keeps the job token in `.git/config` (`claude.yml`) | A live `@claude` run passes with `persist-credentials: false`, or a comment says why the action needs the token |
| B24 | open | Pagefind assigns different document numbers between fresh builds of identical HTML | Three fresh builds of identical HTML produce byte-identical Pagefind files; logical postings remain unchanged |
| B25 | open | Stale B9 warnings in `.claude/skills/verify-blog/features/post.md` and `scripts/overview.py` still say tied posts can swap order | Both descriptions state that equal `date_created` values sort by ascending ID, without excusing a Previous/Next regression |
| B26 | open | Review the 191 Markdown images with empty `alt` across 42 pages ([#93](https://github.com/pascalandy/pascalandy-blog-paper/pull/93)) | Informative images have useful French alt text; decorative images keep intentional `alt=""`; a content check flags new unreviewed empty alt |
| B27 | open | `SITE.showBackButton` enables `BackButton.astro`, but no page mounts it while pages still store `backUrl` ([#96](https://github.com/pascalandy/pascalandy-blog-paper/pull/96)) | Mount the button where intended and verify its navigation, or remove the unused component, flag, and storage |
| B28 | open | Upgrade ESLint 9 and eslint-plugin-astro 1 to ESLint 10 and eslint-plugin-astro 3 | Lint and `just check` pass with the new majors |
| B29 | open | Upgrade TypeScript 5 to TypeScript 6 | Astro check and `just check` pass with TypeScript 6 |
| B30 | open | Upgrade Pagefind 1.4 to 1.5 | Search results and the Pagefind page count match the prior build; `just check` passes |
| B31 | open | Upgrade satori 0.18 to 0.63 | OG image pixels are reviewed and `just check` passes |
| B32 | open | Evaluate moving Markdown from unified to Astro 7's default Sätteri processor | French punctuation and heading IDs match the current build, or each accepted difference has a parity entry |
| B33 | open | `just check` does not guard `compressHTML: true` or `markdown.processor: unified()` after Astro 7 ([#96](https://github.com/pascalandy/pascalandy-blog-paper/pull/96)) | Removing `compressHTML: true` fails on home closing text or tag emoji spacing; removing `unified()` fails on French punctuation in the eight posts or heading IDs |
| B34 | open | `just check` accepts a lockfile with both Vite 7 and Vite 8 after an Astro bump ([#96](https://github.com/pascalandy/pascalandy-blog-paper/pull/96)) | A check rejects nested Vite copies in `bun.lock` when Astro and Tailwind should share one version; remove the manual `AGENTS.md` gotcha when it lands |
| B35 | open | CI and dependency guidance can reuse `cache/assets/` across a Sharp encoder upgrade ([#96](https://github.com/pascalandy/pascalandy-blog-paper/pull/96)) | CI invalidates optimized images when the dependency lock changes, and the dependency and verify-blog playbooks match the fresh-build cleanup in `AGENTS.md` |
| B19 | done | Astro docs MCP server | `.mcp.json` configures `astro-docs` (#70, M3) |
| B20 | done | Sitemap integration | `@astrojs/sitemap` runs in `astro.config.ts` |
| B21 | done | Remove the "Share this post on" block from posts | 0 posts contain it |

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

