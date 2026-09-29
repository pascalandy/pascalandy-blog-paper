# Search

Search finds posts by their text through Pagefind, keeps the query in the URL, and shows a result count in French.

## Sub-features

- `search-type` returns results while the reader types, under a count such as `12 résultats`
- `search-url` writes the query to `?q=` and runs a query found there on load
- `search-empty` shows `Aucun résultat` for a query with no match
- `search-clear` empties the query with `Effacer`

## How to get to it (user POV)

- Choose `search` in the header
- Open `$URL/search?q=QUERY` directly

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- The instance serves a Pagefind index: the preview always does; Pascal's dev server needs a prior build, which copies the index into `public/pagefind`

- **Open search.** Run `agent-browser open "$URL/search"` and `agent-browser get title`. The title is `Recherche | Le blog de Pascal Andy`, and the box shows `Rechercher...`.
- **Type a query.** Run `agent-browser fill ".pagefind-ui__search-input" "bitcoin"`, then `agent-browser wait ".pagefind-ui__result"`. A count such as `12 résultats` appears above linked results.
- **Check the URL.** Run `agent-browser get url`. It ends with `?q=bitcoin`.
- **Miss.** Replace the query with `zzqqxx`. The message reads `Aucun résultat`.
- **Clear.** Run `agent-browser click ".pagefind-ui__search-clear"`. The box and the results empty.
- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/search/results.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/search" --out cache/verify-blog/$RUN/search --step 'fill:.pagefind-ui__search-input=bitcoin' --step 'wait:.pagefind-ui__result'`. `state.json` holds the URL with `?q=bitcoin`, and `aria.txt` the results.

## Gotchas

- Pagefind indexes only the post body (`data-pagefind-body`); page chrome and tag lists stay out of the results
- Results appear after a short debounce: wait for `.pagefind-ui__result` or the message, never a fixed sleep
- Search indexes French text as English until backlog B2 sets the page language
