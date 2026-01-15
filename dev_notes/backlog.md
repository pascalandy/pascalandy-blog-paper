---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# BACKLOG

Now, I would like to think about all the good utilities that are useful when managing any given project on GitHub. 

Here are the three ones I have in mind. 

1)
Renovate

For an Astro/TypeScript project, Renovate wins because:

1. Grouped PRs - One PR for all ESLint plugins, one for Astro ecosystem, etc.
2. Dependency Dashboard - Single issue showing all pending updates
3. Better defaults - Community presets like config:recommended handle 90% of cases
4. Automerge for patches - Can auto-merge patch updates that pass CI

2)
Release Drafter

3)
| pr-labeler | Auto-label PRs by file paths |

Other Essential GitHub Utilities for OSS Maintainers ??

4)
GitHub Secret Scanning

5)

GitHub Actions Optimizations

Caching (actions/cache) │ Cache node_modules, .astro build cache
Parallel jobs           │ Split lint/test/build into separate jobs  
Skip unchanged          │ paths filter to skip CI on docs-only changes
Timeout limits      │ Prevent runaway jobs

6)
Dependency Security

| Tool | Purpose |
|------|---------|
| OSSF Scorecard | Security health metrics for your repo |
| Socket.dev | Supply chain security (detect malicious packages) |
| Stale | Auto-close stale issues/PRs |
| Lock Threads | Lock old resolved issues |
| Codecov / Coveralls | Code coverage reports on PRs |
| All Contributors | Recognize all contributors (not just code) |

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Sponsorships   Loading
Sponsorships help your community know how to financially support this repository.

Display a "Sponsor" button
Add links to GitHub Sponsors or third-party methods your repository accepts for financial contributions to your project.

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

faire apparaitre une image header par défault.

attention à : La génération pas de casque... celle née avant 1990

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Add MCP

https://docs.astro.build/en/guides/build-with-ai/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

correct pattern for inline picture:

```md
![image-rsvp](../../assets/images/og-legacy/2017/11/rsvp-2.jpg)
```

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=


=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Tell me about this warning.

13:43:00 [build] output: "static"
13:43:00 [build] mode: "static"
13:43:00 [build] directory: /Users/andy16/Documents/github_local/pascalandy-blog-paper/dist/
13:43:00 [build] Collecting build info...
13:43:00 [build] ✓ Completed in 211ms.
13:43:00 [build] Building static entrypoints...
13:43:00 [WARN] [vite] "matchHostname", "matchPathname", "matchPort" and "matchProtocol" are imported from external module "@astrojs/internal-helpers/remote" but never used in "node_modules/astro/dist/assets/utils/remotePattern.js" and "node_modules/astro/dist/assets/services/service.js".

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=


=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

shit show about stuff at the end of each posts

Share this post on:

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

example:
Would copy: dev_to_import/images_to_Import/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg
-> src/assets/images/og-legacy/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg

so exclude the  
do not copy these pics with this pattern "pascalandy-com_header\*"

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

broken
ogImage: /og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg

update it to:
ogImage: ../../assets/images/og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Issues:

- 8 S3 images are gone (404 errors) - the S3 bucket g00000017_001 no longer hosts these files:
  - ombre_sur_container_130-1466968864108.JPG
  - Comment_int_grer_IFTTT_dropbox_instagram_blog_006-1462883913445.jpg
  - lancer_une_startup_2014_09_26_22h03-1462844793432.jpg
  - result1-1486228849099.png
  - un_selfie_en_1980b\_\_\_pascal_andy_blog-1462843185197.jpg
  - picture_placeholder-1465435648969.png
  - docker_splash_c-1486227924505.png
  - mobile_24h_pascal_andy-1462898373886.jpg
