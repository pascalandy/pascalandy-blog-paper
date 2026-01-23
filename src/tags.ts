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
};

export const TAGS: TagConfig[] = [
  {
    slug: "crypto-in-montreal",
    name: "Crypto In Montreal",
    description: "41 meetups organisés depuis 2017",
    hiddenFromTagsPage: true,
  },
  {
    slug: "void",
    name: "void",
    description: "",
    hiddenFromTagsPage: true,
  },
  {
    slug: "dev-notes",
    name: "dev-notes",
    description: "Notes about how to run this website",
  },
  {
    slug: "random",
    name: "random",
    description: "Random thoughts and musings",
  },
  {
    slug: "biographie",
    name: "Biographie",
    description: "À propos de Pascal Andy",
    hiddenFromTagsPage: true,
  },
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
