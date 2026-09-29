#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.56.0"]
# ///
"""Drive one page with Playwright, then save a screenshot, an ARIA snapshot, and its state."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import NoReturn
from urllib.parse import urljoin

from playwright.sync_api import Error, Page, sync_playwright

EPILOG = """\
Steps run in order, each as ACTION:ARGUMENT, with Playwright selectors such as
#theme-btn, role=link[name="tags"], or text=Rechercher:
  click:SELECTOR          click an element
  fill:SELECTOR=TEXT      type TEXT into a field
  press:KEY               press a key, such as Enter
  wait:SELECTOR           wait until the element is visible
  goto:PATH               open a path on the same site, such as /tags

Then OUT receives screenshot.png (the viewport, at most 1920 CSS pixels a side),
aria.txt (the accessibility snapshot), and state.json (url, title, theme, and
console errors). The paths print on stdout.

examples:
  uv run browse.py http://127.0.0.1:4330/ --out cache/verify-blog/run/home
  uv run browse.py http://127.0.0.1:4330/search --out cache/verify-blog/run/search \\
    --step 'fill:.pagefind-ui__search-input=bitcoin' --step 'wait:.pagefind-ui__result'
  uv run browse.py http://127.0.0.1:4330/ --out cache/verify-blog/run/theme \\
    --color-scheme light --step 'click:#theme-btn'

exit codes:
  0    every step ran and the evidence is saved
  1    a step or the page failed, and the evidence saved so far stays; or
       Chromium is not installed
  2    bad usage
  130  interrupted (SIGINT)"""

VIEWPORTS = {"desktop": {"width": 1440, "height": 900}}
ACTIONS = ("click", "fill", "press", "wait", "goto")
# The browser matching the pinned Playwright, with the system libraries it needs
# on Linux; a cloud sandbox may ship both already
INSTALL = (
    "uv run --with playwright==1.56.0 python -m playwright install --with-deps chromium"
)


class Parser(argparse.ArgumentParser):
    """argparse whose usage errors print short usage and the help hint, then exit 2."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\nrun '{self.prog} --help'\n")


def step(value: str) -> tuple[str, str]:
    action, _, argument = value.partition(":")
    if action not in ACTIONS or not argument:
        raise argparse.ArgumentTypeError(
            f"invalid step {value!r}; use ACTION:ARGUMENT with ACTION one of {', '.join(ACTIONS)}"
        )
    return action, argument


def run(page: Page, base: str, action: str, argument: str) -> None:
    if action == "click":
        page.locator(argument).first.click()
    elif action == "fill":
        selector, _, text = argument.partition("=")
        page.locator(selector).first.fill(text)
    elif action == "press":
        page.keyboard.press(argument)
    elif action == "wait":
        page.locator(argument).first.wait_for(state="visible")
    else:
        # /tags resolves against the site's origin, whatever page it starts from
        page.goto(urljoin(base, argument))
    page.wait_for_load_state("networkidle")


def main(argv: list[str] | None = None) -> int:
    cli = Parser(
        prog="browse.py",
        description="Drive one page with Playwright, then save a screenshot, "
        "an ARIA snapshot, and its state",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    cli.add_argument("url", help="the page to open, such as http://127.0.0.1:4330/")
    cli.add_argument(
        "--out", required=True, type=Path, help="directory for the evidence"
    )
    cli.add_argument(
        "--device",
        choices=["desktop", "iphone"],
        default="desktop",
        help="desktop at 1440x900 (default), or an emulated iPhone 15; not Safari",
    )
    cli.add_argument(
        "--color-scheme",
        choices=["light", "dark"],
        help="the operating system color scheme the page sees",
    )
    cli.add_argument(
        "--step",
        action="append",
        type=step,
        default=[],
        metavar="ACTION:ARGUMENT",
        help="an action to run before the capture; repeat for more",
    )
    argv = sys.argv[1:] if argv is None else argv
    # -h wins over every other argument before --, as the CLI contract asks
    if {"-h", "--help"} & set(itertools.takewhile(lambda arg: arg != "--", argv)):
        cli.print_help()
        return 0
    args = cli.parse_args(argv)
    try:
        return drive(args)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


def drive(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    failure = ""
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Error as error:
            print(str(error).splitlines()[0], file=sys.stderr)
            print(f"error: Chromium did not start; run: {INSTALL}", file=sys.stderr)
            return 1
        if args.device == "iphone":
            options = dict(playwright.devices["iPhone 15"])
        else:
            options = {"viewport": VIEWPORTS["desktop"]}
        if args.color_scheme:
            options["color_scheme"] = args.color_scheme
        page = browser.new_context(**options).new_page()
        page.on(
            "console",
            lambda message: message.type == "error" and errors.append(message.text),
        )
        page.on("pageerror", lambda error: errors.append(str(error)))
        try:
            page.goto(args.url)
            page.wait_for_load_state("networkidle")
            for action, argument in args.step:
                run(page, args.url, action, argument)
        except Error as error:
            failure = str(error).splitlines()[0]
        screenshot = args.out / "screenshot.png"
        page.screenshot(path=screenshot, scale="css")
        (args.out / "aria.txt").write_text(page.locator("body").aria_snapshot() + "\n")
        state = {
            "url": page.url,
            "title": page.title(),
            "theme": page.evaluate("document.documentElement.dataset.theme ?? null"),
            "device": args.device,
            "steps": [f"{action}:{argument}" for action, argument in args.step],
            "console_errors": errors,
            "failure": failure or None,
        }
        (args.out / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n"
        )
        browser.close()
    print(
        "\n".join(
            str(args.out / name)
            for name in ("screenshot.png", "aria.txt", "state.json")
        )
    )
    if failure:
        print(
            f"error: {failure}; the evidence above shows the page when it failed",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
