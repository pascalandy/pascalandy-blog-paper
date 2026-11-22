# Navigation

The header links every section, collapses into a menu on narrow screens, and the blog roll pages its posts 20 at a time.

## Sub-features

- `nav-header` links the site name to `/`, then `/blog/`, `tags`, `à propos`, `rechercher`, and the RSS feed
- `nav-mobile` opens and closes the header links with the `Ouvrir le menu` button on narrow screens; open, it reads `Fermer le menu`
- `nav-breakpoint` shows the menu button at 639 px and shows the header links directly from 640 px
- `nav-pagination` pages the blog roll at `/blog/`, `/blog/2/`, and on
- `nav-skip` offers the `Aller au contenu` skip link to the main content for keyboard readers

## How to get to it (user POV)

- Use the header on any page
- Narrow the window, or open the site on a phone, for the menu button
- Scroll to the end of `/blog/` for the page links

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- `just overview --json | jq '.posts.counts.blog_roll'` gives the blog roll size; pages hold 20 posts each

- **Follow the header.** Run `agent-browser open "$URL/"`, then `agent-browser find role link click --name "tags"`. The page moves to `/tags/`. Repeat with `rechercher` and `à propos`.
- **Open the blog roll.** At desktop width, run `agent-browser open "$URL/"`, then `agent-browser click 'a[href="/blog/"]'` and `agent-browser get title`. The URL ends with `/blog/` and the title is `Blog | Le blog de Pascal Andy`.
- **Page forward.** Scroll down, then run `agent-browser find role link click --name "Page suivante"`. The URL ends with `/blog/2/`.
- **Open the mobile menu.** Run `agent-browser set viewport 390 844`, `agent-browser open "$URL/"`, and `agent-browser click "#menu-btn"`. `agent-browser get attr "#menu-btn" aria-expanded` gives `true`, its `aria-label` gives `Fermer le menu`, and the links show.
- **Check 639 px.** Run `agent-browser set viewport 639 900` and open `"$URL/"` in a fresh tab. `agent-browser is visible "#menu-btn"` gives `true` and `agent-browser is visible '#menu-items a[href="/blog/"]'` gives `false`. Run `agent-browser click "#menu-btn"`. Repeat the link check and expect `true`.
- **Check 640 px.** Run `agent-browser set viewport 640 900` and open `"$URL/"` in a fresh tab. `agent-browser is visible "#menu-btn"` gives `false` and `agent-browser is visible '#menu-items a[href="/blog/"]'` gives `true`.
- **Proof.** After each width check, save `agent-browser snapshot -i` and a screenshot under `cache/verify-blog/$RUN/navigation/` with the width in each filename.
- **Fallback.** Run the same breakpoint checks and blog-roll click with Playwright.

  ```bash
  BROWSE=.claude/skills/verify-blog/scripts/browse.py
  OUT="cache/verify-blog/$RUN/navigation"

  uv run "$BROWSE" "$URL/" --out "$OUT/639" --viewport 639x900 \
    --step 'eval:getComputedStyle(document.querySelector("#menu-btn")).display' \
    --step 'eval:getComputedStyle(document.querySelector("#menu-items")).visibility' \
    --step 'click:#menu-btn' --step 'wait:#menu-items a[href="/blog/"]'

  uv run "$BROWSE" "$URL/" --out "$OUT/640" --viewport 640x900 \
    --step 'eval:getComputedStyle(document.querySelector("#menu-btn")).display' \
    --step 'wait:#menu-items a[href="/blog/"]'

  uv run "$BROWSE" "$URL/" --out "$OUT/blog-roll" --step 'click:a[href="/blog/"]'
  ```

  At 639 px, `state.json` records a button display other than `none` and menu visibility of `hidden` before the click. After the click, `aria.txt` lists the links and the menu button named `Fermer le menu`. At 640 px, `state.json` records a button display of `none`, and `aria.txt` lists the header links. The blog-roll capture ends at `/blog/`.

  For the phone-width check, run `uv run "$BROWSE" "$URL/" --out "$OUT/iphone" --device iphone --step 'click:#menu-btn'`. `aria.txt` lists the open menu's links.

## Gotchas

- On desktop widths the menu button is hidden and the links always show; test the menu at a phone width
- Choosing the theme button inside the open menu also closes the menu
