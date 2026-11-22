import assert from "node:assert/strict";
import { options, search } from "../dist/search/pagefind.js";
import { search as nativeSearch } from "../dist/pagefind/pagefind.js";

await options({
  basePath: new URL("../dist/pagefind/", import.meta.url).href,
  baseUrl: "/",
});

const ids = response => response.results.map(hit => hit.id);
const accented = await search("système");
assert.ok(accented.results.length);
await search("systeme");
assert.deepEqual(ids(await search("système")), ids(accented), "Accented search must also work from a cold index");

const absent = ["coquecigruegalactique", "zzqqxx"];
for (const term of absent) assert.deepEqual(ids(await search(term)), [], term);

for (const term of ["bitcoin", "bitco", "écon", "principaleme", "monde bitcoin", '"trou noir"']) {
  const matches = await search(term);
  assert.ok(matches.results.length, `Expected results for ${term}`);
  assert.deepEqual(ids(matches), ids(await nativeSearch(term)), `Preserve Pagefind ranking for ${term}`);
}
for (const term of absent) {
  assert.deepEqual(ids(await search(term)), [], `Edited search for ${term}`);
}
