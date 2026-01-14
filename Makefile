# marking them .PHONY ensures they always execute when called.
.PHONY: dev build preview lint format format-check check clean ci

# === Development ===

# Full workflow: lint, format, build, then dev (user runs de server)
# user runs this locally
dev:
	bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin && bun run dev | tspin

# qa workflow for agent (without running server)
# this autoformat issues
qa:
	bun run lint && bun run format && bun run format:check | tspin && bun run build | tspin

# this do NOT autoformat
ci:
	bun run lint && bun run format:check && bun run build | tspin

preview:
	bun run preview | tspin

# === Build ===

build:
	bun run build | tspin

check:
	bun run sync && astro check | tspin

# === Code Quality ===

lint:
	bun run lint | tspin

format:
	bun run format | tspin

format-check:
	bun run format:check

# === Cleanup ===

clean:
	rm -rf dist node_modules/.cache .astro
