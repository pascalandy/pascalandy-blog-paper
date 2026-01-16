# Visual Test Plan - E2E Browser Testing

## Overview

This test plan validates visual rendering across resolutions and color modes.
Execute in order. Each test has a unique ID for tracking.

**Prerequisites:**
- Dev server running at `http://localhost:4321/`
- Session name: `visual-test`

---

## SECTION A: Environment Setup

### A-001: Initialize Session
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 2000
```
**Verify:** Page loads without errors.

### A-002: Clear Console Errors
```bash
agent-browser --session visual-test errors --clear
agent-browser --session visual-test console --clear
```

---

## SECTION B: Dark Mode Tests

### B.1: Mobile Portrait (375x667 - iPhone SE)

#### B-101: Set viewport and dark mode
```bash
agent-browser --session visual-test set viewport 375 667
agent-browser --session visual-test set media dark
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-102: Home page - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-102-home-375-dark-top.png
```
**Check:**
- [ ] Header logo visible, not clipped
- [ ] Hamburger menu icon visible (3 lines)
- [ ] No horizontal overflow/scroll
- [ ] Background color is dark theme
- [ ] Text contrast readable

#### B-103: Home page - menu open
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-103-home-375-dark-menu-open.png
```
**Check:**
- [ ] Menu expands below header
- [ ] Menu items visible: /blog, Tags, About, Search, Theme toggle
- [ ] X icon replaces hamburger
- [ ] Menu background contrasts with page
- [ ] Touch targets appear adequate (min 44x44px visual)

#### B-104: Home page - menu close
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-104-home-375-dark-menu-closed.png
```
**Check:**
- [ ] Menu collapses
- [ ] Hamburger icon returns
- [ ] No layout shift

#### B-105: Home page - scroll to content
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-105-home-375-dark-content.png
```
**Check:**
- [ ] Post cards visible
- [ ] Card spacing consistent
- [ ] Text wraps properly, no overflow
- [ ] Dates/meta readable

#### B-106: Home page - scroll to footer
```bash
agent-browser --session visual-test scroll down 2000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-106-home-375-dark-footer.png
```
**Check:**
- [ ] Footer visible
- [ ] Social icons present
- [ ] Copyright text wraps or fits
- [ ] Border above footer visible
- [ ] No content cut off

#### B-107: Blog list page - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-107-blog-375-dark-top.png
```
**Check:**
- [ ] Breadcrumb visible
- [ ] Page title present
- [ ] First cards visible
- [ ] No horizontal overflow

#### B-108: Blog list page - scroll mid
```bash
agent-browser --session visual-test scroll down 600
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-108-blog-375-dark-mid.png
```
**Check:**
- [ ] Spacing between cards consistent
- [ ] Card borders/separators visible
- [ ] Tag pills render correctly

#### B-109: Blog list page - pagination
```bash
agent-browser --session visual-test scroll down 3000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-109-blog-375-dark-pagination.png
```
**Check:**
- [ ] Pagination controls visible
- [ ] Buttons have adequate touch size
- [ ] Current page indicator visible

#### B-110: Blog post detail - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-110-post-375-dark-top.png
```
**Check:**
- [ ] Post title visible, wraps correctly
- [ ] Date/author meta visible
- [ ] Back button present
- [ ] No title overflow

#### B-111: Blog post detail - content body
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-111-post-375-dark-body.png
```
**Check:**
- [ ] Paragraph spacing adequate
- [ ] Headings hierarchy visible (size difference)
- [ ] Line height readable
- [ ] Text margins appropriate (not edge-to-edge)

#### B-112: Blog post detail - mid content
```bash
agent-browser --session visual-test scroll down 800
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-112-post-375-dark-mid.png
```
**Check:**
- [ ] Code blocks render (if present)
- [ ] Block quotes styled (if present)
- [ ] Images don't overflow (if present)
- [ ] Lists properly indented (if present)

#### B-113: Blog post detail - bottom
```bash
agent-browser --session visual-test scroll down 5000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-113-post-375-dark-bottom.png
```
**Check:**
- [ ] Tags section visible
- [ ] Share links present
- [ ] Related posts or nav visible
- [ ] Footer renders correctly

#### B-114: Tags page
```bash
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-114-tags-375-dark.png
```
**Check:**
- [ ] Page title visible
- [ ] Tag pills wrap correctly
- [ ] Spacing between tags consistent
- [ ] Count badges visible

#### B-115: Search page
```bash
agent-browser --session visual-test open http://localhost:4321/search
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-115-search-375-dark.png
```
**Check:**
- [ ] Search input visible
- [ ] Input has proper width (not overflowing)
- [ ] Placeholder text visible

#### B-116: 404 page
```bash
agent-browser --session visual-test open http://localhost:4321/nonexistent-page-test
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-116-404-375-dark.png
```
**Check:**
- [ ] 404 message visible
- [ ] Navigation options present
- [ ] No broken layout

---

### B.2: Mobile Large (390x844 - iPhone 12/13/14)

#### B-201: Set viewport
```bash
agent-browser --session visual-test set viewport 390 844
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-202: Home page - full page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/B-202-home-390-dark-full.png
```
**Check:**
- [ ] Compare to 375: no new issues
- [ ] Slightly more content visible
- [ ] Spacing scales appropriately

#### B-203: Menu interaction
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-203-home-390-dark-menu.png
agent-browser --session visual-test click "#menu-btn"
```
**Check:**
- [ ] Menu renders same as 375
- [ ] No new spacing issues

