import assert from "node:assert/strict";
import { options, search } from "../dist/search/pagefind.js";
import { destroy, preload, search as nativeSearch } from "../dist/pagefind/pagefind.js";

const settings = {
  basePath: new URL("../dist/pagefind/", import.meta.url).href,
  baseUrl: "/",
};
const ids = response => response.results.map(hit => hit.id);
const fetchFile = globalThis.fetch;
const bitcoinChunks = new Set();
let outage = false;
let recording = true;
globalThis.fetch = (url, ...args) => {
  const path = new URL(url).pathname;
  if (recording && path.endsWith(".pf_index")) bitcoinChunks.add(path);
  if (outage && bitcoinChunks.has(path)) return Promise.resolve(new Response(null, {status: 503}));
  return fetchFile(url, ...args);
};
try {
  await options(settings);
  const bitcoins = ids(await nativeSearch("bitcoin"));
  assert.ok(bitcoinChunks.size && bitcoins.length);
  await destroy();
  await options(settings);
  recording = false;
  outage = true;
  const direct = ids(await search("utiliser IA"));
  outage = false;
  assert.deepEqual(ids(await search("bitcoin")), bitcoins, "An unrelated search must not poison the Bitcoin index");
  await search("util");
  assert.deepEqual(ids(await search("utiliser IA")), direct);
  assert.ok(direct.length);
} finally {
  globalThis.fetch = fetchFile;
}
// These French terms straddle native chunks with accented and plain spellings.
for (const term of ["demai", "repas", "repa"]) {
  await destroy();
  await options(settings);
  const cold = ids(await search(term));
  await preload("abcdefghijklmnopqrstuvwxyz".split("").join(" "));
  assert.deepEqual(ids(await search(term)), cold, term);
}
const accented = await search("système");
assert.ok(accented.results.length);
assert.deepEqual(
  ids(await search("système".normalize("NFD"))),
  ids(accented),
  "Canonically equivalent French spellings must return the same articles"
);
await search("systeme");
assert.deepEqual(
  ids(await search("système")),
  ids(accented),
  "Accented search must also work from a cold index"
);

const absent = [
  "coquecigruegalactique",
  "zzqqxx",
  "bitcoinement",
  '"bitcoinement"',
  "communistes",
  "organiste",
  "bitcoin coquecigruegalactique",
];
for (const term of absent) assert.deepEqual(ids(await search(term)), [], term);

for (const term of [
  "bitcoin",
  "bitco",
  "écon",
  "système",
  "monde bitcoin",
  "travailler rythme",
  "utiliser IA",
  "rencontrées",
  "démos",
  "plaisirs",
  '"trou noir"',
  "bitcoin ?",
  "bitcoin & monde",
  "bitcoin & blockchain",
  "« trou noir »",
]) {
  const matches = await search(term);
  assert.ok(matches.results.length, `Expected results for ${term}`);
  assert.deepEqual(
    ids(matches),
    ids(await nativeSearch(term)),
    `Preserve Pagefind ranking for ${term}`
  );
}

const unaccented = await search("rencontrees");
assert.ok(unaccented.results.length);
assert.deepEqual(ids(unaccented), ids(await nativeSearch("rencontrees")));
for (const [term, prefix] of [
  ["sommes dollars", /(?:^|[^\p{L}\p{N}_])sommes\b/iu],
  ["datecre", /(?:^|[^\p{L}\p{N}_])date_?cre/iu],
  ["camé", /(?:^|[^\p{L}\p{N}_])came/iu],
  ["deuxiè", /(?:^|[^\p{L}\p{N}_])deuxie/iu],
  ["systè", /(?:^|[^\p{L}\p{N}_])syste/iu],
  ["principaleme", /(?:^|[^\p{L}\p{N}_])principaleme/iu],
]) {
  const matches = await search(term);
  const expected = [];
  for (const hit of (await nativeSearch(term)).results) {
    const article = (await hit.data()).content
      .normalize("NFD")
      .replace(/\p{M}/gu, "");
    if (prefix.test(article)) expected.push(hit.id);
  }
  assert.ok(expected.length, `The corpus must exercise the prefix ${term}`);
  assert.equal(
    matches.unfilteredResultCount,
    expected.length,
    `Search count for ${term}`
  );
  assert.deepEqual(
    ids(matches),
    expected,
    `Keep each article containing ${term} in native order`
  );
}
for (const term of absent) {
  assert.deepEqual(ids(await search(term)), [], `Edited search for ${term}`);
}

for (const term of ["filles", '"filles"']) {
  const hits = await search(term);
  const articles = await Promise.all(hits.results.map(hit => hit.data()));
  assert.ok(
    articles.some(article => article.url === "/blog/etre-a-son-compte-cest-bien-construire-une-entreprise-cest-mieux/"),
    `The query ${term} must keep the article containing “une fille sur appel”`
  );
  for (const article of articles) assert.match(article.content, /\bfilles?\b/iu, article.url);
}
for (const [term, pattern] of [["voitures", /\bvoitures?\b/iu], ["ecrites", /(?:^|[^\p{L}])écrit/iu]]) {
  const expected = [];
  for (const hit of (await nativeSearch(term)).results) {
    const text = (await hit.data()).content;
    if (pattern.test(text)) expected.push(hit.id);
  }
  const found = ids(await search(term));
  assert.ok(expected.length, term);
  assert.ok(expected.every(id => found.includes(id)), term);
}
