#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright==1.56.0", "pillow==12.0.0"]
# [tool.uv]
# exclude-newer = "1 week"
# ///
"""Capture a dist with verify-blog's browser setup, or compare screenshot sets."""

from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import math
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import browse
from PIL import Image, ImageChops, ImageDraw, ImageEnhance
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent
MATRIX = ROOT.parent / "shots.json"


class DistHandler(http.server.SimpleHTTPRequestHandler):
    """Serve only the chosen dist and its real 404 document."""

    def log_message(self, format: str, *args: object) -> None:
        pass

    def send_error(
        self, code: int, message: str | None = None, explain: str | None = None
    ) -> None:
        file = Path(self.directory) / "404.html"
        if code == 404 and file.is_file():
            content = file.read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(content)
        else:
            super().send_error(code, message, explain)


def matrix() -> dict[str, Any]:
    value = json.loads(MATRIX.read_text(encoding="utf-8"))
    count = (
        len(value["viewports"])
        * len(value["themes"])
        * sum(len(route["positions"]) for route in value["routes"])
    )
    if count != 44:
        raise ValueError(f"shots.json defines {count} shots, expected 44")
    return value


def settle(page: Page) -> None:
    page.wait_for_load_state("networkidle", timeout=20000)
    page.evaluate("() => document.fonts.ready")
    page.evaluate("""async () => {
      await Promise.all([...document.images].filter(i => i.getBoundingClientRect().top < innerHeight && i.getBoundingClientRect().bottom > 0)
        .map(async i => {
          if (!i.complete) await new Promise(r => { i.addEventListener('load',r,{once:true}); i.addEventListener('error',r,{once:true}); });
          if (i.naturalWidth) await i.decode();
        }));
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    }""")


