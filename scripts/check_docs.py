#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check that agent-facing docs cite only repo paths, recipes, and checks that exist."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import NoReturn

from check import CHECKS

ROOT = Path(__file__).resolve().parent.parent

EPILOG = """\
What counts as a citation:
  paths    inline code that starts with a tracked top-level name or a dot, such
           as `src/tags.ts` or `.mcp.json`, must exist from the repo root; a
           source file named bare, such as `Layout.astro`, or under another
           folder, such as `dev_workflows/image_path.md`, must end a tracked
           path; relative Markdown links must resolve
  recipes  `just NAME` in inline code or a code block
  checks   `--only NAME` after `just check` or `just ci`

Skipped: code blocks for paths, URLs, site routes and commands (`/tags/`), home
paths (`~/`), gitignored paths such as `dist/`, folders under another folder
such as `dev_workflows/`, placeholders such as `<name>` or `NAME`, bare names of
generated files such as `state.json`, CSS classes such as `.card`, and names
starting with `_`, the prefix of unpublished playbooks and examples. Link a
command's file, as in [/worktree](.claude/commands/worktree.md), to check it.

examples:
  just check --only docs
  uv run scripts/check_docs.py AGENTS.md

exit codes:
  0    every citation exists
  1    a citation names something missing
  2    bad usage"""

# The docs agents read: the contract, the README, the PR template, Claude
# commands and skills, and the published playbooks
DOCS = (
    "AGENTS.md",
    "README.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".claude/**/*.md",
    "src/data/blog/dev_workflows/[!_]*.md",
)

