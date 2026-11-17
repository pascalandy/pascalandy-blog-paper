"""The content row rejects invalid posts with the schema's own messages (#94).

Each case copies the site's source into a throwaway folder, drops one fixture
post into its collection, and runs that copy's `check.py --only content`, so
Astro's real loader and Zod run while the repository's collection stays as is.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# What `astro sync` reads besides the posts
SOURCES = ("astro.config.ts", "package.json", "tsconfig.json", "scripts/check.py")

FRONTMATTER = {
    "author": "Fixture",
    "date_created": "2026-01-01",
    "title": "Fixture",
    "description": "A post the content check reads",
    "tags": "\n  - dev-notes",
}


def post(**changes: str) -> str:
    fields = {**FRONTMATTER, **changes}
    lines = "".join(f"{key}: {value}\n" for key, value in fields.items())
    return f"---\n{lines}---\n\nBody.\n"


class ContentSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not (ROOT / "node_modules").is_dir():
            raise unittest.SkipTest("dependencies are not installed; run: just install")

    def content_check(self, name: str, text: str) -> tuple[int, str, str]:
        """Run the content row on a copy whose collection holds only this post.

        Returns the exit code, stderr, and the row's full log."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        copy = Path(folder.name)
        for source in SOURCES:
            (copy / source).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / source, copy / source)
        # Posts and their images stay behind: the copy's collection is the fixture
        shutil.copytree(
            ROOT / "src",
            copy / "src",
            ignore=lambda folder, _: (
                {"data", "assets"} if Path(folder) == ROOT / "src" else set()
            ),
        )
        (copy / "node_modules").symlink_to(ROOT / "node_modules")
        blog = copy / "src" / "data" / "blog"
        blog.mkdir(parents=True)
        (blog / f"{name}.md").write_text(text, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(copy / "scripts" / "check.py"), "--only", "content"],
            cwd=copy,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        log = copy / "cache" / "check" / "content.log"
        return result.returncode, result.stderr, log.read_text(encoding="utf-8")

    def assert_rejected(self, name: str, text: str, message: str) -> None:
        code, errors, log = self.content_check(name, text)
        self.assertEqual(code, 1, f"{name}: {errors}")
        # Astro prints each issue as `  PATH: MESSAGE` on its own line, so the
        # message must fill the rest of that line: an appended word fails too
        line = re.compile(rf"^  \S+: {re.escape(message)}$", re.MULTILINE)
        self.assertRegex(errors, line, f"{name}: the failure replay lacks it")
        self.assertRegex(log, line, f"{name}: the content log lacks it")
        self.assertIn("error: content failed; rerun: just check --only content", errors)

    def test_valid_post_passes_silently(self) -> None:
        code, errors, log = self.content_check("valid", post())
        self.assertEqual((code, errors), (0, ""), log)

    def test_unknown_key_is_named(self) -> None:
        self.assert_rejected(
            "unknown-key",
            post(subtitle="not in the schema"),
            "unknown key subtitle: remove it, or add it to the schema in src/content.config.ts",
        )

    def test_unregistered_tag_is_named(self) -> None:
        self.assert_rejected(
            "unregistered-tag",
            post(tags="\n  - no-such-tag"),
            'tag "no-such-tag" is not registered: add it to TAGS in src/tags.ts',
        )

    def test_tag_outside_url_form_is_named(self) -> None:
        self.assert_rejected(
            "tag-not-url-form",
            post(tags="\n  - Dev_Notes"),
            'tag "Dev_Notes" is not in URL form: rename it to "dev-notes" in src/tags.ts'
            " and in the posts that use it",
        )


if __name__ == "__main__":
    unittest.main()
