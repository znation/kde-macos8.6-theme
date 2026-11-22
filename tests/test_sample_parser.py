"""Compatibility and declaration-family checks for the sampler parser."""

from __future__ import annotations

import argparse
import unittest

from support import repo_root  # noqa: F401 (puts the repository root on sys.path)
from tools.sample_lib import arguments
from tools.sample_lib import parser


class TestSampleParser(unittest.TestCase):
    def test_compatibility_entry_point_delegates_and_keeps_validation_exports(self):
        parsed = arguments.build_parser().parse_args(
            ("reference.png", "3", "4", "--histogram", "--top-colors", "2")
        )
        self.assertEqual((parsed.image, parsed.x, parsed.y), ("reference.png", 3, 4))
        self.assertTrue(parsed.histogram)
        self.assertEqual(parsed.top_colors, 2)
        self.assertEqual(arguments.build_parser().format_help(),
                         parser.build_parser().format_help())
        self.assertTrue(callable(arguments.option_error))
        self.assertTrue(callable(arguments.region_error))
        self.assertTrue(callable(arguments.rgb_argument))

    def test_mode_options_remain_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as raised:
            arguments.build_parser().parse_args(
                ("reference.png", "0", "0", "--histogram", "--runs")
            )
        self.assertEqual(raised.exception.code, 2)

    def test_declaration_helpers_are_partitioned_by_option_family(self):
        cases = (
            (parser._add_region_arguments, ("reference.png", "1", "2"),
             "image", "reference.png"),
            (parser._add_histogram_arguments, ("--top-colors", "3"),
             "top_colors", 3),
            (parser._add_run_arguments, ("--min-run-length", "2"),
             "min_run_length", 2),
            (parser._add_find_color_arguments, ("--color-tolerance", "4"),
             "color_tolerance", 4),
        )
        for add_arguments, argv, attribute, expected in cases:
            with self.subTest(helper=add_arguments.__name__):
                option_parser = argparse.ArgumentParser()
                add_arguments(option_parser)
                self.assertEqual(getattr(option_parser.parse_args(argv), attribute), expected)


if __name__ == "__main__":
    unittest.main()
