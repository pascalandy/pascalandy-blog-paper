import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";
import { TAGS } from "./tags";

export const BLOG_PATH = "src/data/blog";

const TAG_SLUGS = new Set(TAGS.map(({ slug }) => slug));

const tag = z.string().refine(
  slug => TAG_SLUGS.has(slug),
  slug => ({
    message: `tag "${slug}" is not registered: add it to TAGS in src/tags.ts`,
  })
);

const blog = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: `./${BLOG_PATH}` }),
  schema: ({ image }) =>
    z.object({
      author: z.string(),
      date_created: z.date(),
      title: z.string(),
      featured: z.boolean().optional(),
      draft: z.boolean().optional(),
      tags: z.array(tag).min(1),
      ogImage: image().or(z.string()).optional(),
      description: z.string(),
      canonicalURL: z.string().optional(),
      hideEditPost: z.boolean().optional(),
      mermaid: z.boolean().optional().default(false),
    }),
});

export const collections = { blog };
