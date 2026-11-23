import { mkdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { fold, initials, shardName } from "../public/search/words.js";

const lexicon = new URL(
  import.meta.resolve("node-lefff/src/lefff-3.4.mlex/lefff-3.4.mlex")
);

function unambiguousInflections(source) {
  const soleLemma = new Map();
  const foldedLemmas = new Map();
  const inflections = new Map();
  function record(map, word, lemma) {
    if (!map.has(word)) map.set(word, lemma);
    else if (map.get(word) !== lemma) map.set(word, null);
  }
  for (const line of source.toString("utf8").split("\n")) {
    const [word, type, lemma] = line.split("\t");
    if (!/^\p{Ll}+$/u.test(word)) continue;
    record(soleLemma, word, lemma);
    record(foldedLemmas, fold(word), lemma);
    if (type === "v" || type === "nc") inflections.set(word, lemma);
  }
  for (const [word, lemma] of inflections) {
    if (soleLemma.get(word) !== lemma) inflections.delete(word);
  }
  const queries = new Map(inflections);
  for (const [word, lemma] of inflections) {
    const folded = fold(word);
    if (foldedLemmas.get(folded) === lemma) queries.set(folded, lemma);
  }
  return { articles: inflections, queries };
}

export async function buildSearchVerbs(articlesByWord, directory) {
  const source = await readFile(lexicon);
  const { articles, queries } = unambiguousInflections(source);
  const pagesByVerb = new Map();
  for (const [word, pages] of articlesByWord) {
    const verb = articles.get(word);
    if (!verb) continue;
    if (!pagesByVerb.has(verb)) pagesByVerb.set(verb, new Set());
    for (const page of pages) pagesByVerb.get(verb).add(page);
  }

  const shards = new Map(
    [...initials, "other"].map(initial => [
      initial,
      { forms: Object.create(null), pages: Object.create(null) },
    ])
  );
  for (const [form, verb] of queries) {
    const pages = pagesByVerb.get(verb);
    if (!pages) continue;
    const shard = shards.get(shardName(fold(form)));
    shard.forms[form] = [verb];
    shard.pages[verb] ??= [...pages].sort();
  }

  await mkdir(directory, { recursive: true });
  const notice =
    "French inflection-to-article index derived from Lefff 3.4 (Benoît Sagot), 2026-11-23. " +
    "The index is licensed under LGPL-LR. See /search/lefff.txt and the original lefff-3.4.mlex.gz.";
  await writeFile(new URL("lefff-3.4.mlex.gz", directory), gzipSync(source));
  for (const [initial, shard] of shards) {
    await writeFile(
      new URL(initial + ".json", directory),
      JSON.stringify({ notice, ...shard })
    );
  }
}
