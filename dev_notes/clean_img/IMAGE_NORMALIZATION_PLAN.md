# Image Normalization Plan

> Normalize image paths and filenames for Ghost → Astro migration

## Overview

| Step | Task | Impact |
|------|------|--------|
| 1 | Fix path prefix | Posts can find images |
| 2 | Fix broken references | No 404s on deleted duplicates |
| 3 | Rename to kebab-case | Clean, consistent filenames |
| 4 | Flatten structure (optional) | Simpler organization |

---

## Step 1: Fix Path Prefix

**Problem:** Posts use `/content/og-legacy/...` but images are at `/og-legacy/...`

**Solution:** Find & replace in all markdown files

```bash
# Preview changes (dry run)
rg "/content/og-legacy/" to_import/ --files-with-matches

# Apply fix
fd -e md . to_import/ -x sed -i '' 's|/content/og-legacy/|/og-legacy/|g' {}
```

**Test:**
```bash
bun run lint && bun run format:check && bun run build
```

**Commit:**
```bash
git add to_import/
git commit -m "🚑 fix: update image paths from /content/og-legacy to /og-legacy"
```

---

## Step 2: Fix Broken References

**Problem:** Some posts reference images that were deleted (duplicates)

**Solution:** Create a script to:
1. Extract all image references from markdown
2. Check if each referenced image exists
3. Find the correct source image (same base name)
4. Update the reference

```bash
uv run scripts/fix_broken_refs.py
```

**Test:**
```bash
bun run lint && bun run format:check && bun run build
```

**Commit:**
```bash
git add to_import/
git commit -m "🚑 fix: update broken image references to source images"
```

---

## Step 3: Rename Images to Kebab-Case

**Problem:** Filenames are messy:
- Mixed case: `IMG_2784.JPG`
- Timestamps: `pascalandy-com_header_2017-04-10_14h46.jpg`
- Underscores: `wolf_of_wall_street.jpg`
- Encoded accents: `Montre-al`

**Target format:** `kebab-case.jpg`
- All lowercase
- Hyphens instead of underscores
- No timestamps
- No special characters
- Extension lowercase

**Examples:**
| Before | After |
|--------|-------|
| `IMG_2784.JPG` | `img-2784.jpg` |
| `pascalandy-com_header_2017-04-10_14h46.jpg` | `pascalandy-com-header.jpg` |
| `CryptoInMontreal_Crypto-In-Montreal_par-Pascal-Andy.jpg` | `cryptoinmontreal-banner.jpg` |
| `Re-novation-Studio-Transology-092.jpg` | `renovation-studio-transology-092.jpg` |

**Solution:** Create a script to:
1. Generate new kebab-case filename for each image
2. Rename the file
3. Update all markdown references

```bash
uv run scripts/rename_to_kebab.py --dry-run  # Preview
uv run scripts/rename_to_kebab.py            # Apply
```

**Test:**
```bash
bun run lint && bun run format:check && bun run build
```

**Commit:**
```bash
git add public/og-legacy/ to_import/ src/data/blog/
git commit -m "♻️ refactor: rename images to kebab-case"
```

---

## Step 4: Flatten Folder Structure (Optional)

**Problem:** Images in `YYYY/MM/` folders from Ghost

**Current:**
```
public/og-legacy/
├── 2017/
│   ├── 04/
│   ├── 10/
│   └── 11/
├── 2018/
│   ├── 03/
│   └── ...
```

**Target:**
```
public/og-legacy/
├── cryptoinmontreal-banner.jpg
├── wolf-of-wall-street.jpg
└── ...
```

**Considerations:**
- Simpler structure
- But loses date context
- May have filename collisions (need to handle)

**Solution:** Only if desired - merge into Step 3 script

---

## Execution Order

```
Step 1: Fix path prefix
    ↓
    Test & Commit
    ↓
Step 2: Fix broken refs
    ↓
    Test & Commit
    ↓
Step 3: Rename to kebab
    ↓
    Test & Commit
    ↓
(Optional) Step 4: Flatten
    ↓
    Test & Commit
```

---

## Scripts to Create

1. `scripts/fix_broken_refs.py` - Find and fix broken image references
2. `scripts/rename_to_kebab.py` - Rename files and update references

Both scripts will:
- Support `--dry-run` flag to preview changes
- Generate a report of changes made
- Be idempotent (safe to run multiple times)
