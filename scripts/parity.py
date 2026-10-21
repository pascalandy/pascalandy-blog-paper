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
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

import cbor2
import tinycss2
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageOps, ImageSequence, UnidentifiedImageError

ASSET = re.compile(r"(/?_astro/)([^\s\"'<>?#]+)")
HASH = re.compile(r"(\.)[A-Za-z0-9_-]{8}(?:_[A-Za-z0-9_-]{4,8})?(?=\.[A-Za-z0-9]+$)")
FONT_REF = re.compile(r"(/_astro/fonts/)[^\s\"'<>?)]+\.woff2")
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
PAGE_FIELDS = (
    "title",
    "metadata",
    "metadata_image_pixels",
    "headings",
    "ids",
    "links",
    "resources",
    "inline_scripts",
    "inline_styles",
    "attributes",
    "duplicate_attributes",
    "structure",
    "preformatted",
    "images",
    "picture_sources",
    "text",
    "inline_text",
)


def norm(value: object, *, preserve_edges: bool = False) -> str:
    text = str(value)
    text = ASSET.sub(lambda m: m[1] + HASH.sub(r"\1HASH", m[2]), text)
    text = re.sub(r"(_astro/fonts/)[0-9a-f]{16,}(?=\.)", r"\1HASH", text)
    result = re.sub(r"[ \t\n\f\r]+", " ", text)
    return result if preserve_edges else result.strip(" \t\n\f\r")


