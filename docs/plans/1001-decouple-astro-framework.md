---
date: 2026-03-30
topic: decouple-astro-framework-from-content
status: ready-for-planning
---

# Decouple Astro Framework from Content

## Problem Frame

Currently, the Astro blog framework and content (Markdown posts, images, configuration) live in the same repository. This creates friction for content creators who want to "push content and forget" without seeing framework code. The goal is to separate concerns:

- **blog-core**: The Astro framework, components, themes, build system
- **cms-md**: Pure content—Markdown posts, images, and minimal configuration

Anyone should be able to clone blog-core, point it at any cms-md repo, and have a working blog without touching framework code.

## Requirements

- **Clean Separation**: Framework code and content must live in separate Git repositories
- **Push-and-Forget Workflow**: Pushing content to cms-md automatically triggers a rebuild and deployment
- **Zero Framework Exposure**: Content creators never see or modify Astro/Tailwind/TypeScript code
- **Template-Based Onboarding**: Users fork cms-md template, configure it, and have a working blog
- **Content Contract**: cms-md provides a predictable structure (posts/, assets/, config.yaml) that blog-core consumes
- **Multi-Tenant Architecture**: ONE blog-core serves THOUSANDS of cms-md repos via reusable workflows
- **Centralized Updates**: Updating blog-core automatically propagates to all cms-md repos on next build
- **Multiple Visual Frameworks**: Support multiple blog-core variants (classic, fanta, yellow, etc.) with different design philosophies

## Success Criteria

- [ ] Pushing content to any cms-md repo triggers build within 2 minutes
- [ ] cms-md template can be forked and deployed without touching framework code
- [ ] One blog-core update affects all cms-md repos on their next build
- [ ] Thousands of cms-md repos can coexist, each with isolated deployments
- [ ] New user goes from "fork cms-md template" to "live site" in under 10 minutes
- [ ] User can switch blog-core variants (classic → fanta → yellow) by changing one line
- [ ] Each blog-core variant has its own themes and design philosophy

## Scope Boundaries

- **In Scope (Phase 0-4)**: Repository separation, reusable GitHub Actions workflow, content contract, personal blog migration, template repository setup, content validation, documentation
- **In Scope (Evolution)**: Local preview, image optimization via remark plugin, additional blog-core variants, multi-tenant workflow stability
- **Out of Scope**: Content editing UI, headless CMS integration (Strapi, etc.), custom domain management, user authentication, variant marketplace/discovery

## Key Decisions

- **Architecture Pattern**: Reusable GitHub Actions workflow + Multiple blog-core variants
  - *Rationale*: blog-core provides a reusable workflow that all cms-md repos call. Each cms-md has its own build and deployment, but uses shared blog-core logic. Multiple variants (classic, fanta, yellow, etc.) allow different visual frameworks to evolve independently.
  
- **Template Repository**: cms-md is a GitHub template repo
  - *Rationale*: Users fork the template, add their content, and the included workflow calls their chosen blog-core variant. Zero framework code in their repo.
  
- **Content Contract**: cms-md provides predictable structure
  - *Rationale*: Each blog-core variant expects specific directories and config files. This decouples content from implementation. Variants may extend the base contract (e.g., fanta might require `hero_image` field).
  
- **Isolated Deployments**: Each cms-md deploys independently
  - *Rationale*: Scales to thousands of users without shared infrastructure complexity. Each user owns their deployment target (Sevalla, Vercel, etc.).
  
- **Versioning Strategy**: Always use `@main` by default, with escape hatch to pin
  - *Rationale*: All cms-md repos automatically get latest updates for their chosen variant. Users can pin to specific versions if needed. Multiple variants reduce pressure on any single repo.
  
- **No Force-Rebuild Mechanism**: Not needed
  - *Rationale*: cms-md repos rebuild on their own schedule (content pushes). If they need latest blog-core immediately, they can trigger a manual rebuild. No centralized orchestration required.

