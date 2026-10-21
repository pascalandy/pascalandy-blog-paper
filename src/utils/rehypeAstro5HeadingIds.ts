import Slugger from "github-slugger";
import { toString } from "hast-util-to-string";
import { visit } from "unist-util-visit";
import type { RehypePlugin } from "@astrojs/markdown-remark";

/** Keep published fragments before Astro collects IDs for the table of contents. */
export const rehypeAstro5HeadingIds: RehypePlugin = () => tree => {
  const slugger = new Slugger();
  visit(tree, "element", node => {
    if (
      !/^h[1-6]$/.test(node.tagName) ||
      typeof node.properties.id === "string"
    ) {
      return;
    }
    // Astro 5 removed one final hyphen after github-slugger handled duplicates.
    const slug = slugger.slug(toString(node));
    node.properties.id = slug.endsWith("-") ? slug.slice(0, -1) : slug;
  });
};
