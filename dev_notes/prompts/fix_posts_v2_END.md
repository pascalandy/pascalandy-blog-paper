# Fix Imported Posts (v2)

Importing old posts from a previous Ghost blog. The JSON-to-Markdown conversion introduced glitches that need fixing.

---

## Workflow

### Step 1: Select Next Post
From `./to_import/`:
- List all `.md` files
- Sort files by filenames.
- Select Z to A
- If no files remain, report "Import complete" and stop

### Step 2: Move File
- Move `mv` selected file to `src/data/blog/`

### Step 3: Fix Issues
Apply fixes per sections below, then report to user.

### Step 4: Approval Gate
**Auto-approve (no confirmation needed):**
- Description improvements (replacing "no_description")
- Basic tag fixes (typos, applying from approved list)
- Image path corrections (`/content/og-legacy/` → `/og-legacy/`)
- Adding `/posts/` prefix to internal links

**Require confirmation:**
- Broken external links (flagged, not auto-removed)
- Unusual patterns or edge cases
- Anything that feels off

### Step 5: Commit & Loop

- ask to continue, Return to Step 1
---

## Fix Categories

### 1. BROKEN LINKS

**External URLs (https://):**
- Test reachability (timeout: 5s)
- If broken (404, 500, timeout): **flag for user review** — do not auto-remove
- Report: URL, status code, line number

**Internal links:**
- Ensure `/posts/` prefix for blog post links
- Verify target exists in:
  - `src/data/blog/` (already imported), OR
  - `./to_import/` (pending import)
- Flag dead internal links for review

**Image paths:**
- `/content/og-legacy/` → `/og-legacy/`

**Markdown syntax:**
- Fix malformed `[]()` patterns
- Fix unclosed brackets or parentheses

### 2. METADATA FIXES

**Description:**
- If `"no_description"` → generate 1 sentence from post content (SEO-friendly, ~150 chars)

**Tags:**
- If `- untagged` → assign from approved list based on content analysis

**Schema compliance:**
Ensure frontmatter matches `src/data/blog/dev_notes/frontmatter-schema.md`:
- Required: `title`, `tags`, `date_created`, `author`, `description`
- Field order: title → tags → date_created → author → description

### 3. APPROVED TAGS

Use these exact values:
- crypto-in-montreal
- technologie
- repost
- crypto
- random
- startups
- emplois
- du-fond-des-tripes
- biographie
- consultation
- personnel
- musique
- deck-cassette
- hifi

New tags allowed if clearly relevant (use `lowercase-kebab-case`).

### 4. import images 

`ogImage:` will be broken

So you must do your due diligence, find the picture within the image to import directory. 
then **copy** the image from the source into the destination 

example:

source: content to import
./to_import/images_to_Import/2021/11/turntable.jpg

destination: actual astro site
ogImage: "../../assets/images/og-legacy/2021/11/turntable.jpg"

be careful about "pascalandy-com_header", there is a lot of duplicates
ogImage: "../../assets/images/og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg"


### 5. DO NOT CHANGE

- Post body content (keep original text intact)
- Writing style, tone, formatting
- Valid existing links
- Existing valid metadata

### 6. test the site

`bun run build`

This will discover if a link is broken. Usually it's about pictures. 

---

## Output Format

For each post, report:

```
## [filename]

**Auto-applied fixes:**
- [fix description] (line X)
- ...

**Flagged for review:**
- [issue description] (line X) — [proposed action]
- ...

Awaiting approval for flagged items...
```

After approval: commit and proceed to next post.
