"""A template-only edit must reach social images on an incremental build."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


RENDER = """
import { generateOgImageForSite, generateOgImageForPost } from "./src/utils/generateOgImages";
const site = await generateOgImageForSite();
const post = await generateOgImageForPost({data: {title: "Blog", author: "Pascal"}});
console.log(JSON.stringify([site, post].map(image => Buffer.from(image).toString("base64"))));
"""


class OgImageTests(unittest.TestCase):
    def test_warm_images_match_a_clean_render_after_template_edits(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            shutil.copytree(ROOT / "src/utils", project / "src/utils")
            shutil.copy2(ROOT / "src/config.ts", project / "src/config.ts")
            shutil.copy2(ROOT / "tsconfig.json", project)
            (project / "node_modules").symlink_to(ROOT / "node_modules")
            templates = project / "src/utils/og-templates"

            def images(color: str) -> list[str]:
                for name, size in (("site", 10), ("post", 20)):
                    svg = (
                        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">'
                        f'<rect width="100%" height="100%" fill="{color}"/></svg>'
                    )
                    (templates / f"{name}.js").write_text(
                        f"export default () => {json.dumps(svg)};"
                    )
                result = subprocess.run(
                    ["bun", "-e", RENDER],
                    cwd=project,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return json.loads(result.stdout)

            original = images("red")
            warm = images("blue")
            if (project / "cache").exists():
                shutil.move(project / "cache", project / "old-cache")
            clean = images("blue")
            for name, before, after, expected in zip(
                ("site", "post"), original, warm, clean, strict=True
            ):
                with self.subTest(image=name):
                    self.assertNotEqual(before, expected)
                    self.assertEqual(after, expected)
