"""Exercise Pagefind through the search page a reader uses."""

from playwright.sync_api import Page, expect


def verify_search(page: Page, base: str) -> None:
    url = f"{base}/search/"
    page.goto(url)
    field = page.get_by_role("textbox", name="Rechercher...")
    result = page.locator(".pagefind-ui__result-title a").first
    field.fill("bitcoin")
    expect(result).to_be_visible()
    expect(page).to_have_url(f"{url}?q=bitcoin")
    first_title = result.inner_text()

    page.reload()
    expect(field).to_have_value("bitcoin")
    expect(result).to_have_text(first_title)

    missing = "coquecigruegalactique"
    field.fill(missing)
    expect(page.get_by_text("Aucun résultat", exact=True)).to_be_visible()
    expect(result).to_have_count(0)
    expect(page).to_have_url(f"{url}?q={missing}")
    page.reload()
    expect(field).to_have_value(missing)
    expect(page.get_by_text("Aucun résultat", exact=True)).to_be_visible()
    expect(result).to_have_count(0)
    page.get_by_role("button", name="Effacer").click()
    expect(field).to_have_value("")
    expect(result).to_have_count(0)
    expect(page).to_have_url(url)

    field.fill('"zzqqxx"')
    expect(page.get_by_text("Aucun résultat", exact=True)).to_be_visible()
    expect(result).to_have_count(0)

    field.fill("bitcoin ?")
    expect(result).to_have_text(first_title)
    page.reload()
    expect(field).to_have_value("bitcoin ?")
    expect(result).to_have_text(first_title)
    field.fill("travailler rythme")
    expect(
        page.get_by_role(
            "link",
            name="Comment reprendre le dessus quand le rythme accélère",
            exact=True,
        ).first
    ).to_be_visible()


def verify_search_layout(page: Page, base: str) -> None:
    page.goto(f"{base}/search/?q=aliexpress")
    result = page.locator(".pagefind-ui__result").filter(
        has=page.get_by_role("link", name="audiophile", exact=True)
    )
    excerpt = result.locator(".pagefind-ui__result-excerpt").first
    expect(excerpt).to_contain_text("https://")
    if excerpt.evaluate("node => node.scrollWidth > node.clientWidth"):
        raise ValueError("A search result excerpt clips its product URL")
    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    if overflow > 0:
        raise ValueError(
            f"Search results overflow the viewport by {overflow} CSS pixels"
        )
