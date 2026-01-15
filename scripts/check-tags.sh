#!/usr/bin/env bash
# Check that all blog post tags follow kebab-case multi-line format
# Exit 1 if any violations found

set -euo pipefail

BLOG_DIR="src/data/blog"

# Verify rg is available
if ! command -v rg &>/dev/null; then
    echo "ERROR: ripgrep (rg) is required but not installed"
    exit 1
fi

errors=0

# Check for inline array format: tags: [...]
# rg returns exit 1 when no matches found - that's success for us
if inline_files=$(rg -l 'tags:\s*\[' "$BLOG_DIR" --glob '*.md' 2>/dev/null); then
    echo "ERROR: Inline array format found (use multi-line bullet format):"
    echo "$inline_files" | while read -r file; do
        echo "  - $file"
    done
    errors=$((errors + 1))
fi

# Check for non-kebab-case tags within frontmatter only
# Extract frontmatter, find tag lines, check format
for file in "$BLOG_DIR"/*.md "$BLOG_DIR"/**/*.md; do
    [[ -f "$file" ]] || continue

    # Extract frontmatter (between first two --- lines)
    frontmatter=$(awk '/^---$/{p++} p==1' "$file" 2>/dev/null)

    # Find tag values (lines starting with "  - " after "tags:")
    in_tags=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^tags: ]]; then
            in_tags=true
            continue
        fi
        if $in_tags; then
            if [[ "$line" =~ ^[[:space:]]+-[[:space:]]+ ]]; then
                # Extract tag value
                tag=$(echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*//')
                # Check if kebab-case (lowercase, hyphens, numbers only)
                if [[ ! "$tag" =~ ^[a-z0-9-]+$ ]]; then
                    echo "ERROR: Non-kebab-case tag in $file: $tag"
                    errors=$((errors + 1))
                fi
            else
                # No longer in tags section
                in_tags=false
            fi
        fi
    done <<< "$frontmatter"
done

if [[ $errors -gt 0 ]]; then
    echo ""
    echo "Fix with: uv run scripts/normalize-tags.py"
    exit 1
fi

echo "All tags follow kebab-case multi-line format"
exit 0
