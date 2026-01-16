# GPT E2E Visual Test Plan (agent-browser)

Goal: catch responsive + theme (dark/light) visual defects, with extra coverage on mobile where issues are known to exist.

---

## Assumptions (state these before running)

- The dev server is already running and reachable at `http://localhost:4321/`.
- `agent-browser` is installed and can launch Chromium in this environment.
- Max viewport is `1920x1920`.
- Screenshots are saved to `~/Documents/screenshots/`.
- This repo’s selectors exist:
  - Menu toggle: `#menu-btn` (mobile only, hidden at `>=640px`)
  - Theme toggle: `#theme-btn`
  - Search input: `.pagefind-ui__search-input`

If any assumption fails, stop and record it as a blocker before continuing.

---

## Output artifacts (what to collect)

- Screenshots: `~/Documents/screenshots/<TEST_ID>__<mode>__<vp>__<page>__<checkpoint>.png`
- Console + page errors: `agent-browser console` and `agent-browser errors`
- Optional: a short defect log using the template at the end of this doc

After each screenshot, downscale (prevents oversized artifacts):
```bash
magick mogrify -resize '1920x1920>' -quality 70 ~/Documents/screenshots/<filename>.png
```

To confirm the last screenshot was written:
```bash
ls -lt ~/Documents/screenshots | head -2
```

---

## Pages under test (fixed URLs)

- HOME: `http://localhost:4321/`
- BLOG LIST: `http://localhost:4321/blog`
- TAGS: `http://localhost:4321/tags`
- SEARCH: `http://localhost:4321/search`
- ABOUT: `http://localhost:4321/about`
- POST (short): `http://localhost:4321/blog/lhorizon-cest-toi`
- POST (media + lists + image): `http://localhost:4321/blog/10-stages-of-the-lifecycle-of-a-business`
- POST (code + tables): `http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme`
- 404 (intentional): `http://localhost:4321/nonexistent-page-test`

---

## Viewport matrix (run all)

| VP ID | WxH | Label |
| --- | --- | --- |
| VP01 | 320x568 | phone XS portrait |
| VP02 | 360x740 | phone S portrait |
| VP03 | 375x667 | phone M portrait |
| VP04 | 390x844 | phone L portrait |
| VP05 | 428x926 | phone XL portrait |
| VP06 | 568x320 | phone XS landscape |
| VP07 | 844x390 | phone L landscape |
| VP08 | 639x900 | breakpoint edge `<640` (menu button should exist) |
| VP09 | 640x900 | breakpoint edge `>=640` (menu button should be hidden) |
| VP10 | 768x1024 | tablet portrait |
| VP11 | 1024x768 | tablet landscape |
| VP12 | 1280x720 | desktop small |
| VP13 | 1440x900 | desktop medium |
| VP14 | 1920x1080 | desktop large |

---

## Global visual checks (apply on every page)

### A. Header + menu (every viewport)

- Logo and menu do not overlap or clip.
- Menu button (`#menu-btn`) behavior:
  - At widths `<640`: visible, toggles open/close, icons swap, `aria-expanded` toggles.
  - At widths `>=640`: hidden, inline nav is visible and spaced, no wrapping collisions.
- Menu items are reachable and visually stable after navigation (page transitions must not break the menu).
- Theme icon looks correct for the current mode (dark should not show “dark” colors on light mode and vice versa).
- No layout shift/jump when opening/closing the menu.

### B. Layout + spacing (scroll top → bottom)

- Consistent vertical rhythm: headings, paragraphs, lists, images, and code blocks have sensible spacing.
- No sections look “stuck together” or “too far apart”.
- No unexpected horizontal scrolling (body should not scroll sideways).
- Footer is visible, aligned, and not cramped or floating with odd whitespace.

### C. Content “stress” elements (blog posts)

- Images: scale to viewport, never overflow, captions do not wrap awkwardly.
- Code blocks: readable, do not force body horizontal scroll, padding and contrast look correct in the current mode.
- Tables: do not break layout; if they overflow, they should scroll inside their own container (not the whole page).

### D. Errors (fast signal)

- `agent-browser errors` shows no uncaught errors.
- `agent-browser console` shows no obvious runtime errors (warnings are allowed but should be reviewed).

---

## One-time CLI setup

Pick one session name and keep it for the whole run:
```bash
agent-browser session
```

