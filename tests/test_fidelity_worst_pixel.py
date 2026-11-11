"""Source-value diagnostics for the maximum-delta fidelity pixel."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_reports import explain_worst_pixel
from tools.fidelity_metrics import Image, compare  # noqa: E402


class TestWorstPixel(FidelityCliTestCase):
    def test_rgba_delta_first_tie_and_distinct_crop_origins(self):
        # Equal maxima at source (2, 2) and (4, 2): the first one, crop-relative (1, 1), is reported.
        _, candidate_png = rgb_image(6, 3, lambda x, y: (9 if y == 2 and x in (2, 4) else 0, 0, 0))
        reference_png = make_png(7, 4, [bytes(21)] * 4)
        result = self._run_png_pair(candidate_png, reference_png,
                                    "--candidate-crop", "1,1,4,2", "--crop", "2,2,4,2",
                                    "--explain-worst", "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["worst_pixel"], {
            "position": [1, 1], "candidate_position": [2, 2], "reference_position": [3, 3],
            "candidate_rgba": [9, 0, 0, 255], "reference_rgba": [0, 0, 0, 255],
            "absolute_delta": [9, 0, 0, 0],
        })

    def test_alpha_only_against_opaque_rgb_peer_and_equal_images(self):
        candidate = Image(2, 1, bytes(6), bytes([255, 200]))
        reference = Image(2, 1, bytes(6))
        explained = explain_worst_pixel(candidate, reference, compare(candidate, reference), None, None)
        self.assertEqual(explained["position"], [1, 0])
        self.assertEqual(explained["candidate_rgba"], [0, 0, 0, 200])
        self.assertEqual(explained["reference_rgba"], [0, 0, 0, 255])
        self.assertEqual(explained["absolute_delta"], [0, 0, 0, 55])
        same = Image(1, 1, bytes([1, 2, 3]))
        self.assertEqual(explain_worst_pixel(same, same, compare(same, same), None, None)["position"], [0, 0])

    def test_text_json_pass_and_unrequested_output(self):
        _, candidate = rgb_image(1, 1, lambda x, y: (3, 0, 0))
        _, reference = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        json_result = self._run_png_pair(candidate, reference, "--max-mae", "3", "--explain-worst", "--json")
        text_result = self._run_png_pair(candidate, reference, "--max-mae", "3", "--explain-worst")
        suffix = text_result.stdout.split("worst pixel: ", 1)[1].splitlines()[0]
        self.assertEqual(json.loads(suffix), json.loads(json_result.stdout)["worst_pixel"])
        self.assertEqual(json_result.returncode, 0)
        self.assertNotIn("worst_pixel", json.loads(self._run_png_pair(candidate, reference, "--json").stdout))
        self.assertNotIn("worst pixel:", self._run_png_pair(candidate, reference).stdout)

    def test_offset_without_worst_pixels_is_refused_before_reads(self):
        # The parser's last cross-check (tools/fidelity_cli_parser.py):
        # --worst-pixel-offset pages a --worst-pixels report, so the offset
        # without its count cap is refused as a usage error that names the
        # cap. The input files do not exist, so any image read would produce
        # a read diagnostic instead; the usage-error shape proves the refusal
        # happens before reads, like the sibling offset refusals do.
        result = self._run("missing.png", "missing.png", "--worst-pixel-offset", "1")
        self._assert_usage_error(result, "--worst-pixel-offset requires --worst-pixels")
        self.assertEqual(result.stdout, "")

    def test_errors_and_direct_script(self):
        _, png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        failed = self._run_png_pair(b"not a png", png, "--explain-worst")
        self.assertEqual(failed.returncode, 2)
        self.assertEqual(failed.stdout, "")
        # Invoke the standalone entry point to cover its sibling-module imports.
        tmp = self._tmp_dir()
        candidate_path = self._write(tmp, "candidate.png", png)
        reference_path = self._write(tmp, "reference.png", png)
        script = repo_root.ROOT / "tools" / "fidelity.py"
        result = subprocess.run([sys.executable, str(script), candidate_path, reference_path,
                                 "--explain-worst", "--json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["worst_pixel"]["absolute_delta"], [0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
