---
title: "Image Paths in Blog Posts"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "How to reference images from blog posts"
---

## For posts in `src/data/blog/` (root level)

```md
![alt](../../assets/images/og-legacy/2017/11/rsvp-2.jpg)
```

## Why two `../`?

```
src/data/blog/your-post.md
       ↑     ↑
      ..    ..   → src/assets/images/...
```

- First `..` goes from `blog/` to `data/`
- Second `..` goes from `data/` to `src/`
- Then into `assets/images/...`

## Common mistake

Single `../` would be wrong — it would look in `src/data/assets/` which doesn't exist.
