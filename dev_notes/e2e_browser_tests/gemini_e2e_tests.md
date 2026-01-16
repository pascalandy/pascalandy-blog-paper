# Gemini End-to-End Visual Regression Test Plan

**Status:** Draft
**Target App:** PascalAndy Blog Paper (Astro)
**Executor:** AI Agent via `agent-browser` CLI
**Date:** 2026-01-15

## 1. Test Philosophy & Failure Definitions
"Code is frozen thought." Visual bugs are where the CSS logic stopped too soon.

**Definition of "Weird" (Failure Criteria):**
1.  **Horizontal Scroll:** The `<body>` has a horizontal scrollbar on mobile (indicates element overflow).
2.  **Touch Targets:** Clickable elements (links, buttons) are too close (< 8px) or overlapping.
3.  **Zero Padding:** Text touches the exact edge of the viewport.
4.  **Header/Footer Collision:** Fixed elements obscure content at the very top or very bottom of the scroll.
5.  **Contrast:** Text is unreadable against the background (especially in code blocks or tags).
6.  **Layout Shift:** Elements jump significantly during loading.

## 2. Environment Setup
All tests assume the dev server is running locally (e.g., `http://localhost:4321`).

**Standard Viewports:**
- **Mobile:** 375x812 (iPhone X/12/13 Mini style) - *Critical Path for existing bugs*
- **Tablet:** 768x1024 (iPad vertical)
- **Desktop:** 1440x900 (Laptop)

**CLI Usage Reference:**
```bash
# Correct Sequence
agent-browser set viewport 375 812
agent-browser set media dark
agent-browser open "http://localhost:4321"
agent-browser screenshot "evidence/dark-mob-home.png"
```

---

## 3. SUITE A: DARK MODE (Primary)
**Pre-condition:**
1. `agent-browser set media dark`
2. `agent-browser set viewport <W> <H>`

### A.1 Mobile (375x812) - *High Risk Area*

| ID | Page | Action / Step | Inspection Criteria |
| :--- | :--- | :--- | :--- |
| **DM-MOB-NAV-001** | Home | `open "http://localhost:4321"` | 1. Hamburger menu icon is visible.<br>2. Logo/Title is aligned.<br>3. No horizontal scrollbar on the page body. |
| **DM-MOB-NAV-002** | Home | `click ".hamburger-menu"` (Adjust selector) | 1. Menu expands/overlays correctly.<br>2. Links (Posts, Tags, About) have vertical spacing > 16px.<br>3. Close button (X) is visible and functional. |
| **DM-MOB-LAY-003** | Home | `scroll down 500` | 1. "Recent Posts" headers have padding from screen edges.<br>2. Date strings are not wrapped awkwardly.<br>3. Footer socials are centered and not touching the bottom edge. |
| **DM-MOB-PST-004** | Blog Post | `open "http://localhost:4321/blog/some-post"` | 1. H1 title does not touch screen edges.<br>2. **Code Blocks:** Scroll horizontally *within* the block, NOT the body.<br>3. Images fit width (contain) and do not cause body overflow. |
| **DM-MOB-TYP-005** | Blog Post | Inspect Paragraphs & Headers. | 1. Vertical spacing between H2 and previous paragraph is distinct.<br>2. Line height is sufficient for readability.<br>3. Breadcrumbs (if any) do not wrap onto text. |
| **DM-MOB-SRC-006** | Search | `open "http://localhost:4321/search"` -> `type "input" "astro"` | 1. Input field has internal padding.<br>2. Results list appears without overlapping the input field.<br>3. Keyboard (simulated) doesn't obscure results. |
| **DM-MOB-TAG-007** | Tags | `open "http://localhost:4321/tags"` | 1. Tag cloud elements have spacing (gap) between them.<br>2. No single long tag breaks the layout. |

### A.2 Tablet (768x1024)

| ID | Page | Action / Step | Inspection Criteria |
| :--- | :--- | :--- | :--- |
| **DM-TAB-NAV-008** | Home | `set viewport 768 1024` | 1. Check if Hamburger exists OR if standard links appear.<br>2. If links: Check spacing between nav items. |
| **DM-TAB-GRD-009** | Home | Inspect Post List. | 1. Check if list is constrained to a central column or uses grid.<br>2. Margins on left/right should be balanced. |
| **DM-TAB-FTR-010** | Home | `scroll down` | 1. Footer separator line extends correctly.<br>2. "Back to Top" button (if present) does not overlap footer text. |

### A.3 Desktop (1440x900)

| ID | Page | Action / Step | Inspection Criteria |
| :--- | :--- | :--- | :--- |
| **DM-DSK-LAY-011** | Home | `set viewport 1440 900` | 1. Main content container is centered.<br>2. Background color extends to full width.<br>3. No "FOUC" (Flash of Unstyled Content). |
| **DM-DSK-HOV-012** | Blog Post | `hover "a"` | 1. Hover states (color change/underline) trigger correctly.<br>2. Contrast remains accessible on hover. |

---

## 4. SUITE B: LIGHT MODE
**Pre-condition:**
1. `agent-browser set media light`
2. `agent-browser click ".theme-toggle"` (If app requires manual toggle)

### B.1 Mobile (375x812) - *High Risk Area*

| ID | Page | Action / Step | Inspection Criteria |
| :--- | :--- | :--- | :--- |
| **LM-MOB-NAV-013** | Home | `set viewport 375 812` -> `open "http://localhost:4321"` | 1. Background is white/light.<br>2. Text is dark.<br>3. **Crucial:** Hamburger menu icon is visible against light background. |
| **LM-MOB-NAV-014** | Home | `click ".hamburger-menu"` | 1. Menu background is opaque (content behind not bleeding through text).<br>2. Links are legible. |
| **LM-MOB-CNT-015** | Blog Post | Check Code Blocks. | 1. Syntax highlighting contrast is good.<br>2. Background of code block differs slightly from body background. |

### B.2 Desktop (1440x900)

| ID | Page | Action / Step | Inspection Criteria |
| :--- | :--- | :--- | :--- |
| **LM-DSK-GEN-016** | Home | General Browse. | 1. Verify no "Dark Mode artifacts" (e.g., dark borders on light cards).<br>2. Images with transparency (PNGs) look correct on light background. |

---

## 5. Execution Manifest (Copy-Paste for Agent)

Use this sequence to run the investigation.

**Phase 1: Dark Mode Mobile Scan**
1. `agent-browser set media dark`
2. `agent-browser set viewport 375 812`
3. `agent-browser open "http://localhost:4321"`
4. `agent-browser screenshot "evidence/DM-MOB-HOME.png"`
5. *Analyzes screenshot for DM-MOB-NAV-001 & DM-MOB-LAY-003*
6. `agent-browser open "http://localhost:4321/blog/post-name-placeholder"`
7. `agent-browser screenshot "evidence/DM-MOB-POST.png"`
8. *Analyzes screenshot for DM-MOB-PST-004*

**Phase 2: Light Mode Switch**
1. `agent-browser set media light`
2. `agent-browser set viewport 375 812`
3. `agent-browser click ".theme-toggle"`
4. `agent-browser screenshot "evidence/LM-MOB-HOME.png"`
5. *Analyzes screenshot for LM-MOB-NAV-013*
