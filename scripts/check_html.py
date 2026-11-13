#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the metadata and internal page links in a production build."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from overview import read, url

ROOT = Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.title = ""
        self.times: list[tuple[str, str]] = []
        self.json_ld: list[str] = []
        self.capture: str | None = None
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        if tag == "title":
            self.capture = "title"
        elif tag == "time":
            self.capture = "time"
            self.times.append((attributes.get("datetime") or "", ""))
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self.capture = "json"
            self.json_ld.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("title", "script", "time"):
            self.capture = None

    def handle_data(self, data: str) -> None:
        if self.capture == "title":
            self.title += data
        elif self.capture == "time":
            value, text = self.times[-1]
            self.times[-1] = (value, text + data)
        elif self.capture == "json":
            self.json_ld[-1] += data


def local_target(href: str, route: str, origin: str) -> str | None:
    url = urlsplit(urljoin(origin + route, href))
    if url.scheme not in ("http", "https") or url.netloc != urlsplit(origin).netloc:
        return None
    return unquote(url.path)


def exists(dist: Path, target: str) -> bool:
    path = dist / target.lstrip("/")
    return path.is_file() or (path / "index.html").is_file()


def problems(
    dist: Path, origin: str, posts: dict[str, dict[str, str]] | None = None
) -> list[str]:
    errors: list[str] = []
    titles: dict[str, str] = {}
    pages = sorted(dist.rglob("*.html"))
    if not pages:
        return [f"{dist}: no HTML pages; run: just build"]
    for path in pages:
        relative = path.relative_to(dist).as_posix()
        route = "/" + relative.removesuffix("index.html")
        page = Page(path.read_text(encoding="utf-8"))
        counts = Counter(tag for tag, _ in page.elements)
        reasons: set[str] = set()
        if not page.title.strip():
            reasons.add("missing title")
        elif page.title in titles:
            reasons.add(f"duplicate title with {titles[page.title]}")
        titles[page.title] = relative
        if counts["h1"] > 1:
            reasons.add(f"{counts['h1']} H1 headings; keep at most one")
        canonicals = []
        noindex = False
        is_post = any(
            a.get("property") == "article:published_time" for _, a in page.elements
        )
        language = (posts or {}).get(route, {}).get("lang", "fr-CA")
        html_languages = [a.get("lang") for tag, a in page.elements if tag == "html"]
        if html_languages != [language]:
            reasons.add(f"html lang must be {language}")
        for name, expected in (
            ("og:type", "article" if is_post else "website"),
            ("og:locale", "en_US" if language == "en" else "fr_CA"),
        ):
            values = [
                a.get("content")
                for tag, a in page.elements
                if tag == "meta" and a.get("property") == name
            ]
            if values != [expected]:
                reasons.add(f"{name} must occur once with {expected}")
        source_date = (posts or {}).get(route, {}).get("date_created")
        if is_post and source_date:
            calendar = datetime.fromisoformat(source_date.replace("Z", "+00:00"))
            months = (
                "janvier",
                "février",
                "mars",
                "avril",
                "mai",
                "juin",
                "juillet",
                "août",
                "septembre",
                "octobre",
                "novembre",
                "décembre",
            )
            expected_date = (
                f"{calendar.day} {months[calendar.month - 1]} {calendar.year}"
            )
            if not any(
                value[:10] == source_date[:10] and text.strip() == expected_date
                for value, text in page.times
            ):
                reasons.add(
                    f"displayed date must be {expected_date}, with calendar day unchanged"
                )
        postings = 0
        for tag, attrs in page.elements:
            if "false" in (attrs.get("class") or "").split():
                reasons.add('class contains "false"; use class:list')
            if tag == "meta":
                if "content" in attrs and not (attrs["content"] or "").strip():
                    reasons.add(
                        f"empty meta content for {attrs.get('name') or attrs.get('property')}"
                    )
                if attrs.get("name") == "robots" and "noindex" in (
                    attrs.get("content") or ""
                ):
                    noindex = True
            href = attrs.get("href")
            if tag == "link" and attrs.get("rel") == "canonical":
                canonicals.append(href)
            if href and tag in ("a", "link"):
                target = local_target(href, route, origin)
                if target is None:
                    continue
                if tag == "link" and not exists(dist, target):
                    reasons.add(f"link target missing: {href}")
                if tag == "a" and not Path(target).suffix and not target.endswith("/"):
                    reasons.add(f"page link needs trailing slash: {href}")
        if relative == "404.html":
            if canonicals or not noindex:
                reasons.add("404 needs noindex and no canonical")
        elif len(canonicals) != 1:
            reasons.add("page needs exactly one canonical")
        for block in page.json_ld:
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                reasons.add("invalid JSON-LD")
                continue
            nodes = data if isinstance(data, list) else [data]
            for node in nodes:
                if not isinstance(node, dict) or node.get("@type") != "BlogPosting":
                    continue
                postings += 1
                try:
                    value = node["datePublished"]
                    if not isinstance(value, str) or not re.match(
                        r"^\d{4}-\d{2}-\d{2}T", value
                    ):
                        raise ValueError
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except (KeyError, TypeError, ValueError):
                    reasons.add("BlogPosting needs an ISO datePublished")
        if postings != int(is_post):
            reasons.add("BlogPosting belongs only on posts, once per post")
        errors.extend(f"{relative}: {reason}" for reason in sorted(reasons))
    robots = dist / "robots.txt"
    if not robots.is_file():
        errors.append("robots.txt missing")
    else:
        sitemaps = re.findall(
            r"^Sitemap:\s*(\S+)", robots.read_text(encoding="utf-8"), re.MULTILINE
        )
        if not sitemaps:
            errors.append("robots.txt: missing Sitemap URL")
        for href in sitemaps:
            target = local_target(href, "/robots.txt", origin)
            if target is None or not exists(dist, target):
                errors.append(f"robots.txt: Sitemap target missing: {href}")
    return errors


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("dist", type=Path, nargs="?", default=ROOT / "dist")
    args = cli.parse_args()
    config = (ROOT / "src/config.ts").read_text(encoding="utf-8")
    origin = re.search(r'website: "([^"]+)"', config)
    if origin is None:
        cli.error("SITE.website not found")
    site_url = urlsplit(origin.group(1))
    state = read()
    posts = {url(post["file"]) + "/": post["data"] for post in state["posts"]}
    errors = problems(args.dist, f"{site_url.scheme}://{site_url.netloc}", posts)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(
            f"error: HTML has {len(errors)} metadata or link problems; fix the sources, then run: just check --only build",
            file=sys.stderr,
        )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
