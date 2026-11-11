"""Tests for metadata shared by sampler report modes."""

from __future__ import annotations

import unittest
from argparse import Namespace

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_common import report_context  # noqa: E402


class TestReportContext(unittest.TestCase):
    """The shared report context's source and region fields."""

    def test_context_contains_source_dimensions_and_requested_region(self):
        args = Namespace(image="reference.png", x=3, y=5, width=7, height=2)

        self.assertEqual(report_context(args, 40, 30), {
            "image": "reference.png",
            "image_width": 40,
            "image_height": 30,
            "region": {"x": 3, "y": 5, "width": 7, "height": 2},
        })


if __name__ == "__main__":
    unittest.main()