# A bare name counts as a path only for source files; a bare `state.json` or
# `aria.txt` usually names a file a tool writes
EXTENSIONS = {
    "astro",
    "cjs",
    "css",
    "js",
    "md",
    "mjs",
    "py",
    "sh",
    "toml",
    "ts",
    "tsx",
    "yaml",
    "yml",
}
# A bare dotfile has an extension, such as `.mcp.json`; `.card` is a CSS class
DOTFILE = re.compile(r"\.[\w-]+\.(json|mjs|js|toml|yaml|yml|md)")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE = re.compile(r"`([^`\n]+)`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
# `just` where a command starts: at the start, after a shell operator, or after
# the uvx fallback `uvx --from rust-just`
JUST = re.compile(
    r"(?:^\s*(?:\$\s+)?|&&\s*|\|\|\s*|;\s*|\(\s*|rust-just\s+)just((?:\s+[^\s`#|;&)]+)*)"
)
# `...` inside brackets is literal, as in the route file `[...slug].astro`
PLACEHOLDER = re.compile(r"[<>{}$…()]|(?<!\[)\.\.\.|^[A-Z_]+$")


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


def git_lines(*args: str, stdin: str | None = None) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.splitlines()


def recipes() -> set[str]:
    """Recipe and alias names, read from the justfile."""
    text = (ROOT / "justfile").read_text(encoding="utf-8")
    names = set(
        re.findall(r"^([a-z][\w-]*)\b[^\n]*?:(?!=)(?:\s|$)", text, re.MULTILINE)
    )
    names |= set(re.findall(r"^alias\s+([\w-]+)\s*:=", text, re.MULTILINE))
    return names - {"set", "alias", "export", "import", "mod"}


def lines(doc: Path) -> Iterator[tuple[int, str, bool]]:
    """Each line with its number and whether it sits in a code block, frontmatter skipped."""
    text = doc.read_text(encoding="utf-8").splitlines()
    start = 0
    if text and text[0] == "---":
        start = next((i + 1 for i, line in enumerate(text[1:], 1) if line == "---"), 0)
    fenced = False
    for number, line in enumerate(text[start:], start + 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        yield number, line, fenced


def just_problems(command: str, names: set[str]) -> Iterator[str]:
    words = command.split()
    if not words or words[0].startswith("-") or PLACEHOLDER.search(words[0]):
        return
    if words[0] not in names:
        yield f'"just {words[0]}" names no recipe; run `just` to list them'
        return
    if words[0] not in ("check", "ci"):
        return
    checks = {check.name for check in CHECKS}
    for index, word in enumerate(words):
        if word == "--only":
            name = words[index + 1] if index + 1 < len(words) else ""
        elif word.startswith("--only="):
            name = word.removeprefix("--only=")
        else:
            continue
        if name and not PLACEHOLDER.search(name) and name not in checks:
            yield f'"--only {name}" names no check; run `just check --list`'


class Paths:
    """Which cited paths exist, judged against the files git would commit."""

    def __init__(self) -> None:
        files = git_lines("ls-files", "--cached", "--others", "--exclude-standard")
        self.files = {name for name in files if (ROOT / name).exists()}
        self.dirs = {
            str(parent) for name in self.files for parent in Path(name).parents
        }
        self.top = {name.split("/")[0] for name in self.files}

    def ignored(self, path: str) -> bool:
        """Whether git ignores the path; the trailing slash matches an absent directory."""
        bare = path.rstrip("/")
        return bool(git_lines("check-ignore", bare, f"{bare}/"))

    def exists(self, path: str) -> bool:
        path = path.rstrip("/")
        if "*" in path or "?" in path:
            return any(Path(name).match(path) for name in self.files)
        return path in self.files or path in self.dirs or (ROOT / path).exists()

    def ends(self, path: str) -> bool:
        """Whether a tracked file's path ends with this one; `*` and `?` glob."""
        if "*" in path or "?" in path:
            return any(Path(name).match(path) for name in self.files)
        return any(name == path or name.endswith(f"/{path}") for name in self.files)

    def problem(self, span: str) -> str | None:
        path = re.sub(r"(:\d+)+$|#.*$", "", span.strip().rstrip(".,;:"))
        if not path or " " in path or PLACEHOLDER.search(path):
            return None
        first = path.split("/")[0]
        if path.startswith(("/", "~", "@", "http", "_")) or first in (".", ".."):
            return None
        if path.startswith("."):
            if "/" not in path and not DOTFILE.fullmatch(path):
                return None
            rooted = True
        elif "/" in path and first in self.top:
            rooted = True
        elif path.rsplit(".", 1)[-1] in EXTENSIONS:
            # A bare source file, or one under another folder, may be
            # relative, as in `dev_workflows/image_path.md`: it must end a
            # tracked path, so a renamed top-level folder still fails it
            rooted = False
        else:
            return None
        if self.ignored(path):
            return None
        found = self.exists(path) if rooted else self.ends(path)
        return None if found else f'path "{span}" does not exist'


def problems(doc: Path, names: set[str], paths: Paths) -> Iterator[str]:
    where = doc.relative_to(ROOT)
    for number, line, fenced in lines(doc):
        # In a code block, a comment is prose
        spans = [line.split(" #")[0]] if fenced else CODE.findall(line)
        for span in spans:
            for match in JUST.finditer(span):
                for problem in just_problems(match.group(1), names):
                    yield f"{where}:{number}: {problem}"
            if not fenced and not span.startswith("just"):
                problem = paths.problem(span)
                if problem:
                    yield f"{where}:{number}: {problem}"
        if fenced:
            continue
        for target in LINK.findall(CODE.sub("", line)):
            if re.match(r"^([a-z]+:|/|#|@)", target):
                continue
            if not (doc.parent / target.split("#")[0]).exists():
                yield f'{where}:{number}: link "{target}" does not resolve'


def main(argv: list[str] | None = None) -> int:
    cli = Parser(
        prog="check_docs.py",
        description="Check that agent-facing docs cite only repo paths, recipes, "
        "and checks that exist",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument("files", nargs="*", metavar="FILE", help="docs to check")
    args = cli.parse_args(sys.argv[1:] if argv is None else argv)
    docs = [ROOT / name for name in args.files] or sorted(
        {path for pattern in DOCS for path in ROOT.glob(pattern)}
    )
    missing = [str(doc) for doc in docs if not doc.is_file()]
    if missing:
        cli.error(f"no such file: {', '.join(missing)}")
    names, paths = recipes(), Paths()
    found = [problem for doc in docs for problem in problems(doc, names, paths)]
    for problem in found:
        print(problem, file=sys.stderr)
    if found:
        print(
            "error: docs cite missing paths, recipes, or checks; fix the lines above",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
