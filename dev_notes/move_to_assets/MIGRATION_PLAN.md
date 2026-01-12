# Migration Plan: Move Images to src/assets/

> Move images from `public/og-legacy/` to `src/assets/` for Astro build-time validation.

## Goal

When an image reference is broken, `bun run build` fails with a clear error instead of silently producing broken links.

---

## Current State

| Metric | Value |
|--------|-------|
| Images in `public/og-legacy/` | 97 |
| Orphaned images | 0 (already cleaned) |
| Broken refs | 0 (already fixed) |

### References to Update

**Frontmatter `ogImage` (9 posts):**

| Post | Current Path |
|------|--------------|
| `vinyl.md` | `/og-legacy/2021/11/vinyl-1.jpg` |
| `assetv-my-new-blockchain-project-idea.md` | `/og-legacy/2018/05/pascalandy-com_header_2017-04-10_14h46.jpg` |
| `au-fond-ce-que-je-tiens-a-partager.md` | `/og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg` |
| `appartement-a-louer-verdun.md` | `/og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg` |
| `andy-media.md` | `/og-legacy/2017/04/pascalandy-com_header_2017-04-10_14h46.jpg` |
| `analyste-daffaires-senior-ti.md` | `/og-legacy/2018/10/pascalandy-com_header_2017-04-10_14h46.jpg` |
| `analyste-daffaires-senior-t-i-bnc-banque-nationale-du-canada.md` | `/og-legacy/2018/10/pascalandy-com_header_2017-04-10_14h46-1.jpg` |
| `analyste-daffaires-bell-business-market-infrastructures-service.md` | `/og-legacy/2018/10/pascalandy-com_header_2017-04-10_14h46-2.jpg` |
| `10-ans-apres-star-academie-1-2003-les-retrouvailles.md` | `/og-legacy/2017/04/10_ans_star_academie-1462895695802.jpg` |

**Markdown inline `![]()` (2 posts):**

| Post | Image |
|------|-------|
| `au-revoir-guerriere.md` | `/og-legacy/2018/09/julie-marchand-2018-09-04-06h56.jpg` |
| `analyste-daffaires-senior-t-i-bnc-banque-nationale-du-canada.md` | `/og-legacy/2018/10/dispo-analyste-affaires-pascal.jpg` |

---

## Validation Behavior (Tested)

| Reference Type | Current (public/) | After (src/assets/) |
|----------------|-------------------|---------------------|
| Markdown `![](path)` | No validation | **Build fails if missing** |
| Frontmatter `ogImage` | No validation | **Build fails if missing** (requires schema fix) |

### Schema Fix Required

Change `src/content.config.ts` line 16:

```typescript
// Before (string matches first, no validation)
ogImage: z.string().or(image()).optional(),

// After (image() validates first, string as fallback for remote URLs)
ogImage: image().or(z.string()).optional(),
```

---

## Migration Steps

### Step 1: Move Images

```bash
# Copy images preserving directory structure
cp -r public/og-legacy/ src/assets/images/og-legacy/
```

**Result:**
```
src/assets/images/og-legacy/
├── 2017/
│   ├── 04/
│   ├── 10/
│   ├── 11/
│   └── 12/
├── 2018/
│   ├── 01/
│   ├── 03/
│   ├── ...
│   └── 11/
├── 2019/
│   ├── 01/
│   ├── ...
│   └── 11/
└── ...
```

---

### Step 2: Update Schema

Edit `src/content.config.ts`:

```typescript
ogImage: image().or(z.string()).optional(),
```

---

### Step 3: Update Frontmatter ogImage Paths

**Pattern:**
```yaml
# Before
ogImage: "/og-legacy/2021/11/vinyl-1.jpg"

# After
ogImage: ../../assets/images/og-legacy/2021/11/vinyl-1.jpg
```

**Files to update (9):**
- `src/data/blog/vinyl.md`
- `src/data/blog/assetv-my-new-blockchain-project-idea.md`
- `src/data/blog/au-fond-ce-que-je-tiens-a-partager.md`
- `src/data/blog/appartement-a-louer-verdun.md`
- `src/data/blog/andy-media.md`
- `src/data/blog/analyste-daffaires-senior-ti.md`
- `src/data/blog/analyste-daffaires-senior-t-i-bnc-banque-nationale-du-canada.md`
- `src/data/blog/analyste-daffaires-bell-business-market-infrastructures-service.md`
- `src/data/blog/10-ans-apres-star-academie-1-2003-les-retrouvailles.md`

---

### Step 4: Update Markdown Inline Images

**Pattern:**
```markdown
# Before
![alt](/og-legacy/2018/10/image.jpg)

# After
![alt](../../assets/images/og-legacy/2018/10/image.jpg)
```

**Files to update (2):**
- `src/data/blog/au-revoir-guerriere.md`
- `src/data/blog/analyste-daffaires-senior-t-i-bnc-banque-nationale-du-canada.md`

---

### Step 5: Verify Build

```bash
bun run build
```

**Expected:** Build succeeds with all images resolved.

---

### Step 6: Test Validation (Optional)

Temporarily break an image reference and verify build fails:

```bash
# Edit any post to reference non-existent image
# Run build - should fail with:
# [ImageNotFound] Could not find requested image `path`. Does it exist?
```

---

### Step 7: Delete Old Location

```bash
rm -rf public/og-legacy/
```

---

### Step 8: Final Build & Commit

```bash
bun run build
git add -A
git commit -m "refactor: move images to src/assets for build-time validation"
```

---

## Rollback

If something breaks:

```bash
# Restore old images
git checkout HEAD~1 -- public/og-legacy/

# Revert schema change
git checkout HEAD~1 -- src/content.config.ts

# Revert markdown changes
git checkout HEAD~1 -- src/data/blog/
```

---

## Notes

### Why Relative Paths?

- Astro's `image()` schema doesn't support `@/` alias in frontmatter
- Relative paths like `../../assets/images/...` work correctly
- All posts in `src/data/blog/` use the same relative path depth

### What Gets Validated?

1. **Frontmatter `ogImage`** - via `image()` schema helper
2. **Markdown `![]()` images** - native Astro processing

### What Doesn't Get Validated?

- Remote URLs (https://...) - passed through as strings
- Images in `public/` - copied as-is, no processing

---

## References

- [Astro Images Guide](https://docs.astro.build/en/guides/images/)
- [Content Collections Schema](https://docs.astro.build/en/guides/content-collections/)
- Previous cleanup: `dev_notes/clean_img/IMAGE_CLEANUP_GUIDE.md`
