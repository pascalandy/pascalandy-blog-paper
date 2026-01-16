# E2E Testing Prompts

Copy-paste prompts for AI coding assistants to execute visual regression tests.

---

## OPTION 1: Single AI Assistant (Orchestrator)

Use this when you want ONE AI assistant to manage the entire test run, optionally delegating to subagents.

### Prompt 1A: Full Test Run (Sequential)

```
Execute a comprehensive E2E visual regression test on my Astro blog.

PREREQUISITES:
- Dev server is running at http://localhost:4321/
- Use agent-browser CLI for all browser interactions
- Save screenshots to ~/Documents/screenshots/
- After each screenshot: magick mogrify -resize '1920x1920>' -quality 70 <filename>

TEST SCOPE:
1. Dark mode testing across all viewports
2. Light mode testing across all viewports
3. Content stress testing (code blocks, tables, images)

VIEWPORTS TO TEST (in order):
- 320x568 (phone XS)
- 375x667 (phone S)
- 390x844 (phone M)
- 428x926 (phone L)
- 568x320 (phone landscape)
- 639x900 (breakpoint edge - menu MUST be visible)
- 640x900 (breakpoint edge - menu MUST be hidden)
- 768x1024 (tablet portrait)
- 1024x768 (tablet landscape)
- 1280x720 (desktop HD)
- 1440x900 (desktop medium)
- 1920x1080 (desktop full HD)

PAGES TO TEST:
- http://localhost:4321/ (home)
- http://localhost:4321/blog (blog list)
- http://localhost:4321/blog/lhorizon-cest-toi (simple post)
- http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme (code post)
- http://localhost:4321/tags (tags page)
- http://localhost:4321/search (search page)
- http://localhost:4321/nonexistent-page-test (404)

PER PAGE CHECKS:
- Take screenshot of top (above fold)
- Check for horizontal overflow: eval "document.documentElement.scrollWidth - document.documentElement.clientWidth" (should be 0)
- Test menu toggle on mobile viewports (click #menu-btn, verify aria-expanded)
- Scroll to footer and screenshot
- Check for: text contrast, touch targets, no content collision

FAILURE CRITERIA:
- Horizontal scrollbar on body
- Menu button visible above 640px width
- Menu button hidden below 640px width
- Text touching viewport edge
- Unreadable contrast
- Elements overlapping

OUTPUT:
- All screenshots organized by theme/viewport/page
- List of any defects found with: test ID, viewport, URL, description, screenshot path
- Summary: PASS/FAIL per viewport per theme
```

### Prompt 1B: Full Test Run (With Subagents)

```
Execute a comprehensive E2E visual regression test using parallel subagents.

PREREQUISITES:
- Dev server running at http://localhost:4321/
- Use agent-browser CLI
- Screenshots to ~/Documents/screenshots/
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

ORCHESTRATION:
Launch 3 subagents in parallel:

SUBAGENT 1 - Dark Mode Testing:
- Set theme to dark (storage local set theme "dark", set media dark)
- Test ALL 12 viewports (320x568 through 1920x1080)
- Test all 7 pages per viewport
- Report defects and screenshots

SUBAGENT 2 - Light Mode Testing:
- Set theme to light (storage local set theme "light", set media light)
- Test ALL 12 viewports
- Test all 7 pages per viewport
- Report defects and screenshots

SUBAGENT 3 - Content Stress Testing:
- Test code-heavy post at smallest (320x568) and largest (1920x1080) viewport, both themes
- Test media-heavy post same viewports, both themes
- Test breakpoint edges specifically (639 vs 640 width)
- Collect console errors and page errors at the end

VIEWPORTS:
320x568, 375x667, 390x844, 428x926, 568x320, 639x900, 640x900, 768x1024, 1024x768, 1280x720, 1440x900, 1920x1080

PAGES:
http://localhost:4321/
http://localhost:4321/blog
http://localhost:4321/blog/lhorizon-cest-toi
http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme
http://localhost:4321/tags
http://localhost:4321/search
http://localhost:4321/nonexistent-page-test

After all subagents complete, compile results into a unified report showing:
- PASS/FAIL per viewport per theme
- All defects with screenshots
- Content stress test results
- Any console errors
```

---

## OPTION 2: Parallel AI Assistants (3-Agent Split)

Launch these 3 prompts in 3 separate AI coding assistant sessions simultaneously.

### Agent 1 of 3: Dark Mode Complete

