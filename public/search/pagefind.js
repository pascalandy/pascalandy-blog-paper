import { preload, search as find } from "../pagefind/pagefind.js";
import { fold, initials, shardName, wordForms } from "./words.js";
export * from "../pagefind/pagefind.js";

const shards = new Map();
let ready;

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

function surfaceFamily(word) {
  return fold(word).replace(/e{0,2}s?$/u, "");
}

async function matchingArticles(hits, spelling, options) {
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
  const family = surfaceFamily(spelling);
  let quoted;
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
    // Pagefind also groups close spellings in this bilingual index (system/système).
    // Confirm a whole surface word before keeping one of its stemmed phrase hits.
    if (!Array.isArray(lemmas) || family.length < 4) continue;
    quoted ??= new Set(
      (await find('"' + spelling + '"', options)).results.map(hit => hit.id)
    );
    if (quoted.has(hit.id)) {
      const { content } = await hit.data();
      if (
        content
          .split(/\s+/u)
          .some(token =>
            wordForms(token).some(word => surfaceFamily(word) === family)
          )
      ) {
        matches.push(hit);
      }
    }
  }
  return matches;
}

export async function search(term, options) {
  if (term) term = term.normalize("NFC");
  if (term?.trim()) {
    // Pagefind's stemming considers the shards loaded by earlier queries.
    // Warm this small index once so opening a shared URL and typing agree.
    ready ??= preload([...initials].join(" ")).catch(error => {
      ready = undefined;
      throw error;
    });
    await ready;
  }
  const matches = await find(term, options);
  if (!matches.results.length || !term) return matches;

  let hits = matches.results;
  for (const word of new Set(term.trim().split(/\s+/u))) {
    const spelling = word.toLowerCase().replace(/[^\p{L}\p{N}_]/gu, "");
    if (!spelling) continue;
    hits = await matchingArticles(hits, spelling, options);
    if (!hits.length) return find("", options);
  }
  return hits.length === matches.results.length
    ? matches
    : { ...matches, results: hits, unfilteredResultCount: hits.length };
}
