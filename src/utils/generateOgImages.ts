import { Resvg } from "@resvg/resvg-js";
import { type CollectionEntry } from "astro:content";
import postOgImage from "./og-templates/post";
import siteOgImage from "./og-templates/site";
import { ACTIVE_THEME } from "@/config";
import {
  generateCacheKey,
  getCachedOgImage,
  cacheOgImage,
} from "./ogImageCache";

function svgBufferToPngBuffer(svg: string) {
  const resvg = new Resvg(svg);
  const pngData = resvg.render();
  return pngData.asPng();
}

export async function generateOgImageForPost(post: CollectionEntry<"blog">) {
  const cacheKey = generateCacheKey(
    post.data.title,
    post.data.date_created,
    ACTIVE_THEME
  );

  // Check cache first
  const cached = getCachedOgImage(cacheKey);
  if (cached) {
    return cached;
  }

  // Generate and cache
  const svg = await postOgImage(post);
  const png = svgBufferToPngBuffer(svg);
  cacheOgImage(cacheKey, png);
  return png;
}

export async function generateOgImageForSite() {
  // Site OG rarely changes, use static cache key
  const cacheKey = generateCacheKey(
    "site-og",
    new Date("2024-01-01"),
    ACTIVE_THEME
  );

  const cached = getCachedOgImage(cacheKey);
  if (cached) {
    return cached;
  }

  const svg = await siteOgImage();
  const png = svgBufferToPngBuffer(svg);
  cacheOgImage(cacheKey, png);
  return png;
}