```
E2E Visual Test - DARK MODE (Agent 1 of 3)

You are testing DARK MODE ONLY. Other agents handle light mode.

SETUP:
- Dev server: http://localhost:4321/
- Tool: agent-browser CLI
- Session name: visual-dark
- Screenshots: ~/Documents/screenshots/DM-*
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME SETUP (run at start and after each viewport change):
agent-browser --session visual-dark storage local set theme "dark"
agent-browser --session visual-dark set media dark
agent-browser --session visual-dark reload
agent-browser --session visual-dark wait 1000

VIEWPORTS (test in order):
1. 320x568 - phone XS
2. 375x667 - phone S
3. 390x844 - phone M
4. 428x926 - phone L
5. 568x320 - phone landscape
6. 639x900 - below breakpoint (hamburger MUST exist)
7. 640x900 - at breakpoint (hamburger MUST NOT exist)
8. 768x1024 - tablet portrait
9. 1024x768 - tablet landscape
10. 1280x720 - desktop HD
11. 1440x900 - desktop medium
12. 1920x1080 - desktop full HD

PAGES (test each at every viewport):
- http://localhost:4321/ (home)
- http://localhost:4321/blog (blog list)
- http://localhost:4321/blog/lhorizon-cest-toi (post)
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE ACTIONS:
1. Open page, wait 1000ms
2. Screenshot top: DM-VP<##>-<page>-top.png
3. Check overflow: eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
4. If viewport < 640: click #menu-btn, screenshot menu open, click again to close
5. Scroll down 500, screenshot mid
6. Scroll to footer, screenshot footer

FAILURE DETECTION:
- Horizontal overflow > 0
- Menu button visible at 640+ width
- Menu button hidden below 640 width
- Text hitting exact edge of viewport
- Low contrast text

SCREENSHOT NAMING:
DM-VP01-home-top.png
DM-VP01-home-menu.png
DM-VP01-home-mid.png
DM-VP01-home-footer.png
etc.

OUTPUT:
Create summary at end:
- Per viewport: PASS or FAIL
- List all defects with: viewport, page, issue, screenshot
- Total defect count
```

### Agent 2 of 3: Light Mode Complete

```
E2E Visual Test - LIGHT MODE (Agent 2 of 3)

You are testing LIGHT MODE ONLY. Other agents handle dark mode.

SETUP:
- Dev server: http://localhost:4321/
- Tool: agent-browser CLI
- Session name: visual-light
- Screenshots: ~/Documents/screenshots/LM-*
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME SETUP (run at start and after each viewport change):
agent-browser --session visual-light storage local set theme "light"
agent-browser --session visual-light set media light
agent-browser --session visual-light reload
agent-browser --session visual-light wait 1000

VIEWPORTS (test in order):
1. 320x568 - phone XS
2. 375x667 - phone S
3. 390x844 - phone M
4. 428x926 - phone L
5. 568x320 - phone landscape
6. 639x900 - below breakpoint (hamburger MUST exist)
7. 640x900 - at breakpoint (hamburger MUST NOT exist)
8. 768x1024 - tablet portrait
9. 1024x768 - tablet landscape
10. 1280x720 - desktop HD
11. 1440x900 - desktop medium
12. 1920x1080 - desktop full HD

PAGES (test each at every viewport):
- http://localhost:4321/ (home)
- http://localhost:4321/blog (blog list)
- http://localhost:4321/blog/lhorizon-cest-toi (post)
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE ACTIONS:
1. Open page, wait 1000ms
2. Screenshot top: LM-VP<##>-<page>-top.png
3. Check overflow: eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
4. If viewport < 640: click #menu-btn, screenshot menu open, click again to close
5. Scroll down 500, screenshot mid
6. Scroll to footer, screenshot footer

FAILURE DETECTION:
- Horizontal overflow > 0
- Menu button visible at 640+ width
- Menu button hidden below 640 width
- Text hitting exact edge of viewport
- Low contrast text
- Dark mode colors appearing (theme artifact)

SCREENSHOT NAMING:
LM-VP01-home-top.png
LM-VP01-home-menu.png
LM-VP01-home-mid.png
LM-VP01-home-footer.png
etc.

OUTPUT:
Create summary at end:
- Per viewport: PASS or FAIL
- List all defects with: viewport, page, issue, screenshot
- Total defect count
```

### Agent 3 of 3: Stress Tests + Errors

