"""The old event addresses removed in d6b2d99 and their static HTML redirects."""

import re
from html.parser import HTMLParser

EVENT_REDIRECTS = {
    f"/blog/cryptoinmontreal-{event:02}/": f"/blog/cim-{event:02}/"
    for event in range(1, 42)
}


class Refresh(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.directives: list[str] = []
        self.has_base = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "base" and "href" in attributes:
            self.has_base = True
        if tag == "meta" and (attributes.get("http-equiv") or "").lower() == "refresh":
            self.directives.append(attributes.get("content") or "")


def redirect_problem(html: str, target: str) -> str | None:
    refresh = Refresh()
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
