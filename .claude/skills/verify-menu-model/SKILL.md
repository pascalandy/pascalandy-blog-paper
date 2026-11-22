---
name: verify-menu-model
description: Use when changing the mobile header, its backdrop, keyboard access, or menu behavior across theme changes and Astro navigation.
---

# Verify the mobile menu

Run `just qa-reader` from the repository root with the [blog prerequisites](../../../README.md#prerequisites) and the [verify-blog Chromium installation](../verify-blog/SKILL.md#drive). The menu result reports the number of completed traces or the actions leading to the failure.

At 639 × 900 in Chromium, Tab from the menu button must skip a closed menu and enter an open one. An open menu must allow the reader to dismiss it and open it again. The [model](../verify-blog/scripts/menu_model.py) runs every combination of these three actions against the built site:

1. Open the menu with a click, or tab to its button and press Enter.
2. Dismiss it with a click on the button, Enter on the focused button, a click outside the menu, a theme change, or the Blog link.
3. Open it again with a click, or tab to its button and press Enter.

On load and after each action, the model starts from the browser's current focus. It uses Tab to reach the menu button, including after a dismissal or navigation. One more Tab checks whether focus enters or skips the menu. Shift+Tab must return focus to the button before the next action. The 20 traces cover three completed actions in one Chromium tab at the specified viewport. Longer histories, simultaneous inputs and native Safari need separate checks.

## Investigate a counterexample

1. Replay the reported sequence on the built site. For `load /: Tab from the menu button should skip its links`, focus the closed menu button and press Tab. Focus moving onto a hidden link reproduces the keyboard regression from [PR #115](https://github.com/pascalandy/pascalandy-blog-paper/pull/115). For a second button click intercepted by the backdrop, inspect the element covering the centre of the close button.
2. Compare the observed state to the [navigation requirements](../verify-blog/features/navigation.md). When the reader loses access, fix the header and rerun the same sequence. When the supported interaction changes intentionally, update its actions and expected outcomes in the model, then rerun `just qa-reader`.
3. Recheck the coverage record when the following files change. Advance the revision only after reviewing their event handlers and running all traces.

Coverage last confirmed at `94d0086665e87687c586b1b45a7a1455ecbf677c`. [Header.astro](../../../src/components/Header.astro) supplies the menu markup, focus visibility, pointer stacking and `toggleNav` handlers, including installation after an Astro page swap. [theme.ts](../../../src/scripts/theme.ts) supplies the theme button's observable light/dark change.