#### B-204: Blog post - content
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test scroll down 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-204-post-390-dark-content.png
```
**Check:**
- [ ] Content uses additional width well
- [ ] No awkward line breaks

---

### B.3: Tablet Portrait (768x1024 - iPad)

#### B-301: Set viewport
```bash
agent-browser --session visual-test set viewport 768 1024
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-302: Home page - header check
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-302-home-768-dark-header.png
```
**Check:**
- [ ] Header switches to inline nav (no hamburger)
- [ ] Logo and nav on same row
- [ ] Nav items: /blog, Tags icon, About icon, Search icon, Theme toggle
- [ ] Adequate spacing between nav items

#### B-303: Home page - full page
```bash
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/B-303-home-768-dark-full.png
```
**Check:**
- [ ] Content centered properly
- [ ] Cards may be 2-column or full width
- [ ] Spacing scales well

#### B-304: Home page - footer
```bash
agent-browser --session visual-test scroll down 3000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-304-home-768-dark-footer.png
```
**Check:**
- [ ] Footer layout changes (social icons position)
- [ ] Copyright text in single line

#### B-305: Blog post - header
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-305-post-768-dark-header.png
```
**Check:**
- [ ] Table of contents may appear (if enabled)
- [ ] Title has more room
- [ ] Meta info layout

#### B-306: Blog post - content width
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-306-post-768-dark-content.png
```
**Check:**
- [ ] Content max-width appropriate (not too wide)
- [ ] Line length readable (50-80 chars ideal)

#### B-307: Tags page - layout
```bash
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-307-tags-768-dark.png
```
**Check:**
- [ ] Tags flow into multiple columns naturally
- [ ] Centered alignment

---

### B.4: Desktop Small (1024x768)

#### B-401: Set viewport
```bash
agent-browser --session visual-test set viewport 1024 768
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-402: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-402-home-1024-dark.png
```
**Check:**
- [ ] Full desktop nav visible
- [ ] Content width contained
- [ ] No awkward gaps

#### B-403: Blog post - full
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/B-403-post-1024-dark-full.png
```
**Check:**
- [ ] Content centered
- [ ] Sidebar or TOC if applicable

---

### B.5: Desktop HD (1280x720)

#### B-501: Set viewport
```bash
agent-browser --session visual-test set viewport 1280 720
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-502: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-502-home-1280-dark.png
```
**Check:**
- [ ] Max-width container working
- [ ] Comfortable margins on sides

#### B-503: Home page - scroll full
```bash
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/B-503-home-1280-dark-full.png
```
**Check:**
- [ ] Full page renders correctly
- [ ] Consistent spacing throughout

#### B-504: Blog list
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-504-blog-1280-dark.png
```

#### B-505: Blog post
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-505-post-1280-dark.png
```

---

### B.6: Desktop Full HD (1920x1080)

#### B-601: Set viewport
```bash
agent-browser --session visual-test set viewport 1920 1080
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### B-602: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-602-home-1920-dark.png
```
**Check:**
- [ ] Content doesn't stretch too wide
- [ ] Margins on sides are generous
- [ ] Still looks intentional, not sparse

#### B-603: Blog post
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-603-post-1920-dark.png
```
**Check:**
- [ ] Content column max-width maintained
- [ ] Large screens don't break layout

#### B-604: All pages - full captures
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/B-604-blog-1920-dark-full.png
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-604-tags-1920-dark.png
agent-browser --session visual-test open http://localhost:4321/search
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/B-604-search-1920-dark.png
```

---

### B.7: Error Collection

