import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const CACHE_DIR = "cache/og-images";

// Bump when OG template changes to invalidate cache
const OG_TEMPLATE_VERSION = "v1";

function ensureCacheDir(): void {
  if (!existsSync(CACHE_DIR)) {
    mkdirSync(CACHE_DIR, { recursive: true });
  }
}

export function generateCacheKey(
  title: string,
  author: string,
  siteTitle: string,
  theme: string
): string {
  const content = `${OG_TEMPLATE_VERSION}-${title}-${author}-${siteTitle}-${theme}`;
  return createHash("sha256").update(content).digest("hex").slice(0, 16);
}

export function getCachedOgImage(cacheKey: string): Buffer | null {
  const cachePath = join(CACHE_DIR, `${cacheKey}.png`);
  if (existsSync(cachePath)) {
    return readFileSync(cachePath);
  }
  return null;
}

export function cacheOgImage(
  cacheKey: string,
  pngBuffer: Buffer | Uint8Array
): void {
  ensureCacheDir();
  const cachePath = join(CACHE_DIR, `${cacheKey}.png`);
  // Node.js writeFileSync accepts Buffer/Uint8Array
  writeFileSync(cachePath, pngBuffer as Uint8Array);
}
