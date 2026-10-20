"""Exercise the parity command against small built-site fixtures."""

import gzip
import json
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "parity"


def png(path: Path, color: tuple[int, int, int], level: int = 6) -> None:
    scanlines = (b"\x00" + bytes(color) * 2) * 2

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scanlines, level))
        + chunk(b"IEND", b"")
    )


class ParityCommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.before = self.folder / "before"
        self.after = self.folder / "after"
        shutil.copytree(FIXTURES / "base", self.before)
        shutil.copytree(FIXTURES / "base", self.after)

    def html(self, side: Path, old: str, new: str) -> None:
        path = side / "index.html"
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def pagefind(self, variant: str) -> None:
        for side, name in ((self.before, "ordered"), (self.after, variant)):
            shutil.rmtree(side / "pagefind")
            shutil.copytree(FIXTURES / name / "pagefind", side / "pagefind")

    def run_parity(
        self, *options: str
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        report_path = self.folder / "report.json"
        result = subprocess.run(
            [
                "uv",
                "run",
                "scripts/parity.py",
                str(self.before),
                str(self.after),
                "--json",
                str(report_path),
                *options,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        report = (
            json.loads(report_path.read_text(encoding="utf-8"))
            if report_path.exists()
            else {}
        )
        return result, report

    def findings(self, report: dict, kind: str) -> list[dict]:
        return [
            item
            for item in report["checks"]
            if item["kind"] == kind and item["classification"] == "material"
        ]

    def test_entity_equivalence_and_character_change(self) -> None:
        self.html(self.before, "before <em>after", "l'événement <em>after")
        self.html(self.after, "before <em>after", "l&#x27;événement <em>after")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "text"))
        self.html(self.after, "l&#x27;événement", "l’autre événement")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "text"))

    def test_inline_glue(self) -> None:
        self.html(self.after, "before <em>after", "before<em>after")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "text"))
        self.assertTrue(self.findings(report, "inline_text"))

    def test_missing_and_empty_alt(self) -> None:
        self.html(self.after, 'height="2">', 'height="2" alt="">')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "images"))

    def test_heading_id(self) -> None:
        self.html(self.after, 'id="start"', 'id="changed"')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "ids"))

    def test_javascript_file(self) -> None:
        (self.after / "_astro" / "app.ABCDEFGH.js").write_text(
            'window.parity = "changed";\n'
        )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "assets"))

    def test_inline_script(self) -> None:
        self.html(self.after, "window.parity = 1", "window.parity = 2")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "inline_scripts"))

    def test_pagefind_renumbering(self) -> None:
        self.pagefind("renumbered")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["verdict"], "IDENTICAL")

    def test_pagefind_removed_posting(self) -> None:
        self.pagefind("removed")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "pagefind_postings"))

    def test_pagefind_fragment_content(self) -> None:
        self.pagefind("ordered")
        path = self.after / "pagefind/fragment/a.pf_fragment"
        marker = b"pagefind_dcd"
        fragment = json.loads(gzip.decompress(path.read_bytes())[len(marker) :])
        fragment["content"] = "changed"
        path.write_bytes(gzip.compress(marker + json.dumps(fragment).encode(), mtime=0))
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "pagefind_fragment"))

    def test_pagefind_fragment_asset_name(self) -> None:
        self.pagefind("ordered")
        marker = b"pagefind_dcd"
        for side, name in ((self.before, "AAAAAAAA"), (self.after, "BBBBBBBB")):
            path = side / "pagefind/fragment/a.pf_fragment"
            fragment = json.loads(gzip.decompress(path.read_bytes())[len(marker) :])
            fragment["image"] = f"/_astro/image.{name}.webp"
            path.write_bytes(
                gzip.compress(marker + json.dumps(fragment).encode(), mtime=0)
            )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "pagefind_fragment"))

    def test_removed_rss_item(self) -> None:
        path = self.after / "rss.xml"
        path.write_text(
            path.read_text().replace(
                "<item><title>Two</title><link>https://example.test/two</link></item>",
                "",
            )
        )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "rss"))

    def test_srcset_pixel_change_and_lossless_encoding(self) -> None:
        png(self.after / "variant.png", (20, 30, 40), level=0)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "image_pixels"))
        png(self.after / "variant.png", (21, 30, 40))
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "image_pixels"))

    def test_exact_ledger_pair(self) -> None:
        self.html(self.after, "<title>Start</title>", "<title>Changed</title>")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        material = [
            item for item in report["checks"] if item["classification"] == "material"
        ]
        self.assertEqual([item["kind"] for item in material], ["title"])
        ledger = self.folder / "ledger.json"
        ledger.write_text(json.dumps({material[0]["fingerprint"]: "fixture title"}))
        result, report = self.run_parity("--accept", str(ledger))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.html(self.after, "<title>Changed</title>", "<title>Another</title>")
        result, report = self.run_parity("--accept", str(ledger))
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "title"))

    def prepare_fonts(self, swap: bool) -> None:
        css_path = "_astro/site.ABCDEFGH.css"
        for side, regular_suffix, italic_suffix in (
            (self.before, "12345678", "87654321"),
            (self.after, "ABCDEFGH", "HGFEDCBA"),
        ):
            regular = f"normal.{regular_suffix}.woff2"
            italic = f"italic.{italic_suffix}.woff2"
            css = (
                f'@font-face {{ font-family: Parity; font-style: normal; font-weight: 400; src: url("/_astro/fonts/{regular}"); }}\n'
                f'@font-face {{ font-family: Parity; font-style: italic; font-weight: 400; src: url("/_astro/fonts/{italic}"); }}\n'
            )
            (side / css_path).write_text(css)
            if side is self.after:
                fonts = side / "_astro/fonts"
                (fonts / "normal.12345678.woff2").rename(fonts / regular)
                (fonts / "italic.87654321.woff2").rename(fonts / italic)
        if swap:
            fonts = self.after / "_astro/fonts"
            normal = (fonts / "normal.ABCDEFGH.woff2").read_bytes()
            italic = (fonts / "italic.HGFEDCBA.woff2").read_bytes()
            (fonts / "normal.ABCDEFGH.woff2").write_bytes(italic)
            (fonts / "italic.HGFEDCBA.woff2").write_bytes(normal)

    def test_fetched_font_names(self) -> None:
        self.prepare_fonts(False)
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["verdict"], "COSMETIC")
        self.assertEqual(len(report["fonts"]["b"]), 2)

    def test_fetched_pairs_script_and_stylesheet_by_page_slot(self) -> None:
        self.prepare_fonts(False)
        (self.after / "_astro/app.ABCDEFGH.js").rename(self.after / "_astro/runtime.js")
        (self.after / "_astro/site.ABCDEFGH.css").rename(self.after / "_astro/site.css")
        self.html(self.after, "/_astro/app.ABCDEFGH.js", "/_astro/runtime.js")
        self.html(self.after, "/_astro/site.ABCDEFGH.css", "/_astro/site.css")
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "attributes"))
        self.assertFalse(self.findings(report, "assets"))

    def test_fetched_font_role_swap(self) -> None:
        self.prepare_fonts(True)
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "font_roles"))

    def test_fetched_checks_inline_font_faces(self) -> None:
        rules = (
            '<style>@font-face{font-family:Parity;font-style:normal;font-weight:400;src:url("/_astro/fonts/normal.12345678.woff2")}'
            '@font-face{font-family:Parity;font-style:italic;font-weight:400;src:url("/_astro/fonts/italic.87654321.woff2")}</style>'
        )
        for side in (self.before, self.after):
            self.html(side, "</head>", rules + "</head>")
        fonts = self.after / "_astro/fonts"
        normal = (fonts / "normal.12345678.woff2").read_bytes()
        italic = (fonts / "italic.87654321.woff2").read_bytes()
        (fonts / "normal.12345678.woff2").write_bytes(italic)
        (fonts / "italic.87654321.woff2").write_bytes(normal)
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "font_roles"))


if __name__ == "__main__":
    unittest.main()
