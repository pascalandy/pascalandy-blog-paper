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

| Tag                | Hidden from `/tags/` | Excluded from `/blog/` & RSS |
| ------------------ | -------------------- | ---------------------------- |
| void               | Yes                  | Yes                          |
| crypto-in-montreal | Yes                  | Yes                          |
| dev-notes          | No                   | Yes                          |
| biographie         | Yes                  | Yes                          |
| random             | No                   | No                           |

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

Edit `src/tags.ts`:

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
