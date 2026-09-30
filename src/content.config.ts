import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";
import { TAGS } from "./tags";
import { slugifyStr } from "./utils/slugify";

export const BLOG_PATH = "src/data/blog";

const TAG_SLUGS = new Set(TAGS.map(({ slug }) => slug));

// A tag page's URL is slugifyStr(slug), and pages look the tag up in TAGS by
// that URL form, so a slug must equal it
const tag = z
  .string()
  .refine(
    slug => TAG_SLUGS.has(slug),
    slug => ({
      message: `tag "${slug}" is not registered: add it to TAGS in src/tags.ts`,
    })
  )
  .refine(
    slug => slugifyStr(slug) === slug,
    slug => ({
      message: `tag "${slug}" is not in URL form: rename it to "${slugifyStr(slug)}" in src/tags.ts and in the posts that use it`,
    })
  );

const blog = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: `./${BLOG_PATH}` }),
  schema: ({ image }) =>
    z
      .object(
        {
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
        },
        {
          errorMap: (issue, ctx) => ({
            message:
              issue.code === "unrecognized_keys"
                ? `unknown key ${issue.keys.join(", ")}: remove it, or add it to the schema in src/content.config.ts`
                : ctx.defaultError,
          }),
        }
      )
      .strict(),
});

export const collections = { blog };
