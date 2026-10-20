"""Exercise screenshot attribution through the shots CLI."""

import json
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / ".claude/skills/verify-blog/scripts/shots.py"


def write_png(path: Path, changed_pixel: tuple[int, int] | None = None) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload))
        )

    pixels = bytearray()
    for y in range(10):
        pixels.append(0)
        for x in range(10):
            pixels.extend((255, 0, 0) if (x, y) == changed_pixel else (0, 0, 0))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 10, 10, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(pixels)))
        + chunk(b"IEND", b"")
    )


class ShotsCommandTest(unittest.TestCase):
    def test_diff_attributes_inside_and_outside_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            first = folder / "first"
            first.mkdir()
            write_png(first / "probe.png")
            shot = {
                "width": 10,
                "height": 10,
                "images": [
                    {
                        "index": 0,
                        "currentSrc": "/_astro/test.png",
                        "box": {"x": 2, "y": 2, "width": 4, "height": 4},
                    },
                    {
                        "index": 1,
                        "currentSrc": "/_astro/unchanged.png",
                        "box": {"x": 0, "y": 0, "width": 2, "height": 2},
                    },
                ],
            }
            manifest = {"failures": [], "shots": {"probe": shot}}
            (first / "manifest.json").write_text(json.dumps(manifest))
            for label, pixel, expected_inside in (
                ("inside", (3, 3), True),
                ("outside", (8, 8), False),
            ):
                with self.subTest(label=label):
                    second = folder / label
                    second.mkdir()
                    write_png(second / "probe.png", pixel)
                    (second / "manifest.json").write_text(json.dumps(manifest))
                    report = folder / f"{label}.json"
                    result = subprocess.run(
                        [
                            "uv",
                            "run",
                            "--quiet",
                            str(SHOTS),
                            "diff",
                            str(first),
                            str(second),
                            "--json",
                            str(report),
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 1, result.stderr)
                    data = json.loads(report.read_text())
                    self.assertEqual(data["compared"], 1)
                    self.assertEqual(data["changed_shots"], 1)
                    finding = data["shots"]["probe.png"]
                    self.assertEqual(finding["changed_pixels"], 1)
                    self.assertEqual(len(finding["image_boxes"]), int(expected_inside))
                    if expected_inside:
                        self.assertEqual(
                            finding["image_boxes"][0]["selected_a"],
                            "/_astro/test.png",
                        )
                        self.assertEqual(finding["image_boxes"][0]["changed_pixels"], 1)
                    self.assertEqual(
                        finding["all_changed_inside_image_boxes"], expected_inside
                    )
                    self.assertEqual(
                        finding["outside_image_pixels"], 0 if expected_inside else 1
                    )


if __name__ == "__main__":
    unittest.main()
