import { defineConfig, envField, fontProviders } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import astroBrokenLinksChecker from "astro-broken-links-checker";

import {
  transformerNotationDiff,
  transformerNotationHighlight,
  transformerNotationWordHighlight,
} from "@shikijs/transformers";
import { transformerFileName } from "./src/utils/transformers/fileName";
import { SITE } from "./src/config";
import { rehypeAstro5HeadingIds } from "./src/utils/rehypeAstro5HeadingIds";

// https://astro.build/config
export default defineConfig({
  site: SITE.website,
  cacheDir: "./cache",
  compressHTML: true,
  integrations: [
    sitemap(),
    astroBrokenLinksChecker({
      logFilePath: "broken-links.log",
      checkExternalLinks: false,
      throwError: true,
    }),
  ],
  markdown: {
    processor: unified({ rehypePlugins: [rehypeAstro5HeadingIds] }),
    syntaxHighlight: {
      type: "shiki",
      excludeLangs: ["mermaid"],
    },
    shikiConfig: {
      // For more themes, visit https://shiki.style/themes
      // Using css-variables theme to inherit colors from the active theme
      theme: "css-variables",
      wrap: false,
      transformers: [
        transformerFileName({ style: "v2", hideDot: false }),
        transformerNotationHighlight(),
        transformerNotationWordHighlight(),
        transformerNotationDiff({ matchAlgorithm: "v3" }),
      ],
    },
  },
  vite: {
    plugins: [tailwindcss()],
    build: {
      cssTarget: [
        "chrome111",
        "edge111",
        "firefox114",
        "safari16.3",
        "ios16.3",
      ],
    },
    optimizeDeps: {
      include: ["@pagefind/default-ui"],
      exclude: ["@resvg/resvg-js"],
    },
  },
  image: {
    // Default layout for all images (can be overridden per-component)
    layout: "constrained",
    // Enable CSS for responsive image resizing
    responsiveStyles: true,
    // Breakpoints for srcset generation (common device widths)
    breakpoints: [640, 750, 828, 1080, 1200, 1920],
  },
  env: {
    schema: {
      PUBLIC_GOOGLE_SITE_VERIFICATION: envField.string({
        access: "public",
        context: "client",
        optional: true,
      }),
    },
  },
  fonts: [
    {
      name: "JetBrains Mono",
      cssVariable: "--font-jetbrains-mono",
      provider: fontProviders.google(),
      fallbacks: ["monospace"],
      weights: [300, 400, 500, 600, 700],
      styles: ["normal", "italic"],
    },
  ],
});