#### B-701: Collect console errors
```bash
agent-browser --session visual-test console
```
**Check:**
- [ ] No JavaScript errors
- [ ] No 404 requests for assets

#### B-702: Collect page errors
```bash
agent-browser --session visual-test errors
```
**Check:**
- [ ] No uncaught exceptions

---

## SECTION C: Light Mode Tests

> **Note:** Duplicate of Section B with `set media light` instead of `set media dark`.
> All test IDs use prefix **C-** instead of **B-**.

### C.1: Mobile Portrait (375x667 - iPhone SE)

#### C-101: Set viewport and light mode
```bash
agent-browser --session visual-test set viewport 375 667
agent-browser --session visual-test set media light
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-102: Home page - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-102-home-375-light-top.png
```
**Check:**
- [ ] Header logo visible, not clipped
- [ ] Hamburger menu icon visible (3 lines)
- [ ] No horizontal overflow/scroll
- [ ] Background color is light theme
- [ ] Text contrast readable

#### C-103: Home page - menu open
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-103-home-375-light-menu-open.png
```
**Check:**
- [ ] Menu expands below header
- [ ] Menu items visible: /blog, Tags, About, Search, Theme toggle
- [ ] X icon replaces hamburger
- [ ] Menu background contrasts with page
- [ ] Touch targets appear adequate

#### C-104: Home page - menu close
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-104-home-375-light-menu-closed.png
```
**Check:**
- [ ] Menu collapses
- [ ] Hamburger icon returns
- [ ] No layout shift

#### C-105: Home page - scroll to content
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-105-home-375-light-content.png
```
**Check:**
- [ ] Post cards visible
- [ ] Card spacing consistent
- [ ] Text wraps properly, no overflow
- [ ] Dates/meta readable

#### C-106: Home page - scroll to footer
```bash
agent-browser --session visual-test scroll down 2000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-106-home-375-light-footer.png
```
**Check:**
- [ ] Footer visible
- [ ] Social icons present
- [ ] Copyright text wraps or fits
- [ ] Border above footer visible

#### C-107: Blog list page - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-107-blog-375-light-top.png
```

#### C-108: Blog list page - scroll mid
```bash
agent-browser --session visual-test scroll down 600
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-108-blog-375-light-mid.png
```

#### C-109: Blog list page - pagination
```bash
agent-browser --session visual-test scroll down 3000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-109-blog-375-light-pagination.png
```

#### C-110: Blog post detail - above fold
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-110-post-375-light-top.png
```

#### C-111: Blog post detail - content body
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-111-post-375-light-body.png
```

#### C-112: Blog post detail - mid content
```bash
agent-browser --session visual-test scroll down 800
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-112-post-375-light-mid.png
```

#### C-113: Blog post detail - bottom
```bash
agent-browser --session visual-test scroll down 5000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-113-post-375-light-bottom.png
```

#### C-114: Tags page
```bash
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-114-tags-375-light.png
```

#### C-115: Search page
```bash
agent-browser --session visual-test open http://localhost:4321/search
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-115-search-375-light.png
```

#### C-116: 404 page
```bash
agent-browser --session visual-test open http://localhost:4321/nonexistent-page-test
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-116-404-375-light.png
```

---

### C.2: Mobile Large (390x844)

#### C-201: Set viewport
```bash
agent-browser --session visual-test set viewport 390 844
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-202: Home page - full page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/C-202-home-390-light-full.png
```

#### C-203: Menu interaction
```bash
agent-browser --session visual-test click "#menu-btn"
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-203-home-390-light-menu.png
agent-browser --session visual-test click "#menu-btn"
```

#### C-204: Blog post - content
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test scroll down 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-204-post-390-light-content.png
```

---

### C.3: Tablet Portrait (768x1024)

#### C-301: Set viewport
```bash
agent-browser --session visual-test set viewport 768 1024
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-302: Home page - header check
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-302-home-768-light-header.png
```

#### C-303: Home page - full page
```bash
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/C-303-home-768-light-full.png
```

#### C-304: Home page - footer
```bash
agent-browser --session visual-test scroll down 3000
agent-browser --session visual-test wait 500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-304-home-768-light-footer.png
```

#### C-305: Blog post - header
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-305-post-768-light-header.png
```

#### C-306: Blog post - content width
```bash
agent-browser --session visual-test scroll down 400
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-306-post-768-light-content.png
```

#### C-307: Tags page - layout
```bash
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-307-tags-768-light.png
```

---

### C.4: Desktop Small (1024x768)

