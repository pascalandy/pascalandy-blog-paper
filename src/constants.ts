import IconRss from "@/assets/icons/IconRss.svg";
import IconGitHub from "@/assets/icons/IconGitHub.svg";
import IconBrandX from "@/assets/icons/IconBrandX.svg";
import IconLinkedin from "@/assets/icons/IconLinkedin.svg";
import IconFacebook from "@/assets/icons/IconFacebook.svg";
import { SITE } from "@/config";
import type { Props } from "astro";

type Social = {
  name: string;
  href: string;
  linkTitle: string;
  icon: (_props: Props) => Element;
};

export const SOCIALS: Social[] = [
  {
    name: "X",
    href: "https://twitter.com/askpascalandy",
    linkTitle: `${SITE.title} on X`,
    icon: IconBrandX,
  },
  {
    name: "LinkedIn",
    href: "/blog/linkedin/",
    linkTitle: `${SITE.title} on LinkedIn`,
    icon: IconLinkedin,
  },
  {
    name: "Facebook",
    href: "https://www.facebook.com/askpascalandy",
    linkTitle: `${SITE.title} on Facebook`,
    icon: IconFacebook,
  },
  {
    name: "GitHub",
    href: "https://github.com/pascalandy",
    linkTitle: `${SITE.title} on GitHub`,
    icon: IconGitHub,
  },
  {
    name: "GitHub",
    href: "https://github.com/firepress-org",
    linkTitle: `FirePress on GitHub`,
    icon: IconGitHub,
  },
  {
    name: "RSS",
    href: "/rss.xml",
    linkTitle: `RSS Feed`,
    icon: IconRss,
  },
] as const;
