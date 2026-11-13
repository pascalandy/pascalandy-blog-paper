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
                '<html lang="fr-CA"><meta property="og:type" content="website"><meta property="og:locale" content="fr_CA"><title>Home</title><link rel="canonical" href="https://elsewhere.test/original"><h1>Home</h1><a href="/">Home</a>'
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
<meta property="og:image" content="https://example.test/_astro/deleted.jpg">
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
                "link target missing",
                "og:image target missing",
                "trailing slash",
                "ISO datePublished",
                "invalid JSON-LD",
                "only on posts",
                "noindex",
            ):
                self.assertIn(expected, errors)

    def test_post_language_and_calendar_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            text = """<html lang="en"><title>Post</title>
<link rel="canonical" href="https://example.test/">
<meta property="article:published_time" content="2020-01-15T00:00:00Z">
<meta property="og:type" content="article"><meta property="og:locale" content="en_US">
<script type="application/ld+json">{"@type":"BlogPosting","datePublished":"2020-01-15T00:00:00Z"}</script>
<time datetime="2020-01-15T00:00:00.000Z">15 janvier 2020</time>"""
            page = dist / "index.html"
            page.write_text(text)
            (dist / "robots.txt").write_text(
                "Sitemap: https://example.test/sitemap.xml"
            )
            (dist / "sitemap.xml").touch()
            source = {"/": {"lang": "en", "date_created": "2020-01-15T00:00:00Z"}}
            self.assertEqual(problems(dist, "https://example.test", source), [])
            page.write_text(
                text.replace('lang="en"', 'lang="fr-CA"').replace(
                    "15 janvier", "14 janvier"
                )
            )
            errors = "\n".join(problems(dist, "https://example.test", source))
            self.assertIn("html lang must be en", errors)
            self.assertIn("displayed date must be 15 janvier 2020", errors)

    def test_missing_post_metadata_is_detected_from_source_role(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            (dist / "index.html").write_text("""<html lang=\"fr-CA\"><title>Post</title>
<link rel=\"canonical\" href=\"https://example.test/\">
<meta property=\"og:type\" content=\"website\"><meta property=\"og:locale\" content=\"fr_CA\">
<time datetime=\"2020-01-15T00:00:00Z\">15 janvier 2020</time>""")
            (dist / "robots.txt").write_text(
                "Sitemap: https://example.test/sitemap.xml"
            )
            (dist / "sitemap.xml").touch()
            source = {"/": {"date_created": "2020-01-15T00:00:00Z"}}
            errors = "\n".join(problems(dist, "https://example.test", source))
            self.assertIn("og:type must occur once with article", errors)
            self.assertIn("BlogPosting belongs only on posts, once per post", errors)
