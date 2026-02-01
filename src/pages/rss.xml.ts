import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { getPath } from "@/utils/getPath";
import getSortedPosts from "@/utils/getSortedPosts";
import { SITE } from "@/config";
import { getExcludedTags } from "@/tags";

const excludedTags = getExcludedTags();

export async function GET() {
  const posts = await getCollection(
    "blog",
    ({ data }) =>
      !data.draft && !data.tags.some(tag => excludedTags.includes(tag))
  );
  const sortedPosts = getSortedPosts(posts);
  return rss({
    title: SITE.title,
    description: SITE.desc,
    site: SITE.website,
    items: sortedPosts.map(({ data, id, filePath }) => ({
      link: getPath(id, filePath),
      title: data.title,
      description: data.description,
      pubDate: new Date(data.date_created),
    })),
  });
}