def capture(args: argparse.Namespace) -> int:
    dist = args.dist.resolve()
    if not (dist / "index.html").is_file():
        raise ValueError(f"not a completed dist: {dist}")
    if args.port == 4320:
        raise ValueError("port 4320 belongs to Pascal's dev server and is refused")
    if not 4391 <= args.port <= 4399:
        raise ValueError("port must be in 4391..4399")
    source_commit = args.source_commit
    if (dist.parent / ".git").exists():
        observed = subprocess.check_output(
            ["git", "-C", str(dist.parent), "rev-parse", "HEAD"], text=True
        ).strip()
        if source_commit and source_commit != observed:
            raise ValueError("source commit does not match the worktree HEAD")
        source_commit = observed
    if args.out.exists() and any(args.out.iterdir()):
        raise ValueError(f"output must be empty to prevent stale evidence: {args.out}")
    args.out.mkdir(parents=True, exist_ok=True)
    specification = matrix()
    pages = (
        json.loads(args.pages.read_text(encoding="utf-8"))
        if args.pages
        else {route["label"]: route["path"] for route in specification["routes"]}
    )
    (args.out / "pages.json").write_text(
        json.dumps(pages, indent=2) + "\n", encoding="utf-8"
    )
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", args.port), functools.partial(DistHandler, directory=str(dist))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{args.port}"
    manifest: dict[str, Any] = {
        "dist": str(dist),
        "base": base,
        "driver": str(ROOT / "browse.py"),
        "driver_sha256": hashlib.sha256((ROOT / "browse.py").read_bytes()).hexdigest(),
        "browser": "Chromium via Playwright 1.56.0",
        "device_scale_factor": args.dpr,
        "screenshot_scale": args.scale,
        "source_commit": source_commit,
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pages": pages,
        "matrix": specification,
        "shots": {},
        "failures": [],
    }
    try:
        with sync_playwright() as playwright:
            browser = browse.launch_chromium(playwright)
            manifest["browser_version"] = browser.version
            for viewport in specification["viewports"]:
                width, height = viewport["width"], viewport["height"]
                for theme in specification["themes"]:
                    for route in specification["routes"]:
                        label = route["label"]
                        path = pages[label]
                        context = browser.new_context(
                            viewport={"width": width, "height": height},
                            device_scale_factor=args.dpr,
                            color_scheme=theme,
                            locale="en-US",
                            timezone_id="America/Montreal",
                            reduced_motion="reduce",
                        )
                        page = context.new_page()
                        errors: list[str] = []
                        browse.collect_page_errors(page, errors)
                        stem = f"{label}-{width}-{theme}"
                        try:
                            response = page.goto(base + path, timeout=30000)
                            expected_status = 404 if label == "404" else 200
                            if response is None or response.status != expected_status:
                                raise ValueError(
                                    f"{label}: expected HTTP {expected_status}, got {response.status if response else None}"
                                )
                            settle(page)
                            if label == "search":
                                browse.run(
                                    page,
                                    base,
                                    "fill",
                                    ".pagefind-ui__search-input=bitcoin",
                                    [],
                                )
                                browse.run(
                                    page, base, "wait", ".pagefind-ui__result", []
                                )
                                if "q=bitcoin" not in page.url:
                                    raise ValueError("search did not update the URL")
                            if label == "mermaid":
                                browse.run(
                                    page, base, "wait", ".mermaid-diagram svg", []
                                )
                                expected = page.locator(".mermaid-diagram svg").count()
                                if expected < 2:
                                    raise ValueError(
                                        f"expected two rendered Mermaid diagrams, got {expected}"
                                    )
                            actual_theme = page.locator("html").get_attribute(
                                "data-theme"
                            )
                            if actual_theme != theme:
                                raise ValueError(
                                    f"expected theme {theme}, got {actual_theme}"
                                )
                            for position_spec in route["positions"]:
                                position = position_spec["name"]
                                selector = position_spec.get("selector")
                                if selector:
                                    page.locator(
                                        selector
                                    ).first.scroll_into_view_if_needed()
                                else:
                                    page.evaluate("scrollTo(0,0)")
                                page.mouse.move(0, 0)
                                settle(page)
                                name = stem + "-" + position
                                page.screenshot(
                                    path=args.out / (name + ".png"),
                                    scale=args.scale,
                                    animations="disabled",
                                    caret="hide",
                                )
                                (args.out / (name + ".aria.txt")).write_text(
                                    page.locator("body").aria_snapshot() + "\n",
                                    encoding="utf-8",
                                )
                                state = {
                                    "route": path,
                                    "url": page.url,
                                    "status": response.status,
                                    "title": page.title(),
                                    "theme": actual_theme,
                                    "device_scale_factor": args.dpr,
                                    "width": width,
                                    "height": height,
                                    "position": position,
                                    "scroll_y": page.evaluate("scrollY"),
                                    "console_errors": list(errors),
                                    "results": page.locator(
                                        ".pagefind-ui__result"
                                    ).count(),
                                    "mermaid_diagrams": page.locator(
                                        ".mermaid-diagram svg"
                                    ).count(),
                                    "images": page.locator("img").evaluate_all(
                                        """images => images.map((i,index) => {
                                          const r=i.getBoundingClientRect(), c=getComputedStyle(i);
                                          return {index,alt:i.alt,src:i.getAttribute('src'),currentSrc:new URL(i.currentSrc || i.src).pathname,
                                            sizes:i.sizes,srcset:i.srcset,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,
                                            box:{x:r.x,y:r.y,width:r.width,height:r.height},objectFit:c.objectFit,objectPosition:c.objectPosition,
                                            sourceSizes:[...i.parentElement.querySelectorAll('source')].map(s=>({type:s.type,sizes:s.sizes,srcset:s.srcset}))};
                                        })"""
                                    ),
                                    "image_failures": page.locator("img").evaluate_all(
                                        "(images) => images.filter(i => i.complete && !i.naturalWidth).map(i => i.src)"
                                    ),
                                }
                                manifest["shots"][name] = state
                                (args.out / (name + ".state.json")).write_text(
                                    json.dumps(state, indent=2, ensure_ascii=False)
                                    + "\n",
                                    encoding="utf-8",
                                )
                            print(f"captured {stem}", file=sys.stderr, flush=True)
                        except (OSError, ValueError, PlaywrightError) as error:
                            manifest["failures"].append(
                                {
                                    "shot": stem,
                                    "error": str(error),
                                    "console_errors": errors,
                                }
                            )
                            page.screenshot(
                                path=args.out / (stem + "-FAILED.png"), scale="css"
                            )
                            print(
                                f"failed {stem}: {error}", file=sys.stderr, flush=True
                            )
                        finally:
                            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        (args.out / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "ok": not manifest["failures"],
                "shots": len(manifest["shots"]),
                "failures": manifest["failures"],
                "manifest": str(args.out / "manifest.json"),
            }
        )
    )
    return 1 if manifest["failures"] else 0


