"""Signed per-channel mean error diagnostics for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools.fidelity_metrics import Image  # noqa: E402
from tools.fidelity_pixels import channel_bias  # noqa: E402
from tools import fidelity  # noqa: E402

BIAS_LINE = "channel bias (candidate - reference): "


class TestChannelBias(unittest.TestCase):
    def test_signed_fractional_and_cancelling_means(self):
        reference = Image(2, 1, bytes(6))
        candidate = Image(2, 1, bytes([1, 0, 0, 0, 3, 0]))
        self.assertEqual(channel_bias(candidate, reference),
                         {"r": 0.5, "g": 1.5, "b": 0.0, "a": 0.0})
        self.assertEqual(channel_bias(reference, candidate)["r"], -0.5)
        opposite = Image(2, 1, bytes([1, 0, 0, 0, 0, 0]))
        peer = Image(2, 1, bytes([0, 0, 0, 1, 0, 0]))
        self.assertEqual(channel_bias(peer, opposite)["r"], 0.0)
        self.assertEqual(channel_bias(reference, reference),
                         {"r": 0.0, "g": 0.0, "b": 0.0, "a": 0.0})

    def test_extrema_and_alpha_missing_means_opaque(self):
        black = Image(1, 1, bytes(3), bytes([0]))
        white = Image(1, 1, bytes([255, 255, 255]), bytes([255]))
        self.assertEqual(channel_bias(white, black), {"r": 255.0, "g": 255.0, "b": 255.0, "a": 255.0})
        self.assertEqual(channel_bias(black, white), {"r": -255.0, "g": -255.0, "b": -255.0, "a": -255.0})
        rgb = Image(1, 1, bytes(3))
        self.assertEqual(channel_bias(rgb, black)["a"], 255.0)
        self.assertEqual(channel_bias(black, rgb)["a"], -255.0)
        alpha_only = Image(1, 1, bytes(3), bytes([10]))
        self.assertEqual(channel_bias(alpha_only, rgb)["a"], -245.0)
        self.assertEqual(channel_bias(rgb, alpha_only)["a"], 245.0)


class TestChannelBiasCli(FidelityCliTestCase):
    def _run_altered_pair(self, *args: str):
        candidate, reference = self._write_altered_pair(self._tmp_dir())
        return self._run(candidate, reference, *args)

    def test_text_json_and_channel_count_outputs_agree(self):
        args = ("--max-mae", "2", "--channel-bias", "--channel-counts")
        text = self._run_altered_pair(*args)
        self._assert_pass(text)
        self.assertIn('channel bias (candidate - reference): {"r": 0.0, "g": -5.555555555555555, "b": 0.0, "a": 0.0}', text.stdout)
        data = json.loads(self._run_altered_pair(*args, "--json").stdout)
        self.assertEqual(data["channel_bias"]["g"], -50 / 9)
        self.assertIn("channel_counts", data)

    def test_text_json_agree_and_flag_does_not_change_fail_or_budget_pass(self):
        tmp = self._tmp_dir()
        reference = make_png(2, 1, [bytes(6)])
        candidate = make_png(2, 1, [bytes([2, 0, 0, 0, 0, 0])])
        cpath = self._write(tmp, "candidate.png", candidate)
        rpath = self._write(tmp, "reference.png", reference)
        text = self._run(cpath, rpath, "--channel-bias")
        self._assert_fail(text)
        bias = {"r": 1.0, "g": 0.0, "b": 0.0, "a": 0.0}
        self.assertEqual(json.loads(text.stdout.split(BIAS_LINE, 1)[1].splitlines()[0]), bias)
        data = json.loads(self._run(cpath, rpath, "--channel-bias", "--json").stdout)
        self.assertEqual(data["channel_bias"], bias)
        passing = self._run(cpath, rpath, "--channel-bias", "--max-mae", "1", "--json")
        self.assertEqual(passing.returncode, 0)
        self.assertEqual(json.loads(passing.stdout)["channel_bias"], bias)

    def test_crops_tolerance_composition_and_default_omission(self):
        _, candidate = rgb_image(4, 2, lambda x, y: (100 if (x, y) == (1, 0) else 0, 0, 0))
        reference = make_png(4, 2, [bytes(12), bytes(12)])
        cropped = self._run_png_pair(candidate, reference, "--channel-bias", "--json",
                                     "--candidate-crop", "2,1,2,1", "--crop", "1,1,2,1")
        self.assertEqual(json.loads(cropped.stdout)["channel_bias"]["r"], 0.0)
        at_zero = self._run_png_pair(candidate, reference, "--channel-bias", "--json")
        at_max = self._run_png_pair(candidate, reference, "--channel-bias", "--json", "--tolerance", "255")
        self.assertEqual(json.loads(at_zero.stdout)["channel_bias"], json.loads(at_max.stdout)["channel_bias"])
        combined = self._run_png_pair(candidate, reference, "--channel-bias", "--channel-counts", "--json")
        self.assertIn("channel_counts", json.loads(combined.stdout))
        with mock.patch.object(fidelity, "channel_bias") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("channel_bias", json.loads(ordinary.stdout))
        self.assertNotIn(BIAS_LINE, self._run_png_pair(candidate, reference).stdout)
        helper.assert_not_called()

    def test_direct_script_and_errors(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_altered_pair(tmp)
        script = self._run_script(candidate, reference, "--channel-bias", "--json")
        self.assertEqual(script.returncode, 1)
        self.assertIn("channel_bias", json.loads(script.stdout))
        bad = self._run(candidate, self._write(tmp, "missing.png", b"bad"), "--channel-bias")
        self.assertEqual((bad.returncode, bad.stdout), (2, ""))
        _, narrow = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        _, wide = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        mismatch = self._run_png_pair(narrow, wide, "--channel-bias")
        self.assertEqual((mismatch.returncode, mismatch.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
