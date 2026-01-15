---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# BACKLOG

broken links

On this page at the end, you see this link, which is plain. And of course, this is not what I want. I want to have like just an internal click, an internal link, sorry. Sorry. So I want you to find all those, I would say lost link in plain text and replace them with a regular link. 

example sur http://localhost:4321/posts/combien-ca-te-coute-quand-des-machines-cliquent-sur-ta-pub/

/blog/combien-ca-te-coute-quand-des-machines-cliquent-sur-ta-pub/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=


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


Now, I would like to think about all the good utilities that are useful when managing any given project on GitHub. So the next one I have in mind is renovate or dependabot. So I don't know which one I should take. I should use actually. actually, and are there any other utilities that are heavily used on GitHub by OSS maintainers.
So I'm open to your suggestions. We are only planning here.
Good question! Let me research the current landscape of GitHub utilities for OSS maintainers to give you an informed comparison.
⚙ exa_web_search_exa [query=Renovate vs Dependabot comparison 2024 2025 dependency management GitHub, numResults=5]
⚙ exa_web_search_exa [query=essential GitHub tools utilities OSS maintainers 2024 2025, numResults=5]
Based on my research, here's a comprehensive overview for your planning:
Renovate vs Dependabot
| Aspect | Dependabot | Renovate |
|--------|---------------|--------------|
| Setup | Built into GitHub, zero config | Requires app install or self-hosting |
| Platforms | GitHub + Azure DevOps only | GitHub, GitLab, Bitbucket, Gitea, Forgejo |
| Package managers | ~14 | 90+ |
| Grouping updates | Manual groups only | Advanced, community presets available |
| Monorepo support | Limited | Excellent |
| Dependency Dashboard | No | Yes (tracks all updates in one issue) |
| Auto-merge | Basic | Highly configurable |
| Scheduling | daily/weekly/monthly | Fine-grained (cron-like) |
My recommendation: Renovate
For an Astro/TypeScript project, Renovate wins because:

1. Grouped PRs - One PR for all ESLint plugins, one for Astro ecosystem, etc.
2. Dependency Dashboard - Single issue showing all pending updates
3. Better defaults - Community presets like config:recommended handle 90% of cases
4. Automerge for patches - Can auto-merge patch updates that pass CI

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

Other Essential GitHub Utilities for OSS Maintainers
| Tool | Purpose |
|------|---------|
| Codecov / Coveralls | Code coverage reports on PRs |
| semantic-release | Automated versioning + changelog from commits |
| Release Drafter | Auto-draft release notes from PR labels |
| All Contributors | Recognize all contributors (not just code) |
| OSSF Scorecard | Security health metrics for your repo |
| Socket.dev | Supply chain security (detect malicious packages) |
| Stale | Auto-close stale issues/PRs |
| Lock Threads | Lock old resolved issues |
| pr-labeler | Auto-label PRs by file paths |

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
