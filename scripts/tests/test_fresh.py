"""Fresh builds preserve fonts and browser receipts but discard generated files."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fresh import clear


class FreshTests(unittest.TestCase):
    def test_preserves_only_named_caches_and_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            keep = ("cache/fonts/nested/font.bin", "cache/verify-blog/run/proof.png")
            discard = (
                "cache/assets/nested/image.webp",
                "cache/data-store.json",
                "public/pagefind/search.js",
                "dist/index.html",
                ".astro/content.json",
            )
            for name in (*keep, *discard):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(name)
            listed = clear(root, dry_run=True)
            self.assertIn(root / "public/pagefind", listed)
            for name in (*keep, *discard):
                self.assertEqual((root / name).read_text(), name)
            clear(root)
            for name in keep:
                self.assertEqual((root / name).read_text(), name)
            for name in discard:
                self.assertFalse((root / name).exists())
            self.assertEqual(clear(root), [])

    def test_unlinks_output_symlinks_without_touching_their_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            outside = Path(temporary) / "outside"
            outside.mkdir()
            (outside / "sentinel").write_text("keep")
            (root / "dist").symlink_to(outside, target_is_directory=True)
            clear(root)
            self.assertEqual((outside / "sentinel").read_text(), "keep")
            self.assertFalse((root / "dist").is_symlink())
