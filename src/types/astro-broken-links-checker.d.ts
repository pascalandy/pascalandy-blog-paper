declare module "astro-broken-links-checker" {
  interface Options {
    logFilePath?: string;
    checkExternalLinks?: boolean;
    throwError?: boolean;
  }

  export default function astroBrokenLinksChecker(
    options?: Options
  ): import("astro").AstroIntegration;
}
