"""Input policy for the fidelity PNG reader."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from support import repo_root  # noqa: F401
from support.png_fixtures import rgb_image
from tools import fidelity_sources, png


class TestFidelitySources(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "image.png"
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 7))
        self.path.write_bytes(data)

    def test_uncropped_read_decodes_alpha_once(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), None)
        self.assertEqual((image.width, image.height), (3, 4))
        read.assert_called_once_with(str(self.path), alpha=True)

    def test_crop_bounds_decoded_rows(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), (0, 1, 2, 2))
        self.assertEqual(image.height, 3)
        read.assert_called_once_with(str(self.path), max_rows=3, alpha=True)

    def test_sideways_overflow_retries_unbounded(self):
        with mock.patch.object(fidelity_sources, "read_png", wraps=png.read_png) as read:
            image = fidelity_sources.read_source(str(self.path), (2, 1, 2, 2))
        self.assertEqual(image.height, 4)
        self.assertEqual([call.kwargs for call in read.call_args_list], [
            {"max_rows": 3, "alpha": True}, {"alpha": True}
        ])

    def test_vertical_and_combined_overflow_stay_bounded(self):
        with mock.patch.object(
            fidelity_sources, "read_png", wraps=png.read_png
        ) as read:
            image = fidelity_sources.read_source(str(self.path), (0, 2, 2, 3))
        self.assertEqual(image.height, 4)
        read.assert_called_once_with(str(self.path), max_rows=5, alpha=True)

        # When both dimensions overflow, sideways overflow still triggers the
        # full read so the crop diagnostic retains the real image dimensions.
        with mock.patch.object(
            fidelity_sources, "read_png", wraps=png.read_png
        ) as read:
            image = fidelity_sources.read_source(str(self.path), (2, 2, 2, 3))
        self.assertEqual(image.height, 4)
        self.assertEqual([call.kwargs for call in read.call_args_list], [
            {"max_rows": 5, "alpha": True}, {"alpha": True}
        ])

    def test_repository_escape_is_rejected_before_decode(self):
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        link = repo / "link.png"
        link.symlink_to(self.path)
        with mock.patch.object(fidelity_sources, "ROOT", repo), mock.patch.object(
            fidelity_sources, "read_png"
        ) as read:
            with self.assertRaisesRegex(ValueError, "resolves outside"):
                fidelity_sources.read_source(str(link), None)
        read.assert_not_called()

    def test_inside_repository_symlink_and_external_path_are_readable(self):
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        target = repo / "target.png"
        target.write_bytes(self.path.read_bytes())
        link = repo / "link.png"
        link.symlink_to(target)
        with mock.patch.object(fidelity_sources, "ROOT", repo):
            self.assertEqual(fidelity_sources.read_source(str(link), None).width, 3)
            self.assertEqual(fidelity_sources.read_source(str(self.path), None).width, 3)


class TestReadSource(unittest.TestCase):
    def test_uncropped_and_in_bounds_reads_preserve_alpha_and_bound_rows(self):
        image = SimpleNamespace(width=8, height=9)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            self.assertIs(fidelity_sources.read_source("external.png", None), image)
            decoder.assert_called_once_with("external.png", alpha=True)
            decoder.reset_mock()
            self.assertIs(
                fidelity_sources.read_source("external.png", (1, 2, 3, 4)), image
            )
            decoder.assert_called_once_with(
                "external.png", max_rows=6, alpha=True
            )

    def test_sideways_overflow_retries_full_image(self):
        image = SimpleNamespace(width=3, height=8)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", (2, 0, 2, 2))
        self.assertEqual(
            decoder.call_args_list,
            [mock.call("image.png", max_rows=2, alpha=True),
             mock.call("image.png", alpha=True)],
        )

    def test_vertical_overflow_stays_bounded_and_combined_retries(self):
        image = SimpleNamespace(width=3, height=3)
        rect = (0, 1, 2, 4)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", rect)
            decoder.assert_called_once_with(
                "image.png", max_rows=rect[1] + rect[3], alpha=True
            )

        # Sideways overflow takes precedence when both dimensions overflow.
        rect = (2, 1, 2, 4)
        with mock.patch.object(fidelity_sources, "require_within_repo"), mock.patch.object(
            fidelity_sources, "read_png", return_value=image
        ) as decoder:
            fidelity_sources.read_source("image.png", rect)
        self.assertEqual(
            decoder.call_args_list,
            [mock.call("image.png", max_rows=5, alpha=True),
             mock.call("image.png", alpha=True)],
        )

    def test_repository_symlink_escape_is_rejected_before_decode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            outside = Path(directory) / "outside.png"
            outside.write_bytes(b"png")
            link = root / "linked.png"
            link.symlink_to(outside)
            with mock.patch.object(fidelity_sources, "ROOT", root), mock.patch.object(
                fidelity_sources, "read_png"
            ) as decoder:
                with self.assertRaises(ValueError):
                    fidelity_sources.read_source(str(link), None)
            decoder.assert_not_called()


if __name__ == "__main__":
    unittest.main()
