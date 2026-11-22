#!/bin/bash
set -euo pipefail

tools_dir=${1:-/opt/blog-reader}
python3 -m venv "$tools_dir"
"$tools_dir/bin/pip" install --disable-pip-version-check playwright==1.56.0
PLAYWRIGHT_BROWSERS_PATH="$tools_dir/browsers" \
  "$tools_dir/bin/playwright" install --with-deps chromium
