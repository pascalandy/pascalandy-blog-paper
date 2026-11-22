"""Check every three-action mobile menu trace against the built header."""

from itertools import product

from playwright.sync_api import Browser, Error, Page, expect

TOGGLE = ("click button", "press Enter")
DISMISS = (*TOGGLE, "click backdrop", "change theme", "follow blog link")


def check_state(page: Page, expanded: bool) -> None:
    button = page.locator("#menu-btn")
    panel = page.locator("#menu-items")
    expect(button).to_have_attribute("aria-expanded", str(expanded).lower())
    button.press("Tab")
    focus_inside = panel.evaluate("menu => menu.contains(document.activeElement)")
    if focus_inside != expanded:
        raise ValueError(
            f"Tab from the menu button should {'enter' if expanded else 'skip'} its links"
        )
    page.keyboard.press("Shift+Tab")
    expect(button).to_be_focused()
    blog = panel.get_by_role("link", name="Blog", exact=True)
    if expanded:
        expect(blog).to_be_visible()
    else:
        expect(blog).to_have_count(0)


def act(page: Page, action: str, base: str) -> None:
    button = page.locator("#menu-btn")
    match action:
        case "click button":
            button.click()
        case "press Enter":
            page.keyboard.press("Enter")
        case "click backdrop":
            page.mouse.click(1, page.evaluate("window.innerHeight - 1"))
        case "change theme":
            html = page.locator("html")
            before = html.get_attribute("data-theme")
            if before not in ("light", "dark"):
                raise ValueError(f"expected a light or dark theme, got {before!r}")
            page.locator("#theme-btn").click()
            expect(html).to_have_attribute(
                "data-theme", "dark" if before == "light" else "light"
            )
        case "follow blog link":
            page.locator("#menu-items").get_by_role(
                "link", name="Blog", exact=True
            ).click()
            expect(page).to_have_url(f"{base}/blog/")
        case _:
            raise ValueError(f"unknown menu action {action!r}")


def verify_menu_model(browser: Browser, base: str) -> int:
    traces = 0
    for actions in product(TOGGLE, DISMISS, TOGGLE):
        path = ["load /"]
        with browser.new_page(
            viewport={"width": 639, "height": 900}, color_scheme="light", locale="fr-CA"
        ) as page:
            page.set_default_timeout(5000)
            try:
                page.goto(f"{base}/")
                expanded = False
                check_state(page, expanded)
                for action in actions:
                    path.append(action)
                    act(page, action, base)
                    expanded = not expanded
                    check_state(page, expanded)
            except (Error, AssertionError, ValueError) as error:
                raise ValueError(
                    f"Mobile menu at {page.url}: {' → '.join(path)}: {error}"
                ) from error
        traces += 1
    return traces
