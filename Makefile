# marking them .PHONY ensures they always execute when called.
.PHONY: dev build preview lint format format-check check check-tags clean ci qa

SHELL := /bin/bash

# === Development ===

# Full workflow: lint, format, build, then dev (user runs de server)
# user runs this locally
dev:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4320 | tspin

tree1:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4321 | tspin

tree2:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4322 | tspin

tree3:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4323 | tspin

tree4:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4324 | tspin

tree5:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev --port 4325 | tspin

# qa workflow for agent (without running server)
# this autoformat issues
qa:
	@set -o pipefail && bun run lint && bun run format && bun run format:check | tspin && ./scripts/check-tags.sh && bun run build | tspin

# this do NOT autoformat
ci:
	@set -o pipefail && bun run lint && bun run format:check && ./scripts/check-tags.sh && bun run build | tspin

preview:
	@set -o pipefail && bun run preview | tspin

# === Build ===

build:
	@set -o pipefail && bun run build | tspin

check:
	@set -o pipefail && bun run sync && astro check | tspin

# === Code Quality ===

lint:
	@set -o pipefail && bun run lint | tspin

format:
	@set -o pipefail && bun run format | tspin

format-check:
	bun run format:check

check-tags:
	@./scripts/check-tags.sh

# === Cleanup ===

clean:
	rm -rf dist node_modules/.cache .astro
