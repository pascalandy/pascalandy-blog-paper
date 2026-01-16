# Master E2E Visual Test Plan

**Synthesized from**: Gemini, GPT, and Opus strategies
**Target**: PascalAndy Blog (Astro)
**Tool**: `agent-browser` CLI

---

## PART 1: Test Architecture

### 1.1 Failure Criteria (What Counts as a Bug)

| ID | Category | Detection |
|----|----------|-----------|
| F1 | Horizontal overflow | Body scrollbar appears sideways |
| F2 | Touch target too small | Clickable element < 44px visual height |
| F3 | Zero padding | Text touches viewport edge exactly |
| F4 | Content collision | Fixed header/footer obscures content |
| F5 | Contrast failure | Text unreadable against background |
| F6 | Layout shift | Elements jump during load/interaction |
| F7 | Breakpoint mismatch | Menu button visible at desktop widths |
| F8 | Theme artifact | Element color ignores theme change |

### 1.2 Target URLs

| Page | URL | Content Type |
|------|-----|--------------|
| HOME | `http://localhost:4321/` | Cards, hero, nav |
| BLOG_LIST | `http://localhost:4321/blog` | Pagination, cards |
| POST_SIMPLE | `http://localhost:4321/blog/lhorizon-cest-toi` | Standard content |
| POST_CODE | `http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme` | Code blocks, tables |
| POST_MEDIA | `http://localhost:4321/blog/10-stages-of-the-lifecycle-of-a-business` | Images, lists |
| TAGS | `http://localhost:4321/tags` | Tag cloud |
| SEARCH | `http://localhost:4321/search` | Pagefind input |
| 404 | `http://localhost:4321/nonexistent-page-test` | Error state |

### 1.3 Viewport Matrix

| ID | Dimensions | Category | Menu Behavior |
|----|------------|----------|---------------|
| VP01 | 320x568 | Phone XS | Hamburger visible |
| VP02 | 375x667 | Phone S (iPhone SE) | Hamburger visible |
| VP03 | 390x844 | Phone M (iPhone 12-14) | Hamburger visible |
| VP04 | 428x926 | Phone L (iPhone Pro Max) | Hamburger visible |
| VP05 | 568x320 | Phone Landscape | Hamburger visible |
| VP06 | 639x900 | Breakpoint Edge (below) | Hamburger visible |
| VP07 | 640x900 | Breakpoint Edge (at) | Inline nav |
| VP08 | 768x1024 | Tablet Portrait | Inline nav |
| VP09 | 1024x768 | Tablet Landscape | Inline nav |
| VP10 | 1280x720 | Desktop HD | Inline nav |
| VP11 | 1440x900 | Desktop Medium | Inline nav |
| VP12 | 1920x1080 | Desktop Full HD | Inline nav |

### 1.4 Session & Screenshot Config

```bash
# Session name (use throughout)
SESSION="visual-e2e"

# Screenshot directory
SCREENSHOT_DIR="~/Documents/screenshots"

# Post-screenshot resize (prevents crash)
magick mogrify -resize '1920x1920>' -quality 70 <filename>

# Verify latest screenshot
ls -lt ~/Documents/screenshots | head -2
```

---

## PART 2: Test Domains

### Domain A: Navigation & Layout
- Header rendering (logo, menu, theme toggle)
- Menu open/close behavior
- Horizontal overflow detection
- Footer alignment and spacing
- Page transition stability

### Domain B: Content Rendering
- Typography hierarchy (H1-H6, paragraphs)
- Code blocks (no body overflow, readable)
- Tables (contained scroll, not page scroll)
- Images (scale within viewport)
- Lists (proper indentation)
- Blockquotes (styled correctly)

### Domain C: Interactive Elements
- Menu toggle (click, aria-expanded)
- Theme toggle (data-theme attribute)
- Search input (fill, results appear)
- Navigation links (work after page transitions)
- Pagination controls (visible, clickable)

### Domain D: Theme Integrity
- Dark mode colors apply everywhere
- Light mode colors apply everywhere
- No "artifact" colors from opposite theme
- Contrast remains readable in both modes
- Icons visible in both modes

---

## PART 3: Reusable Command Blocks

### BLOCK-INIT: Session Setup
```bash
agent-browser --session $SESSION open http://localhost:4321/
agent-browser --session $SESSION wait 1000
agent-browser --session $SESSION errors --clear
agent-browser --session $SESSION console --clear
```

### BLOCK-THEME: Set Theme Mode
```bash
# For DARK mode
agent-browser --session $SESSION storage local clear
agent-browser --session $SESSION storage local set theme "dark"
agent-browser --session $SESSION set media dark
agent-browser --session $SESSION reload
agent-browser --session $SESSION wait 1000
agent-browser --session $SESSION get attr data-theme html

# For LIGHT mode
agent-browser --session $SESSION storage local clear
agent-browser --session $SESSION storage local set theme "light"
agent-browser --session $SESSION set media light
agent-browser --session $SESSION reload
agent-browser --session $SESSION wait 1000
agent-browser --session $SESSION get attr data-theme html
```

### BLOCK-VP: Set Viewport
```bash
agent-browser --session $SESSION set viewport <W> <H>
agent-browser --session $SESSION wait 200
```

### BLOCK-OVERFLOW: Check Horizontal Overflow
```bash
# Expected output: 0 (or negative)
agent-browser --session $SESSION eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
```

