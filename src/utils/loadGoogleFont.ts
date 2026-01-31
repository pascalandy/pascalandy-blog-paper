import { getFontCacheKey, getCachedFont, cacheFont } from "./fontCache";

async function loadGoogleFont(
  font: string,
  weight: number
): Promise<ArrayBuffer> {
  // Check cache first
  const cacheKey = getFontCacheKey(font, weight);
  const cached = getCachedFont(cacheKey);
  if (cached) {
    return cached;
  }

  // Download full font (no text subset for better caching)
  const API = `https://fonts.googleapis.com/css2?family=${font}:wght@${weight}`;

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
  // Text parameter kept for API compatibility, full fonts are cached
  text?: string
): Promise<
  Array<{ name: string; data: ArrayBuffer; weight: number; style: string }>
> {
  void text; // Intentionally unused - full fonts are cached instead of subsets
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
      const data = await loadGoogleFont(font, weight);
      return { name, data, weight, style };
    })
  );

  return fonts;
}

export default loadGoogleFonts;
