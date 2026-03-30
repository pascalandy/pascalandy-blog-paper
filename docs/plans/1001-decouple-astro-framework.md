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

- **In Scope**: Repository separation, reusable GitHub Actions workflow, content contract, template repository setup, multi-tenant build orchestration, multiple blog-core variants (classic, fanta, yellow, etc.)
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

## Architecture

### Repository Structure

**blog-core variants** (Multiple Visual Frameworks)

Each variant is a separate repo with its own design philosophy:

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

blog-core-fanta/              # Fanta - Colorful, playful, bold
├── .github/workflows/
│   └── build-blog.yml        # Reusable workflow (fanta variant)
├── src/
│   ├── components/           # Fanta components (cards, gradients, animations)
│   ├── layouts/              # Fanta layouts
│   ├── pages/                # Route definitions
│   └── themes/               # Fanta themes (vibrant, neon, pastel)
└── README.md                 # "Use me for colorful, modern blogs"

blog-core-yellow/             # Yellow - Minimalist, typography-focused
├── .github/workflows/
│   └── build-blog.yml        # Reusable workflow (yellow variant)
├── src/
│   ├── components/           # Yellow components (clean, minimal)
│   ├── layouts/              # Yellow layouts
│   ├── pages/                # Route definitions
│   └── themes/               # Yellow themes (mono, serif, Swiss)
└── README.md                 # "Use me for minimalist blogs"
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
│       └── deploy.yml                 # Calls chosen blog-core variant
│
├── blog/                              # Blog posts (flat, date-prefixed)
│   ├── 2014-04-17-hello-world.md
│   ├── 2014-04-21-my-second-post.md
│   ├── 2024-05-22-new-year-thoughts.md
│   ├── 2025-01-15-ai-reflections.md
│   └── drafts/                        # Draft posts (_prefix = ignored)
│       └── _2025-03-30-unfinished-post.md
│
├── blog-img/                          # Blog post images (flat, date-prefixed)
│   ├── 2014-04-17-hello-world-hero.jpg
│   ├── 2014-04-17-hello-world-diagram.png
│   ├── 2014-04-21-my-second-post-screenshot.png
│   ├── 2024-05-22-new-year-thoughts-fireworks.jpg
│   └── 2025-01-15-ai-reflections-cover.jpg
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
    │   └── site.yaml                  # Site metadata, theme, author
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
      - Copy ./content/blog/ → ./framework/src/content/blog/
      - Copy ./content/pages/ → ./framework/src/content/pages/
      - Copy ./content/blog-img/ → ./framework/public/blog-img/
      - Copy ./content/pages-img/ → ./framework/public/pages-img/
      - Copy ./content/system/assets/ → ./framework/public/assets/
      - Generate ./framework/src/config.ts from ./content/system/config/site.yaml
   4. Build Astro site in ./framework/
   5. Deploy dist/ to user's target (Sevalla, etc.)
