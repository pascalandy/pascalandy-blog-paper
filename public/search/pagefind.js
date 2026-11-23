import { preload, search as find } from "../pagefind/pagefind.js";
import { fold, shardName, wordForms } from "./words.js";
export * from "../pagefind/pagefind.js";

const shards = new Map();

async function loadShard(kind, initial, retry = true) {
  const url = new URL(`../pagefind/${kind}/${initial}.json`, import.meta.url);
  if (!shards.has(url.href)) {
    const request = fetch(url, { cache: "no-cache" })
      .then(response => {
        if (!response.ok) throw new Error(String(response.status));
        return response.json();
      })
      .catch(() => {
        shards.delete(url.href);
        return retry ? loadShard(kind, initial, false) : null;
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
      if (words.includes("\n" + prefix)) {
        matches.push(hit);
        continue;
      }
    } else {
      const { content } = await hit.data();
      if (
        content
          .split(/\s+/u)
          .some(token => wordForms(token).some(form => form.startsWith(prefix)))
      ) {
        matches.push(hit);
        continue;
      }
    }
  }
  return matches;
}

export async function search(term, options) {
  if (term) term = term.normalize("NFC");
  if (term?.trim()) {
    // Warm nearby native index chunks for each query word.
    const prefixes = new Set();
    for (const word of fold(term).match(/[\p{L}\p{N}]+/gu) ?? []) {
      prefixes.add(word);
      // Geometric prefix lengths keep the preload text linear for long pasted words.
      for (let width = 1; width < word.length; width *= 2)
        prefixes.add(word.slice(0, width));
    }
    if (prefixes.size) await preload([...prefixes].join(" "), options);
  }
  const matches = await find(term, options);
  if (!matches.results.length || !term) return matches;

  let hits = matches.results;
  for (const word of new Set(term.trim().split(/\s+/u))) {
    const spelling = word.toLowerCase().replace(/[^\p{L}\p{N}_]/gu, "");
    if (!spelling) continue;
    hits = await matchingArticles(hits, spelling);
    if (!hits.length) return find("", options);
  }
  return hits.length === matches.results.length
    ? matches
    : { ...matches, results: hits, unfilteredResultCount: hits.length };
}
