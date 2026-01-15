#!/usr/bin/env bash
# Check that all blog post tags follow kebab-case multi-line format
# Exit 1 if any violations found

set -euo pipefail

BLOG_DIR="src/data/blog"
errors=0

# Check for inline array format: tags: [...]
inline_files=$(rg -l 'tags:\s*\[' "$BLOG_DIR" --glob '*.md' 2>/dev/null || true)
if [[ -n "$inline_files" ]]; then
    echo "ERROR: Inline array format found (use multi-line bullet format):"
    echo "$inline_files" | while read -r file; do
        echo "  - $file"
    done
    errors=$((errors + 1))
fi

# Check for non-kebab-case tags (uppercase, underscore, or space in tag values)
# Look for lines that are tag items:   - TagValue
bad_tags=$(rg -n '^\s+-\s+\S' "$BLOG_DIR" --glob '*.md' 2>/dev/null | \
    rg -v '^\s+-\s+[a-z0-9-]+$' | \
    rg '^\s+-\s+' 2>/dev/null || true)

if [[ -n "$bad_tags" ]]; then
    echo "ERROR: Non-kebab-case tags found (must be lowercase with hyphens only):"
    echo "$bad_tags" | head -20
    errors=$((errors + 1))
fi

if [[ $errors -gt 0 ]]; then
    echo ""
    echo "Fix with: uv run scripts/normalize-tags.py"
    exit 1
fi

echo "All tags follow kebab-case multi-line format"
exit 0
