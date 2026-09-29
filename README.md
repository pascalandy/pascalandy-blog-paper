# Le blog de Pascal Andy

This is my personal blog built on the AstroPaper theme - a minimal, responsive, accessible and SEO-friendly Astro blog theme.

Source: https://github.com/pascalandy/pascalandy-blog-paper

## Prerequisites

- [Bun](https://bun.sh/) - Package manager & runtime
- [Just](https://just.systems/) - Command runner (required for hooks and CI)
- [uv](https://docs.astral.sh/uv/) - Runs the Python scripts behind `just signoff` and `just deploy`
- [GitHub CLI](https://cli.github.com/) with [gh-signoff](https://github.com/basecamp/gh-signoff) - Posts the `signoff` status that gates merges
- [gitleaks](https://github.com/gitleaks/gitleaks) - Scans a branch for secrets before signoff

```bash
# macOS
brew install bun just uv gh gitleaks
gh extension install basecamp/gh-signoff

# Verify installation
bun --version && just --version && uv --version && gh signoff version && gitleaks version
```

## Quick Start

```bash
just install
just dev
just qa
```

## Tech Stack

- [Astro](https://astro.build/) - Static site generator
- [TypeScript](https://www.typescriptlang.org/) - Type checking
- [Tailwind CSS v4](https://tailwindcss.com/) - Styling
- [Pagefind](https://pagefind.app/) - Static search
- [Just](https://just.systems/) - Command runner
- [Prettier](https://prettier.io/) + [ESLint](https://eslint.org) - Code quality

## Documentation

- See [AGENTS.md](AGENTS.md) for development guidelines and architecture details.
- Original theme by [Sat Naing](https://satnaing.dev) and [contributors](https://github.com/satnaing/astro-paper/graphs/contributors). A fork of [AstroPaper](https://github.com/satnaing/astro-paper).

## License

- **Code:** MIT License (inherited from AstroPaper)
- **Content** (`src/data/blog/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) - You may reuse with attribution to Pascal Andy.
