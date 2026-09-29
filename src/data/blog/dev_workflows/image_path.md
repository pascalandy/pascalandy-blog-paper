---
title: "Image Paths in Blog Posts"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "How to reference images from blog posts"
---

Images live in `src/assets/images/`; the ones imported from Ghost sit in `src/assets/images/og-legacy/`.

## For posts in `src/data/blog/` (root level)

Most posts use a relative path with two `../`:

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

## For posts in a subfolder

A post in a subfolder, such as `src/data/blog/dev_workflows/`, needs one more `../` per level. The `@/` alias for `src/` works at any depth:

```md
![alt](@/assets/images/mermaid-rendering.png)
```

## Common mistake

A single `../` stops at `src/data/`, which has no `assets` folder. The build then fails with `ImageNotFound` and names the path, so `just check --only build` catches it.
