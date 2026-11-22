import { writeFile } from "node:fs/promises";
import { options, search } from "../dist/pagefind/pagefind.js";
import { wordForms } from "../public/search/words.js";

await options({ basePath: new URL("../dist/pagefind/", import.meta.url).href });
const { results } = await search(null);
const words = new Set();
for (const hit of results) {
  const { content } = await hit.data();
  for (const token of content.split(/\s+/u)) {
    for (const form of wordForms(token)) words.add(form);
  }
}
const sorted = [...words].sort();
const prefixes = sorted.filter((word, i) => !sorted[i + 1]?.startsWith(word));
await writeFile(new URL("../dist/pagefind/words.txt", import.meta.url), `\n${prefixes.join("\n")}\n`);
