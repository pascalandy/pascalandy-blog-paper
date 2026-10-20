#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["beautifulsoup4==4.14.3", "pillow==12.0.0", "tinycss2==1.4.0", "cbor2==6.1.5", "fonttools[woff]==4.60.1"]
# [tool.uv]
# exclude-newer = "1 week"
# ///
"""Compare two static Astro builds. Exit 1 means material differences, 2 means error."""

from __future__ import annotations

import argparse
import collections
import difflib
import gzip
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from functools import cache
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

import cbor2
import tinycss2
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageSequence, UnidentifiedImageError

ASSET = re.compile(r"(/?_astro/)([^\s\"'<>?#]+)")
HASH = re.compile(r"([._])[A-Za-z0-9_-]{8,}(?=\.)")
CID = re.compile(r"data-astro-cid-[a-z0-9]+", re.IGNORECASE)
BLOCKS = frozenset(
    [
        "article",
        "aside",
        "blockquote",
        "body",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    ]
)
HIDDEN = frozenset(["head", "script", "style", "template", "noscript"])
PAGEFIND_MARKER = b"pagefind_dcd"
# Only explicitly labelled build clocks are noise; publication dates remain intact.
BUILD_CLOCK = re.compile(
    r"((?:build[-_ ]?(?:time|timestamp|date)|built[-_ ]?at)[\s\"':=]+)"
    r"\d{4}-\d\d-\d\d[T ][\d:.+Z-]+",
    re.IGNORECASE,
)


def norm(value: object) -> str:
    text = str(value)
    text = ASSET.sub(lambda m: m[1] + HASH.sub(r"\1HASH", m[2]), text)
    text = re.sub(r"(_astro/fonts/)[0-9a-f]{16,}(?=\.)", r"\1HASH", text)
    return " ".join(
        BUILD_CLOCK.sub(r"\1BUILD_TIME", CID.sub("data-astro-cid-HASH", text)).split()
    )


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def route(path: Path, root: Path) -> str:
    name = path.relative_to(root).as_posix()
    if name == "index.html":
        return "/"
    if name.endswith("/index.html"):
        return "/" + name[:-10]
    return "/" + name


def local_file(root: Path, href: str, page_route: str = "/") -> Path | None:
    url = urlsplit(urljoin("https://dist.invalid" + page_route, href))
    if url.netloc != "dist.invalid":
        return None
    candidate = (root / unquote(url.path).lstrip("/")).resolve()
    if not candidate.is_relative_to(root.resolve()):
        return None
    return candidate


@cache
def css_declarations(css: str) -> set[str]:
    # Tokenize instead of matching var(--x) uses or strings/comments as definitions.
    found: set[str] = set()

    def walk(tokens: list[Any]) -> None:
        for index, token in enumerate(tokens):
            if token.type == "ident" and token.value.startswith("--"):
                following = [
                    t
                    for t in tokens[index + 1 :]
                    if t.type not in ("whitespace", "comment")
                ]
                if (
                    following
                    and following[0].type == "literal"
                    and following[0].value == ":"
                ):
                    found.add(token.value)
            for attr in ("content", "arguments"):
                nested = getattr(token, attr, None)
                if nested:
                    walk(nested)

    walk(tinycss2.parse_component_value_list(css))
    return found


@cache
def image_data_from_bytes(payload: bytes) -> dict[str, Any]:
    encoding_hash = hashlib.sha256(payload).hexdigest()
    result: dict[str, Any] = {"bytes": len(payload), "sha256": encoding_hash}
    try:
        with Image.open(io.BytesIO(payload)) as source:
            pixels = hashlib.sha256()
            frames = 0
            frames_to_decode = (
                [source] if source.format == "MPO" else ImageSequence.Iterator(source)
            )
            for frame in frames_to_decode:
                pixels.update(frame.convert("RGBA").tobytes())
                pixels.update(str(frame.info.get("duration", 0)).encode())
                frames += 1
            result.update(
                dimensions=list(source.size), frames=frames, pixels=pixels.hexdigest()
            )
    except UnidentifiedImageError:
        # Conservatively retain byte identity for vectors the raster decoder cannot read.
        result["pixels"] = "unrendered:" + encoding_hash
    return result