#### C-401: Set viewport
```bash
agent-browser --session visual-test set viewport 1024 768
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-402: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-402-home-1024-light.png
```

#### C-403: Blog post - full
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/C-403-post-1024-light-full.png
```

---

### C.5: Desktop HD (1280x720)

#### C-501: Set viewport
```bash
agent-browser --session visual-test set viewport 1280 720
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-502: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-502-home-1280-light.png
```

#### C-503: Home page - scroll full
```bash
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/C-503-home-1280-light-full.png
```

#### C-504: Blog list
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-504-blog-1280-light.png
```

#### C-505: Blog post
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-505-post-1280-light.png
```

---

### C.6: Desktop Full HD (1920x1080)

#### C-601: Set viewport
```bash
agent-browser --session visual-test set viewport 1920 1080
agent-browser --session visual-test reload
agent-browser --session visual-test wait 1500
```

#### C-602: Home page
```bash
agent-browser --session visual-test open http://localhost:4321/
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-602-home-1920-light.png
```

#### C-603: Blog post
```bash
agent-browser --session visual-test open http://localhost:4321/blog/lhorizon-cest-toi
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-603-post-1920-light.png
```

#### C-604: All pages - full captures
```bash
agent-browser --session visual-test open http://localhost:4321/blog
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot -f ~/Documents/screenshots/C-604-blog-1920-light-full.png
agent-browser --session visual-test open http://localhost:4321/tags
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-604-tags-1920-light.png
agent-browser --session visual-test open http://localhost:4321/search
agent-browser --session visual-test wait 1500
agent-browser --session visual-test screenshot ~/Documents/screenshots/C-604-search-1920-light.png
```

---

### C.7: Error Collection

#### C-701: Collect console errors
```bash
agent-browser --session visual-test console
```

#### C-702: Collect page errors
```bash
agent-browser --session visual-test errors
```

---

## SECTION D: Cleanup

### D-001: Close session
```bash
agent-browser --session visual-test close
```

---

## Appendix: Known Issue Detection

### Mobile-Specific Issues to Watch

| ID | Issue Type | Detection Method |
|----|------------|------------------|
| M1 | Horizontal overflow | Screenshot shows scrollbar or content cut off |
| M2 | Menu not closing | X icon persists after tap |
| M3 | Touch target too small | Visual inspection < 44px height |
| M4 | Text overflow | Words extend past viewport edge |
| M5 | Header overlap | Logo overlaps nav or gets clipped |
| M6 | Footer cut off | Content below viewport edge |
| M7 | Card spacing uneven | Visible gap differences between cards |
| M8 | Font too small | Text appears < 14px equivalent |

### Cross-Viewport Issues

| ID | Issue Type | Detection Method |
|----|------------|------------------|
| V1 | Breakpoint jump | Layout drastically different between adjacent sizes |
| V2 | Nav mode mismatch | Hamburger visible on tablet/desktop |
| V3 | Max-width ignored | Content stretches to viewport edges on wide screens |
| V4 | Orphaned elements | Elements that only appear at certain sizes |

### Theme Issues

| ID | Issue Type | Detection Method |
|----|------------|------------------|
| T1 | Contrast insufficient | Text barely visible against background |
| T2 | Hardcoded color | Element color doesn't change with theme |
| T3 | Icon visibility | Icons disappear or blend into background |
| T4 | Border invisible | Borders disappear in one mode |

---

## Test Execution Summary Template

```
Date: _______________
Executor: _______________
Commit: _______________

DARK MODE
---------
Mobile 375:  [ ] Pass  [ ] Fail - Issues: _____
Mobile 390:  [ ] Pass  [ ] Fail - Issues: _____
Tablet 768:  [ ] Pass  [ ] Fail - Issues: _____
Desktop 1024: [ ] Pass  [ ] Fail - Issues: _____
Desktop 1280: [ ] Pass  [ ] Fail - Issues: _____
Desktop 1920: [ ] Pass  [ ] Fail - Issues: _____

LIGHT MODE
----------
Mobile 375:  [ ] Pass  [ ] Fail - Issues: _____
Mobile 390:  [ ] Pass  [ ] Fail - Issues: _____
Tablet 768:  [ ] Pass  [ ] Fail - Issues: _____
Desktop 1024: [ ] Pass  [ ] Fail - Issues: _____
Desktop 1280: [ ] Pass  [ ] Fail - Issues: _____
Desktop 1920: [ ] Pass  [ ] Fail - Issues: _____

Critical Issues Found:
1.
2.
3.

Screenshots Location: ~/Documents/screenshots/
```
