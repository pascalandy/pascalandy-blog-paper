import { preload, search as find } from "../pagefind/pagefind.js";
import { fold, shardName, wordForms } from "./words.js";
export * from "../pagefind/pagefind.js";

const shards = new Map();

async function withPrefix(hits, prefix) {
  const initial = shardName(prefix);
  if (!shards.has(initial)) {
    const url = new URL(
      `../pagefind/prefixes/${initial}.json`,
      import.meta.url
    );
    shards.set(
      initial,
      fetch(url, { cache: "no-cache" })
        .then(response => (response.ok ? response.json() : null))
        .catch(() => null)
    );
  }

  const pages = await shards.get(initial);
  const matches = [];
  for (const hit of hits) {
    const words = pages?.[hit.id];
    if (typeof words === "string") {
      if (words.includes("\n" + prefix)) matches.push(hit);
    } else {
      const { content } = await hit.data();
      if (
        content
          .split(/\s+/u)
          .some(token => wordForms(token).some(form => form.startsWith(prefix)))
      ) {
        matches.push(hit);
      }
    }
  }
  return matches;
}

export async function search(term, options) {
  if (term) term = term.normalize("NFC");
  const folded = term && fold(term);
  if (folded && folded !== term) await preload(folded, options);
  const matches = await find(term, options);
  if (!matches.results.length || !term || /^\s*".+"\s*$/.test(term)) {
    return matches;
  }

  let hits = matches.results;
  for (const word of new Set(term.trim().split(/\s+/u))) {
    const prefix = fold(word).replace(/[^\p{L}\p{N}_]/gu, "");
    if (!prefix) continue;
    const exact = await find(`"${word}"`, options);
    const accepted = new Set(exact.results.map(hit => hit.id));
    const ambiguous = hits.filter(hit => !accepted.has(hit.id));
    if (!ambiguous.length) continue;
    for (const hit of await withPrefix(ambiguous, prefix)) accepted.add(hit.id);
    hits = hits.filter(hit => accepted.has(hit.id));
    if (!hits.length) return find("", options);
  }
  return hits.length === matches.results.length
    ? matches
    : { ...matches, results: hits, unfilteredResultCount: hits.length };
}
