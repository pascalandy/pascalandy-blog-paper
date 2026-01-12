# Image Cleanup Guide

> Generated from `scripts/analyze_images.py` analysis

## Summary

| Category | Count | Size |
|----------|-------|------|
| Total images | 710 | 176.3 MB |
| Orphaned (unused) | 613 | 155.9 MB |
| Duplicate files | 206 | 37.6 MB |
| Used images | 97 | - |

---

## Test Command (run after each stage)

```bash
bun run lint && bun run format:check && bun run build
```

---

## Stage 1: Delete Orphaned Images

These 613 images are NOT referenced by any markdown post. Safe to delete.

### 1.1 Preview what will be deleted

```bash
# Count orphaned images
cat dev_notes/clean_img/image_analysis_report.json | uv run python -c "
import json, sys
data = json.load(sys.stdin)
orphaned = data.get('orphaned_images', [])
total_size = sum(img['size_bytes'] for img in orphaned)
print(f'Orphaned images: {len(orphaned)}')
print(f'Total size: {total_size / 1024 / 1024:.1f} MB')
"
```

### 1.2 Delete orphaned images

```bash
# Delete all orphaned images
cat dev_notes/clean_img/image_analysis_report.json | uv run python -c "
import json, sys
data = json.load(sys.stdin)
for img in data.get('orphaned_images', []):
    print(img['path'])
" | xargs rm -v
```

### 1.3 Clean up empty directories

```bash
# Remove empty directories in og-legacy
find public/og-legacy -type d -empty -delete
```

### 1.4 Run tests

```bash
bun run lint && bun run format:check && bun run build
```

### 1.5 Commit Stage 1

```bash
git add -A
git status
# Review changes, then:
git commit -m "chore: remove 613 orphaned images (155.9 MB)"
```

---

## Stage 2: Consolidate Duplicate Images

63 groups of duplicate images. For each group, keep the largest (source) and delete the rest.

**Important:** Some duplicates may be referenced in markdown. We need to:
1. Update markdown references to point to source image
2. Then delete duplicates

### 2.1 Preview duplicate groups

```bash
# Show top 10 duplicate groups by savings
cat dev_notes/clean_img/image_analysis_report.json | uv run python -c "
import json, sys
data = json.load(sys.stdin)
for i, group in enumerate(data.get('duplicate_groups', [])[:10], 1):
    print(f\"{i}. {group['base_name']}\")
    print(f\"   Source: {group['source_image']['path']}\")
    print(f\"   Duplicates: {len(group['duplicates'])}\")
    print(f\"   Savings: {group['potential_savings']}\")
    print()
"
```

### 2.2 Delete duplicate images (keeps source)

```bash
# Delete all duplicate images (source images are preserved)
cat dev_notes/clean_img/image_analysis_report.json | uv run python -c "
import json, sys
data = json.load(sys.stdin)
for group in data.get('duplicate_groups', []):
    for dup in group['duplicates']:
        print(dup['path'])
" | xargs rm -v
```

### 2.3 Clean up empty directories

```bash
find public/og-legacy -type d -empty -delete
```

### 2.4 Run tests

```bash
bun run lint && bun run format:check && bun run build
```

### 2.5 Commit Stage 2

```bash
git add -A
git status
# Review changes, then:
git commit -m "chore: remove 206 duplicate images (37.6 MB)"
```

---

## Stage 3: Verify and Final Cleanup

### 3.1 Re-run analysis to verify

```bash
uv run scripts/analyze_images.py
```

### 3.2 Check remaining image count

```bash
find public/og-legacy -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.webp" \) | wc -l
```

### 3.3 Check remaining size

```bash
du -sh public/og-legacy/
```

---

## Expected Results

After cleanup:

| Metric | Before | After |
|--------|--------|-------|
| Images | 710 | 78 |
| Size | 176.3 MB | 18 MB |
| Savings | - | 158 MB (89%) |

---

## Rollback (if needed)

If something breaks, revert to the previous commit:

```bash
git checkout HEAD~1 -- public/og-legacy/
```

Or reset the entire branch:

```bash
git reset --hard origin/main
```
