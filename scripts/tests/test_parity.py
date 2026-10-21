"""Exercise the parity command against small built-site fixtures."""

import concurrent.futures
import gzip
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "parity"


def png(
    path: Path,
    color: tuple[int, int, int],
    level: int = 6,
    width: int = 2,
    height: int = 2,
) -> None:
    scanlines = (b"\x00" + bytes(color) * width) * height

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(scanlines, level))
        + chunk(b"IEND", b"")
    )


def add_png_chunk(path: Path, kind: bytes, payload: bytes) -> None:
    original = path.read_bytes()
    chunk = (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload))
    )
    path.write_bytes(original[:33] + chunk + original[33:])


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
        self, *options: str, reverse: bool = False, env: dict[str, str] | None = None
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        report_path = self.folder / "report.json"
        report_path.unlink(missing_ok=True)
        first, second = (
            (self.after, self.before) if reverse else (self.before, self.after)
        )
        result = subprocess.run(
            [
                "uv",
                "run",
                "scripts/parity.py",
                str(first),
                str(second),
                "--json",
                str(report_path),
                *options,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
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

    def test_french_spacing_is_not_collapsed(self) -> None:
        for space in ("\u00a0", "\u202f", "\u2009"):
            with self.subTest(space=repr(space)):
                shutil.copyfile(FIXTURES / "base/index.html", self.after / "index.html")
                self.html(self.after, "before <em>after", f"before{space}<em>after")
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(self.findings(report, "text"))

    def test_preformatted_spacing_is_exact(self) -> None:
        for side in (self.before, self.after):
            self.html(
                side,
                "</body>",
                "<pre>one\n    two</pre><textarea>a  b</textarea></body>",
            )
        for old, new in (("    two", "  two"), ("one\n", "one "), ("a  b", "a b")):
            with self.subTest(change=(old, new)):
                shutil.copyfile(self.before / "index.html", self.after / "index.html")
                self.html(self.after, old, new)
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(self.findings(report, "preformatted"))

    def test_missing_and_empty_alt(self) -> None:
        self.html(self.after, 'height="2">', 'height="2" alt="">')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "images"))

    def test_duplicate_attribute_cannot_hide_browser_first_value(self) -> None:
        self.html(self.after, 'width="2"', 'width="3" width="2"')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "duplicate_attributes"))

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
        self.assertEqual(
            [item["target"] for item in self.findings(report, "assets")],
            ["_astro/app.ABCDEFGH.js"],
        )

    def test_external_css_change_has_one_material_finding(self) -> None:
        path = self.after / "_astro/site.ABCDEFGH.css"
        path.write_text(path.read_text().replace("#000", "#111"))
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        material = [
            item for item in report["checks"] if item["classification"] == "material"
        ]
        self.assertEqual(
            [(item["kind"], item["target"]) for item in material],
            [("assets", "_astro/site.ABCDEFGH.css")],
        )

    def test_page_loaded_asset_swap_is_material_inside_multi_file_group(self) -> None:
        for label, old, new, payload, added_tag in (
            (
                "stylesheet",
                "site.ABCDEFGH.css",
                "site.ZZZZZZZZ.css",
                "body { color: red; }\n",
                None,
            ),
            (
                "script",
                "app.ABCDEFGH.js",
                "app.ZZZZZZZZ.js",
                "window.parity = 2;\n",
                None,
            ),
            (
                "modulepreload",
                "app.ABCDEFGH.js",
                "app.ZZZZZZZZ.js",
                "window.parity = 2;\n",
                '<link rel="modulepreload" href="/_astro/app.ABCDEFGH.js">',
            ),
            (
                "uppercase-preload",
                "site.ABCDEFGH.css",
                "site.ZZZZZZZZ.css",
                "body { color: red; }\n",
                '<link rel="PRELOAD" as="STYLE" href="/_astro/site.ABCDEFGH.css">',
            ),
        ):
            with self.subTest(resource=label):
                case = self.folder / label
                self.before = case / "before"
                self.after = case / "after"
                shutil.copytree(FIXTURES / "base", self.before)
                shutil.copytree(FIXTURES / "base", self.after)
                for side in (self.before, self.after):
                    (side / "_astro" / new).write_text(payload)
                    if added_tag:
                        self.html(side, "</head>", added_tag + "</head>")
                if added_tag:
                    self.html(self.after, added_tag, added_tag.replace(old, new))
                else:
                    self.html(self.after, old, new)
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(
                    [
                        (item["kind"], item["target"])
                        for item in self.findings(report, "resources")
                    ],
                    [("resources", "/")],
                )
                self.assertFalse(self.findings(report, "assets"))

    def test_page_loaded_hash_only_renames_remain_cosmetic(self) -> None:
        for old, new in (
            ("site.ABCDEFGH.css", "site.ZZZZZZZZ.css"),
            ("app.ABCDEFGH.js", "app.ZZZZZZZZ.js"),
        ):
            (self.after / "_astro" / old).rename(self.after / "_astro" / new)
            self.html(self.after, old, new)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["verdict"], "COSMETIC")
        self.assertFalse(self.findings(report, "resources"))
        self.assertFalse(self.findings(report, "assets"))

    def test_exact_path_image_swap_with_equal_group_multiset_is_material(self) -> None:
        names = ("bg.AAAAAAAA.png", "bg.ZZZZZZZZ.png")
        for side in (self.before, self.after):
            for name, color in zip(names, ((10, 20, 30), (40, 50, 60))):
                png(side / "_astro" / name, color)
            (side / "_astro/site.ABCDEFGH.css").write_text(
                "body { background: url('/_astro/bg.AAAAAAAA.png') }\n"
            )
        paths = [self.after / "_astro" / name for name in names]
        first, second = (path.read_bytes() for path in paths)
        paths[0].write_bytes(second)
        paths[1].write_bytes(first)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(
            [
                (item["kind"], item["target"])
                for item in self.findings(report, "assets")
            ],
            [("assets", f"_astro/{name}") for name in names],
        )

    def test_avif_color_signalling_is_material_but_equal_render_is_cosmetic(
        self,
    ) -> None:
        source = FIXTURES / "rendering"
        name = "banner.AAAAAAAA.avif"
        for side in (self.before, self.after):
            shutil.copyfile(source / "primaries-1.avif", side / "_astro" / name)
            shutil.copyfile(
                source / "primaries-1.avif", side / "_astro/banner.BBBBBBBB.avif"
            )
            self.html(side, "</body>", f'<img src="/_astro/{name}"></body>')
        target = self.after / "_astro" / name
        shutil.copyfile(source / "primaries-9.avif", target)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(
            [
                (item["kind"], item["target"])
                for item in self.findings(report, "assets")
            ],
            [("assets", f"_astro/{name}")],
        )
        self.assertTrue(self.findings(report, "image_pixels"))
        shutil.copyfile(source / "reencoded-same-color.avif", target)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "assets"))
        self.assertFalse(self.findings(report, "image_pixels"))
        target.write_bytes(
            (source / "primaries-1.avif").read_bytes()
            + struct.pack(">I", 16)
            + b"free"
            + b"\0" * 8
        )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "assets"))
        self.assertFalse(self.findings(report, "image_pixels"))

    def test_animated_webp_loop_change_is_material(self) -> None:
        source = FIXTURES / "rendering"
        name = "recording.AAAAAAAA.webp"
        for side in (self.before, self.after):
            shutil.copyfile(source / "loop-0.webp", side / "_astro" / name)
            shutil.copyfile(
                source / "loop-0.webp", side / "_astro/recording.BBBBBBBB.webp"
            )
            self.html(side, "</body>", f'<img src="/_astro/{name}"></body>')
        shutil.copyfile(source / "loop-1.webp", self.after / "_astro" / name)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(
            [
                (item["kind"], item["target"])
                for item in self.findings(report, "assets")
            ],
            [("assets", f"_astro/{name}")],
        )
        self.assertTrue(self.findings(report, "image_pixels"))

    def test_exact_group_equal_pixel_reencodes_remain_cosmetic(self) -> None:
        for side, level in ((self.before, 6), (self.after, 0)):
            for name, color in (
                ("group.AAAAAAAA.png", (10, 20, 30)),
                ("group.BBBBBBBB.png", (40, 50, 60)),
            ):
                png(side / "_astro" / name, color, level=level)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["verdict"], "COSMETIC")
        self.assertFalse(self.findings(report, "assets"))

    def test_identical_truncated_image_in_group_skips_decode(self) -> None:
        for side in (self.before, self.after):
            png(side / "_astro/group.AAAAAAAA.png", (10, 20, 30))
            shutil.copyfile(
                FIXTURES / "rendering/truncated.png",
                side / "_astro/group.BBBBBBBB.png",
            )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["verdict"], "IDENTICAL")

    def test_multi_file_asset_group_hash_renames_are_cosmetic(self) -> None:
        folder = self.before / "_astro"
        png(folder / "group.ABCDEFGH.png", (10, 20, 30))
        png(folder / "group.BCDEFGHI.png", (20, 30, 40))
        shutil.copyfile(
            folder / "group.ABCDEFGH.png", self.after / "_astro/group.CDEFGHIJ.png"
        )
        shutil.copyfile(
            folder / "group.BCDEFGHI.png", self.after / "_astro/group.DEFGHIJK.png"
        )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "assets"))
        self.assertTrue(
            any(
                item["kind"] == "assets"
                and item.get("normalization") == "asset hash filename"
                for item in report["checks"]
            )
        )

    def test_inline_css_change_is_material(self) -> None:
        for side in (self.before, self.after):
            self.html(side, "</head>", "<style>body { color: red; }</style></head>")
        self.html(self.after, "color: red", "color: blue")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "inline_styles"))

    def test_social_image_metadata_checks_local_pixels(self) -> None:
        for side in (self.before, self.after):
            png(side / "_astro/social.ABCDEFGH.png", (10, 20, 30), width=4, height=4)
            png(side / "_astro/social.BCDEFGHI.png", (10, 20, 30), width=2, height=2)
            self.html(
                side,
                "</head>",
                '<link rel="canonical" href="https://example.test/"><meta property="og:image" content="https://example.test/_astro/social.ABCDEFGH.png"><meta property="twitter:image" content="https://example.test/_astro/social.ABCDEFGH.png"></head>',
            )
        self.html(self.after, "social.ABCDEFGH.png", "social.BCDEFGHI.png")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(self.findings(report, "metadata"))
        self.assertTrue(self.findings(report, "metadata_image_pixels"))

    def test_inline_script(self) -> None:
        self.html(self.after, "window.parity = 1", "window.parity = 2")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.findings(report, "inline_scripts"))

    def test_missing_stylesheet_and_script_references_are_material(self) -> None:
        for old, new in (
            ("site.ABCDEFGH.css", "site.ZZZZZZZZ.css"),
            ("app.ABCDEFGH.js", "app.ZZZZZZZZ.js"),
        ):
            with self.subTest(resource=new):
                shutil.copyfile(FIXTURES / "base/index.html", self.after / "index.html")
                self.html(self.after, old, new)
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(self.findings(report, "resources"))

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

    def test_pagefind_fragment_distinct_asset_sources_are_material(self) -> None:
        self.pagefind("ordered")
        marker = b"pagefind_dcd"
        for side, name in (
            (self.before, "header_2017.AAAAAAAA.png"),
            (self.after, "header_2020.BBBBBBBB.png"),
        ):
            path = side / "pagefind/fragment/a.pf_fragment"
            fragment = json.loads(gzip.decompress(path.read_bytes())[len(marker) :])
            fragment["image"] = f"/_astro/{name}"
            path.write_bytes(
                gzip.compress(marker + json.dumps(fragment).encode(), mtime=0)
            )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "pagefind_fragment"))

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

    def test_jpeg_orientation_and_icc_change_are_material(self) -> None:
        for side in (self.before, self.after):
            self.html(side, "</body>", '<img src="/photo.jpg"></body>')
        original = (self.before / "photo.jpg").read_bytes()
        exif = bytes.fromhex(
            "ffe100224578696600004d4d002a00000008000101120003000000010006000000000000"
        )
        icc_payload = b"ICC_PROFILE\x00\x01\x01different-profile"
        icc = b"\xff\xe2" + struct.pack(">H", len(icc_payload) + 2) + icc_payload
        for segment in (exif, icc):
            with self.subTest(segment=segment[:2].hex()):
                (self.after / "photo.jpg").write_bytes(
                    original[:2] + segment + original[2:]
                )
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(self.findings(report, "image_pixels"))

    def test_png_color_chunks_affect_content_and_og_pixels(self) -> None:
        for kind, payload in (
            (b"gAMA", struct.pack(">I", 33333)),
            (b"cICP", bytes((9, 13, 0, 1))),
        ):
            with self.subTest(chunk=kind):
                shutil.copyfile(self.before / "image.png", self.after / "image.png")
                for side in (self.before, self.after):
                    png(side / "og.png", (253, 245, 230))
                add_png_chunk(self.after / "image.png", kind, payload)
                add_png_chunk(self.after / "og.png", kind, payload)
                result, report = self.run_parity()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(self.findings(report, "image_pixels"))
                self.assertTrue(self.findings(report, "og_pixels"))

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

    def test_second_title_text_is_compared(self) -> None:
        for side in (self.before, self.after):
            self.html(side, "</head>", "<title>Second</title></head>")
        self.html(self.after, "<title>Second</title>", "<title>Changed</title>")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "title"))

    def test_ledger_is_directional_and_rejects_stale_entries(self) -> None:
        self.html(self.after, "<title>Start</title>", "<title>Changed</title>")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1)
        finding = self.findings(report, "title")[0]
        ledger = self.folder / "ledger.json"
        ledger.write_text(json.dumps({finding["fingerprint"]: "fixture title"}))
        result, report = self.run_parity("--accept", str(ledger), reverse=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "title"))
        self.html(self.after, "<title>Changed</title>", "<title>Start</title>")
        result, report = self.run_parity("--accept", str(ledger))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(report)

    def test_accepted_title_does_not_hide_other_page_change(self) -> None:
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
        self.html(self.after, "before <em>after</em>", "<em>before after</em>")
        result, report = self.run_parity("--accept", str(ledger))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "structure"))
        self.assertTrue(self.findings(report, "title"))

    def test_rejects_malformed_ledger_and_decode_errors_as_errors(self) -> None:
        ledger = self.folder / "ledger.json"
        ledger.write_text("[]")
        result, report = self.run_parity("--accept", str(ledger))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(report)
        (self.after / "pagefind/pagefind.en_0.pf_meta").write_bytes(b"invalid CBOR")
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(report)

    def test_removed_known_noise_flag_is_usage_error(self) -> None:
        result, report = self.run_parity("--known-noise", "unused.json")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(report)

    def test_scoped_style_attribute_is_not_deleted(self) -> None:
        self.html(self.after, "<p>before", '<p data-astro-cid-example="">before')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "attributes"))

    def test_build_clock_and_island_uid_are_not_masked(self) -> None:
        for side in (self.before, self.after):
            self.html(
                side,
                "</body>",
                '<p>Build time: 2025-01-01T00:00:00Z</p><astro-island uid="one"></astro-island></body>',
            )
        self.html(self.after, "2025-01-01", "2026-01-01")
        self.html(self.after, 'uid="one"', 'uid="two"')
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "text"))
        self.assertTrue(self.findings(report, "attributes"))

    def test_rss_last_build_date_is_compared(self) -> None:
        for side in (self.before, self.after):
            path = side / "rss.xml"
            path.write_text(
                path.read_text().replace(
                    "<title>Feed</title>",
                    "<title>Feed</title><lastBuildDate>Tue, 20 Oct 2026 00:00:00 GMT</lastBuildDate>",
                )
            )
        path = self.after / "rss.xml"
        path.write_text(path.read_text().replace("20 Oct", "21 Oct"))
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "rss"))

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
        self.assertFalse(self.findings(report, "resources"))

    def test_fetched_page_loaded_css_swap_is_material(self) -> None:
        other = "site.ZZZZZZZZ.css"
        for side in (self.before, self.after):
            (side / "_astro" / other).write_text("body { color: red; }\n")
        self.html(self.after, "site.ABCDEFGH.css", other)
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(
            [
                (item["kind"], item["target"])
                for item in self.findings(report, "resources")
            ],
            [("resources", "/")],
        )

    def test_fetched_relative_stylesheet_swap_ignores_alias_order(self) -> None:
        css = (
            '@font-face { font-family: P; font-style: normal; font-weight: 400; src: url("/_astro/fonts/normal.12345678.woff2"); }\n'
            '@font-face { font-family: P; font-style: italic; font-weight: 400; src: url("/_astro/fonts/italic.87654321.woff2"); }\n'
        )
        for side in (self.before, self.after):
            (side / "_astro/site.ABCDEFGH.css").write_text(css)
            styles = side / "styles"
            styles.mkdir()
            (styles / "a.css").write_text("body { color: #000; }\n")
            (styles / "b.css").write_text("body { color: red; }\n")
            self.html(
                side,
                "</head>",
                '<link rel="stylesheet" href="styles/a.css"></head>',
            )
            other = side / "other"
            other.mkdir()
            (other / "index.html").write_text(
                '<!doctype html><html lang="en"><head><title>Other</title><link rel="stylesheet" href="/styles/b.css"></head><body><p>x</p></body></html>'
            )
        self.html(self.after, 'href="styles/a.css"', 'href="styles/b.css"')
        fingerprints = set()
        for seed in range(12):
            result, report = self.run_parity(
                "--fetched", env={**os.environ, "PYTHONHASHSEED": str(seed)}
            )
            self.assertEqual(result.returncode, 1, (seed, result.stderr))
            resources = self.findings(report, "resources")
            self.assertEqual(
                [(item["kind"], item["target"]) for item in resources],
                [("resources", "/")],
            )
            fingerprints.add(resources[0]["fingerprint"])
        self.assertEqual(len(fingerprints), 1)

    def test_fetched_subset_of_asset_group_skips_unfetched_file(self) -> None:
        css = (
            '@font-face { font-family: P; font-style: normal; font-weight: 400; src: url("/_astro/fonts/normal.12345678.woff2"); }\n'
            '@font-face { font-family: P; font-style: italic; font-weight: 400; src: url("/_astro/fonts/italic.87654321.woff2"); }\n'
        )
        for side in (self.before, self.after):
            (side / "_astro/site.ABCDEFGH.css").write_text(css)
        (self.before / "_astro/app.ZZZZZZZZ.js").write_text("window.other = 1;\n")
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "assets"))

    def test_added_resource_fingerprint_ignores_hash_only_rename(self) -> None:
        old, new = "extra.AAAAAAAA.js", "extra.ZZZZZZZZ.js"
        path = self.after / "_astro" / old
        path.write_text("window.extra = 1;\n")
        self.html(
            self.after, "</head>", f'<script src="/_astro/{old}"></script></head>'
        )
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        first = self.findings(report, "resources")[0]["fingerprint"]
        path.rename(self.after / "_astro" / new)
        self.html(self.after, old, new)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(self.findings(report, "resources")[0]["fingerprint"], first)

    def test_static_page_loaded_font_reference_swap_is_material(self) -> None:
        old, new = "site.ABCDEFGH.css", "site.ZZZZZZZZ.css"
        css = '@font-face { src: url("/_astro/fonts/normal.12345678.woff2"); }\n'
        for side in (self.before, self.after):
            (side / "_astro" / old).write_text(css)
            (side / "_astro" / new).write_text(
                css.replace("normal.12345678", "italic.87654321")
            )
        self.html(self.after, old, new)
        result, report = self.run_parity()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(
            [
                (item["kind"], item["target"])
                for item in self.findings(report, "resources")
            ],
            [("resources", "/")],
        )

    def test_fetched_font_preload_byte_drift_uses_font_roles(self) -> None:
        self.prepare_fonts(False)
        for side, name in (
            (self.before, "normal.12345678.woff2"),
            (self.after, "normal.ABCDEFGH.woff2"),
        ):
            self.html(
                side,
                "</head>",
                f'<link rel="preload" as="font" href="/_astro/fonts/{name}"></head>',
            )
        font = self.after / "_astro/fonts/normal.ABCDEFGH.woff2"
        payload = bytearray(font.read_bytes() + b"\0")
        payload[8:12] = len(payload).to_bytes(4, "big")
        font.write_bytes(payload)
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "resources"))
        self.assertFalse(self.findings(report, "font_roles"))

    def test_fetched_inline_font_references_use_one_placeholder(self) -> None:
        self.prepare_fonts(False)
        for side, name in (
            (self.before, "normal.12345678.woff2"),
            (self.after, "normal.ABCDEFGH.woff2"),
        ):
            self.html(
                side,
                "</head>",
                f'<style>@font-face{{font-family:Parity;font-style:normal;font-weight:400;src:url("/_astro/fonts/{name}")}}</style></head>',
            )
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.findings(report, "inline_styles"))

    def test_fetched_subset_skips_images_not_downloaded(self) -> None:
        self.prepare_fonts(False)
        for side in (self.before, self.after):
            self.html(
                side,
                "</head>",
                '<link rel="canonical" href="https://example.test/"><meta property="og:image" content="https://example.test/image.png"></head>',
            )
        for name in ("image.png", "variant.png"):
            (self.after / name).unlink()
        result, report = self.run_parity("--fetched")
        self.assertEqual(
            result.returncode,
            0,
            [
                (item["kind"], item["target"])
                for item in report.get("checks", [])
                if item["classification"] == "material"
            ],
        )
        self.assertFalse(self.findings(report, "metadata_image_pixels"))
        self.assertFalse(self.findings(report, "image_pixels"))

    def test_fetched_subset_requires_linked_stylesheet(self) -> None:
        self.prepare_fonts(False)
        self.html(self.after, "site.ABCDEFGH.css", "site.ZZZZZZZZ.css")
        result, report = self.run_parity("--fetched")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(self.findings(report, "resources"))

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


class ParallelParitySuite(unittest.TestSuite):
    def run(
        self, result: unittest.TestResult, debug: bool = False
    ) -> unittest.TestResult:
        if debug or result.failfast:
            return super().run(result, debug=debug)

        def execute(case: unittest.TestCase) -> unittest.TestResult:
            local = unittest.TestResult()
            case.run(local)
            return local

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(8, os.cpu_count() or 1)
        ) as workers:
            outcomes = list(workers.map(execute, self))
        for local in outcomes:
            result.testsRun += local.testsRun
            for field in (
                "failures",
                "errors",
                "skipped",
                "expectedFailures",
                "unexpectedSuccesses",
            ):
                getattr(result, field).extend(getattr(local, field))
        return result


def load_tests(
    loader: unittest.TestLoader, standard_tests: unittest.TestSuite, pattern: str | None
) -> unittest.TestSuite:
    def cases(suite: unittest.TestSuite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from cases(test)
            else:
                yield test

    return ParallelParitySuite(cases(standard_tests))


if __name__ == "__main__":
    unittest.main()
