import { getExcludedTags } from "@/tags";
import type { CollectionEntry } from "astro:content";

const excludedTags = new Set(getExcludedTags());

export const blogRollFilter = ({ data }: CollectionEntry<"blog">) =>
  !data.draft && !data.tags.some(tag => excludedTags.has(tag));
