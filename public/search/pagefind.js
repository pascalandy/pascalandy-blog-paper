import { preload, search as find } from "../pagefind/pagefind.js";
import { fold, shardName, wordForms } from "./words.js";
export * from "../pagefind/pagefind.js";

const shards = new Map();

async function loadShard(kind, initial) {
  const url = new URL(`../pagefind/${kind}/${initial}.json`, import.meta.url);
  if (!shards.has(url.href)) {
    const request = fetch(url, { cache: "no-cache" })
      .then(response => {
        if (!response.ok) throw new Error(String(response.status));
        return response.json();
      })
      .catch(() => {
        shards.delete(url.href);
        return null;
      });
    shards.set(url.href, request);
  }
  return shards.get(url.href);
}

async function matchingArticles(hits, spelling) {
  const prefix = fold(spelling);
  const initial = shardName(prefix);
  const [pages, verbs] = await Promise.all([
    loadShard("prefixes", initial),
    loadShard("verbs", initial),
  ]);
  const lemmas = verbs?.forms[spelling];
  const conjugated = new Set(
    Array.isArray(lemmas) ? lemmas.flatMap(lemma => verbs.pages[lemma]) : []
  );
  const matches = [];
  for (const hit of hits) {
    if (conjugated.has(hit.id)) {
      matches.push(hit);
      continue;
    }
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
    const spelling = word.toLowerCase().replace(/[^\p{L}\p{N}_]/gu, "");
    if (!spelling) continue;
    const exact = await find(`"${word}"`, options);
    const accepted = new Set(exact.results.map(hit => hit.id));
    const ambiguous = hits.filter(hit => !accepted.has(hit.id));
    if (!ambiguous.length) continue;
    for (const hit of await matchingArticles(ambiguous, spelling))
      accepted.add(hit.id);
    hits = hits.filter(hit => accepted.has(hit.id));
    if (!hits.length) return find("", options);
  }
  return hits.length === matches.results.length
    ? matches
    : { ...matches, results: hits, unfilteredResultCount: hits.length };
}
