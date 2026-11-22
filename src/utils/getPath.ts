import { slug as githubSlug } from "github-slugger";
import { slugifyStr } from "./slugify";

export const BLOG_PATH = "src/data/blog";

export function blogEntryId({
  entry,
  data,
}: {
  entry: string;
  data: Record<string, unknown>;
}) {
  if (data.slug) return String(data.slug);
  return entry
    .replace(/\.md$/, "")
    .split("/")
    .map(segment => githubSlug(segment))
    .join("/")
    .replace(/\/index$/, "");
}

export function getPath(
  id: string,
  filePath: string | undefined,
  includeBase = true
) {
  const folders = (filePath ?? "")
    .replace(BLOG_PATH, "")
    .split("/")
    .slice(0, -1)
    .filter(folder => folder && !folder.startsWith("_"))
    .map(slugifyStr);
  const slug = [...folders, id.split("/").at(-1)].join("/");
  return includeBase ? `/blog/${slug}/` : `/${slug}`;
}
