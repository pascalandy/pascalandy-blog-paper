---
name: "verify-blog"
description: "Use when a change to Pascal Andy's blog must be seen or proven in a real browser: launch or reuse the site, drive the home page, a post, tags, search, navigation, or the theme toggle, and capture screenshots and accessibility snapshots on desktop or iOS."
---

# Verify the blog in a browser

Prove how the site behaves for a reader: launch an instance, drive a feature the way a reader would, capture evidence, clean up. The [feature map](features/README.md) says what to drive; this file says how. Run every command from the repository root.

## Launch

```bash
uv run .claude/skills/verify-blog/scripts/site.py up
```

It prints the base URL once the site answers, and records it in `cache/verify-blog/server.json`:

- When Pascal's dev server answers on http://localhost:4320, it is reused and never restarted, unless its pages show it serves another checkout, such as the main one seen from a worktree
- Otherwise it builds the site (`bun run build:ci`, about a minute when cold) and serves the build with `astro preview` on http://127.0.0.1:4330; a later `up` reuses that preview until a build input changes (`src/`, `public/`, `astro.config.ts`, `package.json`, `bun.lock`), then rebuilds
- It never starts the dev server: Pascal runs `just dev` himself
- The state records this checkout's path, so a state copied from another checkout is ignored

Set `URL` to the printed base URL for the commands below.

## Doctor

```bash
uv run .claude/skills/verify-blog/scripts/site.py doctor
```

Read-only. It names the instance (Pascal's dev server or this run's preview) and checks that it answers with the blog's title. It exits 1 when a build input changed after the build or the dev server serves another checkout; exit 0 means worth driving. Run it first whenever anything looks off.

## Drive

Pick the feature file in [features/](features/README.md) and follow its steps with one harness.

**Desktop, agent-browser** (Pascal's Mac):

```bash
agent-browser set viewport 1440 900
agent-browser open "$URL/"
agent-browser snapshot -i
agent-browser click "#theme-btn"
agent-browser screenshot cache/verify-blog/$RUN/home/after.png
```

**iOS, agent-browser**: real Mobile Safari in the iOS Simulator; needs macOS with Xcode and Appium (`npm install -g appium`, `appium driver install xcuitest`). The first launch takes 30 to 60 seconds:

```bash
agent-browser -p ios --device "iPhone 16 Pro" open "$URL/"
agent-browser -p ios snapshot -i
agent-browser -p ios tap @e1
agent-browser -p ios screenshot cache/verify-blog/$RUN/home/ios.png
```

**Cloud fallback, Playwright**: without agent-browser, `browse.py` drives Chromium through Playwright, runs its steps in order, and saves the evidence:

```bash
uv run .claude/skills/verify-blog/scripts/browse.py "$URL/search" --out cache/verify-blog/$RUN/search \
  --step 'fill:.pagefind-ui__search-input=bitcoin' --step 'wait:.pagefind-ui__result'
```

It needs the Chromium build of Playwright 1.56; when `browse.py` says Chromium did not start, run `uv run --with playwright==1.56.0 python -m playwright install chromium`. `--device iphone` emulates an iPhone viewport in Chromium; it is not Safari, so iOS proof needs the agent-browser path.

Browser rules:

- Keep the viewport at most 1920×1920: larger crashes the browser
- Read no screenshot larger than 1920 pixels a side. `browse.py` saves the viewport in CSS pixels; shrink an agent-browser capture first: `magick mogrify -resize '1920x1920>' -quality 70 FILE`
- Drive by stable handles: ids such as `#theme-btn`, ARIA roles and names, and route paths; never by coordinates

## Evidence

Save everything under `cache/verify-blog/$RUN/FEATURE/`, with `RUN=$(date +%Y%m%d-%H%M%S)`.

- Drive the real reader path: click the control, type in the box. Never set state through scripts, local storage, or URLs the reader would not use
- Capture the action and the resulting state: a screenshot and an accessibility snapshot after the action, and the state before it when the action changes state, such as the theme
- Check what else the action changed, such as the URL, local storage, or the `data-theme` attribute; `browse.py` records the URL, title, theme, and console errors in `state.json`
- Record the instance (dev server or preview), the feature file, and the entry point used

## Cleanup

```bash
uv run .claude/skills/verify-blog/scripts/site.py down
agent-browser close
```

`down` stops only the preview this run started: the process ID it recorded, once `ps` shows that process still runs the preview. It never touches Pascal's dev server, and it never deletes the evidence in `cache/verify-blog/`. `just clean` deletes `cache/`, evidence included: copy what you keep first.

## Helpers

- `uv run .claude/skills/verify-blog/scripts/site.py up|doctor|down`: launch, check, and stop the instance, as above
- `uv run .claude/skills/verify-blog/scripts/browse.py URL --out DIR [--device desktop|iphone] [--color-scheme light|dark] [--step ACTION:ARGUMENT]...`: steps are `click:SELECTOR`, `fill:SELECTOR=TEXT`, `press:KEY`, `wait:SELECTOR`, and `goto:PATH`; `--help` shows examples
