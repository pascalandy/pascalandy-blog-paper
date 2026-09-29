#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print the blog's computed state: posts by bucket, tags, site, and the docs index."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, NoReturn

ROOT = Path(__file__).resolve().parent.parent
BLOG = "src/data/blog"
PLAYBOOKS = f"{BLOG}/dev_workflows/"

# The registry, the site config, and every post's frontmatter, read by Bun from
# the source files, so no value is copied here. Frontmatter goes through the regex
# and the js-yaml parser behind Astro's parseFrontmatter
READ = (
    'const { TAGS } = await import("./src/tags.ts"); '
    'const { SITE, ACTIVE_THEME } = await import("./src/config.ts"); '
    'const yaml = (await import("js-yaml")).default; '
    "const posts = []; "
    f'for await (const file of new Bun.Glob("{BLOG}/**/*.md").scan(".")) '
    "posts.push({ file, data: yaml.load("
    "/(?:^\\uFEFF?|^\\s*\\n)---([\\s\\S]*?\\n)---/.exec(await Bun.file(file).text())[1]) }); "
    "console.log(JSON.stringify({ site: SITE, theme: ACTIVE_THEME, tags: TAGS, posts }));"
)

BUCKETS = ("draft", "scheduled", "excluded_by_tag", "blog_roll")

EPILOG = """\
Buckets are disjoint and tested in this order, as the site filters posts:
  draft            draft: true; never built
  scheduled        date_created later than now plus the scheduling margin
  excluded_by_tag  a tag with excludeFromBlogRoll; built, but not in /blog/ or RSS
  blog_roll        every other post

Tag counts cover built, listed posts, as on /tags/. Posts that share a date sort
by file name here; the site gives them no stable order (backlog B9).

examples:
  just overview
  just overview --json
  just overview --json | jq '.posts.counts'

exit codes:
  0    success
  1    the registry or the posts could not be read
  2    bad usage"""


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


class Failure(Exception):
    """An expected failure; the message says what to fix."""


def kebab(text: str) -> str:
    """lodash.kebabcase, as src/utils/slugify.ts applies it to folder names."""
    words = re.findall(r"[A-Z]{2,}(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|[A-Z]+|\d+", text)
    return "-".join(word.lower() for word in words)


def url(file: str) -> str:
    """The post's path as src/utils/getPath.ts builds it."""
    parts = Path(file).relative_to(BLOG).parts
    folders = [kebab(part) for part in parts[:-1] if not part.startswith("_")]
    return "/".join(["/blog", *folders, Path(parts[-1]).stem.lower()])


def read() -> dict[str, Any]:
    if shutil.which("bun") is None:
        raise Failure(
            "bun not found on PATH; install Bun (https://bun.sh), then run: just install"
        )
    result = subprocess.run(
        ["bun", "-e", READ], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise Failure(
            "could not read the registry and posts; run: just check --only content"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise Failure(
            f"Bun printed unreadable JSON ({error}); rerun: just overview"
        ) from None


def published(date: str, margin: timedelta, now: datetime) -> bool:
    """Whether postFilter lists a post dated `date` at `now`."""
    moment = datetime.fromisoformat(date)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return now > moment - margin


def overview(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    site = state["site"]
    registry = {tag["slug"]: tag for tag in state["tags"]}
    excluded = {
        slug for slug, tag in registry.items() if tag.get("excludeFromBlogRoll")
    }
    margin = timedelta(milliseconds=site["scheduledPostMargin"])
    buckets: dict[str, list[dict[str, Any]]] = {name: [] for name in BUCKETS}
    featured, docs = [], []
    counts: dict[str, int] = dict.fromkeys(registry, 0)
    for entry in sorted(state["posts"], key=lambda post: post["file"]):
        if Path(entry["file"]).name.startswith("_"):
            continue
        data = entry["data"]
        date = str(data["date_created"])
        post = {
            "title": data["title"],
            "date": date[:10],
            "url": url(entry["file"]),
            "file": entry["file"],
            "tags": data["tags"],
        }
        if data.get("draft"):
            bucket = "draft"
        elif not published(date, margin, now):
            bucket = "scheduled"
        elif set(data["tags"]) & excluded:
            bucket = "excluded_by_tag"
        else:
            bucket = "blog_roll"
        buckets[bucket].append(post)
        if data.get("featured"):
            featured.append({**post, "bucket": bucket})
        if bucket in ("excluded_by_tag", "blog_roll"):
            for tag in data["tags"]:
                counts[tag] = counts.get(tag, 0) + 1
        if entry["file"].startswith(PLAYBOOKS):
            docs.append(
                {
                    "title": data["title"],
                    "description": data["description"],
                    "url": post["url"],
                    "file": entry["file"],
                }
            )
    total = sum(len(posts) for posts in buckets.values())
    latest = sorted(buckets["blog_roll"], key=lambda post: post["date"], reverse=True)
    tags = [
        {
            "slug": slug,
            "name": registry.get(slug, {}).get("name", slug),
            "posts": count,
            "registered": slug in registry,
            "hiddenFromTagsPage": bool(
                registry.get(slug, {}).get("hiddenFromTagsPage")
            ),
            "excludeFromBlogRoll": slug in excluded,
        }
        for slug, count in sorted(counts.items())
    ]
    return {
        "site": {
            "title": site["title"],
            "url": site["website"],
            "lang": site["lang"],
            "timezone": site["timezone"],
            "theme": state["theme"],
        },
        "posts": {
            "total": total,
            "counts": {name: len(posts) for name, posts in buckets.items()},
            "buckets": buckets,
        },
        "featured": featured,
        "latest": latest[:5],
        "tags": tags,
        "docs": docs,
    }


def summary(state: dict[str, Any]) -> str:
    site, posts, tags = state["site"], state["posts"], state["tags"]
    counts = posts["counts"]
    buckets = ", ".join(
        [
            f"{counts['draft']} draft",
            f"{counts['scheduled']} scheduled",
            f"{counts['excluded_by_tag']} excluded by tag",
            f"{counts['blog_roll']} in the blog roll",
        ]
    )
    flags = ", ".join(
        [
            f"{sum(tag['hiddenFromTagsPage'] for tag in tags)} hidden from /tags/",
            f"{sum(tag['excludeFromBlogRoll'] for tag in tags)} excluded from the blog roll",
            f"{sum(not tag['registered'] for tag in tags)} unregistered",
        ]
    )
    lines = [
        f"{site['title']} · {site['url']} · lang {site['lang']} · theme {site['theme']}",
        f"posts {posts['total']}: {buckets} · {len(state['featured'])} featured",
        "latest in the blog roll:",
        *(
            f"  {post['date']}  {post['title']}  {post['url']}"
            for post in state["latest"]
        ),
        f"tags {len(tags)}: {flags}",
        f"docs {len(state['docs'])} playbooks; the index: just overview --json | jq .docs",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    cli = Parser(
        prog="just overview",
        description="Print the blog's computed state: posts by bucket, tags, site, "
        "and the docs index",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument(
        "--json", action="store_true", help="print one JSON object instead"
    )
    args = cli.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        state = overview(read(), datetime.now(UTC))
    except Failure as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    print(
        json.dumps(state, ensure_ascii=False, indent=2) if args.json else summary(state)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
