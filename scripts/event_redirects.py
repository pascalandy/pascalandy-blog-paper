"""The old event addresses removed in d6b2d99 and their static HTML redirects."""

import re
from html.parser import HTMLParser

EVENT_REDIRECTS = {
    f"/blog/cryptoinmontreal-{event:02}/": f"/blog/cim-{event:02}/"
    for event in range(1, 42)
}


class PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.language: str | None = None
        self.generator: str | None = None
        self.canonicals: list[str] = []
        self.indexed = False
        self.in_article = False
        self.article_text = False
        self.directives: list[str] = []
        self.has_base = False
        self.inert: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"template", "script", "style", "noscript"}:
            self.inert.append(tag)
        if self.inert:
            return
        values = dict(attrs)
        if tag == "base" and "href" in values:
            self.has_base = True
        if "data-pagefind-body" in values:
            self.indexed = True
        if tag == "article" and values.get("id") == "article":
            self.in_article = True
        if tag == "meta" and (values.get("http-equiv") or "").lower() == "refresh":
            self.directives.append(values.get("content") or "")
        if tag == "link" and "canonical" in (values.get("rel") or "").lower().split():
            self.canonicals.append(values.get("href") or "")
        elif tag == "html":
            self.language = values.get("lang")
        elif tag == "meta" and (values.get("name") or "").lower() == "generator":
            self.generator = values.get("content")

    def handle_endtag(self, tag: str) -> None:
        if self.inert:
            if tag == self.inert[-1]:
                self.inert.pop()
            return
        if tag == "article":
            self.in_article = False

    def handle_data(self, data: str) -> None:
        if self.in_article and not self.inert and data.strip():
            self.article_text = True


def redirect_problem(html: str, target: str) -> str | None:
    refresh = PageMetadata()
    refresh.feed(html)
    refresh.close()
    if refresh.has_base:
        return f"remove the base URL so the redirect stays on this site at {target}"
    if len(refresh.directives) == 1:
        directive = re.fullmatch(
            r"\s*0\s*;\s*url\s*=\s*(\S+)\s*", refresh.directives[0], re.IGNORECASE
        )
        if directive and directive[1] == target:
            return None
    return f"expected an immediate refresh to {target}, received {refresh.directives!r}"
