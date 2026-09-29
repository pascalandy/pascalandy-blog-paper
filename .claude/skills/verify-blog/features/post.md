# Post

A post page shows one article with its title, date, and tags, then links to the previous and next posts.

## Sub-features

- `post-article` renders the title as the page heading and the body inside `#article`
- `post-tags` links each tag to its tag page
- `post-neighbors` links the previous and next posts under `Post navigation`
- `post-mermaid` renders Mermaid diagrams on posts that set `mermaid: true`
- `post-draft` gives a draft no page at all

## How to get to it (user POV)

- Choose a post in the blog roll at `/blog`, on a tag page, or in search results
- Open its URL directly, such as `$URL/blog/lhorizon-cest-toi`

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- The steps use `/blog/lhorizon-cest-toi`; its overview entry is `just overview --json | jq '.posts.buckets.blog_roll[] | select(.url == "/blog/lhorizon-cest-toi")'`. For another post, take its `url` and `title` from the overview the same way

- **Open the post.** Run `agent-browser open "$URL/blog/lhorizon-cest-toi"` and `agent-browser get title`. The title is `L'horizon, c'est toi | Le blog de Pascal Andy`.
- **Read the title.** Run `agent-browser get text "#main-content > h1"`. It matches the `title` of that overview entry; the body sits in `#article`, below the heading.
- **Follow a tag.** Run `agent-browser snapshot -i`, then click the tag link. The page moves to `/tags/TAG/` and lists the post.
- **Follow a neighbor.** Return to the post and run `agent-browser find role link click --name "Next"`. The next post opens, and its `Previous` link leads back.
- **Check a Mermaid post.** Run `agent-browser open "$URL/blog/dev-workflows/using-mermaid"` and `agent-browser wait ".mermaid-diagram svg"`. Each diagram renders as an SVG inside `.mermaid-diagram`.
- **Check a draft.** Pick a path from `just overview --json | jq '.posts.buckets.draft[0].url'` and open it. The site answers with its 404 page.
- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/post/post.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/blog/lhorizon-cest-toi" --out cache/verify-blog/$RUN/post --step 'click:role=link[name="Next"]'`. `state.json` holds the next post's URL and title.

## Gotchas

- Posts that share a `date_created` have no stable order, so `Previous` and `Next` can swap between builds (backlog B9)
- A post with a future `date_created` still has a page, though listings hide it
- Folder names are slugified in URLs: `dev_workflows/` becomes `/blog/dev-workflows/`
- Mermaid loads from cdn.jsdelivr.net in the browser; when the CDN is unreachable, the code block gets the `mermaid-error` class instead of a diagram
