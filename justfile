# Bare `just` lists these in file order: the commands you run most, the checks,
# shipping, then the GitHub workflows, which run only by hand.
# Each recipe calls one script or tool; logic lives in scripts/.
# Without just installed: uvx --from rust-just just <recipe>
set positional-arguments
# Every script and tool reports its own errors
set no-exit-message

[private]
default:
    @{{ just_executable() }} --list --unsorted

# Print the blog's state: posts by bucket, tags, site, docs index; --json for one object
[group('commands')]
overview *args:
    @uv run --quiet scripts/overview.py "$@"

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
    @env -u GITLEAKS_CONFIG GITLEAKS_CONFIG_TOML="$(printf '[extend]\nuseDefault = true\n')" gitleaks git "$(git rev-parse --git-dir)" --staged --gitleaks-ignore-path /dev/null --ignore-gitleaks-allow --no-banner --redact --log-level warn --verbose --no-color

# Scan this branch's commits since origin/main for secrets
[group('checks')]
gitleaks:
    @env -u GITLEAKS_CONFIG GITLEAKS_CONFIG_TOML="$(printf '[extend]\nuseDefault = true\n')" gitleaks git "$(git rev-parse --git-dir)" --log-opts="origin/main..HEAD" --gitleaks-ignore-path /dev/null --ignore-gitleaks-allow --no-banner --redact --verbose

# Install, run `just ci` and `just gitleaks`, then mark the pushed HEAD green on GitHub; push first
[group('ship')]
signoff:
    @uv run --quiet scripts/signoff.py

# Verify that main requires the signoff status to merge; reads GitHub, changes nothing
[group('ship')]
signoff-check:
    @uv run --quiet scripts/signoff.py check

# Require the signoff status to merge into main, then verify it; once per repository
[group('ship')]
signoff-setup:
    @uv run --quiet scripts/signoff.py setup

# Deploy GitHub's main to production on Sevalla and wait for the build; --dry-run checks the setup
[group('ship')]
deploy *args:
    @uv run --quiet scripts/deploy.py production "$@"

# Deploy a pushed branch, the current one by default, to the Sevalla preview site
[group('ship')]
deploy-preview *args:
    @uv run --quiet scripts/deploy.py preview "$@"

# Run the CI workflow on GitHub for a pushed ref; deploy is none, preview, or production (main only)
[group('github')]
gh-ci ref=`git branch --show-current` deploy="none":
    @test -n "$1" || { echo "error: HEAD is detached; pass a ref" >&2; exit 1; }
    @test "$2" != production || test "$1" = main || { echo "error: production deploys only main" >&2; exit 1; }
    @gh workflow run ci.yml --ref "$1" -f "deploy=$2"

# Scan the full history of a pushed ref for secrets on GitHub
[group('github')]
gh-gitleaks ref=`git branch --show-current`:
    @test -n "$1" || { echo "error: HEAD is detached; pass a ref" >&2; exit 1; }
    @gh workflow run gitleaks.yml --ref "$1"

# Label a pull request on GitHub from the paths it changes
[group('github')]
gh-labels pr:
    @gh workflow run pr-labeler.yml -f "pr=$1"
