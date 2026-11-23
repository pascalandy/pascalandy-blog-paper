import { mkdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";
import { fold, initials, shardName } from "../public/search/words.js";

const lexicon = new URL(
  import.meta.resolve("node-lefff/src/lefff-3.4.mlex/lefff-3.4.mlex")
);

function recordLemma(map, form, lemma) {
  if (!map.has(form)) map.set(form, lemma);
  else if (map.get(form) !== lemma) map.set(form, null);
}

function lexicalGroups(source) {
  const lemmas = new Map();
  const folded = new Map();
  const nouns = new Map();
  const verbs = new Map();
  for (const line of source.toString("utf8").split("\n")) {
    const [word, type, lemma] = line.split("\t");
    if (!/^\p{Ll}+$/u.test(word)) continue;
    recordLemma(lemmas, word, lemma);
    recordLemma(folded, fold(word), lemma);
    if (type === "nc") recordLemma(nouns, word, lemma);
    if (type === "v") recordLemma(verbs, word, lemma);
  }

  function groups(word, forQuery) {
    const keys = [];
    const noun = nouns.get(word);
    // The bilingual blog uses both spellings for this technical term.
    if (noun) keys.push("noun:" + (noun === "system" ? "système" : noun));
    const verb = verbs.get(word);
    if (verb) {
      const unambiguous = lemmas.get(word) === verb;
      if (unambiguous) keys.push("verb:" + verb);
      // An ambiguous article form can support a close, dictionary-attested
      // inflection (écrit/écrites) without linking sommes to unrelated être forms.
      if (unambiguous || !forQuery) {
        keys.push("ending:" + verb + ":" + fold(word).replace(/e{0,2}s?$/u, ""));
      }
    }
    return keys;
  }
  return { lemmas, folded, groups };
}

export async function buildSearchVerbs(articlesByWord, directory) {
  const source = await readFile(lexicon);
  const { lemmas, folded, groups } = lexicalGroups(source);
  const pagesByGroup = new Map();
  for (const [word, pages] of articlesByWord) {
    for (const key of groups(word, false)) {
      if (!pagesByGroup.has(key)) pagesByGroup.set(key, new Set());
      for (const page of pages) pagesByGroup.get(key).add(page);
    }
  }
  const shards = new Map(
    [...initials, "other"].map(initial => [
      initial,
      { forms: Object.create(null), pages: Object.create(null) },
    ])
  );
  for (const [word, lemma] of lemmas) {
    const keys = groups(word, true).filter(key => pagesByGroup.has(key));
    if (!keys.length) continue;
    const plain = fold(word);
    const shard = shards.get(shardName(plain));
    const spellings = word !== plain && lemma && folded.get(plain) === lemma ? [word, plain] : [word];
    for (const form of spellings) {
      shard.forms[form] = [...new Set([...(shard.forms[form] ?? []), ...keys])];
    }
    for (const key of keys) shard.pages[key] ??= [...pagesByGroup.get(key)].sort();
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
