# Home

The home page greets the reader with Pascal's introduction in French and lists the featured posts, when any post sets `featured: true`.

## Sub-features

- `home-hero` shows the introduction ending with `Bienvenue dans mon monde,` and `Pascal`
- `home-featured` lists the featured posts under the `Featured` heading, only when at least one exists
- `home-chrome` shows the header, the banner, and the footer

## How to get to it (user POV)

- Open the site root, `$URL/`
- Choose the site name in the header from any page

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- `just overview --json | jq '.featured | length'` gives the number of featured posts to expect

- **Open the page.** Run `agent-browser open "$URL/"` and `agent-browser get title`. The title is `Le blog de Pascal Andy`.
- **Read the introduction.** Run `agent-browser get text "#hero"`. It starts with `J'ai toujours été un patenteux` and ends with `Pascal`.
- **Check the featured list.** Run `agent-browser get count "#featured li"`. The count equals the featured count from the overview; with none, the `#featured` section is absent.
- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/home/home.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/" --out cache/verify-blog/$RUN/home`. `aria.txt` holds the introduction and `state.json` the title.

## Gotchas

- No post is featured today, so an empty `Featured` section is correct, not a regression
- The page has no list of recent posts: the blog roll lives at `/blog`
