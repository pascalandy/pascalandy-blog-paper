---
title: "Tag Visibility System"
tags:
  - dev-notes
date_created: 2026-01-31
author: Pascal Andy
description: "How tags are shown or hidden on the blog"
---

# Tag Visibility System

> Configuration reference for controlling tag visibility across the blog.

Based on `src/tags.ts`.

## Tag Configuration

Each tag can have two visibility flags:

| Flag                  | Controls                         | Default |
| --------------------- | -------------------------------- | ------- |
| `hiddenFromTagsPage`  | Hide from `/tags/` listing       | `false` |
| `excludeFromBlogRoll` | Hide posts from `/blog/` and RSS | `false` |

## Current Configuration

The registry, `TAGS` in `src/tags.ts`, is the only list of tags and their flags. A post may use only a registered slug: `just check --only content` fails on any other tag and names the registry.

## How It Works

### Tags Page (`/tags/`)

Uses `hiddenFromTagsPage` from tag config:

```typescript
// src/pages/tags/index.astro
let tags = getUniqueTags(posts).filter(
  ({ tag }) => !getTagConfig(tag).hiddenFromTagsPage
);
```

### Blog Roll (`/blog/`) and RSS

Uses `excludeFromBlogRoll` via `getExcludedTags()`:

```typescript
// src/pages/blog/[...page].astro
const excludedTags = getExcludedTags();
const posts = await getCollection(
  "blog",
  ({ data }) =>
    !data.draft && !data.tags.some(tag => excludedTags.includes(tag))
);
```

## Adding a New Tag

Register the tag in `src/tags.ts` before a post uses it. The slug appears in post frontmatter and in the tag's URL, so it must already be in URL form: lowercase words and numbers joined by hyphens (`web-3`, not `web3` or `web_3`). `just check --only content` fails on any other slug and names the rename:

```typescript
export const TAGS: TagConfig[] = [
  {
    slug: "my-tag",
    name: "My Tag",
    description: "Description for the tags page",
    hiddenFromTagsPage: false, // show on /tags/
    excludeFromBlogRoll: false, // show in /blog/ and RSS
  },
  // ...
];
```

## Direct Access

Hidden tags are still accessible via direct URL:

- `/tags/void/` - lists all posts with the void tag
- Individual posts remain accessible via their URLs

## Files

- `src/tags.ts` - Tag configuration
- `src/pages/tags/index.astro` - Tags listing page
- `src/pages/blog/[...page].astro` - Blog roll
- `src/pages/rss.xml.ts` - RSS feed