```
E2E Visual Test - CONTENT STRESS + ERRORS (Agent 3 of 3)

You test content-heavy pages and edge cases. Other agents handle standard page testing.

SETUP:
- Dev server: http://localhost:4321/
- Tool: agent-browser CLI
- Session name: visual-stress
- Screenshots: ~/Documents/screenshots/STRESS-*
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

TEST 1: CODE-HEAVY POST
URL: http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme

Test at these viewports (both themes):
- 320x568 (smallest phone)
- 1920x1080 (largest desktop)

Per viewport + theme:
1. Set viewport
2. Set theme (dark first, then light)
3. Open URL, wait 1500ms
4. Screenshot top
5. Scroll to first <pre> element (code block)
6. Screenshot code block
7. Check overflow (CRITICAL: code should NOT cause body to scroll sideways)
8. If page has <table>, scroll to it, screenshot
9. Scroll to footer, screenshot

Naming: STRESS-code-<VP>-<theme>-<checkpoint>.png

TEST 2: MEDIA-HEAVY POST
URL: http://localhost:4321/blog/10-stages-of-the-lifecycle-of-a-business

Same viewports (320x568, 1920x1080), both themes:
1. Set viewport + theme
2. Open URL, wait 1500ms
3. Screenshot top
4. Scroll to first image
5. Screenshot (verify image scales, no overflow)
6. Check for nested lists, verify indentation
7. Scroll to footer, screenshot

Naming: STRESS-media-<VP>-<theme>-<checkpoint>.png

TEST 3: BREAKPOINT EDGE CASES
Critical test: Menu button appearance

639x900 (dark mode):
1. Set viewport 639 900
2. Set theme dark
3. Open http://localhost:4321/
4. VERIFY: #menu-btn IS visible (is visible "#menu-btn")
5. Screenshot: STRESS-breakpoint-639-dark.png

640x900 (dark mode):
1. Set viewport 640 900
2. VERIFY: #menu-btn IS NOT visible
3. VERIFY: inline nav IS visible (#menu-items or nav links)
4. Screenshot: STRESS-breakpoint-640-dark.png

Repeat for light mode.

TEST 4: 404 PAGE
URL: http://localhost:4321/nonexistent-page-test

Test at 375x667 and 1920x1080, both themes:
1. Open page
2. Screenshot
3. Verify layout isn't broken
4. Verify navigation still works

Naming: STRESS-404-<VP>-<theme>.png

TEST 5: ERROR COLLECTION
After all tests:
agent-browser --session visual-stress errors
agent-browser --session visual-stress console

Document any errors found.

OUTPUT:
Structured report:
- CODE POST: PASS/FAIL per viewport/theme
- MEDIA POST: PASS/FAIL per viewport/theme
- BREAKPOINT: 639=hamburger? 640=inline?
- 404: PASS/FAIL
- ERRORS: List any console/page errors
- All defects with screenshots
```

---

## OPTION 3: Maximum Parallel (5 Agents)

For fastest execution. Launch all 5 simultaneously.

### Agent 1 of 5: Dark Mode Mobile

```
E2E Visual Test - DARK MODE MOBILE (Agent 1 of 5)

Test dark mode on mobile phone viewports only.

SETUP:
- Session: visual-dm-mobile
- Screenshots: ~/Documents/screenshots/DM-MOB-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME: dark (storage local set theme "dark", set media dark)

VIEWPORTS:
- 320x568 (VP01)
- 375x667 (VP02)
- 390x844 (VP03)
- 428x926 (VP04)

PAGES (each viewport):
- http://localhost:4321/
- http://localhost:4321/blog
- http://localhost:4321/blog/lhorizon-cest-toi
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE:
1. Screenshot top
2. Check overflow
3. Test menu toggle (click #menu-btn, screenshot, click again)
4. Scroll mid, screenshot
5. Scroll footer, screenshot

OUTPUT: Summary with PASS/FAIL per viewport, defect list with screenshots.
```

### Agent 2 of 5: Dark Mode Tablet/Desktop

```
E2E Visual Test - DARK MODE TABLET/DESKTOP (Agent 2 of 5)

Test dark mode on tablet and desktop viewports.

SETUP:
- Session: visual-dm-desktop
- Screenshots: ~/Documents/screenshots/DM-DSK-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME: dark

VIEWPORTS:
- 639x900 (VP06 - hamburger MUST exist)
- 640x900 (VP07 - hamburger MUST NOT exist)
- 768x1024 (VP08)
- 1024x768 (VP09)
- 1280x720 (VP10)
- 1440x900 (VP11)
- 1920x1080 (VP12)

PAGES (each viewport):
- http://localhost:4321/
- http://localhost:4321/blog
- http://localhost:4321/blog/lhorizon-cest-toi
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE:
1. Screenshot top
2. Check overflow
3. VP06: verify hamburger visible, test toggle
4. VP07+: verify inline nav visible, no hamburger
5. Scroll footer, screenshot

OUTPUT: Summary with PASS/FAIL per viewport, defect list.
```

### Agent 3 of 5: Light Mode Mobile