This plan assumes: `--session visual-gpt`

Optional install step (only if Chromium is missing):
```bash
agent-browser install
```

---

## Reusable command blocks

### BLOCK-0: Reset + set theme (use at start of each test)

Replace `<THEME>` with `dark` or `light`.
```bash
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 500
agent-browser --session visual-gpt cookies clear
agent-browser --session visual-gpt storage local clear
agent-browser --session visual-gpt storage session clear
agent-browser --session visual-gpt storage local set theme "<THEME>"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt get attr data-theme html
agent-browser --session visual-gpt errors --clear
agent-browser --session visual-gpt console --clear
```

### BLOCK-1: Viewport set

Replace `<W> <H>`.
```bash
agent-browser --session visual-gpt set viewport <W> <H>
agent-browser --session visual-gpt wait 200
```

### BLOCK-2: Horizontal overflow check (body should not scroll sideways)

Expected output: `0` (or a non-positive number).
```bash
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
```

### BLOCK-3: Menu toggle check (mobile only)

Run this only if `#menu-btn` is visible.
```bash
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200
agent-browser --session visual-gpt get attr aria-expanded "#menu-btn"
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200
agent-browser --session visual-gpt get attr aria-expanded "#menu-btn"
```

### BLOCK-4: Scroll to footer checkpoint

```bash
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
```

---

## Dark mode run (primary)

Mode under test: `dark`

### Dark mode preflight

#### VT-DM-0001: Session boots and theme applies
```bash
# BLOCK-0 with <THEME>=dark
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 500
agent-browser --session visual-gpt cookies clear
agent-browser --session visual-gpt storage local clear
agent-browser --session visual-gpt storage session clear
agent-browser --session visual-gpt storage local set theme "dark"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt get attr data-theme html
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-0001__dark__preflight__home__top.png
```
Check:
- [ ] `data-theme` is `dark`
- [ ] No flash of incorrect theme
- [ ] Screenshot shows dark background and readable text

---

## Dark mode per-viewport tests

For each viewport VP01–VP14, run the 3 test cases below.

ID convention (unique per run):
- `VT-DM-<VPID>-01` = menu + home + blog list
- `VT-DM-<VPID>-02` = post (code + table) sweep
- `VT-DM-<VPID>-03` = tags + search

Example: `VT-DM-VP01-01` (dark, viewport VP01, test case 01)

### Run checklist (dark mode)

| VP | WxH | Expect `#menu-btn` | Run IDs |
| --- | --- | --- | --- |
| VP01 | 320x568 | visible | `VT-DM-VP01-01`, `VT-DM-VP01-02`, `VT-DM-VP01-03`, `VT-DM-VP01-04` |
| VP02 | 360x740 | visible | `VT-DM-VP02-01`, `VT-DM-VP02-02`, `VT-DM-VP02-03`, `VT-DM-VP02-04` |
| VP03 | 375x667 | visible | `VT-DM-VP03-01`, `VT-DM-VP03-02`, `VT-DM-VP03-03`, `VT-DM-VP03-04` |
| VP04 | 390x844 | visible | `VT-DM-VP04-01`, `VT-DM-VP04-02`, `VT-DM-VP04-03`, `VT-DM-VP04-04` |
| VP05 | 428x926 | visible | `VT-DM-VP05-01`, `VT-DM-VP05-02`, `VT-DM-VP05-03`, `VT-DM-VP05-04` |
| VP06 | 568x320 | visible | `VT-DM-VP06-01`, `VT-DM-VP06-02`, `VT-DM-VP06-03`, `VT-DM-VP06-04` |
| VP07 | 844x390 | visible | `VT-DM-VP07-01`, `VT-DM-VP07-02`, `VT-DM-VP07-03`, `VT-DM-VP07-04` |
| VP08 | 639x900 | visible | `VT-DM-VP08-01`, `VT-DM-VP08-02`, `VT-DM-VP08-03` |
| VP09 | 640x900 | hidden | `VT-DM-VP09-01`, `VT-DM-VP09-02`, `VT-DM-VP09-03` |
| VP10 | 768x1024 | hidden | `VT-DM-VP10-01`, `VT-DM-VP10-02`, `VT-DM-VP10-03` |
| VP11 | 1024x768 | hidden | `VT-DM-VP11-01`, `VT-DM-VP11-02`, `VT-DM-VP11-03` |
| VP12 | 1280x720 | hidden | `VT-DM-VP12-01`, `VT-DM-VP12-02`, `VT-DM-VP12-03` |
| VP13 | 1440x900 | hidden | `VT-DM-VP13-01`, `VT-DM-VP13-02`, `VT-DM-VP13-03` |
| VP14 | 1920x1080 | hidden | `VT-DM-VP14-01`, `VT-DM-VP14-02`, `VT-DM-VP14-03` |

