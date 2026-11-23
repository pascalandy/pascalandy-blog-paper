import { mkdir, writeFile } from "node:fs/promises";
import { options, search } from "../dist/pagefind/pagefind.js";
import { fold, initials, shardName, wordForms } from "../public/search/words.js";
import { buildSearchVerbs } from "./build_search_verbs.mjs";

const base = new URL("../dist/pagefind/", import.meta.url);
await options({ basePath: base.href });
const { results } = await search(null);
const shards = new Map([...initials, "other"].map(initial => [initial, {}]));

const seeds = new Map([...shards.keys()].map(initial => [initial, new Set()]));
const articlesByWord = new Map();
for (const hit of results) {
  const { content } = await hit.data();
  for (const word of new Set(content.normalize("NFC").toLowerCase().match(/\p{L}+|\p{N}+/gu))) {
    const seed = word.slice(0, 2);
    const group = seeds.get(shardName(fold(word)));
    group.add(seed);
    group.add(fold(seed));
    if (!articlesByWord.has(word)) articlesByWord.set(word, []);
    articlesByWord.get(word).push(hit.id);
  }
  const words = new Set(content.split(/\s+/u).flatMap(wordForms));
  const sorted = [...words].sort();
  const longest = sorted.filter((word, i) => !sorted[i + 1]?.startsWith(word));
  const groups = Map.groupBy(longest, shardName);
  for (const [initial, pages] of shards) {
    pages[hit.id] = "\n" + (groups.get(initial) ?? []).join("\n");
  }
}

const directory = new URL("prefixes/", base);
await mkdir(directory, { recursive: true });
for (const [initial, pages] of shards) {
  pages.seeds = [...seeds.get(initial)].sort().join(" ");
  await writeFile(new URL(initial + ".json", directory), JSON.stringify(pages));
}

await buildSearchVerbs(articlesByWord, new URL("verbs/", base));
