import type { CollectionEntry } from "astro:content";
import postFilter from "./postFilter";

const getSortedPosts = (posts: CollectionEntry<"blog">[]) => {
  return posts.filter(postFilter).sort((a, b) => {
    const dateDifference =
      Math.floor(new Date(b.data.date_created).getTime() / 1000) -
      Math.floor(new Date(a.data.date_created).getTime() / 1000);

    return dateDifference || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  });
};

export default getSortedPosts;
