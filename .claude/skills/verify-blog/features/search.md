# Search

Search finds posts by their text through Pagefind, keeps the query in the URL, and shows a result count in French.

## Sub-features

- `search-type` returns results while the reader types, under a count such as `12 résultats`
- `search-url` writes the query to `?q=` and runs a query found there on load
- `search-empty` shows `Aucun résultat` for a query with no match
- `search-clear` empties the query with `Effacer`
- `search-excerpt` wraps long words inside the result column

## How to get to it (user POV)

- Choose `rechercher` in the header
- Open `$URL/search/?q=QUERY` directly

## Driving it with agent-browser

Preconditions:

- `site.py doctor` exits 0
- The instance serves a Pagefind index: the preview always does; Pascal's dev server needs a prior build, which copies the index into `public/pagefind`

- **Open search.** Run `agent-browser open "$URL/search/"` and `agent-browser get title`. The title is `Recherche | Le blog de Pascal Andy`, and the box shows `Rechercher...`.
- **Type a query.** Run `agent-browser fill ".pagefind-ui__search-input" "bitcoin"`, then `agent-browser wait ".pagefind-ui__result"`. A count such as `12 résultats` appears above linked results.
- **Check the URL.** Run `agent-browser get url`. It ends with `?q=bitcoin`.
- **Miss.** Replace `bitcoin` with `coquecigruegalactique` and wait for `Aucun résultat`. Reload and check for the same message. Repeat from `bitcoin` with `zzqqxx`.
- **Clear.** Run `agent-browser click ".pagefind-ui__search-clear"`. The box and the results empty.
- **Check a long excerpt.** The PSU result for `toroidal` contains a URL over 1,000 characters long. Check that the full word is present and the page fits at both widths.

  ```bash
  (
    set -e
    session=$(agent-browser session id --scope worktree --prefix search-wrap)
    browser=(agent-browser --session "$session")
    trap '"${browser[@]}" close' EXIT
    for width in 390 1440; do
      "${browser[@]}" set viewport "$width" 900
      "${browser[@]}" open "$URL/search/?q=toroidal"
      "${browser[@]}" wait --text "PSU"
      "${browser[@]}" wait --fn 'Array.from(document.querySelectorAll(".pagefind-ui__result")).some(result => result.querySelector(".pagefind-ui__result-title")?.textContent.includes("PSU") && Array.from(result.querySelectorAll(".pagefind-ui__result-excerpt")).some(el => /\S{1000}/u.test(el.textContent) && el.clientWidth > 0 && el.clientHeight > 0 && el.scrollWidth <= el.clientWidth && el.scrollHeight <= el.clientHeight))'
      test "$("${browser[@]}" eval 'document.documentElement.scrollWidth === document.documentElement.clientWidth')" = true
    done
  )
  ```

- **Proof.** Run `agent-browser snapshot -i` and `agent-browser screenshot cache/verify-blog/$RUN/search/results.png`.
- **Fallback.** Run `uv run .claude/skills/verify-blog/scripts/browse.py "$URL/search/" --out cache/verify-blog/$RUN/search --step 'fill:.pagefind-ui__search-input=bitcoin' --step 'wait:.pagefind-ui__result'`. `state.json` holds the URL with `?q=bitcoin`, and `aria.txt` the results.

## Gotchas

- Pagefind indexes only the post body (`data-pagefind-body`); article tags inside that body are searchable, and page chrome stays out of the results
- Results appear after a short debounce: wait for `.pagefind-ui__result` or the message, never a fixed sleep
- Pagefind reports the index language as `fr-ca` in `dist/pagefind/pagefind-entry.json`