def image_data(path: Path) -> dict[str, Any]:
    return image_data_from_bytes(path.read_bytes())


def image_assets(
    soup: BeautifulSoup, root: Path, page_route: str
) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for index, tag in enumerate(soup.select("img,picture source")):
        refs = []
        if tag.get("src"):
            refs.append(("src", str(tag["src"])))
        for candidate, value in enumerate(str(tag.get("srcset", "")).split(",")):
            pieces = value.strip().split()
            if pieces:
                refs.append(
                    ("srcset:" + str(candidate) + ":" + " ".join(pieces[1:]), pieces[0])
                )
        for attribute, href in refs:
            path = local_file(root, href, page_route)
            slot = str(index) + ":" + attribute
            if path is None:
                continue
            assets.append(
                {
                    "slot": slot,
                    "href": href,
                    "exists": path.is_file(),
                    **(image_data(path) if path.is_file() else {}),
                }
            )
    return assets


def visible_text(soup: BeautifulSoup) -> str:
    parts: list[str] = []

    def walk(node: Tag | NavigableString) -> None:
        if isinstance(node, NavigableString):
            if not isinstance(node, Comment):
                parts.append(str(node))
            return
        if (
            node.name in HIDDEN
            or node.has_attr("hidden")
            or node.get("aria-hidden") == "true"
        ):
            return
        if node.name in BLOCKS:
            parts.append(" ")
        for child in node.children:
            walk(child)
        if node.name in BLOCKS:
            parts.append(" ")

    walk(soup)
    return norm("".join(parts))


