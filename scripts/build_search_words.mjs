import { mkdir, writeFile } from "node:fs/promises";
import { options, search } from "../dist/pagefind/pagefind.js";
import { initials, shardName, wordForms } from "../public/search/words.js";

const base = new URL("../dist/pagefind/", import.meta.url);
await options({ basePath: base.href });
const { results } = await search(null);
const shards = new Map([...initials, "other"].map(initial => [initial, {}]));

for (const hit of results) {
  const { content } = await hit.data();
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
  await writeFile(new URL(initial + ".json", directory), JSON.stringify(pages));
}
