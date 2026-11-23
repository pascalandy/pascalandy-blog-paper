import license from "node-lefff/src/lefff-3.4.mlex/LICENSE?raw";

export function GET() {
  return new Response(
    "Lefff 3.4, Benoît Sagot. Index des formes nominales et verbales adapté au blogue le 23 novembre 2026.\n" +
      "Source du lexique : /pagefind/verbs/lefff-3.4.mlex.gz\n\n" +
      license
  );
}
