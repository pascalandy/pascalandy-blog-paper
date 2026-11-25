![Isometric drawing of a person writing in a notebook on the lakeshore rocks at sunrise, with a small tower-house among the pines across the misty water](docs/assets/hero-v2b.png)

# Le blog de Pascal Andy

The source of Pascal Andy's blog, written in French and published at [blog.pascalandy.com](https://blog.pascalandy.com). Built with Astro on the [AstroPaper](https://github.com/satnaing/astro-paper) theme.

Run it locally, once the [prerequisites](#prerequisites) are installed:

```bash
just install # dependencies and git hooks
just dev     # then open http://localhost:4320/
```

Each post is one Markdown file in `src/data/blog/`. To add one, save a file such as this as `src/data/blog/<slug>.md`:

```markdown
---
author: Pascal Andy
date_created: 2026-11-20
title: "Mon billet"
description: "Une phrase qui résume le billet."
tags:
  - random
---

Le texte du billet, en français.
```

The file name becomes the URL, `/blog/<slug>/`, so write it in lowercase words joined by hyphens. Astro skips any file whose name starts with `_`. Every tag must exist in `src/tags.ts`, and `just check --only content` reports any unknown key or tag.

## Prerequisites

Use a Node version satisfying `engines.node` in `package.json`, currently Node 22.23.4 or newer. `just check` reports an unsupported version and the executable on `PATH`.

- [Bun](https://bun.sh/) - Package manager & runtime
- [Just](https://just.systems/) - Command runner (required for hooks and CI)
- [uv](https://docs.astral.sh/uv/) - Runs the Python scripts behind the recipes
- [GitHub CLI](https://cli.github.com/) with [gh-signoff](https://github.com/basecamp/gh-signoff) - Posts the `signoff` status that gates merges
- [gitleaks](https://github.com/gitleaks/gitleaks) - Scans staged changes for secrets before each commit, and a branch before signoff

The tools work on any operating system. For example, on macOS:

```bash
# macOS
brew install bun just uv gh gitleaks
gh extension install basecamp/gh-signoff

# Verify installation
bun --version && just --version && uv --version && gh signoff version && gitleaks version
```

Install the Chromium version used by the reader checks with `uv run --with playwright==1.56.0 playwright install chromium`. On a fresh Ubuntu machine, add `--with-deps` to install its system libraries.

For a hosted Claude Code environment, load `.claude/setup-reader-browser.sh` as its setup script. Allow `cdn.playwright.dev` and `playwright.download.prss.microsoft.com` alongside the default package domains, and set `PLAYWRIGHT_BROWSERS_PATH=/opt/blog-reader/browsers` in the environment. The cloud image caches the installation across sessions. [Cloud environment setup](https://code.claude.com/docs/en/cloud-environments#setup-scripts)

Without Just, run any recipe through uv: `uvx --from rust-just just check`.

## Quick Start

```bash
just install # dependencies and git hooks
just dev     # dev server on port 4320
just qa      # format, then run the same checks as CI
```

## Tech Stack

- [Astro](https://astro.build/) - Static site generator
- [TypeScript](https://www.typescriptlang.org/) - Type checking
- [Tailwind CSS v4](https://tailwindcss.com/) - Styling
- [Pagefind](https://pagefind.app/) - Static search
- [Just](https://just.systems/) - Command runner
- [Prettier](https://prettier.io/) + [ESLint](https://eslint.org) - Code quality

## Documentation

- See [AGENTS.md](AGENTS.md) for the working contract: first moves, rules, and where to read more.
- Original theme by [Sat Naing](https://satnaing.dev) and [contributors](https://github.com/satnaing/astro-paper/graphs/contributors). A fork of [AstroPaper](https://github.com/satnaing/astro-paper).

## License

- **Code:** MIT License (inherited from AstroPaper)
- **Content** (`src/data/blog/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) - You may reuse with attribution to Pascal Andy.

French noun and verb search uses Benoît Sagot’s Lefff 3.4 under the LGPL-LR. Each build publishes the license at `/search/lefff.txt` and the source lexicon at `/pagefind/verbs/lefff-3.4.mlex.gz`.
