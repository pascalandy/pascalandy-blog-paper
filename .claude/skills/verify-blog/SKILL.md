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

Read-only. It names the instance (Pascal's dev server or this run's preview) and checks that it answers with the blog's title. It exits 1 when a build input changed after the build or the dev server's pages show another checkout; exit 0 means worth driving. Run it first whenever anything looks off.

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

It needs the Chromium build of Playwright 1.56; when `browse.py` says Chromium did not start, run `uv run --with playwright==1.56.0 python -m playwright install --with-deps chromium`; on Linux, `--with-deps` also installs the system libraries it needs, through apt. `--device iphone` emulates an iPhone viewport in Chromium; it is not Safari, so iOS proof needs the agent-browser path.

`browse.py` also accepts `--step back`, `--step reload`, and `--step 'eval:<JavaScript>'`. It writes `network.json` with each response status and a separate list of failed requests. `probes.json` records the `<html>` theme at `DOMContentLoaded`, `astro:after-swap`, and `astro:page-load`.

On `astro:after-swap`, `theme` comes from a listener registered after initial page load, following the site's theme handler in the same event dispatch; `theme_before_handlers` preserves the early init-script reading. A full reload installs both listeners in the new document. A link click and cross-route back wait for the navigation's `astro:page-load` or a full page load before the next step. Fragment-only back completes when the URL fragment changes.

## Compare two builds

Build each commit in its own worktree. Use the same `cache/fonts/` contents for both builds because Google Fonts can return different files. Keep Pascal's dev server on port 4320 untouched.

```bash
just parity /absolute/trunk/dist /absolute/head/dist --json /absolute/parity.json
just shots capture /absolute/trunk/dist --out /absolute/trunk-shots --port 4391
just shots capture /absolute/head/dist --out /absolute/head-shots --port 4392
just shots diff /absolute/trunk-shots /absolute/head-shots --json /absolute/shots.json
```

`just parity` exits 0 and prints `IDENTICAL` when the output matches. It reports route, text, heading and element IDs, linked resource availability and page-to-content binding for local CSS, JS, modulepreload, and script/style preloads, plus image, feed, Pagefind, and asset differences. For an approved change, copy only that finding's exact `fingerprint` from the JSON report into a ledger that maps it to a reason, then rerun with `--accept /absolute/ledger.json`. The ledger applies to that baseline-to-candidate direction; a new value fails again, and an unmatched entry is an error when no material finding remains. Runs of ASCII whitespace normalize, but removing an entire text node remains material. Use `--fetched` when the second folder contains a subset fetched from a deployed site. Preserve the URL paths of fetched files and include every font referenced by `@font-face`, script, stylesheet, modulepreload target, and `preload` target with `as="script"` or `as="style"` referenced by the fetched pages and CSS. Missing `@font-face` fonts are input errors; missing other required resources are material findings. The command checks each fetched font against the CSS role that uses it.

Acceptance fingerprints also belong to the parity tool version that produced them. Regenerate a ledger from a new report after a tool change; a stale ledger fails closed.

Image comparison includes animation loop count, but ignores the WebP/GIF background hint when decoded frames are unchanged. For an `av01` primary AVIF item, parity follows its item-property associations and item location, then compares the effective color settings from associated `colr` properties or its reduced still-image AV1 header. A non-`av01` primary item, including a grid, is compared conservatively by file bytes: identical bytes pass, and any byte change is material. A non-reduced AV1 sequence header is outside the normalized AVIF path and produces an explicit input error; report that file for a parser extension before accepting the comparison.

The 44 shots come from [shots.json](shots.json). Capture waits for visible images to decode at each scroll position and records the selected local image hashes in the manifest. The diff report gives each shot's changed-pixel ratio. It names image boxes with changed pixels only when their selected local image bytes differed at capture, even if a dist changes afterward. Older manifests without hashes fall back to their current dist files. Capture accepts private ports 4391 to 4399 and refuses 4320. For gallery checks, pass `--pages /absolute/pages.json` with extra labels mapped to root-relative routes; labels use lowercase letters, digits, and hyphens. Each extra route gets `top` and first article-image shots in addition to the 44. Use `--dpr 2 --scale device` and `--dpr 3 --scale device` to capture native gallery variants, with the same pages file for both builds.

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
