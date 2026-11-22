"""A post keeps its diagram sources readable when the browser blocks the CDN."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BROWSE = ROOT / ".claude/skills/verify-blog/scripts/browse.py"


class MermaidFallbackTest(unittest.TestCase):
    def test_blocked_cdn_marks_the_sources_and_handles_the_import_error(self) -> None:
        script = subprocess.check_output(
            ["bun", "build", "src/scripts/mermaid.ts", "--target=browser"],
            cwd=ROOT,
            text=True,
        )
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / "post.html"
            page.write_text(
                """<meta http-equiv="Content-Security-Policy" content="script-src 'unsafe-inline'">
                <pre><code class="language-mermaid">graph TD; A-->B</code></pre>
                <pre><code class="language-mermaid">graph LR; C-->D</code></pre>
                <script>addEventListener('unhandledrejection', () => document.body.dataset.rejected = 'yes')</script>
                """
                + f'<script type="module">{script}</script>',
                encoding="utf-8",
            )
            out = Path(folder) / "evidence"
            run = subprocess.run(
                [
                    "uv",
                    "run",
                    "--quiet",
                    str(BROWSE),
                    page.as_uri(),
                    "--out",
                    str(out),
                    "--step",
                    (
                        "eval:[...document.querySelectorAll('pre.mermaid-error > code')]"
                        ".map(block => block.textContent)"
                    ),
                    "--step",
                    "eval:document.body.hasAttribute('data-rejected')",
                ],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            if "Chromium did not start" in run.stderr and not os.environ.get("CI"):
                self.skipTest(run.stderr.strip())
            self.assertEqual(run.returncode, 0, run.stderr)
            state = json.loads((out / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [value["result"] for value in state["evaluations"]],
                [["graph TD; A-->B", "graph LR; C-->D"], False],
            )