Additional one-offs:
- 404 at VP01: `VT-DM-VP01-05`
- 404 at VP14: `VT-DM-VP14-05`

### TEST CASE 1 (menu + home + blog list)

#### VT-DM-VP01-01: VP01 home + menu + blog list
Viewport: VP01 `320x568`
```bash
# BLOCK-1 (viewport)
agent-browser --session visual-gpt set viewport 320 568
agent-browser --session visual-gpt wait 200

# BLOCK-0 (reset + dark)
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 500
agent-browser --session visual-gpt cookies clear
agent-browser --session visual-gpt storage local clear
agent-browser --session visual-gpt storage session clear
agent-browser --session visual-gpt storage local set theme "dark"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt get attr data-theme html
agent-browser --session visual-gpt errors --clear
agent-browser --session visual-gpt console --clear

# Home (header/menu closed)
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 800
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__home__top.png

# Menu toggle (mobile expected)
agent-browser --session visual-gpt is visible "#menu-btn"
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__home__menu-open.png
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__home__menu-closed.png

# Overflow check (home)
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"

# Navigate to blog list using the header nav
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 150
agent-browser --session visual-gpt click "a[href='/blog']"
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__blog__top.png

# Verify menu still works after navigation
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__blog__menu-open.png
agent-browser --session visual-gpt click "#menu-btn"
agent-browser --session visual-gpt wait 200

# Overflow check (blog list)
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"

# Footer checkpoint
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__blog__footer.png

# Return to home and verify mid-content + footer spacing
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 800
agent-browser --session visual-gpt scroll down 700
agent-browser --session visual-gpt wait 250
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__home__content.png
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-01__dark__VP01__home__footer.png
```
Check:
- [ ] Header: no overlap, logo not clipped
- [ ] Menu opens/closes, icons swap, content does not jump
- [ ] Menu works after navigation to `/blog`
- [ ] Blog list cards do not overflow, spacing between cards looks intentional
- [ ] Home mid-content spacing looks intentional (cards, headings)
- [ ] Footer layout is clean, no odd whitespace

Run this exact test for VP02–VP08 by copy/pasting the block and changing:
- `set viewport ...`
- `VT-DM-VP01-01` → `VT-DM-VP02-01` (and the `VPxx` in filenames)

For VP09–VP14, the menu button should be hidden and nav should be inline. Use this block instead:
```bash
# Desktop/tablet branch (menu is inline; no hamburger)
agent-browser --session visual-gpt is visible "#menu-btn"
agent-browser --session visual-gpt is visible "#menu-items"
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP09-01__dark__VP09__home__top.png
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
agent-browser --session visual-gpt click "a[href='/blog']"
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP09-01__dark__VP09__blog__top.png
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP09-01__dark__VP09__blog__footer.png

agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 800
agent-browser --session visual-gpt scroll down 700
agent-browser --session visual-gpt wait 250
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP09-01__dark__VP09__home__content.png
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP09-01__dark__VP09__home__footer.png
```
Desktop/tablet check:
- [ ] Inline nav is visible, spaced, and does not wrap awkwardly
- [ ] Theme toggle is visible and aligned

### TEST CASE 2 (post with code + tables)

