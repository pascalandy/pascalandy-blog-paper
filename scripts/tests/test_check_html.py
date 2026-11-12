"""Metadata validation protects emitted pages and advertised local resources."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_html import problems


class HtmlTests(unittest.TestCase):
    def test_valid_pages_and_external_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            (dist / "index.html").write_text(
                '<title>Home</title><link rel="canonical" href="https://elsewhere.test/original"><h1>Home</h1><a href="/">Home</a>'
            )
            (dist / "robots.txt").write_text(
                "Sitemap: https://example.test/sitemap.xml"
            )
            (dist / "sitemap.xml").touch()
            self.assertEqual(problems(dist, "https://example.test"), [])

    def test_broken_metadata_names_each_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            (
                dist / "index.html"
            ).write_text("""<title>Repeated</title><h1>A</h1><h1>B</h1>
<meta name="theme-color" content=""><div class="false"></div>
<link rel="alternate" href="/missing.xml"><a href="/blog">Blog</a>
<script type="application/ld+json">{"@type":"BlogPosting","datePublished":"undefined"}</script>
<script type="application/ld+json">bad</script>""")
            (dist / "404.html").write_text(
                '<title>Repeated</title><link rel="canonical" href="/404/">'
            )
            (dist / "robots.txt").write_text(
                "Sitemap: https://example.test/missing.xml"
            )
            errors = "\n".join(problems(dist, "https://example.test"))
            for expected in (
                "duplicate title",
                "H1",
                "empty meta",
                '"false"',
                "target missing",
                "trailing slash",
                "ISO datePublished",
                "invalid JSON-LD",
                "only on posts",
                "noindex",
            ):
                self.assertIn(expected, errors)
