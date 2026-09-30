# Tags

The tags page lists every visible tag with its post count, and each tag page lists that tag's posts, 20 per page.

## Sub-features

- `tags-list` shows each tag not flagged `hiddenFromTagsPage`, with its count
- `tags-page` lists one tag's posts under the heading `🏷️ NAME`
- `tags-hidden` keeps a hidden tag's page reachable by its URL
- `tags-pagination` pages a tag's posts 20 at a time

## How to get to it (user POV)

- Choose `tags` in the header
- Choose a tag on a post page
- Open `$URL/tags/SLUG/` directly

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- `just overview --json | jq '.tags'` gives each tag's slug, name, visible post count, and flags

- **Open the list.** Run `agent-browser open "$URL/tags"` and `agent-browser get title`. The title is `Tags | Le blog de Pascal Andy`.
- **Compare the counts.** Run `agent-browser snapshot -i`. Each tag with `hiddenFromTagsPage: false` in the overview appears with its `posts` count, and no hidden tag appears.
- **Open one tag.** Run `agent-browser open "$URL/tags/technologie"`. The heading reads `🏷️ technologie` and the list matches the tag's count.
- **Open a hidden tag.** Run `agent-browser open "$URL/tags/void"`. The page lists the `void` posts, though `/tags` does not show the tag.
- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/tags/tags.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/tags" --out cache/verify-blog/$RUN/tags`. `aria.txt` lists the tags and counts.

## Gotchas

- Counts cover built, listed posts: drafts and scheduled posts do not count
- A post may use only registered tags, so a missing tag page usually means a registry change in `src/tags.ts`
