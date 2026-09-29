# Navigation

The header links every section, collapses into a menu on narrow screens, and the blog roll pages its posts 20 at a time.

## Sub-features

- `nav-header` links the site name to `/`, then `/blog`, `tags`, `à propos`, `search`, and the RSS feed
- `nav-mobile` opens and closes the header links with the `Open Menu` button on narrow screens
- `nav-pagination` pages the blog roll at `/blog`, `/blog/2`, and on
- `nav-skip` offers a skip link to the main content for keyboard readers

## How to get to it (user POV)

- Use the header on any page
- Narrow the window, or open the site on a phone, for the menu button
- Scroll to the end of `/blog` for the page links

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- `just overview --json | jq '.posts.counts.blog_roll'` gives the blog roll size; pages hold 20 posts each

- **Follow the header.** Run `agent-browser open "$URL/"`, then `agent-browser find role link click --name "tags"`. The page moves to `/tags`; repeat with `search` and `à propos`.
- **Open the blog roll.** Run `agent-browser click 'a[href="/blog"]'` and `agent-browser get title`. The title is `Blog | Le blog de Pascal Andy`.
- **Page forward.** Scroll down, then choose the next page link. The URL ends with `/blog/2`.
- **Open the mobile menu.** Run `agent-browser set viewport 390 844`, `agent-browser open "$URL/"`, and `agent-browser click "#menu-btn"`. `agent-browser get attr "#menu-btn" aria-expanded` gives `true`, and the links show.
- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/navigation/menu.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/" --out cache/verify-blog/$RUN/navigation --device iphone --step 'click:#menu-btn'`. `aria.txt` lists the open menu's links.

## Gotchas

- On desktop widths the menu button is hidden and the links always show; test the menu at a phone width
- Choosing the theme button inside the open menu also closes the menu