- **Image Strategy**: Serve from `public/` now, add Astro optimization later via remark plugin
  - *Rationale*: Phase 1 copies images to `public/blog-img/` and serves them as-is (no optimization). This is simple and works. Later, blog-core adds a remark plugin that rewrites `![alt](/blog-img/x.jpg)` into Astro's `<Image>` component and moves images from `public/` to `src/assets/` during the overlay step. This restores full Astro optimization (responsive breakpoints, WebP, lazy loading) without any change to cms-md. The key guarantee: cms-md image paths never change. Optimization is a blog-core internal concern.

- **File Naming**: Slug-based filenames, no date prefix required
  - *Rationale*: The date is already in frontmatter (`date_created`). Forcing it into the filename is redundant and would break all ~185 existing URLs during migration. Filenames like `vinyl.md`, `lhorizon-cest-toi.md` produce clean URLs (`/blog/vinyl/`, `/blog/lhorizon-cest-toi/`). Subdirectories are supported and preserved in URLs (e.g., `dev_workflows/image_path.md` → `/blog/dev_workflows/image_path/`).

- **Config Ownership**: All user-specific config lives in cms-md's `site.yaml`
  - *Rationale*: Social links, share links, and tag configuration are personal to each site. Putting them in `site.yaml` means content creators control everything about their site from one file. blog-core reads these during config generation and provides sensible defaults for anything missing.

- **Variant Phasing**: Design for multiple variants, build only classic in Phase 1
  - *Rationale*: Keep the architecture variant-aware (don't hardcode assumptions that there's only one blog-core), but only build the classic variant initially. Fanta/yellow are separate projects after the core decoupling is proven. Copying the repo to create a new variant is low friction.

