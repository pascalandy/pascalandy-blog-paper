"""Check how a saved theme and the system color scheme interact on the built blog."""

from typing import Literal

from playwright.sync_api import Browser, Page, expect

Theme = Literal["light", "dark"]


def change_system_theme(page: Page, theme: Theme) -> None:
    event = page.evaluate_handle("""() => {
        const observed = {changed: false};
        matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
            observed.changed = true;
        }, {once: true});
        return observed;
    }""")
    try:
        page.emulate_media(color_scheme=theme)
        page.wait_for_function("event => event.changed", arg=event, timeout=5000)
    finally:
        event.dispose()


def verify_theme_journey(browser: Browser, base: str) -> None:
    for system, other in (("light", "dark"), ("dark", "light")):
        with browser.new_page(color_scheme=system) as page:
            page.goto(base + "/")
            root = page.locator("html")
            expect(root).to_have_attribute("data-theme", system)
            change_system_theme(page, other)
            expect(root).to_have_attribute("data-theme", other)
            change_system_theme(page, system)
            expect(root).to_have_attribute("data-theme", system)

            page.locator("#theme-btn").click()
            expect(root).to_have_attribute("data-theme", other)
            change_system_theme(page, other)
            change_system_theme(page, system)
            expect(root).to_have_attribute("data-theme", other)
            page.reload()
            expect(root).to_have_attribute("data-theme", other)
            page.get_by_role("link", name="tags", exact=True).click()
            expect(page).to_have_url(base + "/tags/")
            expect(root).to_have_attribute("data-theme", other)
