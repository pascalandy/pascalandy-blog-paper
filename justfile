# Bare `just` lists these in file order: the commands you run most, then checks.
# Each recipe is one line that calls one script or tool; logic lives in scripts/.
# Without just installed: uvx --from rust-just just <recipe>
set positional-arguments
# Every script and tool reports its own errors
set no-exit-message

[private]
default:
    @{{ just_executable() }} --list --unsorted

# Install dependencies; this also installs the git hooks
[group('commands')]
install *args:
    @bun install "$@"

alias i := install

# Start the dev server, on port 4320 unless given another; Pascal runs it, agents do not
[group('commands')]
dev port="4320" *args:
    @uv run --quiet scripts/pretty.py bun run dev --port "$@"

# Format, then run the verdict: the last step before a commit
[group('commands')]
qa: format check

# Format files, or the whole repo, with Prettier and ruff
[group('commands')]
format *files:
    @uv run --quiet scripts/tidy.py format "$@"

# Build the production site into dist/
[group('commands')]
build *args:
    @uv run --quiet scripts/pretty.py bun run build "$@"

# Serve the production build from dist/
[group('commands')]
preview *args:
    @uv run --quiet scripts/pretty.py bun run preview "$@"

# Delete build output and caches
[group('commands')]
clean:
    @rm -rf dist cache .astro

# Delete build output, caches, and dependencies before archiving a workspace
[group('commands')]
archive:
    @rm -rf dist cache .astro node_modules

# Run the same verdict as CI; --list names each check, --only NAME reruns one
[group('checks')]
check *args:
    @uv run --quiet scripts/check.py "$@"

alias ci := check

# Lint files, or the whole repo, with ESLint and ruff
[group('checks')]
lint *files:
    @uv run --quiet scripts/tidy.py lint "$@"

# Scan staged changes for secrets; lefthook runs it on every commit
[group('checks')]
gitleaks-staged:
    @gitleaks git --staged --no-banner --redact --log-level warn --verbose --no-color
