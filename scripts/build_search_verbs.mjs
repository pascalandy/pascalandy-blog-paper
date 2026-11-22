import { mkdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { fold, initials, shardName } from "../public/search/words.js";

const lexicon = new URL(
  import.meta.resolve("node-lefff/src/lefff-3.4.mlex/lefff-3.4.mlex")
);

export async function buildSearchVerbs(articlesByWord, directory) {
  const readings = new Map();
  const formsByVerb = new Map();
  const source = await readFile(lexicon);
  const lines = source.toString("utf8").split("\n");
  for (const line of lines) {
    const [word, type, lemma] = line.split("\t");
    if (!/^\p{Ll}+$/u.test(word)) continue;
    if (articlesByWord.has(word)) {
      if (!readings.has(word)) readings.set(word, new Set());
      readings.get(word).add(lemma);
    }
    if (type === "v") {
      if (!formsByVerb.has(lemma)) formsByVerb.set(lemma, new Set());
      formsByVerb.get(lemma).add(word);
    }
  }

  const pagesByVerb = new Map();
  for (const [word, lemmas] of readings) {
    if (lemmas.size !== 1) continue;
    const [lemma] = lemmas;
    if (!formsByVerb.get(lemma)?.has(word)) continue;
    if (!pagesByVerb.has(lemma)) pagesByVerb.set(lemma, new Set());
    for (const id of articlesByWord.get(word)) pagesByVerb.get(lemma).add(id);
  }

  const shards = new Map(
    [...initials, "other"].map(initial => [
      initial,
      { forms: Object.create(null), pages: Object.create(null) },
    ])
  );
  for (const [verb, pages] of pagesByVerb) {
    const ids = [...pages].sort();
    for (const form of formsByVerb.get(verb)) {
      const shard = shards.get(shardName(fold(form)));
      (shard.forms[form] ??= []).push(verb);
      shard.pages[verb] = ids;
    }
  }

  await mkdir(directory, { recursive: true });
  const notice =
    "French verb-to-article index derived from Lefff 3.4 (Benoît Sagot), 2026-11-22. " +
    "The index is licensed under LGPL-LR. See /search/lefff.txt and the original lefff-3.4.mlex.gz.";
  await writeFile(new URL("lefff-3.4.mlex.gz", directory), gzipSync(source));
  for (const [initial, shard] of shards) {
    await writeFile(
      new URL(initial + ".json", directory),
      JSON.stringify({ notice, ...shard })
    );
  }
}
