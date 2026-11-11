"""Per-channel over-tolerance counts for the fidelity comparison tool."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_metrics import Image  # noqa: E402
from tools.fidelity_pixels import channel_counts  # noqa: E402
from tools import fidelity  # noqa: E402

COUNT_LINE = "channel differing pixels (R, G, B, A): "


class TestChannelCounts(unittest.TestCase):
    """Test per-channel counts of differing pixels."""
    def test_distinct_channels_count_their_own_pixels(self):
        ref = Image(2, 1, bytes(6))
        cand = Image(2, 1, bytes([30, 10, 5, 0, 20, 40]))
        self.assertEqual(channel_counts(cand, ref, 9),
                         {"r": 1, "g": 2, "b": 1, "a": 0})

    def test_one_pixel_counted_in_multiple_channels(self):
        ref = Image(1, 1, bytes(3))
        cand = Image(1, 1, bytes([30, 30, 0]))
        self.assertEqual(channel_counts(cand, ref, 0), {"r": 1, "g": 1, "b": 0, "a": 0})

    def test_alpha_only_mismatch_against_an_rgb_peer(self):
        ref = Image(1, 1, bytes(3))
        cand = Image(1, 1, bytes(3), bytes([10]))
        self.assertEqual(channel_counts(cand, ref, 0), {"r": 0, "g": 0, "b": 0, "a": 1})

    def test_rgb_only_peers_count_opaque_alpha_zero(self):
        ref = Image(1, 1, bytes(3))
        cand = Image(1, 1, bytes([255, 255, 255]))
        self.assertEqual(channel_counts(cand, ref, 0), {"r": 1, "g": 1, "b": 1, "a": 0})

    def test_tolerance_boundary_is_strict(self):
        ref = Image(1, 1, bytes(3))
        at_tolerance = Image(1, 1, bytes([10, 11, 12]))
        self.assertEqual(channel_counts(at_tolerance, ref, 10),
                         {"r": 0, "g": 1, "b": 1, "a": 0})
        one_above = Image(1, 1, bytes([11, 12, 13]))
        self.assertEqual(channel_counts(one_above, ref, 10),
                         {"r": 1, "g": 1, "b": 1, "a": 0})

    def test_tolerance_255_counts_nothing(self):
        ref = Image(1, 1, bytes(3))
        cand = Image(1, 1, bytes([255, 255, 255]), bytes([0]))
        self.assertEqual(channel_counts(cand, ref, 255),
                         {"r": 0, "g": 0, "b": 0, "a": 0})

    def test_identical_images_count_nothing(self):
        image, png = rgb_image(3, 2, lambda x, y: (x * 40, y * 40, 7))
        self.assertEqual(channel_counts(image, image, 0),
                         {"r": 0, "g": 0, "b": 0, "a": 0})


class TestChannelCountsCli(FidelityCliTestCase):
    """Test channel-count output and crop handling in the CLI."""
    def _run_altered_pair(self, *args: str):
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)
        return self._run(candidate, altered, *args)

    def test_json_counts_and_text_agree(self):
        text = self._run_altered_pair("--max-mae", "2", "--channel-counts")
        self._assert_pass(text)
        counts = {"r": 0, "g": 1, "b": 0, "a": 0}
        self.assertIn(COUNT_LINE + "0 1 0 0", text.stdout)
        lines = text.stdout.splitlines()
        self.assertIn(COUNT_LINE + "0 1 0 0", lines[-2])
        self.assertTrue(lines[-1].startswith("PASS:"), lines[-1])
        data = json.loads(self._run_altered_pair(
            "--max-mae", "2", "--channel-counts", "--json").stdout)
        self.assertEqual(data["channel_counts"], counts)

    def test_fail_keeps_exit_one_and_still_counts(self):
        result = self._run_altered_pair("--channel-counts")
        self._assert_fail(result)
        self.assertIn(COUNT_LINE + "0 1 0 0", result.stdout.splitlines()[-2])

    def test_nonzero_origins_exclude_mismatches_outside_the_regions(self):
        # Only pixel (1, 0) of the candidate differs (red 10 vs black); the
        # reference is four black pixels. Windows that avoid x=1 must count
        # nothing even though the pair as a whole has a mismatch.
        _, candidate = rgb_image(
            4, 1, lambda x, y: (10 if x == 1 else 0, 0, 0))
        reference = make_png(4, 1, [bytes(12)])
        whole = self._run_png_pair(candidate, reference, "--channel-counts", "--json")
        self.assertEqual(json.loads(whole.stdout)["channel_counts"],
                         {"r": 1, "g": 0, "b": 0, "a": 0})
        avoided = self._run_png_pair(candidate, reference, "--channel-counts",
                                     "--json", "--candidate-crop", "2,0,2,1",
                                     "--crop", "2,0,2,1")
        self.assertEqual(json.loads(avoided.stdout)["channel_counts"],
                         {"r": 0, "g": 0, "b": 0, "a": 0})
        self.assertEqual(avoided.returncode, 0, avoided.stderr)

    def test_default_omits_counts_and_skips_the_helper(self):
        text = self._run_altered_pair("--max-mae", "2")
        self._assert_pass(text)
        self.assertNotIn(COUNT_LINE, text.stdout)
        with mock.patch.object(fidelity, "channel_counts") as helper:
            no_flag = self._run_altered_pair("--max-mae", "2", "--json")
        self.assertNotIn("channel_counts", json.loads(no_flag.stdout))
        helper.assert_not_called()

    def test_direct_script_invocation_succeeds(self):
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)
        result = self._run_script(candidate, altered,
                                  "--max-mae", "2", "--channel-counts", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["channel_counts"],
                         {"r": 0, "g": 1, "b": 0, "a": 0})

    def test_read_and_size_errors_with_the_flag_return_two_silently(self):
        tmp = self._tmp_dir()
        candidate, _ = self._write_altered_pair(tmp)
        missing = self._run(candidate, self._write(tmp, "nope.png", b"not a png"),
                            "--channel-counts")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        _, narrow = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        _, wide = rgb_image(3, 1, lambda x, y: (0, 0, 0))
        size_error = self._run_png_pair(narrow, wide, "--channel-counts")
        self.assertEqual(size_error.returncode, 2)
        self.assertEqual(size_error.stdout, "")


if __name__ == "__main__":
    unittest.main()