def normalize_asset_names(value: Any) -> Any:
    if isinstance(value, str):
        return ASSET.sub(lambda match: match[1] + HASH.sub(r"\1HASH", match[2]), value)
    if isinstance(value, list):
        return [normalize_asset_names(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_asset_names(item) for key, item in value.items()}
    return value


def normalize_font_refs(value: Any) -> Any:
    if isinstance(value, str):
        return FONT_REF.sub(r"\1FONT.woff2", value)
    if isinstance(value, list):
        return [normalize_font_refs(item) for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_font_refs(item) for item in value)
    if isinstance(value, dict):
        return {key: normalize_font_refs(item) for key, item in value.items()}
    return value


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


def local_file(
    root: Path,
    href: str,
    page_route: str = "/",
    allowed_hosts: frozenset[str] = frozenset(),
) -> Path | None:
    url = urlsplit(urljoin("https://dist.invalid" + page_route, href))
    if url.netloc != "dist.invalid" and url.netloc not in allowed_hosts:
        return None
    candidate = (root / unquote(url.path).lstrip("/")).resolve()
    if not candidate.is_relative_to(root.resolve()):
        return None
    return candidate


PNG_RENDER_CHUNKS = frozenset({b"cICP", b"mDCV", b"cLLI"})


def png_render_chunks(payload: bytes) -> list[tuple[str, str]]:
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return []
    result = []
    position = 8
    while position + 12 <= len(payload):
        length = int.from_bytes(payload[position : position + 4], "big")
        end = position + 12 + length
        if end > len(payload):
            raise ValueError("truncated PNG chunk")
        kind = payload[position + 4 : position + 8]
        if kind == b"IDAT":
            break
        if kind in PNG_RENDER_CHUNKS:
            result.append((kind.decode("ascii"), payload[position + 8 : end - 4].hex()))
        position = end
    return result


class BitReader:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.offset = 0

    def read(self, count: int = 1) -> int:
        if self.offset + count > len(self.payload) * 8:
            raise ValueError("truncated AV1 sequence header")
        value = 0
        for _ in range(count):
            value = (value << 1) | (
                self.payload[self.offset // 8] >> (7 - self.offset % 8) & 1
            )
            self.offset += 1
        return value


def av1_color_config(payload: bytes) -> dict[str, Any]:
    bits = BitReader(payload)
    profile = bits.read(3)
    still_picture = bits.read()
    reduced = bits.read()
    if not still_picture or not reduced:
        raise ValueError(
            "unsupported non-reduced AVIF sequence header: only reduced still images are normalized"
        )
    bits.read(5)  # level
    width_bits, height_bits = bits.read(4) + 1, bits.read(4) + 1
    bits.read(width_bits)
    bits.read(height_bits)
    for _ in range(6):
        bits.read()  # coding tools before color_config
    high_bitdepth = bits.read()
    depth = (
        (12 if bits.read() else 10)
        if profile == 2 and high_bitdepth
        else (10 if high_bitdepth else 8)
    )
    monochrome = 0 if profile == 1 else bits.read()
    if bits.read():
        primaries, transfer, matrix = bits.read(8), bits.read(8), bits.read(8)
    else:
        primaries, transfer, matrix = 2, 2, 2
    if monochrome:
        color_range = bits.read()
        subsampling_x = subsampling_y = 1
        chroma_position = 0
    elif (primaries, transfer, matrix) == (1, 13, 0):
        color_range = 1
        subsampling_x = subsampling_y = chroma_position = 0
        bits.read()  # separate_uv_delta_q
    else:
        color_range = bits.read()
        if profile == 0:
            subsampling_x = subsampling_y = 1
        elif profile == 1:
            subsampling_x = subsampling_y = 0
        elif depth == 12:
            subsampling_x = bits.read()
            subsampling_y = bits.read() if subsampling_x else 0
        else:
            subsampling_x, subsampling_y = 1, 0
        chroma_position = bits.read(2) if subsampling_x and subsampling_y else 0
        bits.read()  # separate_uv_delta_q
    return {
        "profile": profile,
        "bit_depth": depth,
        "monochrome": monochrome,
        "primaries": primaries,
        "transfer": transfer,
        "matrix": matrix,
        "range": color_range,
        "subsampling": [subsampling_x, subsampling_y],
        "chroma_position": chroma_position,
        "film_grain": bits.read(),
    }


def bmff_boxes(payload: bytes, start: int, end: int) -> list[tuple[bytes, int, int]]:
    result = []
    position = start
    while position < end:
        if position + 8 > end:
            raise ValueError("truncated AVIF box")
        size = int.from_bytes(payload[position : position + 4], "big")
        kind = payload[position + 4 : position + 8]
        header = 8
        if size == 1:
            if position + 16 > end:
                raise ValueError("truncated extended AVIF box")
            size = int.from_bytes(payload[position + 8 : position + 16], "big")
            header = 16
        elif size == 0:
            size = end - position
        if size < header or position + size > end:
            raise ValueError("invalid AVIF box size")
        result.append((kind, position + header, position + size))
        position += size
    return result


def av1_sequence_header(payload: bytes) -> bytes:
    position = 0
    while position < len(payload):
        header = payload[position]
        position += 1
        if header & 0x81 or not header & 0x02:
            raise ValueError("unsupported AVIF OBU header")
        kind = (header >> 3) & 15
        if header & 0x04:
            position += 1
        size = 0
        for shift in range(0, 56, 7):
            if position >= len(payload):
                raise ValueError("truncated AVIF OBU size")
            part = payload[position]
            position += 1
            size |= (part & 127) << shift
            if not part & 128:
                break
        else:
            raise ValueError("invalid AVIF OBU size")
        if position + size > len(payload):
            raise ValueError("truncated AVIF OBU")
        if kind == 1:
            return payload[position : position + size]
        position += size
    raise ValueError("AVIF sequence header not found")


def avif_render_metadata(payload: bytes) -> dict[str, Any]:
    def box(boxes: list[tuple[bytes, int, int]], kind: bytes) -> tuple[int, int]:
        matches = [(start, end) for name, start, end in boxes if name == kind]
        if len(matches) != 1:
            raise ValueError(f"AVIF requires one {kind.decode('ascii')} box")
        return matches[0]

    def number(position: int, width: int, end: int) -> int:
        if width < 0 or position + width > end:
            raise ValueError("truncated AVIF item table")
        return int.from_bytes(payload[position : position + width], "big")

    top = bmff_boxes(payload, 0, len(payload))
    meta_start, meta_end = box(top, b"meta")
    if meta_start + 4 > meta_end:
        raise ValueError("truncated AVIF meta box")
    meta = bmff_boxes(payload, meta_start + 4, meta_end)

    pitm_start, pitm_end = box(meta, b"pitm")
    pitm_version = number(pitm_start, 1, pitm_end)
    if pitm_version not in (0, 1):
        raise ValueError("unsupported AVIF primary-item table")
    primary_id = number(pitm_start + 4, 2 if pitm_version == 0 else 4, pitm_end)

    iinf_start, iinf_end = box(meta, b"iinf")
    iinf_version = number(iinf_start, 1, iinf_end)
    if iinf_version not in (0, 1):
        raise ValueError("unsupported AVIF item-information table")
    count_width = 2 if iinf_version == 0 else 4
    item_count = number(iinf_start + 4, count_width, iinf_end)
    item_boxes = bmff_boxes(payload, iinf_start + 4 + count_width, iinf_end)
    if len(item_boxes) < item_count:
        raise ValueError("truncated AVIF item information")
    primary_type: bytes | None = None
    for kind, start, end in item_boxes[:item_count]:
        if kind != b"infe":
            continue
        version = number(start, 1, end)
        if version not in (2, 3):
            raise ValueError("unsupported AVIF item information")
        width = 2 if version == 2 else 4
        if number(start + 4, width, end) == primary_id:
            position = start + 4 + width + 2
            number(position, 4, end)
            primary_type = payload[position : position + 4]
    if primary_type is None:
        raise ValueError("AVIF primary item information not found")
    if primary_type != b"av01":
        return {
            "primary_item_type": primary_type.decode("latin1"),
            "conservative_bytes": hashlib.sha256(payload).hexdigest(),
        }

    iprp_start, iprp_end = box(meta, b"iprp")
    iprp = bmff_boxes(payload, iprp_start, iprp_end)
    ipco_start, ipco_end = box(iprp, b"ipco")
    properties = bmff_boxes(payload, ipco_start, ipco_end)
    associated: list[tuple[bytes, int, int]] = []
    for kind, start, end in iprp:
        if kind != b"ipma":
            continue
        version = number(start, 1, end)
        if version not in (0, 1):
            raise ValueError("unsupported AVIF property-association table")
        wide = number(start + 3, 1, end) & 1
        position = start + 4
        entry_count = number(position, 4, end)
        position += 4
        for _ in range(entry_count):
            id_width = 2 if version == 0 else 4
            item_id = number(position, id_width, end)
            position += id_width
            association_count = number(position, 1, end)
            position += 1
            for _ in range(association_count):
                index_width = 2 if wide else 1
                value = number(position, index_width, end)
                position += index_width
                index = value & (0x7FFF if wide else 0x7F)
                if index > len(properties):
                    raise ValueError("invalid AVIF property association")
                if item_id == primary_id and index:
                    associated.append(properties[index - 1])

    iloc_start, iloc_end = box(meta, b"iloc")
    iloc_version = number(iloc_start, 1, iloc_end)
    if iloc_version not in (0, 1, 2):
        raise ValueError("unsupported AVIF item-location table")
    sizes = number(iloc_start + 4, 2, iloc_end)
    offset_width, length_width = sizes >> 12, sizes >> 8 & 15
    base_width = sizes >> 4 & 15
    index_width = sizes & 15 if iloc_version else 0
    if max(offset_width, length_width, base_width, index_width) > 8:
        raise ValueError("unsupported AVIF item-location width")
    id_width = 4 if iloc_version == 2 else 2
    position = iloc_start + 6
    entry_count = number(position, id_width, iloc_end)
    position += id_width
    primary_location: tuple[int, int, list[tuple[int, int]]] | None = None
    for _ in range(entry_count):
        item_id = number(position, id_width, iloc_end)
        position += id_width
        method = number(position, 2, iloc_end) & 15 if iloc_version else 0
        position += 2 if iloc_version else 0
        reference = number(position, 2, iloc_end)
        position += 2
        base = number(position, base_width, iloc_end)
        position += base_width
        extent_count = number(position, 2, iloc_end)
        position += 2
        extents = []
        for _ in range(extent_count):
            number(position, index_width, iloc_end)
            position += index_width
            offset = number(position, offset_width, iloc_end)
            position += offset_width
            length = number(position, length_width, iloc_end)
            position += length_width
            extents.append((base + offset, length))
        if item_id == primary_id:
            primary_location = method, reference, extents
    if primary_location is None:
        raise ValueError("AVIF primary item location not found")
    method, reference, extents = primary_location
    if reference:
        raise ValueError("unsupported external AVIF item reference")
    if method == 0:
        origin, limit = 0, len(payload)
    elif method == 1:
        origin, limit = box(meta, b"idat")
    else:
        raise ValueError("unsupported AVIF item construction method")
    if not extents or any(length == 0 for _, length in extents):
        raise ValueError("unsupported empty AVIF primary extent")
    if any(origin + offset + length > limit for offset, length in extents):
        raise ValueError("AVIF primary extent exceeds item data")
    item_data = b"".join(
        payload[origin + offset : origin + offset + length]
        for offset, length in extents
    )
    try:
        sequence = av1_sequence_header(item_data)
    except ValueError as error:
        if str(error) != "AVIF sequence header not found":
            raise
        configurations = [
            payload[start:end]
            for kind, start, end in associated
            if kind == b"av1C" and end - start >= 4
        ]
        if len(configurations) != 1:
            raise
        sequence = av1_sequence_header(configurations[0][4:])
    color = av1_color_config(sequence)
    container_colors: list[tuple[int, int, int, int]] = []
    render_properties: list[tuple[str, str]] = []
    transform_seen = False
    ispe_seen = False
    invalid_ispe_after_transform = False
    for kind, start, end in associated:
        if kind in {b"clap", b"irot", b"imir"}:
            transform_seen = True
        elif kind == b"ispe":
            invalid_ispe_after_transform = (
                invalid_ispe_after_transform or transform_seen or ispe_seen
            )
            ispe_seen = True
        value = payload[start:end]
        if kind == b"colr" and value.startswith(b"nclx"):
            if len(value) < 11:
                raise ValueError("truncated AVIF nclx property")
            container_colors.append(
                (
                    number(start + 4, 2, end),
                    number(start + 6, 2, end),
                    number(start + 8, 2, end),
                    value[10] >> 7,
                )
            )
        elif kind == b"colr":
            render_properties.append(("colr", hashlib.sha256(value).hexdigest()))
        elif kind in {b"irot", b"imir", b"clap", b"mdcv", b"clli"}:
            render_properties.append((kind.decode("ascii"), value.hex()))
    unique_colors = list(dict.fromkeys(container_colors))
    if len(unique_colors) == 1:
        color = {
            **color,
            **dict(zip(("primaries", "transfer", "matrix", "range"), unique_colors[0])),
        }
    transforms = [
        item for item in render_properties if item[0] in {"clap", "irot", "imir"}
    ]
    metadata = sorted(
        (item for item in render_properties if item[0] not in {"clap", "irot", "imir"}),
        key=lambda item: item[0],
    )
    result = {
        "av1": color,
        "container_color_overrides": [],
        "properties": transforms + metadata,
    }
    if invalid_ispe_after_transform:
        result["invalid_ispe_after_transform"] = True
    if len(unique_colors) > 1:
        result["conflicting_container_colors"] = unique_colors
    return result


@cache
def image_data_from_bytes(payload: bytes) -> dict[str, Any]:
    encoding_hash = hashlib.sha256(payload).hexdigest()
    result: dict[str, Any] = {"bytes": len(payload), "sha256": encoding_hash}
    try:
        with Image.open(io.BytesIO(payload)) as source:
            pixels = hashlib.sha256()
            frames = 0
            dimensions = list(source.size)
            icc = hashlib.sha256(source.info.get("icc_profile") or b"").hexdigest()
            pixels.update(bytes.fromhex(icc))
            color_metadata = {
                key: source.info[key]
                for key in ("gamma", "chromaticity", "srgb", "loop")
                if key in source.info
            }
            render_chunks = png_render_chunks(payload)
            if render_chunks:
                color_metadata["png_render_chunks"] = render_chunks
            if source.format == "AVIF":
                color_metadata["avif"] = avif_render_metadata(payload)
            pixels.update(digest(color_metadata).encode())
            frames_to_decode = (
                [source] if source.format == "MPO" else ImageSequence.Iterator(source)
            )
            for frame in frames_to_decode:
                oriented = ImageOps.exif_transpose(frame)
                if frames == 0:
                    dimensions = list(oriented.size)
                pixels.update(oriented.convert("RGBA").tobytes())
                pixels.update(str(frame.info.get("duration", 0)).encode())
                frames += 1
            result.update(
                dimensions=dimensions,
                frames=frames,
                pixels=pixels.hexdigest(),
                icc=icc,
                color_metadata=color_metadata,
            )
    except UnidentifiedImageError:
        # Conservatively retain byte identity for vectors the raster decoder cannot read.
        result["pixels"] = "unrendered:" + encoding_hash
    return result


@cache
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


def dom_structure(node: Tag | NavigableString, parent: str = "") -> Any:
    if isinstance(node, NavigableString):
        value = (
            ""
            if parent in {"title", "script", "style", "pre", "textarea"}
            else norm(node, preserve_edges=True)
        )
        return ["text", value]
    return [node.name, [dom_structure(child, node.name) for child in node.children]]


class DuplicateAttributeProbe(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.element = 0
        self.duplicates: list[tuple[int, str, str, list[str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values: dict[str, list[str | None]] = collections.defaultdict(list)
        for key, value in attrs:
            values[key].append(value)
        for key, items in values.items():
            if len(items) > 1:
                self.duplicates.append((self.element, tag, key, items))
        self.element += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


@cache
def resource_content_sha(path: Path, fetched: bool) -> str:
    payload = path.read_bytes()
    if fetched and path.suffix.lower() == ".css":
        payload = normalize_font_refs(payload.decode("utf-8")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def page_data(path: Path, root: Path, fetched: bool = False) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    duplicate_probe = DuplicateAttributeProbe()
    duplicate_probe.feed(raw)
    # Decode HTML character references once, as the browser does. Do not unescape
    # these DOM values again: &amp;#39; is literal text, unlike &#39; or an apostrophe.
    soup = BeautifulSoup(raw, "html.parser")
    page_route = route(path, root)
    title = [norm(tag.get_text()) for tag in soup.select("title")]
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
    site_hosts = frozenset(
        urlsplit(str(link.get("href", ""))).netloc
        for link in soup.select('link[rel~="canonical"]')
        if urlsplit(str(link.get("href", ""))).netloc
    )
    metadata_image_pixels = []
    for element in soup.select("meta"):
        key = str(element.get("property", element.get("name", ""))).lower()
        if key not in {
            "og:image",
            "og:image:url",
            "og:image:secure_url",
            "twitter:image",
            "twitter:image:src",
        }:
            continue
        href = str(element.get("content", ""))
        image = local_file(root, href, page_route, site_hosts)
        entry: dict[str, Any] = {"key": key, "url": norm(href) if image else href}
        if image is not None:
            entry["path"] = norm(image.relative_to(root.resolve()).as_posix())
            entry["exists"] = image.is_file()
            if image.is_file():
                entry.update(
                    {
                        field: image_data(image).get(field)
                        for field in ("dimensions", "frames", "pixels")
                    }
                )
        metadata_image_pixels.append(entry)
    resources = []
    for tag in soup.select("link[href],script[src]"):
        attr = "src" if tag.name == "script" else "href"
        href = str(tag[attr])
        relations = tag.get("rel", [])
        relation_names = {
            str(name).lower()
            for name in (relations.split() if isinstance(relations, str) else relations)
        }
        required_when_fetched = tag.name == "script" or bool(
            relation_names & {"stylesheet", "modulepreload"}
            or (
                "preload" in relation_names
                and str(tag.get("as", "")).lower() in {"script", "style"}
            )
        )
        resource = local_file(root, href, page_route, site_hosts)
        exists = resource.is_file() if resource is not None else None
        entry: dict[str, Any] = {
            "tag": tag.name,
            "href": norm(href),
            "required_when_fetched": required_when_fetched,
            "local": resource is not None,
            "exists": exists,
            "_resolved_path": (
                resource.relative_to(root.resolve()).as_posix()
                if resource is not None
                else None
            ),
        }
        if resource is not None and exists and required_when_fetched:
            entry["content_sha256"] = resource_content_sha(resource, fetched)
        resources.append(entry)
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
    inline_styles = [str(tag.string or tag.get_text()) for tag in soup.select("style")]
    attributes = [
        (
            tag.name,
            sorted(
                (key, norm(" ".join(value) if isinstance(value, list) else value))
                for key, value in tag.attrs.items()
            ),
        )
        for tag in soup.find_all(True)
    ]
    assets = image_assets(soup, root, page_route)
    preformatted = [(tag.name, tag.get_text()) for tag in soup.select("pre,textarea")]
    for comment in soup.find_all(string=lambda value: isinstance(value, Comment)):
        comment.extract()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            value = tag.attrs[attr]
            tag.attrs[attr] = norm(
                " ".join(value) if isinstance(value, list) else value
            )
        tag.attrs = dict(sorted(tag.attrs.items()))
    structure = dom_structure(soup)
    normalized_html = norm(soup.decode())
    for tag in soup.select(
        "script,style,template,noscript,head,[hidden],[aria-hidden='true']"
    ):
        tag.decompose()
    text = visible_text(soup)
    return {
        "title": title,
        "metadata": sorted(metadata, key=str),
        "metadata_image_pixels": metadata_image_pixels,
        "headings": headings,
        "ids": ids,
        "links": links,
        "resources": resources,
        "inline_scripts": inline_scripts,
        "inline_styles": inline_styles,
        "attributes": attributes,
        "duplicate_attributes": duplicate_probe.duplicates,
        "structure": structure,
        "preformatted": preformatted,
        "images": images,
        "picture_sources": sources,
        "image_assets": assets,
        "text": text,
        "inline_text": [
            norm(tag.get_text())
            for tag in soup.select("p,h1,h2,h3,h4,h5,h6,figcaption")
        ],
        "html": digest(normalized_html),
        "html_content": normalized_html,
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
        rss["channel"] = [xml_value(e) for e in channel if e.tag != "item"]
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
        metadata_changed = (
            not changed and image_data(first)["pixels"] != image_data(second)["pixels"]
        )
        if metadata_changed:
            changed = a.width * a.height
        return {
            "dimensions": sizes,
            "ratio": changed / (a.width * a.height),
            "changed_pixels": changed,
            "metadata_changed": metadata_changed,
        }


def sample(a: Any, b: Any) -> dict[str, Any]:
    left = json.dumps(a, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    right = json.dumps(b, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    if isinstance(a, str) and isinstance(b, str):
        return {
            "hunks": [
                {
                    "a_offset": start_a,
                    "b_offset": start_b,
                    "a": a[max(0, start_a - 80) : end_a + 80],
                    "b": b[max(0, start_b - 80) : end_b + 80],
                }
                for operation, start_a, end_a, start_b, end_b in difflib.SequenceMatcher(
                    None, a, b
                ).get_opcodes()
                if operation != "equal"
            ],
            "a_hash": digest(a),
            "b_hash": digest(b),
        }
    return {
        "diff": list(difflib.unified_diff(left, right, fromfile="A", tofile="B", n=2)),
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
    for url in sorted(pages.keys() & other.keys()):
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


def page_asset_refs(first_page: Path, second_page: Path) -> dict[str, str]:
    left = BeautifulSoup(first_page.read_text(encoding="utf-8"), "html.parser")
    right = BeautifulSoup(second_page.read_text(encoding="utf-8"), "html.parser")
    aliases = {}
    for selector, attribute in (
        ("script[src]", "src"),
        ("link[rel~=stylesheet]", "href"),
    ):
        for a_tag, b_tag in zip(left.select(selector), right.select(selector)):
            aliases[norm(b_tag[attribute])] = norm(a_tag[attribute])
    return aliases


def replace_refs(value: Any, aliases: dict[str, str]) -> Any:
    if isinstance(value, str):
        for actual, local in aliases.items():
            value = value.replace(actual, local)
        return value
    if isinstance(value, list):
        return [replace_refs(item, aliases) for item in value]
    if isinstance(value, tuple):
        return tuple(replace_refs(item, aliases) for item in value)
    if isinstance(value, dict):
        return {key: replace_refs(item, aliases) for key, item in value.items()}
    return value


def font_names(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*.woff2"))


@cache
def font_properties(path: Path) -> tuple[bool, float, float]:
    with TTFont(path, lazy=True) as font:
        italic = bool(font["head"].macStyle & 2 or font["OS/2"].fsSelection & 1)
        axis = (
            next((axis for axis in font["fvar"].axes if axis.axisTag == "wght"), None)
            if "fvar" in font
            else None
        )
        low, high = (
            (axis.minValue, axis.maxValue)
            if axis
            else (font["OS/2"].usWeightClass,) * 2
        )
    return italic, low, high


def font_roles(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    roles: dict[tuple[str, str, tuple[int, ...]], dict[str, Any]] = {}
    mismatches: set[str] = set()
    referenced: set[str] = set()

    def sources():
        for css_file in root.rglob("*.css"):
            css = css_file.read_text(encoding="utf-8")
            if "@font-face" in css:
                yield css_file, css
        for page in root.rglob("*.html"):
            soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
            for tag in soup.select("style"):
                css = str(tag.string or tag.get_text())
                if "@font-face" in css:
                    yield page, css

    for css_file, css in sources():
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
                italic, low, high = font_properties(font_path)
                name = font_path.relative_to(root).as_posix()
                referenced.add(name)
                wanted_italic = style.startswith(("italic", "oblique"))
                if italic != wanted_italic or min(weights) < low or max(weights) > high:
                    mismatches.add(
                        f"{font_path.relative_to(root)}: expected {style} {values.get('font-weight', '400')} from {css_file.relative_to(root)}, font has italic={italic} weight={low}..{high}"
                    )
                roles[(name, style, tuple(weights))] = {
                    "file": name,
                    "style": style,
                    "weight": weights,
                    "font_italic": italic,
                    "font_weight": [low, high],
                }
    for name in font_names(root):
        if name not in referenced:
            mismatches.add(f"{name}: font has no @font-face rule")
    return list(roles.values()), sorted(mismatches)


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
    accepted: dict[str, str] | None = None,
    fetched: bool = False,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    accepted = accepted or {}
    page_pairs: dict[str, tuple[str, str]] = {}

    def check(
        kind: str, target: str, a: Any, b: Any, normalization: str | None = None
    ) -> None:
        classification = (
            "identical" if a == b else ("cosmetic" if normalization else "material")
        )
        fingerprint = digest(
            [kind, target, digest(a), digest(b), page_pairs.get(target)]
        )
        acceptance = accepted.get(fingerprint) if a != b else None
        item: dict[str, Any] = {
            "kind": kind,
            "target": target,
            "classification": "cosmetic" if acceptance else classification,
        }
        if a != b:
            item.update(sample=sample(a, b), fingerprint=fingerprint)
            if normalization:
                item["normalization"] = normalization
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
        a, b = (
            page_data(a_pages[url], first, fetched),
            page_data(b_pages[url], second, fetched),
        )
        for left, right in zip(a["resources"], b["resources"]):
            if left["_resolved_path"] == right["_resolved_path"]:
                left.pop("content_sha256", None)
                right.pop("content_sha256", None)
        for page in (a, b):
            for resource in page["resources"]:
                resource.pop("_resolved_path")
        if fetched:
            aliases = page_asset_refs(a_pages[url], b_pages[url])
            resource_pairs = [
                (left, right)
                for left, right in zip(a["resources"], b["resources"])
                if right["required_when_fetched"] or right.get("exists")
            ]
            a["resources"] = [left for left, _ in resource_pairs]
            b["resources"] = [right for _, right in resource_pairs]
            metadata_image_pairs = [
                (left, right)
                for left, right in zip(
                    a["metadata_image_pixels"], b["metadata_image_pixels"]
                )
                if right.get("exists")
            ]
            a["metadata_image_pixels"] = [left for left, _ in metadata_image_pairs]
            b["metadata_image_pixels"] = [right for _, right in metadata_image_pairs]
            image_pairs = [
                (left, right)
                for left, right in zip(a["image_assets"], b["image_assets"])
                if right.get("exists")
            ]
            a["image_assets"] = [left for left, _ in image_pairs]
            b["image_assets"] = [right for _, right in image_pairs]
            for page in (a, b):
                for field in ("attributes", "inline_scripts", "inline_styles"):
                    page[field] = normalize_font_refs(page[field])
            b["attributes"] = replace_refs(b["attributes"], aliases)
            b["resources"] = replace_refs(b["resources"], aliases)
            a["html"] = digest(normalize_font_refs(a["html_content"]))
            b["html"] = digest(
                normalize_font_refs(replace_refs(b["html_content"], aliases))
            )
        page_pairs[url] = (a["html"], b["html"])
        for key in PAGE_FIELDS:
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
        explained = any(a[field] != b[field] for field in PAGE_FIELDS)
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
        if not fetched:
            for side, data in (("a", a_index), ("b", b_index)):
                if not data["present"] or data["indexed_pages"] <= 0:
                    check("pagefind_invalid", side, "present, nonempty index", data)
        for key in sorted(a_index["routes"].keys() | b_index["routes"].keys()):
            a_route = a_index["routes"].get(key, {})
            b_route = b_index["routes"].get(key, {})
            a_fragment, b_fragment = a_route.get("fragment"), b_route.get("fragment")
            normalization = (
                "asset hash filename"
                if a_fragment != b_fragment
                and normalize_asset_names(a_fragment)
                == normalize_asset_names(b_fragment)
                else None
            )
            check("pagefind_fragment", key, a_fragment, b_fragment, normalization)
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

    def asset_normalization(
        a_name: str, a_info: dict[str, Any], b_name: str, b_info: dict[str, Any]
    ) -> str | None:
        if a_info["sha256"] == b_info["sha256"] and a_name != b_name:
            return "asset hash filename"
        if (
            Path(a_name).suffix.lower()
            in (".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif")
            and Path(b_name).suffix.lower() == Path(a_name).suffix.lower()
        ):
            a_pixels, b_pixels = image_data(first / a_name), image_data(second / b_name)
            if all(
                a_pixels.get(field) == b_pixels.get(field)
                for field in ("dimensions", "frames", "pixels")
            ):
                return "lossless image encoding"
        if fetched and a_name.endswith(".css") and b_name.endswith(".css"):
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
                return "fetched font filename"
        if (
            a_name.endswith(".xml")
            and b_name.endswith(".xml")
            and xml_value(ET.parse(first / a_name).getroot())
            == xml_value(ET.parse(second / b_name).getroot())
        ):
            return "XML serialization"
        if a_name == b_name == "robots.txt" and a_feed["robots"] == b_feed["robots"]:
            return "robots comment or whitespace"
        return None

    for key in sorted(b_groups if fetched else a_groups.keys() | b_groups.keys()):
        a_by_name = dict(a_groups.get(key, []))
        b_by_name = dict(b_groups.get(key, []))
        for name in sorted(a_by_name.keys() & b_by_name.keys()):
            a_info, b_info = a_by_name.pop(name), b_by_name.pop(name)
            check(
                "assets",
                name,
                [{"name": name, **a_info}],
                [{"name": name, **b_info}],
                asset_normalization(name, a_info, name, b_info)
                if a_info != b_info
                else None,
            )
        a_rows, b_rows = sorted(a_by_name.items()), sorted(b_by_name.items())
        if not a_rows and not b_rows:
            continue
        if fetched and not b_rows:
            continue
        a_values = [{"name": name, **value} for name, value in a_rows]
        b_values = [{"name": name, **value} for name, value in b_rows]
        normalization = None
        if len(a_rows) == len(b_rows) == 1:
            a_name, a_info = a_rows[0]
            b_name, b_info = b_rows[0]
            normalization = asset_normalization(a_name, a_info, b_name, b_info)
        elif len(a_rows) == len(b_rows) and collections.Counter(
            (info["bytes"], info["sha256"]) for _, info in a_rows
        ) == collections.Counter((info["bytes"], info["sha256"]) for _, info in b_rows):
            normalization = "asset hash filename"
        check("assets", key, a_values, b_values, normalization)
    a_fonts, b_fonts = font_names(first), font_names(second)
    font_checks: dict[str, Any] = {"a": a_fonts, "b": b_fonts}
    if fetched:
        font_checks["roles_a"], mismatches_a = font_roles(first)
        font_checks["roles_b"], mismatches_b = font_roles(second)
        check("font_roles", "fetched fonts", [], mismatches_a + mismatches_b)
    counts = dict(collections.Counter(item["classification"] for item in checks))
    material = counts.get("material", 0)
    matched_acceptance = {item["fingerprint"] for item in checks if "accepted" in item}
    unmatched_acceptance = sorted(accepted.keys() - matched_acceptance)
    if unmatched_acceptance and not material:
        raise ValueError(
            "accept ledger contains unmatched fingerprints: "
            + ", ".join(unmatched_acceptance[:5])
        )
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
        "acceptance_matches": sum("accepted" in item for item in checks),
        "unmatched_acceptance": unmatched_acceptance,
    }


def main() -> int:
    cli = argparse.ArgumentParser(
        description=__doc__,
        epilog="Example: uv run parity.py baseline/dist candidate/dist --json parity.json",
    )
    cli.add_argument("dist_a", type=Path)
    cli.add_argument("dist_b", type=Path)
    cli.add_argument("--json", type=Path, help="write the full machine-readable report")
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
            args.dist_a.resolve(), args.dist_b.resolve(), accepted, args.fetched
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
    except Exception as error:  # noqa: BLE001
        print(json.dumps({"ok": False, "errors": [str(error)]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