@functools.cache
def selected_sha(dist: str, src: str, current: str) -> str | None:
    if not dist or urlsplit(src).scheme or urlsplit(src).netloc:
        return None
    selected = urlsplit(current)
    if selected.scheme or selected.netloc:
        return None
    root = Path(dist).resolve()
    file = (root / unquote(selected.path).lstrip("/")).resolve()
    if not file.is_relative_to(root) or not file.is_file():
        return None
    return hashlib.sha256(file.read_bytes()).hexdigest()


def diff(args: argparse.Namespace) -> int:
    first = {p.name: p for p in args.first.glob("*.png")}
    second = {p.name: p for p in args.second.glob("*.png")}
    if not first or not second:
        raise ValueError("both shot directories must contain PNGs")
    manifests = []
    for folder in (args.first, args.second):
        file = folder / "manifest.json"
        manifests.append(
            json.loads(file.read_text(encoding="utf-8"))
            if file.exists()
            else {"failures": ["missing manifest"], "shots": {}}
        )
    differences = {}
    for name in sorted(first.keys() & second.keys()):
        with Image.open(first[name]) as a, Image.open(second[name]) as b:
            if a.size != b.size:
                result = {
                    "ratio": 1.0,
                    "dimensions_a": list(a.size),
                    "dimensions_b": list(b.size),
                    "all_changed_inside_image_boxes": False,
                }
            else:
                delta = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
                channels = delta.split()
                maximum = ImageChops.lighter(
                    ImageChops.lighter(channels[0], channels[1]), channels[2]
                )
                changed = sum(maximum.histogram()[args.channel_threshold + 1 :])
                changed_mask = maximum.point(
                    lambda value: 255 if value > args.channel_threshold else 0
                )
                allowed = Image.new("L", a.size)
                draw = ImageDraw.Draw(allowed)
                boxes = []
                state_a = manifests[0]["shots"].get(Path(name).stem, {})
                state_b = manifests[1]["shots"].get(Path(name).stem, {})
                scale_x = a.width / state_a["width"] if state_a.get("width") else 1
                scale_y = a.height / state_a["height"] if state_a.get("height") else 1
                for image_a, image_b in zip(
                    state_a.get("images", []), state_b.get("images", [])
                ):
                    box = image_a.get("box")
                    if (
                        image_a.get("index") != image_b.get("index")
                        or box != image_b.get("box")
                        or not box
                        or image_a.get("objectFit") != image_b.get("objectFit")
                        or image_a.get("objectPosition")
                        != image_b.get("objectPosition")
                    ):
                        continue
                    sha_a = selected_sha(
                        manifests[0].get("dist", ""),
                        image_a.get("src") or "",
                        image_a.get("currentSrc") or "",
                    )
                    sha_b = selected_sha(
                        manifests[1].get("dist", ""),
                        image_b.get("src") or "",
                        image_b.get("currentSrc") or "",
                    )
                    if sha_a is None or sha_b is None or sha_a == sha_b:
                        continue
                    rect = [
                        max(0, math.floor(box["x"] * scale_x)),
                        max(0, math.floor(box["y"] * scale_y)),
                        min(a.width, math.ceil((box["x"] + box["width"]) * scale_x)),
                        min(a.height, math.ceil((box["y"] + box["height"]) * scale_y)),
                    ]
                    if rect[0] >= rect[2] or rect[1] >= rect[3]:
                        continue
                    draw.rectangle(
                        (rect[0], rect[1], rect[2] - 1, rect[3] - 1), fill=255
                    )
                    changed_in_box = sum(changed_mask.crop(tuple(rect)).histogram()[1:])
                    if changed_in_box:
                        boxes.append(
                            {
                                "index": image_a["index"],
                                "selected_a": image_a.get("currentSrc"),
                                "selected_b": image_b.get("currentSrc"),
                                "box": box,
                                "changed_pixels": changed_in_box,
                                "sha256_a": sha_a,
                                "sha256_b": sha_b,
                            }
                        )
                outside = ImageChops.subtract(changed_mask, allowed)
                outside_pixels = sum(outside.histogram()[1:])
                result = {
                    "ratio": changed / (a.width * a.height),
                    "changed_pixels": changed,
                    "dimensions": list(a.size),
                    "outside_image_pixels": outside_pixels,
                    "all_changed_inside_image_boxes": outside_pixels == 0,
                    "image_boxes": boxes,
                }
                if args.diff_images and changed:
                    args.diff_images.mkdir(parents=True, exist_ok=True)
                    ImageEnhance.Contrast(delta).enhance(4).save(
                        args.diff_images / name
                    )
            differences[name] = result
    ratios = [row["ratio"] for row in differences.values()]
    runtime_differences = {}
    for name in sorted(
        manifests[0].get("shots", {}).keys() & manifests[1].get("shots", {}).keys()
    ):
        fields = (
            "route",
            "status",
            "title",
            "theme",
            "width",
            "height",
            "device_scale_factor",
            "position",
            "results",
            "mermaid_diagrams",
            "console_errors",
            "image_failures",
        )
        left = {
            key: manifests[0]["shots"][name].get(
                key, 1 if key == "device_scale_factor" else None
            )
            for key in fields
        }
        right = {
            key: manifests[1]["shots"][name].get(
                key, 1 if key == "device_scale_factor" else None
            )
            for key in fields
        }
        if left != right:
            runtime_differences[name] = {"a": left, "b": right}
    report = {
        "ok": True,
        "first": str(args.first),
        "second": str(args.second),
        "shots": differences,
        "channel_threshold": args.channel_threshold,
        "max_ratio": max(ratios, default=0),
        "mean_ratio": sum(ratios) / len(ratios) if ratios else 0,
        "changed_shots": sum(r > 0 for r in ratios),
        "compared": len(ratios),
        "added": sorted(second.keys() - first.keys()),
        "removed": sorted(first.keys() - second.keys()),
        "capture_failures_a": manifests[0]["failures"],
        "capture_failures_b": manifests[1]["failures"],
        "runtime_differences": runtime_differences,
    }
    report["passed"] = (
        bool(ratios)
        and not report["added"]
        and not report["removed"]
        and not any(m["failures"] for m in manifests)
        and not runtime_differences
        and all(r <= args.max_ratio for r in ratios)
    )
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "shots"}
            | {"report": str(args.json)}
        )
    )
    return 0 if report["passed"] else 1


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    shoot = sub.add_parser(
        "capture",
        help="serve a dist on an isolated port and capture all four viewport/theme combinations",
    )
    shoot.add_argument("dist", type=Path)
    shoot.add_argument("--out", type=Path, required=True)
    shoot.add_argument("--port", type=int, default=4391)
    shoot.add_argument("--source-commit", help="exact source commit for this dist")
    shoot.add_argument(
        "--scale",
        choices=["css", "device"],
        default="css",
        help="screenshot pixel scale; device preserves native DPR pixels",
    )
    shoot.add_argument(
        "--pages",
        type=Path,
        help="reuse the exact pages.json from the baseline capture",
    )
    shoot.add_argument(
        "--dpr",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="browser device pixel ratio",
    )
    compare = sub.add_parser(
        "diff", help="pixel diff with a ratio for every shot; default is exact pixels"
    )
    compare.add_argument("first", type=Path)
    compare.add_argument("second", type=Path)
    compare.add_argument("--json", type=Path, required=True)
    compare.add_argument(
        "--channel-threshold", type=int, default=0, choices=range(256), metavar="0..255"
    )
    compare.add_argument("--max-ratio", type=float, default=0.0)
    compare.add_argument("--diff-images", type=Path)
    args = cli.parse_args()
    try:
        if args.command == "diff" and not 0 <= args.max_ratio <= 1:
            raise ValueError("max-ratio must be in 0..1")
        return capture(args) if args.command == "capture" else diff(args)
    except (OSError, ValueError, PlaywrightError) as error:
        print(json.dumps({"ok": False, "errors": [str(error)]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