### BLOCK-MENU-MOBILE: Test Mobile Menu
```bash
agent-browser --session $SESSION is visible "#menu-btn"
agent-browser --session $SESSION click "#menu-btn"
agent-browser --session $SESSION wait 300
agent-browser --session $SESSION get attr aria-expanded "#menu-btn"
agent-browser --session $SESSION screenshot $SCREENSHOT_DIR/<ID>-menu-open.png
agent-browser --session $SESSION click "#menu-btn"
agent-browser --session $SESSION wait 300
```

### BLOCK-SCROLL-FOOTER: Scroll to Footer
```bash
agent-browser --session $SESSION scrollintoview "footer"
agent-browser --session $SESSION wait 300
agent-browser --session $SESSION screenshot $SCREENSHOT_DIR/<ID>-footer.png
```

### BLOCK-ERRORS: Collect Errors
```bash
agent-browser --session $SESSION errors
agent-browser --session $SESSION console
```

---

## PART 4: Test Suites

### Suite 1: Mobile Portrait Tests (VP01-VP04)

**Per viewport, test these pages:**
1. HOME: header, menu toggle, content scroll, footer
2. BLOG_LIST: cards, pagination
3. POST_SIMPLE: title, body, bottom
4. TAGS: tag cloud wrap
5. SEARCH: input, results
6. 404: layout check

**Checkpoints per page:**
- Screenshot top (above fold)
- Overflow check
- Menu interaction (if mobile)
- Screenshot mid (scroll down 400-600)
- Screenshot footer (scroll to bottom)

### Suite 2: Phone Landscape + Breakpoint Edge (VP05-VP07)

**Critical tests:**
- VP06 (639px): Hamburger MUST be visible
- VP07 (640px): Hamburger MUST be hidden, inline nav visible
- Landscape: Content doesn't get cramped

### Suite 3: Tablet Tests (VP08-VP09)

**Focus areas:**
- Inline nav spacing
- Content max-width behavior
- Two-column layouts (if any)
- Footer layout changes

### Suite 4: Desktop Tests (VP10-VP12)

**Focus areas:**
- Max-width container working
- Generous side margins
- No stretched content
- Hover states (if applicable)

### Suite 5: Content Stress Tests

**POST_CODE page:**
- Code block at VP01 (narrowest)
- Code block at VP12 (widest)
- Table rendering both viewports
- Syntax highlighting contrast

**POST_MEDIA page:**
- Image scaling at VP01
- Image scaling at VP12
- Nested list indentation
- Caption alignment

---

## PART 5: Execution Patterns

### Pattern A: Full Sequential (Single Agent)
1. Initialize session
2. Dark mode: VP01-VP12, all pages
3. Light mode: VP01-VP12, all pages
4. Content stress tests
5. Error collection
6. Generate report

### Pattern B: Theme-Split Parallel (2 Agents)
- **Agent 1**: Dark mode, all viewports
- **Agent 2**: Light mode, all viewports

### Pattern C: Viewport-Split Parallel (3 Agents)
- **Agent 1**: Mobile (VP01-VP05), both themes
- **Agent 2**: Tablet (VP06-VP09), both themes
- **Agent 3**: Desktop (VP10-VP12) + stress tests, both themes

### Pattern D: Domain-Split Parallel (4 Agents)
- **Agent 1**: Dark mode, mobile (VP01-VP05)
- **Agent 2**: Dark mode, tablet/desktop (VP06-VP12)
- **Agent 3**: Light mode, mobile (VP01-VP05)
- **Agent 4**: Light mode, tablet/desktop (VP06-VP12)

### Pattern E: Maximum Parallel (5 Agents)
- **Agent 1**: Dark mode, mobile phones (VP01-VP04)
- **Agent 2**: Dark mode, tablet + desktop (VP06-VP12)
- **Agent 3**: Light mode, mobile phones (VP01-VP04)
- **Agent 4**: Light mode, tablet + desktop (VP06-VP12)
- **Agent 5**: Breakpoint edges (VP05-VP07) + content stress + errors

---

## PART 6: Defect Report Template

```
DEFECT: <short title>

Test ID: <e.g., DM-VP01-HOME-001>
Theme: dark | light
Viewport: <ID> <WxH>
URL: <page URL>

Repro:
1. <step>
2. <step>

Expected: <what should happen>
Actual: <what happened>

Screenshots:
- ~/Documents/screenshots/<file1>.png

Console/Errors:
<paste from agent-browser errors>
```

---

## PART 7: Summary Template

```
E2E VISUAL TEST REPORT
======================
Date: _______________
Commit: _______________
Agent(s): _______________

DARK MODE RESULTS
-----------------
VP01 (320x568):  PASS | FAIL - Notes: _____
VP02 (375x667):  PASS | FAIL - Notes: _____
VP03 (390x844):  PASS | FAIL - Notes: _____
VP04 (428x926):  PASS | FAIL - Notes: _____
VP05 (568x320):  PASS | FAIL - Notes: _____
VP06 (639x900):  PASS | FAIL - Notes: _____
VP07 (640x900):  PASS | FAIL - Notes: _____
VP08 (768x1024): PASS | FAIL - Notes: _____
VP09 (1024x768): PASS | FAIL - Notes: _____
VP10 (1280x720): PASS | FAIL - Notes: _____
VP11 (1440x900): PASS | FAIL - Notes: _____
VP12 (1920x1080): PASS | FAIL - Notes: _____

LIGHT MODE RESULTS
------------------
<same structure>

CONTENT STRESS RESULTS
----------------------
Code blocks: PASS | FAIL
Tables: PASS | FAIL
Images: PASS | FAIL
Lists: PASS | FAIL

CRITICAL ISSUES
---------------
1.
2.
3.

TOTAL: __ issues found
```
