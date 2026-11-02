"""Maximum absolute channel delta diagnostics for fidelity comparisons."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools.fidelity_pixels import channel_maxima  # noqa: E402
from tools.png import Image  # noqa: E402
from tools import fidelity  # noqa: E402


class TestChannelMaxima(unittest.TestCase):
    def test_channel_peaks_and_alpha_semantics(self):
        reference = Image(3, 1, bytes(9), bytes([0, 255, 0]))
        candidate = Image(3, 1, bytes([10, 0, 0, 0, 20, 0, 0, 0, 255]), bytes([255, 0, 0]))
        expected = {"r": 10, "g": 20, "b": 255, "a": 255}
        self.assertEqual(channel_maxima(candidate, reference), expected)
        self.assertEqual(channel_maxima(reference, candidate), expected)
        self.assertEqual(channel_maxima(Image(1, 1, bytes(3)), Image(1, 1, bytes(3))),
                         {"r": 0, "g": 0, "b": 0, "a": 0})
        self.assertEqual(channel_maxima(Image(1, 1, bytes([255, 0, 0])), Image(1, 1, bytes(3))),
                         {"r": 255, "g": 0, "b": 0, "a": 0})


class TestChannelMaximaCli(FidelityCliTestCase):
    def test_crops_tolerance_composition_and_default_omission(self):
        candidate = make_png(4, 1, [bytes([255, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])])
        reference = make_png(4, 1, [bytes(12)])
        args = ("--channel-maxima", "--candidate-crop", "1,0,2,1", "--crop", "2,0,2,1")
        output = self._run_png_pair(candidate, reference, *args)
        self._assert_fail(output)
        self.assertIn("channel maximum delta (R, G, B, A): 0 1 0 0", output.stdout)
        data = json.loads(self._run_png_pair(candidate, reference, *args, "--json").stdout)
        self.assertEqual(data["channel_maxima"], {"r": 0, "g": 1, "b": 0, "a": 0})
        tolerant = self._run_png_pair(candidate, reference, *args, "--tolerance", "255", "--json")
        self.assertEqual(json.loads(tolerant.stdout)["channel_maxima"], data["channel_maxima"])
        combined = self._run_png_pair(candidate, reference, "--channel-maxima", "--channel-counts",
                                      "--channel-bias", "--max-mae", "22", "--json")
        combined_data = json.loads(combined.stdout)
        self.assertEqual(combined.returncode, 0)
        self.assertTrue({"channel_counts", "channel_bias", "channel_maxima"} <= combined_data.keys())
        with mock.patch.object(fidelity, "channel_maxima") as helper:
            ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("channel_maxima", json.loads(ordinary.stdout))
        self.assertNotIn("channel maximum delta", self._run_png_pair(candidate, reference).stdout)
        helper.assert_not_called()

    def test_direct_script_and_errors(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_altered_pair(tmp)
        script = self._run_script(candidate, reference, "--channel-maxima", "--json")
        self.assertIn("channel_maxima", json.loads(script.stdout))
        bad = self._run(candidate, self._write(tmp, "missing.png", b"bad"), "--channel-maxima")
        self.assertEqual((bad.returncode, bad.stdout), (2, ""))
        mismatch = self._run_png_pair(make_png(1, 1, [bytes(3)]), make_png(2, 1, [bytes(6)]),
                                      "--channel-maxima")
        self.assertEqual((mismatch.returncode, mismatch.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
