# Le blog de Pascal Andy

This is my personal blog built on the AstroPaper theme - a minimal, responsive, accessible and SEO-friendly Astro blog theme.

Source: https://github.com/pascalandy/pascalandy-blog-paper

## Prerequisites

- [Bun](https://bun.sh/) - Package manager & runtime
- [Just](https://just.systems/) - Command runner (required for hooks and CI)
- [uv](https://docs.astral.sh/uv/) - Runs the Python scripts behind the recipes
- [gitleaks](https://github.com/gitleaks/gitleaks) - Scans staged changes for secrets before each commit

```bash
# macOS
brew install bun just uv gitleaks

# Verify installation
bun --version && just --version && uv --version && gitleaks version
```

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
