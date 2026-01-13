# Project preferences

## CLI Tools
- `rg` not grep | `fd` not find | `uv` not python3 | `bun` not npm | `gh` ready
- Screenshots: `ls -lt ~/Documents/screenshots | head -2`

## Make Targets
- `make qa` pre-commit | `make ci` fast check | `make build` | `make lint` | `make format`

## Pre-commit
- Spawn @charlie → "run: make qa"

## Design/Style
- Verify w/ MCP Chrome DevTools
- Max viewport: 1400x900 (prevents crash)
- resize_page before screenshots

## Git
Atomic commits only. "and" in msg = split it.
- `git status` + `git diff --stat`
- Group by purpose, not filetype
- Separate commits per logical change

## CI
- via gihub actions: `@greptileai` triggers review | 👍=keep | 👎=stop | reply=teach
- Deploy in done via GH Actions on Sevalla

## Stack
- Astro 5 | TS strict | Tailwind v4 | Pagefind

## Astro Docs
- Index: docs.astro.build/llms-small.txt

## Architecture
```
astro.config.ts → src/config.ts + content.config + src/constants
                         ↓
              src/layouts/ (SEO, themes, transitions)
                         ↓
         src/pages/ + src/components/ + src/utils/
```

## Routes
`/` home | `/posts/[...page]` list | `/posts/[...slug]/` post | `/tags/[tag]/` filter | `/search/` | `/rss.xml`

## Post Visibility
- Drafts: dev only | Scheduled: visible after pubDatetime-15min

## Dev Cmds
- USER runs dev server, not agent (if not ask)

## Code Style
- TS strict, `@/*` alias, `type` not interface
- Imports: external → @/ → relative → type
- Prettier: semicolons, double quotes, 2 spaces, 80 chars
- ESLint: no console.log
- Names: Components=PascalCase | utils=camelCase | CONSTANTS=SCREAMING_SNAKE

## Tailwind
- `class:list` for conditionals
- Never hardcode colors → use theme vars
- `app-layout` = container util

## Themes
`src/config.ts` THEMES/ACTIVE_THEME | 19 OKLCH vars per mode | shadcn compatible

## Content
Posts: `src/data/blog/` | Zod validated | `_` prefix = ignored | subdirs preserved in URL

---

# Global User Preferences

## Communication Style
- Never end sentences with ellipses (...) - it comes across as passive aggressive
- Ask questions one at a time
- Acknowledge requests neutrally without enthusiasm inflation
- Skip validation language ("great idea!", "perfect!", "excellent!", "amazing!", "kick ass!")
- Skip affirmations ("you're right!", "exactly!", "absolutely!")
- Use neutral confirmations: "Got it", "On it", "Understood", "Starting now"
- Focus on execution over commentary

## AI Slop Patterns to Avoid
- Never use "not X, but Y" or "not just X, but Y" - state things directly
- No hedging: "I'd be happy to...", "I'd love to...", "Let me go ahead and...", "I'll just...", "If you don't mind..."
- No false collaboration: "Let's dive in", "Let's get started", "We can see that...", "As we discussed..."
- No filler transitions: "Now, let's...", "Next, I'll...", "Moving on to...", "With that said..."
- No overclaiming: "I completely understand", "That makes total sense"
- No performative narration: Don't announce actions then do them - just do them
- No redundant confirmations: "Sure thing!", "Of course!", "Certainly!"
