import eslintPluginAstro from "eslint-plugin-astro";
import globals from "globals";
import tseslint from "typescript-eslint";

export default [
  ...tseslint.configs.recommended,
  ...eslintPluginAstro.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  { rules: { "no-console": "error" } },
  // Declaration files keep `interface`, which merges into globals such as Window
  {
    files: ["**/*.{ts,tsx,mts,cts,astro}"],
    ignores: ["**/*.d.ts"],
    rules: {
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
    },
  },
  { ignores: ["dist/**", ".astro", "public/pagefind/**"] },
];
