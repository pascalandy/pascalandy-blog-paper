---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# BACKLOG

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

use graphite in my workflow ?

https://graphite.com

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

mettre à jour l'image header par défault

En ce moment, ça ne fait pas de sens de la conserver puisque mon logo, c'est la chaise avec le mot Pascal Indi écrit. et ensuite de ça on a l'image d'une main en nature et ensuite j'ai un autre texte qui crée le blog de Pascal Indy, l'homme et les relations technologiques. donc je ne veux pas de texte là-dedans Je veux seulement une image qui... on produit une image de marque de mon blog. 

attention à : La génération pas de casque... celle née avant 1990

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Add MCP

https://docs.astro.build/en/guides/build-with-ai/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

So when I build, sometimes I see these warnings. 

What do I need to know ? Should I fix something about it? 

--

Result (57 files): 
- 0 errors
- 0 warnings
- 0 hints

14:55:40 [content] Syncing content
14:55:40 [content] Synced content
14:55:40 [types] Generated 241ms
14:55:40 [build] output: "static"
14:55:40 [build] mode: "static"
14:55:40 [build] directory: /Users/andy16/Documents/github_local/pascalandy-blog-paper/dist/
14:55:40 [build] Collecting build info...
14:55:40 [build] ✓ Completed in 250ms.
14:55:40 [build] Building static entrypoints...
14:55:41 [WARN] [vite] "matchHostname", "matchPathname", "matchPort" and "matchProtocol" are imported from external module "@astrojs/internal-helpers/remote" but never used in "node_modules/astro/dist/assets/utils/remotePattern.js" and "node_modules/astro/dist/assets/services/service.js".
14:55:41 [assets] Copying fonts (12 files)...
14:55:42 [vite] ✓ built in 1.57s
14:55:42 [build] ✓ Completed in 1.60s.



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

SEO stuff

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Sponsorships   Loading
Sponsorships help your community know how to financially support this repository.

Display a "Sponsor" button
Add links to GitHub Sponsors or third-party methods your repository accepts for financial contributions to your project.
