"""Exercise screenshot attribution through the shots CLI."""

import hashlib
import json
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / ".claude/skills/verify-blog/scripts/shots.py"


def write_png(
    path: Path, changed_pixel: tuple[int, int] | None = None, size: int = 10
) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload))
        )

    pixels = bytearray()
    for y in range(size):
        pixels.append(0)
        for x in range(size):
            pixels.extend((255, 0, 0) if (x, y) == changed_pixel else (0, 0, 0))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(pixels)))
        + chunk(b"IEND", b"")
    )


class ShotsCommandTest(unittest.TestCase):
    def test_diff_uses_capture_time_image_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            first = folder / "first"
            second = folder / "second"
            for shot in (first, second):
                shot.mkdir()
            write_png(first / "probe.png")
            write_png(second / "probe.png", (3, 3))
            first_dist = folder / "first-dist"
            second_dist = folder / "second-dist"
            for dist in (first_dist, second_dist):
                (dist / "_astro").mkdir(parents=True)
            first_image = first_dist / "_astro/test.png"
            second_image = second_dist / "_astro/test.png"
            write_png(first_image)
            write_png(second_image, (3, 3))
            first_hash = hashlib.sha256(first_image.read_bytes()).hexdigest()
            second_hash = hashlib.sha256(second_image.read_bytes()).hexdigest()

            def manifest(dist: Path, image_hash: str) -> dict:
                return {
                    "dist": str(dist),
                    "failures": [],
                    "shots": {
                        "probe": {
                            "width": 10,
                            "height": 10,
                            "images": [
                                {
                                    "index": 0,
                                    "src": "/_astro/test.png",
                                    "currentSrc": "/_astro/test.png",
                                    "sha256": image_hash,
                                    "objectFit": "cover",
                                    "objectPosition": "center",
                                    "box": {
                                        "x": 2,
                                        "y": 2,
                                        "width": 4,
                                        "height": 4,
                                    },
                                }
                            ],
                        }
                    },
                }

            (first / "manifest.json").write_text(
                json.dumps(manifest(first_dist, first_hash))
            )
            second_manifest = second / "manifest.json"

            def diff() -> dict:
                report = folder / "report.json"
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
                return json.loads(report.read_text())["shots"]["probe.png"]

            second_manifest.write_text(json.dumps(manifest(second_dist, second_hash)))
            write_png(second_image)
            changed_at_capture = diff()
            self.assertTrue(changed_at_capture["all_changed_inside_image_boxes"])
            self.assertEqual(changed_at_capture["outside_image_pixels"], 0)

            second_manifest.write_text(json.dumps(manifest(second_dist, first_hash)))
            write_png(second_image, (3, 3))
            changed_after_capture = diff()
            self.assertFalse(changed_after_capture["all_changed_inside_image_boxes"])
            self.assertEqual(changed_after_capture["outside_image_pixels"], 1)

    def test_diff_attributes_inside_and_outside_pixels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for label, pixel, bytes_change, fit, position, src, size, inside in (
                (
                    "image",
                    (3, 3),
                    True,
                    "cover",
                    "center",
                    "/_astro/test.png",
                    10,
                    True,
                ),
                (
                    "same-bytes",
                    (3, 3),
                    False,
                    "cover",
                    "center",
                    "/_astro/test.png",
                    10,
                    False,
                ),
                (
                    "same-bytes-fit",
                    (3, 3),
                    False,
                    "none",
                    "center",
                    "/_astro/test.png",
                    10,
                    False,
                ),
                ("fit", (3, 3), True, "none", "center", "/_astro/test.png", 10, False),
                (
                    "position",
                    (3, 3),
                    True,
                    "cover",
                    "left top",
                    "/_astro/test.png",
                    10,
                    False,
                ),
                (
                    "outside",
                    (8, 8),
                    True,
                    "cover",
                    "center",
                    "/_astro/test.png",
                    10,
                    False,
                ),
                (
                    "remote",
                    (3, 3),
                    True,
                    "cover",
                    "center",
                    "https://images.example/_astro/test.png",
                    10,
                    False,
                ),
                ("dpr2", (6, 6), True, "cover", "center", "/_astro/test.png", 20, True),
            ):
                with self.subTest(label=label):
                    case = folder / label
                    first = case / "first"
                    second = case / "second"
                    first.mkdir(parents=True)
                    second.mkdir()
                    write_png(first / "probe.png", size=size)
                    write_png(second / "probe.png", pixel, size=size)
                    first_dist = case / "first-dist"
                    second_dist = case / "second-dist"
                    for dist in (first_dist, second_dist):
                        (dist / "_astro").mkdir(parents=True)
                        write_png(dist / "_astro/unchanged.png")
                    write_png(first_dist / "_astro/test.png")
                    write_png(
                        second_dist / "_astro/test.png",
                        (3, 3) if bytes_change else None,
                    )

                    def state(
                        object_fit: str, object_position: str, source: str = src
                    ) -> dict:
                        return {
                            "width": 10,
                            "height": 10,
                            "images": [
                                {
                                    "index": 0,
                                    "src": source,
                                    "currentSrc": "/_astro/test.png",
                                    "objectFit": object_fit,
                                    "objectPosition": object_position,
                                    "box": {"x": 2, "y": 2, "width": 4, "height": 4},
                                },
                                {
                                    "index": 1,
                                    "src": "/_astro/unchanged.png",
                                    "currentSrc": "/_astro/unchanged.png",
                                    "objectFit": "cover",
                                    "objectPosition": "center",
                                    "box": {"x": 0, "y": 0, "width": 2, "height": 2},
                                },
                            ],
                        }

                    for shots, dist, shot in (
                        (first, first_dist, state("cover", "center")),
                        (second, second_dist, state(fit, position)),
                    ):
                        manifest = {
                            "dist": str(dist),
                            "failures": [],
                            "shots": {"probe": shot},
                        }
                        (shots / "manifest.json").write_text(json.dumps(manifest))
                    report = case / "report.json"
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
                    self.assertEqual(len(finding["image_boxes"]), int(inside))
                    if inside:
                        self.assertEqual(
                            finding["image_boxes"][0]["selected_a"],
                            "/_astro/test.png",
                        )
                        self.assertEqual(finding["image_boxes"][0]["changed_pixels"], 1)
                        self.assertNotEqual(
                            finding["image_boxes"][0]["sha256_a"],
                            finding["image_boxes"][0]["sha256_b"],
                        )
                    self.assertEqual(finding["all_changed_inside_image_boxes"], inside)
                    self.assertEqual(
                        finding["outside_image_pixels"], 0 if inside else 1
                    )


if __name__ == "__main__":
    unittest.main()
