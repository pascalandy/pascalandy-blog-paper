"""The image guard sees frontmatter, code, CSS, public paths, and drafts."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_images import inspect, problems


class ImageTests(unittest.TestCase):
    def test_real_reference_forms_keep_images_and_missing_or_orphan_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            images = root / "src/assets/images"
            images.mkdir(parents=True)
            for name in (
                "front.jpg",
                "import.png",
                "draft.webp",
                "style.gif",
                "reference.png",
                "html.svg",
            ):
                (images / name).write_bytes(b"image fixture")
            blog = root / "src/data/blog"
            blog.mkdir(parents=True)
            (blog / "post.md").write_text("""---
ogImage: ../../assets/images/front.jpg
---

[Open image][photo]
[photo]: ../../assets/images/reference.png

<img src="/public-image.jpg">

```md
![Example](./not-an-actual-image.jpg)
```
""")
            (blog / "_draft.md").write_text("""---
draft: true
---
![Draft](@/assets/images/draft.webp)""")
            (root / "src/component.astro").write_text("""---
import picture from "@/assets/images/import.png";
// A comment naming "not-an-actual-image.jpg" is not a reference.
---
<img src="./assets/images/html.svg">
""")
            (root / "src/style.css").write_text(
                'div { background: url("./assets/images/style.gif"); }'
            )
            (root / "public").mkdir()
            (root / "public/public-image.jpg").write_bytes(b"public fixture")
            self.assertEqual(problems(root), [])
            (images / "unreferenced.jpg").write_bytes(b"orphan")
            self.assertIn(
                "unreferenced image: src/assets/images/unreferenced.jpg",
                problems(root),
            )
            (images / "unreferenced.jpg").unlink()
            self.assertEqual(problems(root), [])
            (images / "front.jpg").unlink()
            errors = problems(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing image ../../assets/images/front.jpg", errors[0])

    def test_generated_image_route_and_remote_images_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src/pages").mkdir(parents=True)
            (root / "src/pages/og.png.ts").write_text(
                "export const GET = () => new Response();"
            )
            (root / "src/page.astro").write_text(
                '<img src="/og.png"><img src="https://example.test/remote.png">'
            )
            self.assertEqual(inspect(root), ([], []))
