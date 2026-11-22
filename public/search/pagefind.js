import { preload, search as find } from "../pagefind/pagefind.js";
import { fold, wordForms } from "./words.js";
export * from "../pagefind/pagefind.js";

let vocabulary;

async function matchesWord(word, hits) {
  if (!hits.length) return false;
  if ((await find(`"${word}"`)).results.length) return true;

  const prefix = fold(word).replace(/[^\p{L}\p{N}_]/gu, "");
  if (!prefix) return true;
  vocabulary ??= fetch(new URL("../pagefind/words.txt", import.meta.url), {
    cache: "no-cache",
  })
    .then(response => (response.ok ? response.text() : null))
    .catch(() => null);
  const words = await vocabulary;
  if (words && !words.includes(`\n${prefix}`)) return false;

  // Pagefind also matches shorter words inside the query. Keep its ranking
  // if an indexed position really contains the requested prefix.
  for (const hit of hits) {
    const tokens = (await hit.data()).content.split(/\s+/u);
    if (
      hit.words.some(at =>
        wordForms(tokens[at] ?? "").some(form => form.startsWith(prefix))
      )
    ) {
      return true;
    }
  }
  return false;
}

export async function search(term, options) {
  const folded = term && fold(term);
  if (folded && folded !== term) await preload(folded, options);
  const matches = await find(term, options);
  if (!matches.results.length || !term || /^\s*".+"\s*$/.test(term))
    return matches;

  const words = new Set(term.trim().split(/\s+/u));
  for (const word of words) {
    const candidates = words.size === 1 ? matches : await find(word, options);
    if (!(await matchesWord(word, candidates.results)))
      return find("", options);
  }
  return matches;
}
