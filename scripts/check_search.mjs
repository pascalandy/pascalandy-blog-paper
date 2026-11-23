import assert from "node:assert/strict";
import { options, search } from "../dist/search/pagefind.js";
import { preload, search as nativeSearch } from "../dist/pagefind/pagefind.js";

await options({
  basePath: new URL("../dist/pagefind/", import.meta.url).href,
  baseUrl: "/",
});

const ids = response => response.results.map(hit => hit.id);
const fetched = new Set();
const originalFetch = globalThis.fetch;
globalThis.fetch = (url, ...args) => {
  const path = new URL(url).pathname;
  if (path.includes("/pagefind/index/")) fetched.add(path.split("/").pop());
  return originalFetch(url, ...args);
};
try {
  const direct = ids(await search("utiliser IA"));
  assert.ok(direct.length);
  const cold = new Set(fetched);
  await search("util");
  assert.deepEqual(ids(await search("utiliser IA")), direct);
  // Ask Pagefind for every word in this build. Older hashed files may remain on disk.
  const vocabulary = new Set();
  for (const hit of (await nativeSearch(null)).results) {
    const { content } = await hit.data();
    for (const word of content.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? []) vocabulary.add(word);
  }
  const words = [...vocabulary];
  for (let i = 0; i < words.length; i += 100) await preload(words.slice(i, i + 100).join(" "));
  assert.ok(cold.size);
  assert.deepEqual(fetched, cold, "Cold search must load all active index shards");
} finally {
  globalThis.fetch = originalFetch;
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
