import { mkdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { fold, initials, shardName } from "../public/search/words.js";

const lexicon = new URL(
  import.meta.resolve("node-lefff/src/lefff-3.4.mlex/lefff-3.4.mlex")
);

function unambiguousVerbForms(source) {
  const soleLemma = new Map();
  const verbs = new Map();
  for (const line of source.toString("utf8").split("\n")) {
    const [word, type, lemma] = line.split("\t");
    if (!/^\p{Ll}+$/u.test(word)) continue;
    if (!soleLemma.has(word)) soleLemma.set(word, lemma);
    else if (soleLemma.get(word) !== lemma) soleLemma.set(word, null);
    if (type === "v") verbs.set(word, lemma);
  }
  for (const [word, lemma] of verbs) {
    if (soleLemma.get(word) !== lemma) verbs.delete(word);
  }
  return verbs;
}

export async function buildSearchVerbs(articlesByWord, directory) {
  const source = await readFile(lexicon);
  const verbForms = unambiguousVerbForms(source);
  const pagesByVerb = new Map();
  for (const [word, pages] of articlesByWord) {
    const verb = verbForms.get(word);
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
  for (const [form, verb] of verbForms) {
    const pages = pagesByVerb.get(verb);
    if (!pages) continue;
    const shard = shards.get(shardName(fold(form)));
    shard.forms[form] = [verb];
    shard.pages[verb] ??= [...pages].sort();
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
