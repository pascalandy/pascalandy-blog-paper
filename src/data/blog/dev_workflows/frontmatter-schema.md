---
title: "Frontmatter Schema"
tags:
  - dev-notes
date_created: 2026-01-11
author: Pascal Andy
description: "Reference for blog post frontmatter fields"
---

# Frontmatter Schema

> Reference for blog post frontmatter fields.

The schema lives in `src/content.config.ts`, and it is strict: an unknown key or an unregistered tag fails the build. After editing frontmatter, run `just check --only content`; a failure names the post, the field, and the fix.

## Required Fields

| Field          | Type       | Format       | Description                                          |
| -------------- | ---------- | ------------ | ---------------------------------------------------- |
| `title`        | `string`   | —            | Post title                                           |
| `tags`         | `string[]` | —            | At least 1 tag; each must be a slug in `src/tags.ts` |
| `date_created` | `date`     | `2026-01-11` | Publication date                                     |
| `author`       | `string`   | —            | Post author, usually `Pascal Andy`                   |
| `description`  | `string`   | —            | SEO meta and post cards (not shown in the body)      |

## Optional Fields

| Field          | Type              | Default | Description                                                                  |
| -------------- | ----------------- | ------- | ---------------------------------------------------------------------------- |
| `featured`     | `boolean`         | —       | Show on the homepage featured section                                        |
| `draft`        | `boolean`         | —       | Exclude the post from every build, dev included: no page, no listing, no RSS |
| `ogImage`      | `image \| string` | —       | Custom OG image (local or URL)                                               |
| `canonicalURL` | `string`          | —       | The original source of duplicated content, so search engines credit it       |
| `hideEditPost` | `boolean`         | —       | Hide the "Edit post" link                                                    |
| `mermaid`      | `boolean`         | `false` | Enable Mermaid diagram rendering                                             |

## Scheduled Posts

A post whose `date_created` is in the future stays out of the home page, the blog roll, the tag pages, and RSS in production until 15 minutes before that date (`SITE.scheduledPostMargin` in `src/config.ts`). Its page is still built at its URL. The dev server lists it right away.

## Examples

### Minimal (5 required fields)

(in this order by default)

```yaml
---
title: "My Post Title"
tags:
  - random
date_created: 2025-01-15
author: Pascal Andy
description: "Brief description for SEO and cards"
---
```

### Full (all fields)

```yaml
---
title: "My Post Title"
tags:
  - technologie
  - dev-notes
date_created: 2025-01-15
author: Pascal Andy
featured: true
draft: false
ogImage: "./custom-og.png"
canonicalURL: "https://original-source.com/post"
hideEditPost: false
mermaid: true
description: "Brief description for SEO and cards"
---
```

## Notes

- **`slug`** is NOT in the schema — derived from filename/path automatically
- **Tags** must be registered first: see [Tag Visibility System](/blog/dev-workflows/tag-visibility-system/)
- **Files prefixed with `_`** are excluded from the collection (e.g., `_draft-post.md`)
- **Subdirectories starting with `_`** are NOT excluded — only filenames matter
- **Subdirectories** affect the URL path, slugified (e.g., `blog/dev_workflows/post.md` -> `/blog/dev-workflows/post/`)
