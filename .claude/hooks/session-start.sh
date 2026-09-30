#!/bin/bash
# Bootstrap a Claude Code web session: uv, just, gitleaks, then the
# dependencies, which install the git hooks. Safe to rerun; local sessions skip it.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

UV_VERSION="0.12.19"
JUST_VERSION="1.50.0"
GITLEAKS_VERSION="8.30.1"
BIN="$HOME/.local/bin"

mkdir -p "$BIN"
export PATH="$BIN:$PATH"
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  line="export PATH=\"$BIN:\$PATH\""
  grep -qxF "$line" "$CLAUDE_ENV_FILE" 2>/dev/null || echo "$line" >>"$CLAUDE_ENV_FILE"
fi

# Download a release archive into $archive and check its pinned SHA-256
fetch() {
  archive="$(mktemp)"
  curl -fsSL --retry 4 --retry-all-errors -o "$archive" "$1"
  echo "$2  $archive" | sha256sum --check --quiet
}

# Every recipe runs its script through uv, so uv comes first
if ! command -v uv >/dev/null 2>&1; then
  case "$(uname -m)" in
    x86_64) target="x86_64-unknown-linux-musl" sum="db7278c9f57981338fddff1fb250e11964bc0a4fafcb9eed8303fdb117dc067b" ;;
    aarch64 | arm64) target="aarch64-unknown-linux-musl" sum="ad8d8448a2ff642ba62c2f684d7dd22a03f8eb3fc9918c2c3e8ec975f4ed6710" ;;
    *) echo "session-start: no uv build for $(uname -m); install uv (https://docs.astral.sh/uv/)" >&2 && exit 1 ;;
  esac
  fetch "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$target.tar.gz" "$sum"
  tar -xzf "$archive" -C "$BIN" --strip-components=1 "uv-$target/uv" "uv-$target/uvx"
  rm -f "$archive"
fi

if ! command -v just >/dev/null 2>&1; then
  uv tool install --quiet "rust-just@$JUST_VERSION" ||
    npm install --global --silent "rust-just@$JUST_VERSION"
fi

if ! command -v gitleaks >/dev/null 2>&1; then
  case "$(uname -m)" in
    x86_64) arch="x64" sum="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb" ;;
    aarch64 | arm64) arch="arm64" sum="e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080" ;;
    *) echo "session-start: no gitleaks build for $(uname -m); install it before committing" >&2 && exit 1 ;;
  esac
  fetch "https://github.com/gitleaks/gitleaks/releases/download/v$GITLEAKS_VERSION/gitleaks_${GITLEAKS_VERSION}_linux_$arch.tar.gz" "$sum"
  tar -xzf "$archive" -C "$BIN" gitleaks
  rm -f "$archive"
fi

cd "$CLAUDE_PROJECT_DIR"
bun install --silent
