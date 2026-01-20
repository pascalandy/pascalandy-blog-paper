---
title: E2E Testing Prompts
description: Copy-paste prompts for AI coding assistants to execute visual regression tests.
---

## Table of Contents

- [OPTION 1: Single AI Assistant (Orchestrator)](#option-1-single-ai-assistant-orchestrator)
  - [Prompt 1A: Full Test Run (Sequential)](#prompt-1a-full-test-run-sequential)
  - [Prompt 1B: Full Test Run (With 3 Subagents)](#prompt-1b-full-test-run-with-3-subagents)
  - [Prompt 1C: Maximum Parallel (10 Subagents)](#prompt-1c-maximum-parallel-10-subagents)

- [OPTION 2: Parallel AI Assistants (3-Agent Split)](#option-2-parallel-ai-assistants-3-agent-split)
  - [Agent 1 of 3: Dark Mode Complete](#agent-1-of-3-dark-mode-complete)
  - [Agent 2 of 3: Light Mode Complete](#agent-2-of-3-light-mode-complete)
  - [Agent 3 of 3: Stress Tests + Errors](#agent-3-of-3-stress-tests--errors)

- [OPTION 3: Maximum Parallel (5 Agents)](#option-3-maximum-parallel-5-agents)
  - [Agent 1 of 5: Dark Mode Mobile](#agent-1-of-5-dark-mode-mobile)
  - [Agent 2 of 5: Dark Mode Tablet/Desktop](#agent-2-of-5-dark-mode-tabletdesktop)
  - [Agent 3 of 5: Light Mode Mobile](#agent-3-of-5-light-mode-mobile)
  - [Agent 4 of 5: Light Mode Tablet/Desktop](#agent-4-of-5-light-mode-tabletdesktop)
  - [Agent 5 of 5: Stress Tests + Edge Cases](#agent-5-of-5-stress-tests--edge-cases)

---

## OPTION 1: Single AI Assistant (Orchestrator)

Use this when you want ONE AI assistant to manage the entire test run, optionally delegating to subagents.

### Prompt 1A: Full Test Run (Sequential)

```
CONTEXT:
- Read and understand: @AGENTS.md
- Read and understand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test using best practices.
- Run `agent-browser --help` to see available commands in order to execute these test. Do not try to use an MCP.

PREREQUISITES:
- Dev server is running at http://localhost:4320/
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
- http://localhost:4320/ (home)
- http://localhost:4320/blog (blog list)
- http://localhost:4320/blog/lhorizon-cest-toi (simple post)
- http://localhost:4320/blog/dev_workflows/how-to-configure-astropaper-theme (code post)
- http://localhost:4320/tags (tags page)
- http://localhost:4320/search (search page)
- http://localhost:4320/nonexistent-page-test (404)

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

### Prompt 1B: Full Test Run (With 3 Subagents)

```
CONTEXT:
- Read and understand: @AGENTS.md
- Read and understand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test using MAXIMUM PARALLELIZATION.
- Run `agent-browser --help` to see available commands in order to execute these test. Do not try to use an MCP.

PREREQUISITES:
- Dev server running at http://localhost:4320/
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
http://localhost:4320/
http://localhost:4320/blog
http://localhost:4320/blog/lhorizon-cest-toi
http://localhost:4320/blog/dev_workflows/how-to-configure-astropaper-theme
http://localhost:4320/tags
http://localhost:4320/search
http://localhost:4320/nonexistent-page-test

After all subagents complete, compile results into a unified report showing:
- PASS/FAIL per viewport per theme
- All defects with screenshots
- Content stress test results
- Any console errors
```

### Prompt 1C: Maximum Parallel (10 Subagents)

```
CONTEXT:
- Read and understand: @AGENTS.md
- Read and understand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test using MAXIMUM PARALLELIZATION.
- Run `agent-browser --help` to see available commands in order to execute these test. Do not try to use an MCP.
- Tell subagents to not try loading any MCP or skills.

PREREQUISITES:
- Dev server running at http://localhost:4320/
- Use agent-browser CLI
- Screenshots to ~/Documents/screenshots/
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

================================================================================
ORCHESTRATION STRATEGY
================================================================================

You are the ORCHESTRATOR. Launch 10 subagents IN PARALLEL. Each subagent has:
- Unique session name (prevents browser conflicts)
- Specific viewport/theme scope (no overlap)
- Clear screenshot naming convention
- Defined success criteria

After ALL 10 subagents complete, YOU compile the unified report.

================================================================================
SUBAGENT ASSIGNMENTS
================================================================================

SUBAGENT 1: DM-SMALL-PHONES
---------------------------
Session: e2e-dm-sm
Theme: dark
Viewports: 320x568 (VP01), 375x667 (VP02)
Pages: home, blog, post, tags, search (5 pages)
Screenshots: ~/Documents/screenshots/DM-VP01-*, DM-VP02-*

Tasks per viewport:
1. Set viewport + theme dark
2. For each page: screenshot top, check overflow, test menu toggle, screenshot footer
3. Report: PASS/FAIL per viewport, defect list

SUBAGENT 2: DM-LARGE-PHONES
---------------------------
Session: e2e-dm-lg
Theme: dark
Viewports: 390x844 (VP03), 428x926 (VP04)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/DM-VP03-*, DM-VP04-*

Tasks: Same as Subagent 1

SUBAGENT 3: DM-TRANSITIONAL (CRITICAL - Breakpoint Edge)
--------------------------------------------------------
Session: e2e-dm-trans
Theme: dark
Viewports: 568x320 (VP05 landscape), 639x900 (VP06 edge), 640x900 (VP07 edge)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/DM-VP05-*, DM-VP06-*, DM-VP07-*

CRITICAL CHECKS:
- VP05: Content readable in cramped landscape
- VP06 (639px): #menu-btn MUST BE VISIBLE
- VP07 (640px): #menu-btn MUST BE HIDDEN, inline nav visible
- Screenshot both 639 and 640 side-by-side for comparison

SUBAGENT 4: DM-LARGE-SCREENS
----------------------------
Session: e2e-dm-desk
Theme: dark
Viewports: 768x1024 (VP08), 1024x768 (VP09), 1280x720 (VP10), 1440x900 (VP11), 1920x1080 (VP12)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/DM-VP08-* through DM-VP12-*

Tasks:
- Verify inline nav (no hamburger)
- Check max-width container behavior
- Verify generous margins on large screens

SUBAGENT 5: LM-SMALL-PHONES
---------------------------
Session: e2e-lm-sm
Theme: light
Viewports: 320x568 (VP01), 375x667 (VP02)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/LM-VP01-*, LM-VP02-*

Tasks: Same as Subagent 1
Extra: Check for dark mode artifacts (wrong background colors)

SUBAGENT 6: LM-LARGE-PHONES
---------------------------
Session: e2e-lm-lg
Theme: light
Viewports: 390x844 (VP03), 428x926 (VP04)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/LM-VP03-*, LM-VP04-*

Tasks: Same as Subagent 2
Extra: Check for dark mode artifacts

SUBAGENT 7: LM-TRANSITIONAL (CRITICAL - Breakpoint Edge)
--------------------------------------------------------
Session: e2e-lm-trans
Theme: light
Viewports: 568x320 (VP05), 639x900 (VP06), 640x900 (VP07)
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/LM-VP05-*, LM-VP06-*, LM-VP07-*

CRITICAL CHECKS: Same as Subagent 3 but for light mode

SUBAGENT 8: LM-LARGE-SCREENS
----------------------------
Session: e2e-lm-desk
Theme: light
Viewports: 768x1024, 1024x768, 1280x720, 1440x900, 1920x1080
Pages: home, blog, post, tags, search
Screenshots: ~/Documents/screenshots/LM-VP08-* through LM-VP12-*

Tasks: Same as Subagent 4 but for light mode

SUBAGENT 9: CONTENT-STRESS
--------------------------
Session: e2e-stress
Viewports: 320x568 (smallest), 1920x1080 (largest)
Themes: BOTH dark and light

Test these content-heavy pages:
1. CODE POST: http://localhost:4320/blog/dev_workflows/how-to-configure-astropaper-theme
   - Screenshot code blocks at both viewports, both themes
   - CRITICAL: Verify code does NOT cause body horizontal scroll
   - If table exists, screenshot and verify contained scroll

2. MEDIA POST: http://localhost:4320/blog/10-stages-of-the-lifecycle-of-a-business
   - Screenshot images at both viewports, both themes
   - Verify images scale properly (no overflow)
   - Check nested list indentation

Screenshots: ~/Documents/screenshots/STRESS-code-*, STRESS-media-*

SUBAGENT 10: EDGE-CASES-AND-ERRORS
----------------------------------
Session: e2e-edge
Viewports: 375x667, 1920x1080
Themes: BOTH

Tasks:
1. 404 PAGE: http://localhost:4320/nonexistent-page-test
   - Both viewports, both themes
   - Verify layout intact, navigation works
   - Screenshots: EDGE-404-*

2. SEARCH INTERACTION:
   - Open search page
   - Fill input with "theme"
   - Verify results appear without overlap
   - Screenshots: EDGE-search-*

3. ERROR COLLECTION (run LAST, after all other subagents):
   - agent-browser --session e2e-edge errors
   - agent-browser --session e2e-edge console
   - Document ANY JS errors or 404 asset requests

Screenshots: ~/Documents/screenshots/EDGE-*

================================================================================
PAGES REFERENCE (for all subagents)
================================================================================

- home: http://localhost:4320/
- blog: http://localhost:4320/blog
- post: http://localhost:4320/blog/lhorizon-cest-toi
- tags: http://localhost:4320/tags
- search: http://localhost:4320/search

================================================================================
PER-PAGE TEST PROTOCOL (for subagents 1-8)
================================================================================

For each page at each viewport:
1. agent-browser --session <SESSION> set viewport <W> <H>
2. agent-browser --session <SESSION> storage local set theme "<THEME>"
3. agent-browser --session <SESSION> set media <THEME>
4. agent-browser --session <SESSION> open <URL>
5. agent-browser --session <SESSION> wait 1000
6. agent-browser --session <SESSION> screenshot <PATH>-top.png
7. agent-browser --session <SESSION> eval "document.documentElement.scrollWidth - document.documentElement.clientWidth"
   - If result > 0: LOG DEFECT (horizontal overflow)
8. IF viewport width < 640:
   - agent-browser --session <SESSION> click "#menu-btn"
   - agent-browser --session <SESSION> wait 300
   - agent-browser --session <SESSION> screenshot <PATH>-menu.png
   - agent-browser --session <SESSION> click "#menu-btn"
9. agent-browser --session <SESSION> scrollintoview "footer"
10. agent-browser --session <SESSION> wait 300
11. agent-browser --session <SESSION> screenshot <PATH>-footer.png

================================================================================
FAILURE CRITERIA (for all subagents)
================================================================================

Flag as DEFECT if:
- Horizontal overflow > 0
- VP06 (639px): #menu-btn NOT visible
- VP07+ (640px+): #menu-btn IS visible (should be hidden)
- Text touching exact viewport edge (zero padding)
- Low contrast (text hard to read)
- Elements overlapping
- Theme artifact (wrong colors for current theme)

================================================================================
ORCHESTRATOR: COMPILE FINAL REPORT
================================================================================

After all 10 subagents complete, compile this report:

```
E2E VISUAL TEST REPORT - 10-AGENT PARALLEL RUN
==============================================
Date: <date>
Commit: <git rev-parse --short HEAD>

DARK MODE RESULTS
-----------------
VP01 (320x568):   [Subagent 1] PASS/FAIL - Notes: ___
VP02 (375x667):   [Subagent 1] PASS/FAIL - Notes: ___
VP03 (390x844):   [Subagent 2] PASS/FAIL - Notes: ___
VP04 (428x926):   [Subagent 2] PASS/FAIL - Notes: ___
VP05 (568x320):   [Subagent 3] PASS/FAIL - Notes: ___
VP06 (639x900):   [Subagent 3] PASS/FAIL - Notes: ___
VP07 (640x900):   [Subagent 3] PASS/FAIL - Notes: ___
VP08 (768x1024):  [Subagent 4] PASS/FAIL - Notes: ___
VP09 (1024x768):  [Subagent 4] PASS/FAIL - Notes: ___
VP10 (1280x720):  [Subagent 4] PASS/FAIL - Notes: ___
VP11 (1440x900):  [Subagent 4] PASS/FAIL - Notes: ___
VP12 (1920x1080): [Subagent 4] PASS/FAIL - Notes: ___

LIGHT MODE RESULTS
------------------
VP01-VP02: [Subagent 5] ___
VP03-VP04: [Subagent 6] ___
VP05-VP07: [Subagent 7] ___
VP08-VP12: [Subagent 8] ___

CONTENT STRESS RESULTS [Subagent 9]
-----------------------------------
Code blocks (320px dark):  PASS/FAIL
Code blocks (320px light): PASS/FAIL
Code blocks (1920px dark): PASS/FAIL
Code blocks (1920px light): PASS/FAIL
Media/Images (320px):      PASS/FAIL
Media/Images (1920px):     PASS/FAIL

EDGE CASES [Subagent 10]
------------------------
404 page:        PASS/FAIL
Search interaction: PASS/FAIL
Console errors:  <count> errors found
Page errors:     <count> errors found

BREAKPOINT VERIFICATION [Subagents 3 & 7]
-----------------------------------------
639px dark - hamburger visible:  YES/NO
640px dark - hamburger hidden:   YES/NO
639px light - hamburger visible: YES/NO
640px light - hamburger hidden:  YES/NO

DEFECT SUMMARY
--------------
Total defects: <count>

1. [ID] VP: ___ | Page: ___ | Issue: ___ | Screenshot: ___
2. ...

SCREENSHOTS LOCATION
--------------------
~/Documents/screenshots/
- DM-* (dark mode)
- LM-* (light mode)
- STRESS-* (content stress)
- EDGE-* (edge cases)
```

================================================================================
EXECUTION ORDER
================================================================================

1. Launch Subagents 1-8 IN PARALLEL (viewport/theme matrix)
2. Launch Subagent 9 IN PARALLEL (content stress)
3. Launch Subagent 10 IN PARALLEL (edge cases - but error collection waits)
4. Wait for all subagents to complete
5. Subagent 10 runs final error collection
6. Orchestrator compiles unified report
```

---

## OPTION 2: Parallel AI Assistants (3-Agent Split)

Launch these 3 prompts in 3 separate AI coding assistant sessions simultaneously.

### Agent 1 of 3: Dark Mode Complete

```
E2E Visual Test - DARK MODE (Agent 1 of 3)

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

You are testing DARK MODE ONLY. Other agents handle light mode.

SETUP:
- Dev server: http://localhost:4320/
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
- http://localhost:4320/ (home)
- http://localhost:4320/blog (blog list)
- http://localhost:4320/blog/lhorizon-cest-toi (post)
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

You are testing LIGHT MODE ONLY. Other agents handle dark mode.

SETUP:
- Dev server: http://localhost:4320/
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
- http://localhost:4320/ (home)
- http://localhost:4320/blog (blog list)
- http://localhost:4320/blog/lhorizon-cest-toi (post)
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

You test content-heavy pages and edge cases. Other agents handle standard page testing.

SETUP:
- Dev server: http://localhost:4320/
- Tool: agent-browser CLI
- Session name: visual-stress
- Screenshots: ~/Documents/screenshots/STRESS-*
- Resize after capture: magick mogrify -resize '1920x1920>' -quality 70 <filename>

TEST 1: CODE-HEAVY POST
URL: http://localhost:4320/blog/dev_workflows/how-to-configure-astropaper-theme

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
URL: http://localhost:4320/blog/10-stages-of-the-lifecycle-of-a-business

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
3. Open http://localhost:4320/
4. VERIFY: #menu-btn IS visible (is visible "#menu-btn")
5. Screenshot: STRESS-breakpoint-639-dark.png

640x900 (dark mode):
1. Set viewport 640 900
2. VERIFY: #menu-btn IS NOT visible
3. VERIFY: inline nav IS visible (#menu-items or nav links)
4. Screenshot: STRESS-breakpoint-640-dark.png

Repeat for light mode.

TEST 4: 404 PAGE
URL: http://localhost:4320/nonexistent-page-test

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

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
- http://localhost:4320/
- http://localhost:4320/blog
- http://localhost:4320/blog/lhorizon-cest-toi
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

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
- http://localhost:4320/
- http://localhost:4320/blog
- http://localhost:4320/blog/lhorizon-cest-toi
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

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
- http://localhost:4320/
- http://localhost:4320/blog
- http://localhost:4320/blog/lhorizon-cest-toi
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

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
- http://localhost:4320/
- http://localhost:4320/blog
- http://localhost:4320/blog/lhorizon-cest-toi
- http://localhost:4320/tags
- http://localhost:4320/search

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

CONTEXT:
- Read and undertand: @AGENTS.md
- Read and undertand: @dev_notes/e2e_browser_tests/E2E_test_plan.md
- Execute a comprehensive E2E visual regression test on my Astro blog.
  - Use run` agent-browser --help` to see avail cmd in order to execute these test.

Test content-heavy pages, breakpoint edges, 404, and collect errors.

SETUP:
- Session: visual-stress
- Screenshots: ~/Documents/screenshots/STRESS-*
- Resize: magick mogrify -resize '1920x1920>' -quality 70 <filename>

PART 1: PHONE LANDSCAPE
Viewport: 568x320
Both themes, test:
- http://localhost:4320/
- http://localhost:4320/blog/lhorizon-cest-toi

Verify content readable in cramped landscape.

PART 2: CODE-HEAVY POST
URL: http://localhost:4320/blog/dev_workflows/how-to-configure-astropaper-theme
Viewports: 320x568, 1920x1080
Both themes

Screenshot code blocks, verify no body horizontal scroll.

PART 3: MEDIA POST
URL: http://localhost:4320/blog/10-stages-of-the-lifecycle-of-a-business
Viewports: 320x568, 1920x1080
Both themes

Screenshot images, verify scaling.

PART 4: 404 PAGE
URL: http://localhost:4320/nonexistent-page-test
Viewports: 375x667, 1920x1080
Both themes

PART 5: ERROR COLLECTION
agent-browser --session visual-stress errors
agent-browser --session visual-stress console

Report any JS errors or 404 asset requests.

OUTPUT: Stress test results, edge case results, error report.
```