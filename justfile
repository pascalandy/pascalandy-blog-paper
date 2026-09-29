# Justfile for Astro blog
# Run `just` to see available recipes

set shell := ["bash", "-euo", "pipefail", "-c"]

# === Setup ===

# Install dependencies
install:
    bun install

alias i := install

# === Code Quality (base recipes) ===

# Run ESLint
lint:
    bun run lint | tspin

# Format code with Prettier
format:
    bun run format | tspin

# Check formatting without changes
format-check:
    bun run format:check | tspin

# Validate tags
check-tags:
    ./scripts/check-tags.sh

# === Build (base recipes) ===

# Build for production
build:
    bun run build | tspin

# Run Astro check
check:
    bun run sync && bun astro check | tspin

# Preview production build
preview:
    bun run preview | tspin

# === Development (composite recipes) ===

# Full workflow: lint, format, then dev server
dev port="4320":
    just lint
    just format
    just format-check
    bun run dev --port {{port}} | tspin

# QA workflow for agents (with autoformat, no server)
qa:
    just lint
    just format
    just format-check
    just check-tags
    just build

# CI workflow (no autoformat)
ci:
    just lint
    just format-check
    just check-tags
    just build

# === Cleanup ===

# Remove build artifacts and cache
clean:
    rm -rf dist cache .astro

# Deep clean before archiving workspace (removes node_modules)
archive:
    rm -rf dist node_modules cache .astro

# === Ship ===

# Install, run `just ci` and `just gitleaks`, then mark the pushed HEAD green on GitHub; push first
signoff:
    uv run --quiet scripts/signoff.py

# Scan this branch's commits since origin/main for secrets
gitleaks:
    gitleaks git --log-opts="origin/main..HEAD" --no-banner --redact --verbose

# Deploy GitHub's main to production on Sevalla and wait for the build; --dry-run checks the setup
deploy *args:
    uv run --quiet scripts/deploy.py production {{args}}

# Deploy a pushed branch, the current one by default, to the Sevalla preview site
deploy-preview *args:
    uv run --quiet scripts/deploy.py preview {{args}}

# === GitHub Actions (manual only) ===

# Run the CI workflow on GitHub for a pushed ref; deploy is none, preview, or production (main only)
[positional-arguments]
gh-ci ref=`git branch --show-current` deploy="none":
    @test -n "$1" || { echo "error: HEAD is detached; pass a ref" >&2; exit 1; }
    @test "$2" != production || test "$1" = main || { echo "error: production deploys only main" >&2; exit 1; }
    gh workflow run ci.yml --ref "$1" -f "deploy=$2"

# Scan the full history of a pushed ref for secrets on GitHub
[positional-arguments]
gh-gitleaks ref=`git branch --show-current`:
    @test -n "$1" || { echo "error: HEAD is detached; pass a ref" >&2; exit 1; }
    gh workflow run gitleaks.yml --ref "$1"

# Label a pull request on GitHub from the paths it changes
[positional-arguments]
gh-labels pr:
    gh workflow run pr-labeler.yml -f "pr=$1"
