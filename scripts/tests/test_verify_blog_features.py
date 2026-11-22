"""Check that verify-blog recipes use URLs accepted by Astro's preview."""

import re
import unittest
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / ".claude/skills/verify-blog/features"
URL_PATH = re.compile(r"\$URL(/[^\s\"'`<>?#)\]]*)")


class VerifyBlogFeaturesTests(unittest.TestCase):
    def test_page_urls_end_with_a_slash(self) -> None:
        missing_slashes = []
        for recipe in sorted(FEATURES.glob("*.md")):
            lines = recipe.read_text(encoding="utf-8").splitlines()
            for number, line in enumerate(lines, 1):
                for match in URL_PATH.finditer(line):
                    path = match[1]
                    if not path.endswith("/") and PurePosixPath(path).suffix in (
                        "",
                        ".",
                    ):
                        missing_slashes.append(
                            f"{recipe.relative_to(ROOT)}:{number}: {match[0]} needs a trailing /"
                        )

        if missing_slashes:
            self.fail("\n".join(missing_slashes))