#### VT-DM-VP01-02: VP01 post rich sweep
Viewport: VP01 `320x568`
```bash
# BLOCK-1 (viewport)
agent-browser --session visual-gpt set viewport 320 568
agent-browser --session visual-gpt wait 200

# BLOCK-0 (reset + dark)
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 500
agent-browser --session visual-gpt cookies clear
agent-browser --session visual-gpt storage local clear
agent-browser --session visual-gpt storage session clear
agent-browser --session visual-gpt storage local set theme "dark"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt get attr data-theme html
agent-browser --session visual-gpt errors --clear
agent-browser --session visual-gpt console --clear

# Open “code + tables” post
agent-browser --session visual-gpt open http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme
agent-browser --session visual-gpt wait 1200
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-02__dark__VP01__post-rich__top.png

# Spacing checkpoint (first paragraphs)
agent-browser --session visual-gpt scroll down 450
agent-browser --session visual-gpt wait 250
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-02__dark__VP01__post-rich__body-1.png

# Overflow check
agent-browser --session visual-gpt eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"

# Code block checkpoint
agent-browser --session visual-gpt scrollintoview "pre"
agent-browser --session visual-gpt wait 250
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-02__dark__VP01__post-rich__code.png

# Table checkpoint
agent-browser --session visual-gpt scrollintoview "table"
agent-browser --session visual-gpt wait 250
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-02__dark__VP01__post-rich__table.png

# Footer checkpoint
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-02__dark__VP01__post-rich__footer.png
```
Check:
- [ ] Title/meta spacing looks intentional (no crowding)
- [ ] Heading-to-paragraph spacing is consistent and readable
- [ ] No body horizontal overflow (JS check is `0`)
- [ ] Code block is readable and does not break layout
- [ ] Table stays within layout (or scrolls locally), does not push the page sideways
- [ ] Footer sits at the bottom cleanly

Repeat this test case for VP02–VP14 by copy/pasting and changing:
- `set viewport ...`
- `VT-DM-VP01-02` → `VT-DM-VPxx-02` (and the `VPxx` in filenames)

### TEST CASE 3 (tags + search)

#### VT-DM-VP01-03: VP01 tags + search
Viewport: VP01 `320x568`
```bash
# BLOCK-1 (viewport)
agent-browser --session visual-gpt set viewport 320 568
agent-browser --session visual-gpt wait 200

# BLOCK-0 (reset + dark)
agent-browser --session visual-gpt open http://localhost:4321/
agent-browser --session visual-gpt wait 500
agent-browser --session visual-gpt cookies clear
agent-browser --session visual-gpt storage local clear
agent-browser --session visual-gpt storage session clear
agent-browser --session visual-gpt storage local set theme "dark"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 1000
agent-browser --session visual-gpt get attr data-theme html
agent-browser --session visual-gpt errors --clear
agent-browser --session visual-gpt console --clear

# Tags
agent-browser --session visual-gpt open http://localhost:4321/tags
agent-browser --session visual-gpt wait 900
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-03__dark__VP01__tags__top.png
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-03__dark__VP01__tags__footer.png

# Search (wait for the Pagefind input)
agent-browser --session visual-gpt open http://localhost:4321/search
agent-browser --session visual-gpt wait ".pagefind-ui__search-input"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-03__dark__VP01__search__empty.png
agent-browser --session visual-gpt fill ".pagefind-ui__search-input" "theme"
agent-browser --session visual-gpt wait 800
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-VP01-03__dark__VP01__search__results.png

# Errors
agent-browser --session visual-gpt errors
agent-browser --session visual-gpt console
```
Check:
- [ ] Tags wrap cleanly, no collisions, no clipping
- [ ] Search input is aligned and does not overflow at the current width
- [ ] Search results list spacing is consistent (titles/excerpts)
- [ ] No obvious runtime errors in `errors`/`console`

Repeat this test case for VP02–VP14 by copy/pasting and changing:
- `set viewport ...`
- `VT-DM-VP01-03` → `VT-DM-VPxx-03` (and the `VPxx` in filenames)

---

## Dark mode mobile “media post” add-on (extra mobile coverage)

Run this only for VP01–VP07 (phone viewports).

#### VT-DM-VPxx-04: Media post (lists + image) checks
```bash
agent-browser --session visual-gpt open http://localhost:4321/blog/10-stages-of-the-lifecycle-of-a-business
agent-browser --session visual-gpt wait 1200
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-<VPID>-04__dark__<VPID>__post-media__top.png

agent-browser --session visual-gpt scrollintoview "img"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-<VPID>-04__dark__<VPID>__post-media__image.png

agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-<VPID>-04__dark__<VPID>__post-media__footer.png
```
Mobile check:
- [ ] Image never overflows the viewport
- [ ] Nested lists indent correctly and do not cause sideways scrolling
- [ ] Headings do not collide with list items

---

## Dark mode single-run sanity (404)

