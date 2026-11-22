"""Check the contrast of rendered reader pages with axe-core."""

from pathlib import Path

from playwright.sync_api import Page

AXE = Path(__file__).resolve().parents[4] / "node_modules/axe-core/axe.min.js"


def verify_contrast(page: Page) -> None:
    page.add_script_tag(path=AXE)
    findings = page.evaluate("""async () => {
        const result = await axe.run(document, { runOnly: ["color-contrast"], iframes: false });
        if (!result.passes.length) throw Error("axe could not verify any text contrast");
        return [...result.violations, ...result.incomplete].flatMap(rule =>
            rule.nodes.map(node => node.target.join(" ") + ": " + node.failureSummary)
        );
    }""")
    if findings:
        raise ValueError("Text contrast: " + "\n".join(findings))

    link = page.locator("#article p a[href]").first
    if link.count():
        underline = link.evaluate("""link => {
            const reference = document.createElement("span");
            reference.style.color = "var(--primary)";
            link.append(reference);
            const primary = getComputedStyle(reference).color;
            reference.remove();
            const style = getComputedStyle(link);
            return style.textDecorationLine.includes("underline") && style.textDecorationColor === primary;
        }""")
        if not underline:
            raise ValueError(
                "Article links need a visible underline in the primary color"
            )
