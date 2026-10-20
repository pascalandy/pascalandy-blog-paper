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
import time
from pathlib import Path
from typing import NoReturn
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import Browser, Error, Page, Playwright, sync_playwright

EPILOG = """\
Steps run in order, each as ACTION:ARGUMENT, with Playwright selectors such as
#theme-btn, role=link[name="tags"], or text=Rechercher:
  click:SELECTOR          click an element
  fill:SELECTOR=TEXT      type TEXT into a field
  press:KEY               press a key, such as Enter
  wait:SELECTOR           wait until the element is visible
  goto:PATH               open a path on the same site, such as /tags
  reload                  reload the current page
  back                    use browser history back
  eval:JS                 evaluate JS and save its result in state.json

A role= name must equal the whole accessible name; a regex, such as
role=link[name=/^Next/], matches part of it.

Then OUT receives screenshot.png (the viewport, at most 1920 CSS pixels a side),
aria.txt (the accessibility snapshot), state.json, network.json (responses and
status codes), and probes.json (DOMContentLoaded and Astro navigation events).
The paths print on stdout.

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
ACTIONS = ("click", "fill", "press", "wait", "goto", "reload", "back", "eval")
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
    if action not in ACTIONS or (not argument and action not in ("reload", "back")):
        raise argparse.ArgumentTypeError(
            f"invalid step {value!r}; use ACTION:ARGUMENT with ACTION one of {', '.join(ACTIONS)}"
        )
    return action, argument


def launch_chromium(playwright: Playwright) -> Browser:
    try:
        return playwright.chromium.launch()
    except Error as error:
        raise ValueError(
            f"{str(error).splitlines()[0]}; Chromium did not start; run: {INSTALL}"
        ) from error


def collect_page_errors(page: Page, errors: list[str]) -> None:
    page.on(
        "console",
        lambda message: message.type == "error" and errors.append(message.text),
    )
    page.on("pageerror", lambda error: errors.append(str(error)))


def await_navigation(
    page: Page, events: list[dict], start: int, previous_url: str | None = None
) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        current = urlsplit(page.url)
        previous = urlsplit(previous_url) if previous_url else None
        anchor_change = bool(
            previous
            and (current.path, current.query) == (previous.path, previous.query)
            and current.fragment != previous.fragment
        )
        if (
            any(
                event["event"] in ("astro:page-load", "load")
                for event in events[start:]
            )
            or anchor_change
        ):
            page.wait_for_load_state("networkidle")
            return
        page.wait_for_timeout(50)
    raise Error("navigation did not reach astro:page-load or load within 20 seconds")


def run(
    page: Page, base: str, action: str, argument: str, events: list[dict]
) -> object:
    if action == "click":
        target = page.locator(argument).first
        href = target.evaluate("element => element.closest('a')?.href ?? null")
        current = urlsplit(page.url)
        destination = urlsplit(href) if href else current
        navigates = bool(
            href
            and (
                (destination.path, destination.query) != (current.path, current.query)
                or not destination.fragment
            )
        )
        start = len(events)
        target.click()
        if navigates:
            await_navigation(page, events, start)
    elif action == "fill":
        selector, _, text = argument.partition("=")
        page.locator(selector).first.fill(text)
    elif action == "press":
        page.keyboard.press(argument)
    elif action == "wait":
        page.locator(argument).first.wait_for(state="visible")
    elif action == "goto":
        # /tags resolves against the site's origin, whatever page it starts from
        page.goto(urljoin(base, argument), wait_until="load")
    elif action == "reload":
        page.reload(wait_until="load")
    elif action == "back":
        start = len(events)
        previous_url = page.url
        page.evaluate("history.back()")
        await_navigation(page, events, start, previous_url)
    elif action == "eval":
        result = page.evaluate(argument)
        page.wait_for_load_state("networkidle")
        return result
    page.wait_for_load_state("networkidle")
    return None


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
    network: list[dict] = []
    failed_requests: list[dict] = []
    probes: list[dict] = []
    events: list[dict] = []
    evaluations: list[dict] = []
    current_step = {"value": "initial"}
    failure = ""
    with sync_playwright() as playwright:
        try:
            browser = launch_chromium(playwright)
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        if args.device == "iphone":
            options = dict(playwright.devices["iPhone 15"])
        else:
            options = {"viewport": VIEWPORTS["desktop"]}
        if args.color_scheme:
            options["color_scheme"] = args.color_scheme
        context = browser.new_context(**options)

        def record_probe(_source: object, payload: dict) -> None:
            row = {**payload, "step": current_step["value"]}
            probes.append(row)
            events.append(row)

        context.expose_binding("__verifyBlogEmit", record_probe)
        context.add_init_script("""(() => {
          const theme = () => document.documentElement.getAttribute('data-theme');
          const record = (event, extra = {}) => window.__verifyBlogEmit({event, theme: theme(), url: location.href, ...extra});
          const before = [];
          let armed = false;
          document.addEventListener('DOMContentLoaded', () => record('DOMContentLoaded'));
          document.addEventListener('astro:after-swap', () => before.push({theme: theme(), url: location.href}));
          document.addEventListener('astro:page-load', () => {
            if (!armed) {
              document.addEventListener('astro:after-swap', () => {
                const early = before.shift();
                record('astro:after-swap', {theme_before_handlers: early?.theme ?? null, before_url: early?.url ?? null});
              });
              armed = true;
            }
            record('astro:page-load');
          });
        })();""")
        page = context.new_page()
        collect_page_errors(page, errors)
        page.on(
            "response",
            lambda response: network.append(
                {
                    "event": "response",
                    "url": response.url,
                    "status": response.status,
                    "resource_type": response.request.resource_type,
                    "step": current_step["value"],
                }
            ),
        )
        page.on(
            "requestfailed",
            lambda request: failed_requests.append(
                {
                    "event": "requestfailed",
                    "url": request.url,
                    "status": None,
                    "failure": request.failure,
                    "resource_type": request.resource_type,
                    "step": current_step["value"],
                }
            ),
        )
        page.on(
            "load",
            lambda: events.append({"event": "load", "step": current_step["value"]}),
        )
        try:
            page.goto(args.url, wait_until="load")
            page.wait_for_load_state("networkidle")
            for index, (action, argument) in enumerate(args.step, start=1):
                current_step["value"] = f"{index}:{action}"
                value = run(page, args.url, action, argument, events)
                if action == "eval":
                    evaluations.append({"step": current_step["value"], "result": value})
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
            "evaluations": evaluations,
            "failure": failure or None,
        }
        (args.out / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n"
        )
        (args.out / "network.json").write_text(
            json.dumps(
                {"responses": network, "failures": failed_requests},
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
        (args.out / "probes.json").write_text(
            json.dumps({"events": probes}, ensure_ascii=False, indent=2) + "\n"
        )
        browser.close()
    print(
        "\n".join(
            str(args.out / name)
            for name in (
                "screenshot.png",
                "aria.txt",
                "state.json",
                "network.json",
                "probes.json",
            )
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
