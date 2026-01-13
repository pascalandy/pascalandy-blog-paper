# Fix Imported Posts (v2)

Importing old posts from a previous Ghost blog. The JSON-to-Markdown conversion introduced glitches that need fixing.

As we work on 9 articles at a time, I want you to spawn 9 agents to:

---

## Workflow

### Step 1: Select Next Post
From `./to_import/`:
- List all `.md` files
- Sort files by filenames.
- Select A to Z
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
- Missing image files (report exact path needed)
- Unusual patterns or edge cases
- Anything that feels off

### Step 5: confirmation

- ask to continue, Return to Step 1
(let the user commit)

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
- **Verify image exists**: Check that referenced images exist in `public/og-legacy/` or `src/assets/images/`
- If image missing: **flag for user review** with the exact path needed

**Bare URLs (not proper links):**
- Detect URLs on their own line without markdown link syntax
- BAD: `/posts/some-article/` (bare path, not clickable)
- GOOD: `[Link text](/posts/some-article/)`
- Auto-fix by wrapping in `[Lire cet article](URL)`

Correct pattern for inline picture:

````md
![image-rsvp](../../assets/images/og-legacy/2017/11/rsvp-2.jpg)
````

**Markdown syntax:**
- Fix malformed `[]()` patterns
- Fix unclosed brackets or parentheses
- Malformed bold markdown weird patterns
- remove any `---` at end of a given post

**Malformed code blocks:**
- Ghost export uses `[code]...[/code]` instead of proper markdown
- BAD:
  ```
  [code]
  bash
  git checkout -b <topic-branch-name>
  [/code]
  ```
- GOOD:
  ````shell
  git checkout -b <topic-branch-name>
  ````
- Auto-fix: Replace `[code]...[/code]` with triple backticks
- Use language hint from first line if present (bash, shell, javascript, etc.)

**Frontmatter url:**
should alway start with: `ogImage: ../../assets/images/og-legacy/`

````md
\*\***
or
  \_\_
````

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

### 4. DO NOT CHANGE

- Post body content (keep original text intact)
- Writing style, tone, formatting
- Valid existing links
- Existing valid metadata

### 5. test the site

`bun run build`

This will discover if a link is broken. Usually it's about pictures. 

---

## Output Format

Five at a time each post, report:

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
