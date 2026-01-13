.PHONY: dev build preview lint format format-check check clean ci

# === Development ===

dev:
	bun run dev | tspin

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

# === Combined Workflows ===

# Fast CI: lint + format check + build (what you run before commits)
ci:
	bun run lint && bun run format:check && bun run build | tspin

# qa workflow for agent
qa:
	bun run lint && bun run format | tspin && bun run build | tspin

# Full workflow: lint, format, build, then dev
devall:
	bun run lint && bun run format | tspin && bun run build | tspin && bun run dev | tspin

# === Cleanup ===

clean:
	rm -rf dist node_modules/.cache .astro
