"""Tests for metadata shared by sampler report modes."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from argparse import Namespace

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_common import (  # noqa: E402
    format_image_header, print_report_header, report_context,
)


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

    def test_image_header_escapes_name_and_includes_decoded_dimensions(self):
        self.assertEqual(
            format_image_header("reference\n.png", 40, 30),
            r"image: reference\u000a.png  40x30",
        )

    def test_plain_text_header_includes_requested_region(self):
        args = Namespace(x=3, y=5, width=7, height=2)
        output = StringIO()

        with redirect_stdout(output):
            print_report_header("reference.png: 40x30", args)

        self.assertEqual(output.getvalue(),
                         "reference.png: 40x30\nregion (3, 5) 7x2:\n")


if __name__ == "__main__":
    unittest.main()
