# Theme

The theme button switches the site between light and dark, and the choice persists across pages and reloads.

## Sub-features

- `theme-initial` starts from the stored choice, else the operating system's color scheme
- `theme-toggle` flips `data-theme` on the page root between `light` and `dark`, and mirrors it in the button's `aria-label`
- `theme-persist` keeps the choice after a reload and on other pages

## How to get to it (user POV)

- Choose the button titled `Toggles light & dark` in the header, on any page
- On a phone, open the menu first; the button sits in it

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- A fresh browser with no stored theme, and a known color scheme: launch with `--color-scheme light`

- **Read the start.** Run `agent-browser open "$URL/"` and `agent-browser get attr html data-theme`. It gives `light`, and `agent-browser get attr "#theme-btn" aria-label` gives `light` too.
- **Toggle.** Run `agent-browser click "#theme-btn"`. `data-theme` and the button's `aria-label` both become `dark`, and the page turns dark.
- **Reload.** Run `agent-browser reload` and read `data-theme` again. It stays `dark`.
- **Change page.** Run `agent-browser open "$URL/tags"`. `data-theme` is still `dark`.
- **Proof.** Screenshot before and after the toggle: `agent-browser screenshot cache/verify-blog/$RUN/theme/before.png` and `.../after.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/" --out cache/verify-blog/$RUN/theme/before --color-scheme light`, then the same with `--out cache/verify-blog/$RUN/theme/after --step 'click:#theme-btn'`. The two `state.json` files show `theme` `light`, then `dark`.

## Gotchas

- The static HTML says `aria-label="auto"` until the theme script runs; read the attribute after the page loads
- A stored choice beats the operating system: clear local storage, or use a fresh browser, before testing `theme-initial`
- Colors come from the active theme in `src/config.ts`; judge contrast on both themes