- **Pages Routing**: Dynamic route in blog-core via pages content collection
  - *Rationale*: blog-core defines a `pages` content collection and a catch-all route (`src/pages/[...slug].astro`) that renders any markdown page from cms-md. Content creators write plain markdown in `cms-md/pages/` (e.g., `about.md`, `now.md`) with no Astro-specific frontmatter. blog-core owns layout assignment—all pages use a `PageLayout` by default, with an optional `layout` frontmatter field that maps to blog-core layout names (e.g., `layout: "about"` → blog-core's `AboutLayout`). This keeps cms-md free of framework code while giving blog-core full control over presentation.

## Architecture

### Repository Structure

**blog-core** (Phase 1 -- Classic variant only)

Only the classic variant is built in Phase 1. The architecture supports multiple variants (fanta, yellow, etc.) but they are deferred to the Evolution roadmap.

```
blog-core/                    # Classic - Traditional, battle-tested
├── .github/workflows/
│   └── build-blog.yml        # Reusable workflow
├── src/
│   ├── components/           # Classic components
│   ├── layouts/              # Classic layouts
│   ├── pages/                # Route definitions
│   └── themes/               # Classic themes (caffeine, elegant-luxury, claude)
└── README.md                 # "Use me for traditional blogs"
```

**cms-md** (Content - Template Repository)
```
cms-md/
├── README.md                          # User guide: how to add content
├── LICENSE                            # MIT (template default)
├── justfile                           # Just commands (validate, format, etc.)
├── lefthook.yml                       # Git hooks for pre-commit validation
│
├── .github/
│   └── workflows/
│       └── deploy.yml                 # Calls blog-core reusable workflow
│
├── blog/                              # Blog posts (slug-based filenames)
│   ├── hello-world.md
│   ├── my-second-post.md
│   ├── vinyl.md
│   ├── lhorizon-cest-toi.md
│   ├── dev_workflows/                 # Subdirectories preserved in URL
│   │   ├── image_path.md
│   │   └── worktree-workflow.md
│   └── drafts/                        # Draft posts (_prefix = ignored)
│       └── _unfinished-post.md
│
├── blog-img/                          # Blog post images
│   ├── hello-world-hero.jpg
│   ├── hello-world-diagram.png
│   ├── vinyl-cover.jpg
│   └── lhorizon-cest-toi-banner.jpg
│
├── pages/                             # Static pages (flat)
│   ├── about.md
│   ├── now.md
│   ├── uses.md
│   └── subscribe.md
│
├── pages-img/                         # Page images (flat)
│   ├── about-portrait.jpg
│   └── uses-workspace.jpg
│
├── scripts/                           # Validation scripts
│   └── validate-content.sh            # Frontmatter validation
│
└── system/                            # Configuration & assets (rarely touched)
    ├── config/
    │   └── site.yaml                  # Site metadata, theme, socials, tags
    └── assets/
        ├── og/                        # Open Graph images
        │   └── default.jpg
        ├── static/                    # Logo, favicon
        │   ├── logo.svg
        │   └── favicon.png
        ├── fonts/                     # Custom fonts (optional)
        └── files/                     # Downloadable files
            └── resume.pdf
```

### CI/CD Flow (Reusable Workflow Pattern)

```
Push to any cms-md repo
         ↓
cms-md workflow runs (deploy.yml)
         ↓
Calls reusable workflow from blog-core:
   uses: owner/blog-core/.github/workflows/build-blog.yml@main
         ↓
Reusable workflow runs in cms-md context:
   1. Checkout blog-core (framework code) → ./framework/
   2. Checkout cms-md (content) → ./content/
   3. Merge content into framework:
      - Copy ./content/blog/ → ./framework/src/data/blog/
      - Copy ./content/pages/ → ./framework/src/content/pages/
      - Copy ./content/blog-img/ → ./framework/public/blog-img/
      - Copy ./content/pages-img/ → ./framework/public/pages-img/
      - Copy ./content/system/assets/ → ./framework/public/assets/
      - Generate ./framework/src/config.ts from ./content/system/config/site.yaml
      - Generate ./framework/src/tags.ts from tags section of site.yaml
      - Generate ./framework/src/constants.ts from socials/share_links sections
   4. Build Astro site in ./framework/
   5. Run Pagefind indexing on ./framework/dist/
   6. Deploy dist/ to user's target (Sevalla, etc.)
```

**Critical Implementation Details:**
- **Content Overlay**: Content is copied into framework directories, not symlinked (works across all platforms)
- **Blog Content Path**: Posts copy to `src/data/blog/` (matching current Astro content loader config)
- **Pages Content Path**: Pages copy to `src/data/pages/`. blog-core defines a `pages` content collection + dynamic route `src/pages/[...slug].astro`. Layout assignment via optional `layout` frontmatter field (defaults to `PageLayout`).
- **Image Handling (Phase 1)**: Images copied to `public/` and served as-is (no optimization). See Evolution section for remark plugin upgrade path.
- **Pagefind**: Search indexing runs after Astro build (`pagefind --site dist`), same as current build chain
- **Dynamic OG Images**: blog-core generates OG images per post via satori + resvg-js at build time (existing feature, stays in blog-core)
- **Config Generation**: YAML → TypeScript config conversion happens during build (generates config.ts, tags.ts, constants.ts)
- **Working Directory**: All operations happen in cms-md's GitHub Actions runner
- **Isolation**: Each build is completely isolated—no shared state between cms-md repos

**Why this works for thousands of users:**
- Each cms-md has its own GitHub Actions minutes and deployment
- blog-core updates automatically propagate (users get latest workflow)
- No shared infrastructure to manage
- Each user configures their own deployment target in cms-md secrets
- Breaking changes in blog-core affect all users simultaneously (acceptable trade-off for simplicity)

### cms-md deploy.yml (Template Workflow)

Each cms-md repo includes this minimal workflow. Users choose their blog-core variant by changing the `uses:` line:

```yaml
# .github/workflows/deploy.yml
name: Deploy Blog

on:
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    # CHOOSE YOUR VARIANT:
    
    # Option 1: Classic (traditional, battle-tested)
    uses: pascalandy/blog-core/.github/workflows/build-blog.yml@main
    
    # Option 2: Fanta (colorful, playful, modern)
    # uses: pascalandy/blog-core-fanta/.github/workflows/build-blog.yml@main
    
    # Option 3: Yellow (minimalist, typography-focused)
    # uses: pascalandy/blog-core-yellow/.github/workflows/build-blog.yml@main
    
    # Option 4: Pin to specific version
    # uses: pascalandy/blog-core/.github/workflows/build-blog.yml@v2.1.0
    
    secrets:
      SEVALLA_TOKEN: ${{ secrets.SEVALLA_TOKEN }}
      SEVALLA_STATIC_SITE_ID: ${{ secrets.SEVALLA_STATIC_SITE_ID }}
```

**Key Points:**
- Single line chooses your visual framework (classic, fanta, yellow, etc.)
- No framework code in cms-md
- Secrets passed through to reusable workflow
- Users can customize triggers (e.g., add `paths:` filter for specific directories)
- Switching variants = changing one line and pushing

### Content Contract

**cms-md must provide:**

1. **Directory Structure** (Base contract)
   ```
   justfile                 # Required: Just commands (validate, format)
   lefthook.yml             # Required: Git hooks for pre-commit validation
   blog/                    # Required: Blog posts (slug-based, subdirs allowed)
   blog/drafts/             # Optional: Draft posts (_prefix = ignored)
   blog-img/                # Required: Blog images
   pages/                   # Optional: Static pages (flat)
   pages-img/               # Optional: Page images (flat)
   scripts/                 # Required: Validation scripts
   system/config/           # Required: Site configuration
   system/assets/og/        # Optional: Open Graph images
   system/assets/static/    # Optional: Site-wide images
   system/assets/fonts/     # Optional: Custom fonts
   system/assets/files/     # Optional: Downloadable files
   ```

2. **File Naming Convention**
   - Blog posts: `slug.md` (e.g., `vinyl.md`, `lhorizon-cest-toi.md`). No date prefix -- date comes from frontmatter `date_created`.
   - Blog subdirectories: supported, preserved in URL (e.g., `dev_workflows/image_path.md` → `/blog/dev_workflows/image_path/`)
   - Blog images: `slug-descriptor.ext` (e.g., `vinyl-cover.jpg`, `hello-world-hero.jpg`)
   - Drafts: `_slug.md` in `blog/drafts/` (underscore prefix = ignored)
   - Pages: `slug.md` (e.g., `about.md`)
   - Page images: `slug-descriptor.ext` (e.g., `about-portrait.jpg`)

3. **Frontmatter Schema** (Base contract)
   ```yaml
   ---
   # Required
   author: string
   date_created: date
   title: string
   tags: string[]            # min 1 tag
   description: string

   # Optional
   featured?: boolean
   draft?: boolean
   ogImage?: string          # Path: /blog-img/hello-world-hero.jpg
   canonicalURL?: string     # Canonical URL for syndicated content
   hideEditPost?: boolean    # Hide "edit this post" link
   mermaid?: boolean         # Enable Mermaid diagram rendering (default: false)
   ---
   ```

4. **Variant-Specific Frontmatter Extensions** (Deferred -- see Evolution section)
   
   Each blog-core variant may define additional optional frontmatter fields. These are not part of the base contract and are ignored by variants that don't use them. Deferred to when additional variants are built.

5. **Site Configuration** (system/config/site.yaml)
   ```yaml
   site:
     title: "Blog Title"
     author: "Author Name"
     profile: "https://example.com/"
     description: "Site description"
     website: "https://example.com/blog/"
     ogImage: "pascalandy_banner.jpg"    # Default OG image in system/assets/static/
     lang: "en"
     dir: "ltr"
     timezone: "America/Montreal"
   
   theme:
     name: "claude"        # Must match theme in your chosen blog-core variant
   
   posts:
     perPage: 20
     perIndex: 4
     scheduledPostMargin: 15    # Minutes before date_created to make post visible
     dynamicOgImage: true       # Generate OG images for posts without ogImage
   
   features:
     rss: true
     sitemap: true
     darkMode: true
     search: true
     showBackButton: true
     editPost:
       enabled: false
       # text: "Edit page"
       # url: "https://github.com/..."
   
   socials:                     # Social links shown on site
     - name: "X"
       href: "https://x.com/username"
       label: "X"
       active: true
     - name: "LinkedIn"
       href: "https://linkedin.com/in/username"
       label: "LinkedIn"
       active: true
     - name: "GitHub"
       href: "https://github.com/username"
       label: "GitHub"
       active: true
   
   share_links:                 # Share buttons on posts
     - name: "WhatsApp"
       active: true
     - name: "Facebook"
       active: true
     - name: "X"
       active: true
     - name: "Telegram"
       active: true
     - name: "Mail"
       active: true
   
   tags:                        # Tag behavior configuration
     - slug: "dev-notes"
       name: "Dev Notes"
       description: "Development workflow documentation"
       excludeFromBlogRoll: true
     - slug: "random"
       name: "Random"
       description: "Random thoughts"
     # Tags not listed here get default behavior (visible everywhere)
     # Available options per tag:
     #   hiddenFromTagsPage: true    # Hide from /tags/ listing
     #   excludeFromBlogRoll: true   # Exclude from blog roll and RSS
   
   deployment:
     target: "sevalla"     # or "vercel", "netlify", etc.
   ```

6. **GitHub Secrets** (configured by user)
   - `SEVALLA_TOKEN` (or platform-specific token)
   - `SEVALLA_STATIC_SITE_ID` (or platform-specific ID)

## Dependencies / Assumptions

- Both repos hosted on GitHub (for reusable workflows)
- cms-md repos are public or have workflow permissions to call blog-core variants
- blog-core variants are public (so reusable workflows are accessible)
- Users configure their own deployment platform credentials as GitHub secrets
- Astro can be configured to load content from a configurable path
- Users accept that blog-core updates may introduce breaking changes (mitigated by testing)
- Each blog-core variant maintains backward compatibility within major versions

## Use Cases

### Switch Visual Framework (Look & Feel) -- Future, see Evolution
**As a user, I want to completely change my website's design without rewriting content**

**Current State:**
- You have a blog using `blog-core` (classic, traditional design)
- Your content is in `blog/` and `pages/`
- Everything works

**Desired Change:**
You want a more colorful, modern look (fanta variant)

**How You Do It:**

**Option A: Try Fanta (One Line Change)**
```yaml
# Edit .github/workflows/deploy.yml in your cms-md repo
# Before:
uses: pascalandy/blog-core/.github/workflows/build-blog.yml@main

# After:
uses: pascalandy/blog-core-fanta/.github/workflows/build-blog.yml@main
```
Push this change → Your site rebuilds with Fanta design → Content unchanged

**Option B: Try Yellow (Minimalist)**
```yaml
uses: pascalandy/blog-core-yellow/.github/workflows/build-blog.yml@main
```

**Option C: Pin to Specific Version (Stability)**
```yaml
uses: pascalandy/blog-core/.github/workflows/build-blog.yml@v2.1.0
```

**What Happens:**
1. Your Markdown files stay exactly the same
2. Your images stay exactly the same
3. Your config stays exactly the same
4. Only the visual framework changes (components, layouts, themes)
5. Build takes 2 minutes
6. Your site has a completely new look

**Result**: Change your entire website design by editing one line. No content migration. No framework code to touch. Just pick a different visual framework.

---

### Content Creator Workflow
**As a content creator, I want to write posts without seeing framework code**

**Your Daily Workflow:**
1. Open `blog/` folder
2. Create `my-new-post.md` (slug-based filename, date in frontmatter)
3. Add images to `blog-img/`
4. Reference images in markdown: `![alt](/blog-img/my-new-post-hero.jpg)`
5. `git add . && git commit -m "new post" && git push`
6. Site deploys automatically in 2 minutes

**You Never See:**
- Astro configuration
- Tailwind CSS
- TypeScript components
- Node modules
- Build scripts

**Result**: Pure content editing. Framework is invisible.

---

### First-Time Setup
**As a new user, I want to go from zero to live blog in 10 minutes**

**Steps:**
1. **Fork** the `cms-md` template (1 minute)
2. **Enable** GitHub Actions in your fork (1 minute)
3. **Add** deployment secrets (SEVALLA_TOKEN, etc.) (2 minutes)
4. **Edit** `system/config/site.yaml` with your info (2 minutes)
5. **Push** a test post to `blog/` (2 minutes)
6. **Watch** it deploy automatically (2 minutes)

**Total Time**: ~10 minutes

**Result**: Live website with your content, your design, your domain.

---

## Risks & Mitigations

### Content Validation
**Risk**: Invalid frontmatter (missing required fields, wrong types) could break builds  

**Solution - Local Validation in cms-md:**
Just like your current repo uses `lefthook` + `just` for pre-commit validation, the cms-md template will include:

```yaml
# lefthook.yml (in cms-md template)
pre-commit:
  parallel: true
  jobs:
    - name: validate-frontmatter
      run: just validate
      fail_text: "Invalid frontmatter found. Check required fields."
```

```bash
# justfile (in cms-md template)
validate:
    # Validate all blog posts have required frontmatter
    ./scripts/validate-content.sh

validate-post POST:
    # Validate single post
    ./scripts/validate-content.sh {{POST}}
```

**What This Gives You:**
- **Before commit**: Lefthook runs `just validate` automatically
- **Catches errors early**: Missing `title`, invalid `date_created`, etc.
- **Fast feedback**: Know about problems before pushing
- **CI backup**: blog-core also validates in CI as safety net

**Example Error (Local):**
```
❌ Content validation failed:
   blog/2024-01-01-my-post.md: Missing required field 'title'
   blog/2024-01-01-my-post.md: 'date_created' must be in YYYY-MM-DD format

Fix these issues before committing.
```

**Who Handles What:**
- **cms-md**: You get local validation via lefthook + just (catches errors before commit)
- **blog-core**: CI validation as backup (safety net if local validation bypassed)

**Result**: Content validation happens locally (fast feedback) AND in CI (safety net). Same pattern you use now with `just qa` and lefthook.

## Outstanding Questions

### Resolved (Review Decisions)
- **Content overlay**: Copy, not symlink (cross-platform). Blog posts → `src/data/blog/`, images → `public/blog-img/`.
- **Config consumption**: Generate `config.ts`, `tags.ts`, `constants.ts` from `site.yaml` during build.
- **Image optimization**: Serve from `public/` in Phase 1. Remark plugin upgrade in Evolution.
- **File naming**: Slug-based, no date prefix. Date from frontmatter only.
- **Config ownership**: All user config (socials, share_links, tags) in cms-md `site.yaml`.
- **Variant phasing**: Design for variants, build only classic in Phase 1.
- **Local preview**: Deferred to Evolution (not needed while sole user).
- **Content validation**: Local via lefthook + just. CI as safety net.
- **Pages routing**: Dynamic route in blog-core via pages content collection + `[...slug].astro` catch-all.

### Deferred to Planning
- Should we support multiple deployment targets (Sevalla, Vercel, Netlify) in one workflow or separate workflows?
- How to handle build caching across thousands of independent repos?
- How to handle missing/invalid themes gracefully?
- How to validate cms-md setup on first run (secrets check, structure validation)?
- Config generation script: exact implementation (shell script, Node script, or Astro integration?)

## Documentation Notes (For cms-md README)

### Build Cost Awareness
**Section to include in cms-md template README:**

```markdown
## ⚠️ Build Cost Awareness

Each time you push content, GitHub Actions builds your site. Be aware of your usage:

**GitHub Free Tier:**
- 2,000 minutes/month included
- ~2 minutes per build
- 50 pushes/day = ~3,000 minutes/month = ~$8 overage

**Tips to minimize costs:**
1. **Batch your pushes**: Write multiple posts locally, push once
2. **Use paths filter**: Edit `.github/workflows/deploy.yml`:
   ```yaml
   on:
     push:
       paths:
         - 'blog/**'
         - 'pages/**'
   ```
3. **Draft locally**: Use `blog/drafts/` folder for work-in-progress

**Upgrade options:**
- GitHub Pro ($4/month): 3,000 minutes/month
- Self-host: Fork blog-core and run on your own infrastructure
```

### Repository Configuration
**Section to include in cms-md template README:**

```markdown
## 🔒 Private Repository Setup

By default, the cms-md template works immediately as a public repository. If you want a private repo:

**One-time setup:**
1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"
4. Save

**Note**: Public repos work without any configuration. Private repos need this one-time settings change.
```

### GitHub Actions Setup
**Section to include in cms-md template README:**

```markdown
## ⚙️ GitHub Actions Setup

When you fork the cms-md template, GitHub Actions is disabled by default. Here's how to enable it:

**Step 1: Enable Actions**
1. Go to Settings → Actions → General
2. Under "Actions permissions", select "Allow all actions and reusable workflows"
3. Save

**Step 2: Add Deployment Secrets**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add your deployment credentials:
   - `SEVALLA_TOKEN` (from your Sevalla dashboard)
   - `SEVALLA_STATIC_SITE_ID` (from your Sevalla dashboard)

**Step 3: Push Content**
```bash
git add .
git commit -m "Initial content"
git push
```

Your site will build and deploy automatically!

**Troubleshooting:**
If your build fails with "Missing secret", double-check Step 2 above.
```

## Migration Path

Start small, prove the pattern, then scale. Each phase must work end-to-end before starting the next.

1. **Phase 0 -- Hello World proof-of-concept**
   - Create `blog-core` repo with minimal Astro framework (one layout, one theme, one page)
   - Create `.github/workflows/build-blog.yml` (reusable workflow)
   - Create `cms-md` repo with a single "Hello World" post and minimal `site.yaml`
   - Prove end-to-end: push to cms-md → reusable workflow triggers → site builds → deploys
   - Goal: validate the reusable workflow + content overlay pattern works

2. **Phase 1 -- Migrate personal blog to blog-core**
   - Extract full framework code from current repo into `blog-core`
   - All components, layouts, themes (caffeine, elegant-luxury, claude), pages routing
   - Pagefind integration, dynamic OG image generation, RSS, sitemap
   - Config generation script (YAML → config.ts, tags.ts, constants.ts)
   - Test with Hello World cms-md to verify nothing broke

3. **Phase 2 -- Migrate personal content to cms-md**
   - Extract ~185 posts from `src/data/blog/` to `cms-md/blog/` (preserve filenames)
   - Extract images from `src/assets/images/` to `cms-md/blog-img/`
   - Rewrite image paths in posts (`../../assets/images/...` → `/blog-img/...`)
   - Create `site.yaml` from current `config.ts`, `tags.ts`, `constants.ts`
   - Extract pages (`a-propos.md`, `maintenant.md`, etc.) to `cms-md/pages/`
   - Deploy personal blog from cms-md → verify URL parity with current site

4. **Phase 3 -- Harden and template-ize**
   - Add content validation (lefthook + just + validate-content.sh) to cms-md
   - Add CI validation as safety net in blog-core's reusable workflow
   - Mark cms-md as GitHub template repository
   - Write "Getting Started" guide for new users
   - Document content contract

5. **Phase 4 -- Documentation**
   - Document deployment configuration (Sevalla, Vercel, Netlify)
   - Build cost awareness guide
   - Private repository setup guide
   - GitHub Actions setup guide

## Evolution (Post-Phase 4)

Items deferred from initial scope. Each is independent and can be prioritized based on need.

### Local Preview for Content Creators
**Problem**: Content creators with only cms-md have no way to preview their site locally. They must push and wait ~2 minutes for the CI build.

**Solution (when needed)**: cms-md's `justfile` includes a `just dev` recipe that:
1. Clones blog-core into a temporary directory (or uses a cached copy)
2. Runs the same content overlay step the CI does (copy blog/ → src/data/blog/, etc.)
3. Runs `astro dev` inside the framework directory
4. Content creator sees their site at `localhost:4320`

**Prerequisite**: Requires Node/bun installed locally. Acceptable trade-off since this is opt-in for users who want local preview.

**Priority**: Low while you're the only user. High before onboarding others.

### Image Optimization via Remark Plugin
**Problem**: Phase 1 serves images from `public/` as-is (no optimization). Large images hurt page load.

**Solution**: blog-core adds a remark plugin that:
1. During the content overlay step, images move from `public/blog-img/` to `src/assets/blog-img/`
2. The remark plugin rewrites `![alt](/blog-img/x.jpg)` → Astro's `<Image>` component
3. Astro's pipeline generates responsive breakpoints, WebP conversion, lazy loading

**Key guarantee**: cms-md image paths never change. Authors keep writing `![alt](/blog-img/x.jpg)`. The remark plugin handles rewriting transparently.

**Priority**: Medium. Implement after Phase 2 when you can measure actual image payload sizes.

### Additional blog-core Variants
**Problem**: One visual framework doesn't fit all use cases.

**Solution**: Create additional blog-core repos, each with its own design philosophy:
- `blog-core-fanta` -- Colorful, playful, bold (gradients, animations, card layouts)
- `blog-core-yellow` -- Minimalist, typography-focused (serif, narrow width, no clutter)

Each variant:
- Is a separate repo with its own reusable workflow
- May define additional optional frontmatter fields (e.g., fanta: `accent_color`, `hero_layout`)
- May add variant-specific sections to `site.yaml` (e.g., yellow: `typography: "serif"`)
- Shares the base content contract (same required frontmatter, same directory structure)

**Switching**: User changes one line in `deploy.yml`:
```yaml
# From classic:
uses: pascalandy/blog-core/.github/workflows/build-blog.yml@main
# To fanta:
uses: pascalandy/blog-core-fanta/.github/workflows/build-blog.yml@main
```

**Priority**: Low. Build after the core decoupling is proven and stable.

### Workflow Stability for Multi-Tenant
**Problem**: If blog-core pushes a broken workflow to `main`, all cms-md repos break on next build.

**Solution options** (pick one when scaling):
- A `stable` branch that `@main` only advances to after CI passes on a test cms-md
- Semantic version tags (`@v1`, `@v2`) with cms-md defaulting to latest stable tag
- Automated smoke test: blog-core CI builds a reference cms-md before merging to main

**Priority**: Low while you're the only user. Required before "THOUSANDS of cms-md repos."

## Next Steps

→ `/ce:plan` for structured implementation planning, starting with Phase 0 (Hello World proof-of-concept).

All key decisions resolved:
- Versioning: Always use `@main` (latest)
- Force-rebuild: Not needed (repos rebuild on their own schedule)
- Images: Serve from `public/` in Phase 1, remark plugin later (Evolution)
- File naming: Slug-based, no date prefix
- Config: All user config in cms-md `site.yaml` (socials, share_links, tags included)
- Variants: Design for them, build only classic
- Local preview: Deferred to Evolution
