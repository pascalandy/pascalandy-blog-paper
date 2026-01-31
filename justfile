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
    bun run sync && astro check | tspin

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
    rm -rf dist node_modules/.cache .astro

# Deep clean before archiving workspace (removes node_modules)
archive:
    rm -rf dist node_modules .astro
