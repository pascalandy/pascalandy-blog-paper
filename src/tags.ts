/**
 * Tag configuration
 * - slug: the URL-safe identifier (used in posts frontmatter and URLs)
 * - name: display name with proper capitalization/spacing
 * - description: short description shown on the tags page
 * - hiddenFromTagsPage: if true, tag won't appear on /tags/ but /tags/[tag]/ still works
 */

type TagConfig = {
  slug: string;
  name: string;
  description: string;
  hiddenFromTagsPage?: boolean;
  excludeFromBlogRoll?: boolean;
};

export const TAGS: TagConfig[] = [
  {
    slug: "crypto-in-montreal",
    name: "Crypto In Montreal",
    description: "41 meetups organisés depuis 2017",
    hiddenFromTagsPage: true,
    excludeFromBlogRoll: true,
  },
  {
    slug: "void",
    name: "void",
    description: "",
    hiddenFromTagsPage: true,
    excludeFromBlogRoll: true,
  },
  {
    slug: "dev-notes",
    name: "dev-notes",
    description: "Notes about how to run this website",
    excludeFromBlogRoll: true,
  },
  {
    slug: "random",
    name: "random",
    description: "Random thoughts and musings",
  },
  {
    slug: "folie",
    name: "folie",
    description: "Folie",
  },
  {
    slug: "biographie",
    name: "Biographie",
    description: "À propos de Pascal Andy",
    hiddenFromTagsPage: true,
    excludeFromBlogRoll: true,
  },
  {
    slug: "comment-le-reflechir",
    name: "comment-le-reflechir",
    description: "",
  },
  { slug: "consultation", name: "consultation", description: "" },
  { slug: "crypto", name: "crypto", description: "" },
  { slug: "du-fond-des-tripes", name: "du-fond-des-tripes", description: "" },
  { slug: "emplois", name: "emplois", description: "" },
  { slug: "musique", name: "musique", description: "" },
  { slug: "personnel", name: "personnel", description: "" },
  { slug: "projets", name: "projets", description: "" },
  { slug: "repost", name: "repost", description: "" },
  { slug: "technologie", name: "technologie", description: "" },
];

/**
 * Get tag config by slug
 * Returns default values if tag is not configured
 */
export function getTagConfig(slug: string): TagConfig {
  const config = TAGS.find(t => t.slug === slug);
  if (config) return config;

  // Default: keep lowercase, no description
  return {
    slug,
    name: slug,
    description: "",
  };
}

/**
 * Get list of tags excluded from blog roll and RSS
 */
export function getExcludedTags(): string[] {
  return TAGS.filter(t => t.excludeFromBlogRoll).map(t => t.slug);
}
