import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const FONT_CACHE_DIR = "cache/fonts";

function ensureFontCacheDir(): void {
  if (!existsSync(FONT_CACHE_DIR)) {
    mkdirSync(FONT_CACHE_DIR, { recursive: true });
  }
}

export function getFontCacheKey(
  font: string,
  weight: number,
  style: string,
  textHash: string
): string {
  return createHash("sha256")
    .update(`${font}-${weight}-${style}-${textHash}`)
    .digest("hex")
    .slice(0, 12);
}

export function hashText(text: string): string {
  return createHash("sha256").update(text).digest("hex").slice(0, 8);
}

export function getCachedFont(cacheKey: string): ArrayBuffer | null {
  const cachePath = join(FONT_CACHE_DIR, `${cacheKey}.ttf`);
  if (existsSync(cachePath)) {
    const buffer = readFileSync(cachePath);
    // Convert Buffer to ArrayBuffer
    return buffer.buffer.slice(
      buffer.byteOffset,
      buffer.byteOffset + buffer.byteLength
    ) as ArrayBuffer;
  }
  return null;
}

export function cacheFont(cacheKey: string, fontBuffer: ArrayBuffer): void {
  ensureFontCacheDir();
  const cachePath = join(FONT_CACHE_DIR, `${cacheKey}.ttf`);
  writeFileSync(cachePath, new Uint8Array(fontBuffer));
}
