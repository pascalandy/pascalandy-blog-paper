/**
 * Mermaid diagram initialization script
 * Loads Mermaid from CDN and renders diagrams client-side
 * Only included on posts with `mermaid: true` in frontmatter
 */

const MERMAID_CDN =
  "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

const getTheme = (): string => {
  const theme = document.documentElement.dataset.theme;
  return theme === "dark" ? "dark" : "default";
};

const initMermaid = async () => {
  const blocks = document.querySelectorAll("pre > code.language-mermaid");

  if (blocks.length === 0) return;

  const mermaid = await import(/* @vite-ignore */ MERMAID_CDN).catch(
    () => null
  );
  if (!mermaid) {
    for (const block of blocks)
      block.parentElement?.classList.add("mermaid-error");
    return;
  }

  mermaid.default.initialize({
    startOnLoad: false,
    theme: getTheme(),
  });

  for (const block of blocks) {
    const pre = block.parentElement;
    if (!pre) continue;

    const code = block.textContent || "";
    const id = `mermaid-${crypto.randomUUID().slice(0, 8)}`;

    try {
      const { svg } = await mermaid.default.render(id, code);
      const wrapper = document.createElement("div");
      wrapper.className = "mermaid-diagram";
      wrapper.innerHTML = svg;
      pre.replaceWith(wrapper);
    } catch {
      pre.classList.add("mermaid-error");
    }
  }
};

initMermaid();

document.addEventListener("astro:page-load", initMermaid);
