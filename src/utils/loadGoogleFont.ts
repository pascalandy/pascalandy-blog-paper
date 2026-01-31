import {
  getFontCacheKey,
  getCachedFont,
  cacheFont,
  hashText,
} from "./fontCache";

async function loadGoogleFont(
  font: string,
  text: string,
  weight: number,
  style: string
): Promise<ArrayBuffer> {
  // Generate cache key with text hash for glyph-specific caching
  const textHash = hashText(text);
  const cacheKey = getFontCacheKey(font, weight, style, textHash);

  // Check cache first
  const cached = getCachedFont(cacheKey);
  if (cached) {
    return cached;
  }

  // Download font subset with specific glyphs
  const API = `https://fonts.googleapis.com/css2?family=${font}:wght@${weight}&text=${encodeURIComponent(text)}`;

  const css = await (
    await fetch(API, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
      },
    })
  ).text();

  const resource = css.match(
    /src: url\((.+?)\) format\('(opentype|truetype)'\)/
  );

  if (!resource) throw new Error("Failed to download dynamic font");

  const res = await fetch(resource[1]);

  if (!res.ok) {
    throw new Error("Failed to download dynamic font. Status: " + res.status);
  }

  const fontBuffer = await res.arrayBuffer();

  // Cache for future use
  cacheFont(cacheKey, fontBuffer);

  return fontBuffer;
}

async function loadGoogleFonts(
  text: string
): Promise<
  Array<{ name: string; data: ArrayBuffer; weight: number; style: string }>
> {
  const fontsConfig = [
    {
      name: "IBM Plex Mono",
      font: "IBM+Plex+Mono",
      weight: 400,
      style: "normal",
    },
    {
      name: "IBM Plex Mono",
      font: "IBM+Plex+Mono",
      weight: 700,
      style: "bold",
    },
  ];

  const fonts = await Promise.all(
    fontsConfig.map(async ({ name, font, weight, style }) => {
      const data = await loadGoogleFont(font, text, weight, style);
      return { name, data, weight, style };
    })
  );

  return fonts;
}

export default loadGoogleFonts;