Run once at VP01 and once at VP14.

#### VT-DM-<VPID>-05: 404 page layout
```bash
agent-browser --session visual-gpt open http://localhost:4321/nonexistent-page-test
agent-browser --session visual-gpt wait 900
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-<VPID>-05__dark__<VPID>__404__top.png
agent-browser --session visual-gpt scrollintoview "footer"
agent-browser --session visual-gpt wait 300
agent-browser --session visual-gpt screenshot ~/Documents/screenshots/VT-DM-<VPID>-05__dark__<VPID>__404__footer.png
```
Check:
- [ ] 404 message is readable and positioned correctly
- [ ] Header/footer still look normal

---

## Light mode run (copy of dark mode)

Mode under test: `light`

Execute the exact same test cases as dark mode, with only these changes:

1. In `BLOCK-0`, set: `storage local set theme "light"`
2. Rename test IDs and filenames:
   - `VT-DM-...` → `VT-LM-...`
   - `__dark__` → `__light__`

If you want a quick proof that theme switched:
```bash
agent-browser --session visual-gpt storage local set theme "light"
agent-browser --session visual-gpt reload
agent-browser --session visual-gpt wait 800
agent-browser --session visual-gpt get attr data-theme html
```

### Run checklist (light mode)

Same as dark mode, with `VT-LM-...` IDs:

| VP | WxH | Expect `#menu-btn` | Run IDs |
| --- | --- | --- | --- |
| VP01 | 320x568 | visible | `VT-LM-VP01-01`, `VT-LM-VP01-02`, `VT-LM-VP01-03`, `VT-LM-VP01-04` |
| VP02 | 360x740 | visible | `VT-LM-VP02-01`, `VT-LM-VP02-02`, `VT-LM-VP02-03`, `VT-LM-VP02-04` |
| VP03 | 375x667 | visible | `VT-LM-VP03-01`, `VT-LM-VP03-02`, `VT-LM-VP03-03`, `VT-LM-VP03-04` |
| VP04 | 390x844 | visible | `VT-LM-VP04-01`, `VT-LM-VP04-02`, `VT-LM-VP04-03`, `VT-LM-VP04-04` |
| VP05 | 428x926 | visible | `VT-LM-VP05-01`, `VT-LM-VP05-02`, `VT-LM-VP05-03`, `VT-LM-VP05-04` |
| VP06 | 568x320 | visible | `VT-LM-VP06-01`, `VT-LM-VP06-02`, `VT-LM-VP06-03`, `VT-LM-VP06-04` |
| VP07 | 844x390 | visible | `VT-LM-VP07-01`, `VT-LM-VP07-02`, `VT-LM-VP07-03`, `VT-LM-VP07-04` |
| VP08 | 639x900 | visible | `VT-LM-VP08-01`, `VT-LM-VP08-02`, `VT-LM-VP08-03` |
| VP09 | 640x900 | hidden | `VT-LM-VP09-01`, `VT-LM-VP09-02`, `VT-LM-VP09-03` |
| VP10 | 768x1024 | hidden | `VT-LM-VP10-01`, `VT-LM-VP10-02`, `VT-LM-VP10-03` |
| VP11 | 1024x768 | hidden | `VT-LM-VP11-01`, `VT-LM-VP11-02`, `VT-LM-VP11-03` |
| VP12 | 1280x720 | hidden | `VT-LM-VP12-01`, `VT-LM-VP12-02`, `VT-LM-VP12-03` |
| VP13 | 1440x900 | hidden | `VT-LM-VP13-01`, `VT-LM-VP13-02`, `VT-LM-VP13-03` |
| VP14 | 1920x1080 | hidden | `VT-LM-VP14-01`, `VT-LM-VP14-02`, `VT-LM-VP14-03` |

Additional one-offs:
- 404 at VP01: `VT-LM-VP01-05`
- 404 at VP14: `VT-LM-VP14-05`

---

## Defect report template (copy/paste)

```
Defect title:

Test ID:
Mode: dark|light
Viewport: VPxx WxH
URL:

Repro steps (minimal):
Expected:
Actual:

Screenshots:
- ~/Documents/screenshots/<file1>.png
- ~/Documents/screenshots/<file2>.png

Console/errors:
- (paste relevant lines from `agent-browser errors` / `agent-browser console`)
```