def page_data(path: Path, root: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    # Decode HTML character references once, as the browser does. Do not unescape
    # these DOM values again: &amp;#39; is literal text, unlike &#39; or an apostrophe.
    soup = BeautifulSoup(raw, "html.parser")
    page_route = route(path, root)
    title = norm(soup.title.get_text()) if soup.title else None
    metadata = []
    for element in soup.select("meta"):
        key = str(element.get("name", element.get("property", ""))).lower()
        if key == "description" or key.startswith(("og:", "twitter:")):
            metadata.append((key, norm(element.get("content", ""))))
    for element in soup.select("link"):
        raw_rel = element.get("rel")
        rel = raw_rel.split() if isinstance(raw_rel, str) else (raw_rel or [])
        if any(r in rel for r in ("canonical", "alternate")):
            metadata.append(
                (
                    "link:" + " ".join(sorted(rel)),
                    tuple(
                        sorted(
                            (key, norm(element.get(key, "")))
                            for key in ("href", "hreflang", "type", "media")
                        )
                    ),
                )
            )
    headings = [
        (tag.name, tag.get("id"), norm(tag.get_text()))
        for tag in soup.select("h1,h2,h3,h4,h5,h6")
    ]
    ids = [(tag.name, str(tag["id"])) for tag in soup.select("[id]")]
    links = [norm(tag.get("href", "")) for tag in soup.select("a[href],area[href]")]
    images = [
        tuple(
            (key, norm(tag[key]) if tag.has_attr(key) else None)
            for key in ("src", "srcset", "width", "height", "alt")
        )
        for tag in soup.select("img")
    ]
    sources = [
        tuple(
            (key, norm(tag[key]) if tag.has_attr(key) else None)
            for key in ("src", "srcset", "type", "media")
        )
        for tag in soup.select("picture source")
    ]
    inline_scripts = [
        str(tag.string or tag.get_text()) for tag in soup.select("script:not([src])")
    ]
    elements = [tag.name for tag in soup.find_all(True)]
    attributes = [
        (
            tag.name,
            sorted(
                (key, norm(" ".join(value) if isinstance(value, list) else value))
                for key, value in tag.attrs.items()
                if not key.startswith("data-astro-cid-")
                and not (tag.name == "astro-island" and key == "uid")
            ),
        )
        for tag in soup.find_all(True)
    ]
    assets = image_assets(soup, root, page_route)
    css_chunks = [str(tag.string or tag.get_text()) for tag in soup.select("style")]
    css_chunks.extend(str(tag.get("style")) for tag in soup.select("[style]"))
    seen: set[Path] = set()
    missing: list[str] = []

    def load_css(href: str, context: str = page_route) -> None:
        file = local_file(root, href, context)
        if file is None:
            missing.append("external:" + href)
            return
        if file in seen:
            return
        seen.add(file)
        if not file.is_file():
            missing.append(href)
            return
        css = file.read_text(encoding="utf-8")
        css_chunks.append(css)
        for match in re.finditer(r"@import\s+(?:url\()?['\"]([^'\"]+)['\"]", css):
            load_css(match[1], "/" + file.relative_to(root).as_posix())

    for tag in soup.select('link[rel~="stylesheet"]'):
        load_css(str(tag.get("href", "")))
    css_text = "\n".join(css_chunks)
    css = {
        "bytes": sum(len(chunk.encode()) for chunk in css_chunks),
        "custom_properties": sorted(css_declarations(css_text)),
        "missing": sorted(missing),
        "content_hash": digest(norm(css_text)),
    }
    # Expose changes outside the requested semantic fields for review as cosmetic.
    # Attribute order, scope IDs, island UIDs, and HTML spacing cannot create noise.
    for comment in soup.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith("data-astro-cid-") or (
                tag.name == "astro-island" and attr == "uid"
            ):
                del tag[attr]
            else:
                value = tag.attrs[attr]
                tag.attrs[attr] = norm(
                    " ".join(value) if isinstance(value, list) else value
                )
        tag.attrs = dict(sorted(tag.attrs.items()))
    normalized_html = norm(soup.decode())
    for tag in soup.select(
        "script,style,template,noscript,head,[hidden],[aria-hidden='true']"
    ):
        tag.decompose()
    text = visible_text(soup)
    return {
        "title": title,
        "metadata": sorted(metadata, key=str),
        "headings": headings,
        "ids": ids,
        "links": links,
        "inline_scripts": inline_scripts,
        "elements": elements,
        "attributes": attributes,
        "images": images,
        "picture_sources": sources,
        "image_assets": assets,
        "text": text,
        "inline_text": [
            norm(tag.get_text())
            for tag in soup.select("p,h1,h2,h3,h4,h5,h6,figcaption")
        ],
        "css": css,
        "html": digest(normalized_html),
        "raw": hashlib.sha256(raw.encode()).hexdigest(),
    }


def xml_value(element: ET.Element) -> Any:
    return {
        "tag": element.tag,
        "attributes": sorted(element.attrib.items()),
        "text": norm(element.text or ""),
        "children": [xml_value(child) for child in element],
    }


def feeds(root: Path) -> dict[str, Any]:
    rss_file = root / "rss.xml"
    rss: dict[str, Any] = {"present": rss_file.is_file()}
    if rss_file.is_file():
        channel = ET.parse(rss_file).getroot().find("channel")
        if channel is None:
            raise ValueError(f"{rss_file}: missing channel")
        rss["channel"] = [
            xml_value(e)
            for e in channel
            if e.tag != "item" and e.tag not in ("lastBuildDate",)
        ]
        rss["items"] = [xml_value(item) for item in channel.findall("item")]
    urls: set[str] = set()
    indexes: set[str] = set()
    files = sorted(root.rglob("sitemap*.xml"))
    for file in files:
        tree = ET.parse(file).getroot()
        for loc in tree.iter():
            if loc.tag.rsplit("}", 1)[-1] == "loc":
                (indexes if tree.tag.endswith("sitemapindex") else urls).add(
                    norm(loc.text or "")
                )
    robots = root / "robots.txt"
    return {
        "rss": rss,
        "sitemap": {
            "present": bool(files),
            "urls": sorted(urls),
            "indexes": sorted(indexes),
        },
        "robots": [
            norm(line)
            for line in robots.read_text(encoding="utf-8").splitlines()
            if norm(line) and not line.lstrip().startswith("#")
        ]
        if robots.is_file()
        else None,
    }


def pagefind_payload(path: Path) -> bytes:
    decoded = gzip.decompress(path.read_bytes())
    if not decoded.startswith(PAGEFIND_MARKER):
        raise ValueError(f"{path}: missing Pagefind payload marker")
    return decoded[len(PAGEFIND_MARKER) :]


def pagefind(root: Path) -> dict[str, Any]:
    folder = root / "pagefind"
    entry_file = folder / "pagefind-entry.json"
    if not entry_file.is_file():
        return {
            "present": False,
            "indexed_pages": 0,
            "languages": {},
            "versions": {},
            "routes": {},
        }
    entry = json.loads(entry_file.read_text(encoding="utf-8"))
    languages = {lang: info["page_count"] for lang, info in entry["languages"].items()}
    meta_paths = sorted(folder.glob("*.pf_meta"))
    if not meta_paths:
        raise ValueError(f"{folder}: no Pagefind metadata")
    routes: dict[str, dict[str, Any]] = {}
    versions: dict[str, str] = {}
    referenced: set[Path] = set()
    for meta_path in meta_paths:
        if not meta_path.name.startswith("pagefind."):
            raise ValueError(f"{meta_path}: unexpected metadata filename")
        language = meta_path.name.removeprefix("pagefind.").split("_", 1)[0]
        if language in versions:
            raise ValueError(f"{folder}: duplicate metadata for {language}")
        metadata = cbor2.loads(pagefind_payload(meta_path))
        versions[language] = str(metadata[0])
        urls: list[str] = []
        for record in metadata[1]:
            fragment_path = folder / "fragment" / f"{record[0]}.pf_fragment"
            fragment = json.loads(pagefind_payload(fragment_path))
            url = fragment["url"]
            if not isinstance(url, str):
                raise TypeError(f"{fragment_path}: URL is not text")
            key = language + " " + url
            if key in routes:
                raise ValueError(f"{folder}: duplicate fragment for {key}")
            routes[key] = {"fragment": fragment, "postings": {}}
            urls.append(url)
            referenced.add(fragment_path)
        shards = sorted((folder / "index").glob(f"{language}_*.pf_index"))
        if not shards:
            raise ValueError(f"{folder}: no index shards for {language}")
        for shard_path in shards:
            shard = cbor2.loads(pagefind_payload(shard_path))
            for word, matches in shard[0]:
                for number, positions in matches:
                    try:
                        url = urls[number]
                    except IndexError as error:
                        raise ValueError(
                            f"{shard_path}: document {number} has no fragment"
                        ) from error
                    postings = routes[language + " " + url]["postings"]
                    postings.setdefault(word, []).append(
                        json.dumps(positions, ensure_ascii=False, separators=(",", ":"))
                    )
    all_fragments = set((folder / "fragment").glob("*.pf_fragment"))
    if all_fragments != referenced:
        raise ValueError(f"{folder}: unreferenced or missing Pagefind fragments")
    if sum(languages.values()) != len(routes):
        raise ValueError(f"{folder}: page count does not match fragments")
    for data in routes.values():
        data["postings"] = {
            key: sorted(values) for key, values in data["postings"].items()
        }
    return {
        "present": True,
        "indexed_pages": len(routes),
        "languages": languages,
        "versions": versions,
        "routes": routes,
    }


def pixel_diff(first: Path, second: Path, threshold: int = 0) -> dict[str, Any]:
    with Image.open(first) as a, Image.open(second) as b:
        sizes = [list(a.size), list(b.size)]
        if a.size != b.size:
            return {"dimensions": sizes, "ratio": 1.0, "changed_pixels": None}
        difference = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA"))
        channels = difference.split()
        maximum = channels[0]
        for channel in channels[1:]:
            maximum = ImageChops.lighter(maximum, channel)
        changed = sum(maximum.histogram()[threshold + 1 :])
        return {
            "dimensions": sizes,
            "ratio": changed / (a.width * a.height),
            "changed_pixels": changed,
        }


def sample(a: Any, b: Any) -> dict[str, Any]:
    left = json.dumps(a, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    right = json.dumps(b, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    # Single-line text fields need a local excerpt around their first change.
    if isinstance(a, str) and isinstance(b, str):
        index = next(
            (i for i, pair in enumerate(zip(a, b)) if pair[0] != pair[1]),
            min(len(a), len(b)),
        )
        return {
            "offset": index,
            "a": a[max(0, index - 80) : index + 220],
            "b": b[max(0, index - 80) : index + 220],
        }
    return {
        "diff": list(difflib.unified_diff(left, right, fromfile="A", tofile="B", n=2))[
            :35
        ],
        "a_hash": digest(a),
        "b_hash": digest(b),
    }


def asset_key(name: str) -> str:
    return HASH.sub(r"\1HASH", name)


def file_inventory(root: Path) -> dict[str, dict[str, Any]]:
    result = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix == ".html":
            continue
        name = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        result[name] = {
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    return result


def page_asset_pairs(
    first: Path, second: Path, pages: dict[str, Path], other: dict[str, Path]
) -> dict[str, str]:
    pairs = {}
    for url in pages.keys() & other.keys():
        left = BeautifulSoup(pages[url].read_text(encoding="utf-8"), "html.parser")
        right = BeautifulSoup(other[url].read_text(encoding="utf-8"), "html.parser")
        for selector, attribute in (
            ("script[src]", "src"),
            ("link[rel~=stylesheet]", "href"),
        ):
            a_refs = [
                local_file(first, str(tag[attribute]), url)
                for tag in left.select(selector)
            ]
            b_refs = [
                local_file(second, str(tag[attribute]), url)
                for tag in right.select(selector)
            ]
            for a_path, b_path in zip(a_refs, b_refs):
                if (
                    a_path is not None
                    and b_path is not None
                    and b_path.is_relative_to(second)
                ):
                    pairs[b_path.relative_to(second).as_posix()] = a_path.relative_to(
                        first
                    ).as_posix()
    return pairs


def font_names(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*.woff2"))


def font_roles(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    roles = []
    mismatches = []
    for css_file in root.rglob("*.css"):
        css = css_file.read_text(encoding="utf-8")
        for rule in tinycss2.parse_stylesheet(
            css, skip_comments=True, skip_whitespace=True
        ):
            if (
                rule.type != "at-rule"
                or rule.lower_at_keyword != "font-face"
                or not rule.content
            ):
                continue
            declarations = tinycss2.parse_declaration_list(
                rule.content, skip_comments=True, skip_whitespace=True
            )
            values = {
                item.lower_name: tinycss2.serialize(item.value).strip()
                for item in declarations
                if item.type == "declaration"
            }
            style = values.get("font-style", "normal").lower()
            weights = [
                int(value)
                for value in re.findall(r"\b\d{3}\b", values.get("font-weight", "400"))
            ]
            if not weights:
                raise ValueError(f"{css_file}: font-face has unsupported font-weight")
            for url in re.findall(r"url\(['\"]?([^'\")]+)", values.get("src", "")):
                if not urlsplit(url).path.endswith(".woff2"):
                    continue
                href = urljoin(
                    "https://dist.invalid/" + css_file.relative_to(root).as_posix(), url
                )
                font_path = local_file(root, href.replace("https://dist.invalid", ""))
                if font_path is None or not font_path.is_file():
                    raise ValueError(f"{css_file}: missing font {url}")
                with TTFont(font_path, lazy=True) as font:
                    italic = bool(
                        font["head"].macStyle & 2 or font["OS/2"].fsSelection & 1
                    )
                    axis = (
                        next(
                            (
                                axis
                                for axis in font["fvar"].axes
                                if axis.axisTag == "wght"
                            ),
                            None,
                        )
                        if "fvar" in font
                        else None
                    )
                    low, high = (
                        (axis.minValue, axis.maxValue)
                        if axis
                        else (font["OS/2"].usWeightClass,) * 2
                    )
                wanted_italic = style.startswith(("italic", "oblique"))
                if italic != wanted_italic or min(weights) < low or max(weights) > high:
                    mismatches.append(
                        f"{font_path.relative_to(root)}: expected {style} {values.get('font-weight', '400')} from {css_file.relative_to(root)}, font has italic={italic} weight={low}..{high}"
                    )
                roles.append(
                    {
                        "file": font_path.relative_to(root).as_posix(),
                        "style": style,
                        "weight": weights,
                        "font_italic": italic,
                        "font_weight": [low, high],
                    }
                )
    return roles, mismatches


def asset_groups(
    root: Path, inventory: dict[str, dict[str, Any]], fetched: bool
) -> dict[str, list[tuple[str, dict[str, Any]]]]:
    groups: dict[str, list[tuple[str, dict[str, Any]]]] = collections.defaultdict(list)
    for name, info in inventory.items():
        if name.startswith("pagefind/") and (
            name.endswith((".pf_meta", ".pf_index", ".pf_fragment"))
            or name == "pagefind/pagefind-entry.json"
        ):
            continue
        if fetched and name.endswith(".woff2"):
            continue
        groups[asset_key(name)].append((name, info))
    return {key: sorted(value) for key, value in groups.items()}


def compare(
    first: Path,
    second: Path,
    known_noise: dict[str, str],
    accepted: dict[str, str] | None = None,
    fetched: bool = False,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    accepted = accepted or {}

    def check(
        kind: str, target: str, a: Any, b: Any, normalization: str | None = None
    ) -> None:
        classification = (
            "identical" if a == b else ("cosmetic" if normalization else "material")
        )
        fingerprint = digest([kind, target, sorted((digest(a), digest(b)))])
        known = known_noise.get(fingerprint) if a != b else None
        acceptance = accepted.get(fingerprint) if a != b else None
        item: dict[str, Any] = {
            "kind": kind,
            "target": target,
            "classification": "cosmetic" if known or acceptance else classification,
        }
        if a != b:
            item.update(sample=sample(a, b), fingerprint=fingerprint)
            if normalization:
                item["normalization"] = normalization
            if known:
                item["known_noise"] = known
            if acceptance:
                item["accepted"] = acceptance
        checks.append(item)

    a_pages = {route(p, first): p for p in first.rglob("*.html")}
    b_pages = {route(p, second): p for p in second.rglob("*.html")}
    if not a_pages or not b_pages:
        raise ValueError("both dist directories must contain HTML pages")
    if fetched:
        check("routes", "/", [], sorted(b_pages.keys() - a_pages.keys()))
    else:
        check("routes", "/", sorted(a_pages), sorted(b_pages))
    inventory: dict[str, Any] = {}
    for url in sorted(b_pages.keys() & a_pages.keys()):
        a, b = page_data(a_pages[url], first), page_data(b_pages[url], second)
        for key in (
            "title",
            "metadata",
            "headings",
            "ids",
            "links",
            "inline_scripts",
            "elements",
            "attributes",
            "images",
            "picture_sources",
            "text",
            "inline_text",
        ):
            check(key, url, a[key], b[key])
        for kind, keys in (
            ("image_pixels", ("slot", "exists", "dimensions", "frames", "pixels")),
            ("image_bytes", ("slot", "exists", "bytes", "sha256")),
        ):
            values = [
                [
                    {key: asset.get(key) for key in keys}
                    for asset in data["image_assets"]
                ]
                for data in (a, b)
            ]
            normalization = (
                "lossless image encoding"
                if kind == "image_bytes"
                and [asset.get("pixels") for asset in a["image_assets"]]
                == [asset.get("pixels") for asset in b["image_assets"]]
                else None
            )
            check(kind, url, *values, normalization=normalization)
        for key in ("bytes", "custom_properties", "missing", "content_hash"):
            normalization = (
                "fetched font filename"
                if fetched
                and key == "bytes"
                and a["css"]["content_hash"] == b["css"]["content_hash"]
                else None
            )
            check("css_" + key, url, a["css"][key], b["css"][key], normalization)
        for side, data in (("A", a), ("B", b)):
            if data["css"]["missing"]:
                check("css_unresolved", url + ":" + side, [], data["css"]["missing"])
        semantic_fields = (
            "title",
            "metadata",
            "headings",
            "ids",
            "links",
            "inline_scripts",
            "elements",
            "attributes",
            "images",
            "picture_sources",
            "text",
            "inline_text",
            "css",
        )
        explained = any(a[field] != b[field] for field in semantic_fields)
        check(
            "normalized_html",
            url,
            a["html"],
            b["html"],
            "covered by parsed DOM fields" if explained else None,
        )
        check(
            "raw_html",
            url,
            a["raw"],
            b["raw"],
            "DOM normalization or parsed fields"
            if a["html"] == b["html"] or explained
            else None,
        )
        inventory[url] = {
            "css_a": a["css"],
            "css_b": b["css"],
            "images_a": a["image_assets"],
            "images_b": b["image_assets"],
        }
    a_feed, b_feed = feeds(first), feeds(second)
    for key in a_feed:
        if (
            not fetched
            or (key == "rss" and (second / "rss.xml").is_file())
            or (key == "sitemap" and any(second.glob("sitemap*.xml")))
            or (key == "robots" and (second / "robots.txt").is_file())
        ):
            check(key, key, a_feed[key], b_feed[key])
    a_index, b_index = pagefind(first), pagefind(second)
    if not fetched or b_index["present"]:
        for field in ("present", "indexed_pages", "languages", "versions"):
            check("pagefind_" + field, "pagefind", a_index[field], b_index[field])
        for key in sorted(a_index["routes"].keys() | b_index["routes"].keys()):
            a_route = a_index["routes"].get(key, {})
            b_route = b_index["routes"].get(key, {})
            check(
                "pagefind_fragment",
                key,
                a_route.get("fragment"),
                b_route.get("fragment"),
            )
            check(
                "pagefind_postings",
                key,
                a_route.get("postings"),
                b_route.get("postings"),
            )

    # OG endpoints only. favicon and content PNGs are not OG endpoint renders.
    def og_files(root: Path) -> dict[str, Path]:
        return {
            p.relative_to(root).as_posix(): p
            for p in root.rglob("*.png")
            if p.name == "og.png" or (p.name == "index.png" and "_astro" not in p.parts)
        }

    a_og, b_og = og_files(first), og_files(second)
    if not fetched:
        check("og_routes", "OG PNG endpoints", sorted(a_og), sorted(b_og))
    og = {}
    for name in sorted(a_og.keys() & b_og.keys()):
        result = pixel_diff(a_og[name], b_og[name])
        og[name] = result
        check("og_dimensions", name, result["dimensions"][0], result["dimensions"][1])
        check("og_pixels", name, 0.0, result["ratio"])
    a_files, b_files = file_inventory(first), file_inventory(second)
    a_groups, b_groups = (
        asset_groups(first, a_files, fetched),
        asset_groups(second, b_files, fetched),
    )
    if fetched:
        pairs = page_asset_pairs(first, second, a_pages, b_pages)
        for b_name, a_name in pairs.items():
            b_key, a_key = asset_key(b_name), asset_key(a_name)
            if b_key != a_key and b_key in b_groups:
                b_groups.setdefault(a_key, []).extend(b_groups.pop(b_key))
    for key in sorted(b_groups if fetched else a_groups.keys() | b_groups.keys()):
        a_rows, b_rows = a_groups.get(key, []), b_groups.get(key, [])
        a_values = [{"name": name, **value} for name, value in a_rows]
        b_values = [{"name": name, **value} for name, value in b_rows]
        normalization = None
        if len(a_rows) == len(b_rows) == 1:
            a_name, a_info = a_rows[0]
            b_name, b_info = b_rows[0]
            if a_info["sha256"] == b_info["sha256"] and a_name != b_name:
                normalization = "asset hash filename"
            elif (
                Path(a_name).suffix.lower()
                in (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif")
                and Path(b_name).suffix.lower() == Path(a_name).suffix.lower()
            ):
                a_pixels, b_pixels = (
                    image_data(first / a_name),
                    image_data(second / b_name),
                )
                if all(
                    a_pixels.get(field) == b_pixels.get(field)
                    for field in ("dimensions", "frames", "pixels")
                ):
                    normalization = "lossless image encoding"
            elif fetched and a_name.endswith(".css") and b_name.endswith(".css"):
                a_css = re.sub(
                    r"/_astro/fonts/[^)\"']+\.woff2",
                    "/_astro/fonts/FONT.woff2",
                    (first / a_name).read_text(encoding="utf-8"),
                )
                b_css = re.sub(
                    r"/_astro/fonts/[^)\"']+\.woff2",
                    "/_astro/fonts/FONT.woff2",
                    (second / b_name).read_text(encoding="utf-8"),
                )
                if a_css == b_css:
                    normalization = "fetched font filename"
            elif a_name.endswith(".xml") and b_name.endswith(".xml"):
                if xml_value(ET.parse(first / a_name).getroot()) == xml_value(
                    ET.parse(second / b_name).getroot()
                ):
                    normalization = "XML serialization"
            elif (
                a_name == b_name == "robots.txt"
                and a_feed["robots"] == b_feed["robots"]
            ):
                normalization = "robots comment or whitespace"
        check("assets", key, a_values, b_values, normalization)
    a_fonts, b_fonts = font_names(first), font_names(second)
    font_checks: dict[str, Any] = {"a": a_fonts, "b": b_fonts}
    if fetched:
        font_checks["roles_a"], mismatches_a = font_roles(first)
        font_checks["roles_b"], mismatches_b = font_roles(second)
        check("font_roles", "fetched fonts", [], mismatches_a + mismatches_b)
    counts = dict(collections.Counter(item["classification"] for item in checks))
    material = counts.get("material", 0)
    return {
        "ok": True,
        "verdict": "MATERIAL"
        if material
        else ("COSMETIC" if counts.get("cosmetic") else "IDENTICAL"),
        "summary": counts,
        "routes": {
            "a": len(a_pages),
            "b": len(b_pages),
            "added": sorted(b_pages.keys() - a_pages.keys()),
            "removed": sorted(a_pages.keys() - b_pages.keys()),
        },
        "pagefind": {"a": a_index, "b": b_index},
        "fonts": font_checks,
        "files": {"a": a_files, "b": b_files},
        "og": og,
        "pages": inventory,
        "checks": checks,
        "inputs": {"a": str(first), "b": str(second)},
        "known_noise_matches": sum("known_noise" in item for item in checks),
        "acceptance_matches": sum("accepted" in item for item in checks),
    }


def main() -> int:
    cli = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: uv run parity.py baseline/dist candidate/dist --json parity.json",
    )
    cli.add_argument("dist_a", type=Path)
    cli.add_argument("dist_b", type=Path)
    cli.add_argument("--json", type=Path, help="write the full machine-readable report")
    cli.add_argument(
        "--known-noise",
        type=Path,
        help="JSON fingerprint-to-evidence map; only exact measured pairs are downgraded",
    )
    cli.add_argument("--accept", type=Path, help="exact fingerprint-to-reason ledger")
    cli.add_argument(
        "--fetched",
        action="store_true",
        help="compare a fetched subset and verify font roles",
    )
    args = cli.parse_args()
    try:
        for path in (args.dist_a, args.dist_b):
            if not path.is_dir():
                raise ValueError(f"not a dist directory: {path}")
        noise = (
            json.loads(args.known_noise.read_text(encoding="utf-8"))
            if args.known_noise
            else {}
        )
        accepted = (
            json.loads(args.accept.read_text(encoding="utf-8")) if args.accept else {}
        )
        if not isinstance(accepted, dict) or any(
            not isinstance(k, str)
            or not re.fullmatch(r"[0-9a-f]{64}", k)
            or not isinstance(v, str)
            or not v.strip()
            for k, v in accepted.items()
        ):
            raise ValueError(
                "accept ledger must map exact SHA-256 fingerprints to reasons"
            )
        report = compare(
            args.dist_a.resolve(), args.dist_b.resolve(), noise, accepted, args.fetched
        )
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(
            json.dumps(
                {
                    key: report[key]
                    for key in (
                        "ok",
                        "verdict",
                        "summary",
                        "routes",
                        "known_noise_matches",
                        "acceptance_matches",
                    )
                }
                | {
                    "pagefind": {
                        side: {
                            key: report["pagefind"][side][key]
                            for key in ("present", "indexed_pages", "languages")
                        }
                        for side in ("a", "b")
                    },
                    "fonts": {side: report["fonts"][side] for side in ("a", "b")},
                    "report": str(args.json) if args.json else None,
                    "material_samples": [
                        item
                        for item in report["checks"]
                        if item["classification"] == "material"
                    ][:8],
                },
                ensure_ascii=False,
            )
        )
        return 1 if report["summary"].get("material") else 0
    except (OSError, ValueError, TypeError, ET.ParseError, KeyError) as error:
        print(json.dumps({"ok": False, "errors": [str(error)]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
