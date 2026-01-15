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

So as you can see in the CI, I have already a few of them. The next one will be the, I would say, the security part of it. Considering that I'm running an astro site Uh What should I monitor here? I don't want it to be overkill, but I think it deserves to have some coverage here. 

examples I found

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

use graphite in my workflow ?

https://graphite.com

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

faire apparaitre une image header par défault.

attention à : La génération pas de casque... celle née avant 1990

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Add MCP

https://docs.astro.build/en/guides/build-with-ai/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

about: img url

I have a question about the links. what's the correct way of linking to an image because sometimes I see this

```md
![image-rsvp](../../assets/images/og-legacy/2017/11/rsvp-2.jpg)
```

sometimes that:

```md
![image-rsvp](../assets/images/og-legacy/2017/11/rsvp-2.jpg)
```

so ?

plan


=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=


=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

What do I need to know about these warnings? 

11:43:52 watching for file changes...
11:49:36 [WARN] [glob-loader] Duplicate id "linkedin" found in /Users/andy16/Documents/github_local/pascalandy-blog-paper/src/data/blog/linkedin.md. Later items with the same id will overwrite earlier ones.
11:49:36 [glob-loader] Reloaded data from linkedin.md
11:50:22 [WARN] [glob-loader] Duplicate id "linkedin" found in /Users/andy16/Documents/github_local/pascalandy-blog-paper/src/data/blog/linkedin.md. Later items with the same id will overwrite earlier ones.
11:50:22 [glob-loader] Reloaded data from linkedin.md

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