```

**Critical Implementation Details:**
- **Content Overlay**: Content is copied into framework directories, not symlinked (works across all platforms)
- **Image Handling**: Images copied to `public/` so Astro serves them at root path
- **Config Generation**: YAML → TypeScript config conversion happens during build
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

1. **Directory Structure** (Base contract - all variants)
   ```
   justfile                 # Required: Just commands (validate, format)
   lefthook.yml             # Required: Git hooks for pre-commit validation
   blog/                    # Required: Blog posts (flat, date-prefixed)
   blog/drafts/             # Optional: Draft posts (_prefix = ignored)
   blog-img/                # Required: Blog images (flat, date-prefixed)
   pages/                   # Optional: Static pages (flat)
   pages-img/               # Optional: Page images (flat)
   scripts/                 # Required: Validation scripts
   system/config/           # Required: Site configuration
   system/assets/og/        # Optional: Open Graph images
   system/assets/static/    # Optional: Site-wide images
   system/assets/fonts/     # Optional: Custom fonts
   system/assets/files/     # Optional: Downloadable files
   ```

2. **File Naming Convention** (All variants)
   - Blog posts: `YYYY-MM-DD-slug.md` (e.g., `2014-04-17-hello-world.md`)
   - Blog images: `YYYY-MM-DD-slug-descriptor.ext` (e.g., `2014-04-17-hello-world-hero.jpg`)
   - Drafts: `_YYYY-MM-DD-slug.md` in `blog/drafts/` (underscore prefix = ignored)
   - Pages: `slug.md` (e.g., `about.md`)
   - Page images: `slug-descriptor.ext` (e.g., `about-portrait.jpg`)

3. **Frontmatter Schema** (Base contract - all variants)
   ```yaml
   ---
   author: string
   date_created: date
   title: string
   tags: string[]
   description: string
   featured?: boolean
   draft?: boolean
   ogImage?: string        # Relative path: blog-img/2014-04-17-hello-world-hero.jpg
   ---
   ```

4. **Variant-Specific Extensions**
   
   Each blog-core variant may require additional fields:
   
   **blog-core-fanta** (colorful variant):
   ```yaml
   ---
   # Base fields (required by all variants)
   author: string
   date_created: date
   title: string
   tags: string[]
   description: string
   
   # Fanta-specific (optional but recommended)
   accent_color: "#FF6B6B"     # Custom accent for this post
   hero_layout: "full-bleed"   # "full-bleed", "split", "minimal"
   ---
   ```
   
   **blog-core-yellow** (minimalist variant):
   ```yaml
   ---
   # Base fields (required by all variants)
   author: string
   date_created: date
   title: string
   tags: string[]
   description: string
   
   # Yellow-specific (optional)
   reading_time: true          # Show reading time
   serif_title: true           # Use serif font for title
   ---
   ```

5. **Site Configuration** (system/config/site.yaml)
   ```yaml
   site:
     title: "Blog Title"
     author: "Author Name"
     description: "Site description"
     website: "https://example.com"
     lang: "en"
     timezone: "America/Montreal"
   
   theme:
     name: "claude"        # Must match theme in your chosen blog-core variant
   
   posts:
     perPage: 20
     perIndex: 4
     dateFormat: "YYYY-MM-DD"
   
   features:
     rss: true
     sitemap: true
     darkMode: true
     search: true
   
   deployment:
     target: "sevalla"     # or "vercel", "netlify", etc.
   
   # Variant-specific settings:
   # fanta:
   #   animations: true
   #   card_style: "rounded"
   # 
   # yellow:
   #   typography: "serif"
   #   max_width: "narrow"
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

### Switch Visual Framework (Look & Feel)
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
2. Create `2025-04-01-my-new-post.md`
3. Add images to `blog-img/`
4. Reference images naturally: `![alt](../blog-img/2025-04-01-my-new-post-hero.jpg)`
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

### Resolve Before Planning
*All questions resolved. Ready for planning.*

### Deferred to Planning
- How does the reusable workflow merge blog-core framework with cms-md content? (Copy vs symlink vs overlay)
- How does blog-core consume system/config/site.yaml? (Generate config.ts vs runtime read)
- Should we support multiple deployment targets (Sevalla, Vercel, Netlify) in one workflow or separate workflows?
- How to handle build caching across thousands of independent repos?
- Should we validate the content contract in CI, or let Astro fail at build time?
- Exact mechanism for copying images to public/ directory during build
- How to handle missing/invalid themes gracefully?
- How to validate cms-md setup on first run (secrets check, structure validation)?
- How much can variants diverge from base content contract? (frontmatter extensions, config options)
- Should variants share common components/utilities, or be completely independent?

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

1. **Phase 1**: Create `blog-core` repository (classic variant) with reusable workflow
   - Extract framework code from current repo
   - Create `.github/workflows/build-blog.yml` (reusable)
   - Make blog-core public

2. **Phase 2**: Create `cms-md` template repository
   - Extract content from current repo
   - Create template structure (blog/, blog-img/, pages/, pages-img/, system/)
   - Add workflow that calls blog-core reusable workflow
   - Mark as GitHub template repository

3. **Phase 3**: Test end-to-end with fork
   - Fork cms-md template to test account
   - Push content, verify build triggers
   - Verify deployment works

4. **Phase 4**: Migrate current site
   - Convert current repo content to cms-md format
   - Either: migrate current repo to use reusable workflow, OR create new cms-md repo

5. **Phase 5**: Create additional blog-core variants (optional)
   - `blog-core-fanta` - Colorful, playful design
   - `blog-core-yellow` - Minimalist, typography-focused
   - Each variant has its own repo, themes, and reusable workflow

6. **Phase 6**: Documentation
   - Write "Getting Started" guide for new users
   - Document content contract (base + variant-specific extensions)
   - Document deployment configuration
   - Create variant comparison guide (classic vs fanta vs yellow)

## Next Steps

→ `/ce:plan` for structured implementation planning. All decisions resolved:
- Versioning: Always use `@main` (latest)
- Force-rebuild: Not needed (repos rebuild on their own schedule)