```
E2E Visual Test - LIGHT MODE MOBILE (Agent 3 of 5)

Test light mode on mobile phone viewports only.

SETUP:
- Session: visual-lm-mobile
- Screenshots: ~/Documents/screenshots/LM-MOB-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME: light (storage local set theme "light", set media light)

VIEWPORTS:
- 320x568 (VP01)
- 375x667 (VP02)
- 390x844 (VP03)
- 428x926 (VP04)

PAGES (each viewport):
- http://localhost:4321/
- http://localhost:4321/blog
- http://localhost:4321/blog/lhorizon-cest-toi
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE:
1. Screenshot top
2. Check overflow
3. Test menu toggle
4. Scroll mid, screenshot
5. Scroll footer, screenshot

EXTRA CHECK: Look for dark mode artifacts (dark borders, wrong background colors).

OUTPUT: Summary with PASS/FAIL per viewport, defect list.
```

### Agent 4 of 5: Light Mode Tablet/Desktop

```
E2E Visual Test - LIGHT MODE TABLET/DESKTOP (Agent 4 of 5)

Test light mode on tablet and desktop viewports.

SETUP:
- Session: visual-lm-desktop
- Screenshots: ~/Documents/screenshots/LM-DSK-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

THEME: light

VIEWPORTS:
- 639x900 (VP06 - hamburger MUST exist)
- 640x900 (VP07 - hamburger MUST NOT exist)
- 768x1024 (VP08)
- 1024x768 (VP09)
- 1280x720 (VP10)
- 1440x900 (VP11)
- 1920x1080 (VP12)

PAGES (each viewport):
- http://localhost:4321/
- http://localhost:4321/blog
- http://localhost:4321/blog/lhorizon-cest-toi
- http://localhost:4321/tags
- http://localhost:4321/search

PER PAGE:
1. Screenshot top
2. Check overflow
3. VP06: verify hamburger visible
4. VP07+: verify inline nav, no hamburger
5. Scroll footer, screenshot

OUTPUT: Summary with PASS/FAIL per viewport, defect list.
```

### Agent 5 of 5: Stress Tests + Edge Cases

```
E2E Visual Test - STRESS + EDGE CASES (Agent 5 of 5)

Test content-heavy pages, breakpoint edges, 404, and collect errors.

SETUP:
- Session: visual-stress
- Screenshots: ~/Documents/screenshots/STRESS-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

PART 1: PHONE LANDSCAPE
Viewport: 568x320
Both themes, test:
- http://localhost:4321/
- http://localhost:4321/blog/lhorizon-cest-toi

Verify content readable in cramped landscape.

PART 2: CODE-HEAVY POST
URL: http://localhost:4321/blog/dev_workflows/how-to-configure-astropaper-theme
Viewports: 320x568, 1920x1080
Both themes

Screenshot code blocks, verify no body horizontal scroll.

PART 3: MEDIA POST
URL: http://localhost:4321/blog/10-stages-of-the-lifecycle-of-a-business
Viewports: 320x568, 1920x1080
Both themes

Screenshot images, verify scaling.

PART 4: 404 PAGE
URL: http://localhost:4321/nonexistent-page-test
Viewports: 375x667, 1920x1080
Both themes

PART 5: ERROR COLLECTION
agent-browser --session visual-stress errors
agent-browser --session visual-stress console

Report any JS errors or 404 asset requests.

OUTPUT: Stress test results, edge case results, error report.
```

---

## Quick Reference: CLI Commands

```bash
# Initialize session
agent-browser --session <name> open http://localhost:4321/

# Set viewport
agent-browser --session <name> set viewport <W> <H>

# Set theme via media
agent-browser --session <name> set media dark|light

# Set theme via storage
agent-browser --session <name> storage local set theme "dark"|"light"

# Reload page
agent-browser --session <name> reload

# Wait (ms)
agent-browser --session <name> wait <ms>

# Screenshot
agent-browser --session <name> screenshot <path>

# Full page screenshot
agent-browser --session <name> screenshot -f <path>

# Check visibility
agent-browser --session <name> is visible "<selector>"

# Click element
agent-browser --session <name> click "<selector>"

# Get attribute
agent-browser --session <name> get attr <attr> "<selector>"

# Scroll
agent-browser --session <name> scroll down <px>
agent-browser --session <name> scrollintoview "<selector>"

# Evaluate JS
agent-browser --session <name> eval "<js>"

# Fill input
agent-browser --session <name> fill "<selector>" "<text>"

# Get errors
agent-browser --session <name> errors
agent-browser --session <name> console

# Clear errors
agent-browser --session <name> errors --clear
agent-browser --session <name> console --clear

# Close session
agent-browser --session <name> close
```
