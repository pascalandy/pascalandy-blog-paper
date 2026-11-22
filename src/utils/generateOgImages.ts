import { createHash, randomUUID } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";
import { Resvg } from "@resvg/resvg-js";
import { version } from "@resvg/resvg-js/package.json";
import postOgImage from "./og-templates/post";
import siteOgImage from "./og-templates/site";
import type { CollectionEntry } from "astro:content";

const CACHE_DIR = "cache/og-images";

function rasterize(svg: string) {
  const key = createHash("sha256")
    .update(version)
    .update("\0")
    .update(svg)
    .digest("hex");
  const path = join(CACHE_DIR, `${key}.png`);
  if (existsSync(path)) return readFileSync(path);

  const png = new Resvg(svg).render().asPng();
  mkdirSync(CACHE_DIR, { recursive: true });
  const temporary = `${path}.${randomUUID()}.tmp`;
  try {
    writeFileSync(temporary, png);
    renameSync(temporary, path);
  } finally {
    rmSync(temporary, { force: true });
  }
  return png;
}

export async function generateOgImageForPost(post: CollectionEntry<"blog">) {
  return rasterize(await postOgImage(post));
}

export async function generateOgImageForSite() {
  return rasterize(await siteOgImage());
}
