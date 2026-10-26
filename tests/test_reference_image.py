"""Tests for support/reference_image.py's decoded-reference cache."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import reference_image  # noqa: E402
from support.symlink_fixtures import symlinked_repo
from tools.png.write import encode_png, encode_rgba_png  # noqa: E402


_RGBA_ALPHAS = bytes((40, 80, 120, 160))


def _write_reference(directory):
    """Write a tiny valid PNG into *directory* and return its path."""
    path = os.path.join(directory, "reference.png")
    with open(path, "wb") as handle:
        handle.write(encode_png(2, 2, bytes(12)))
    return path


def _write_rgba_reference(directory):
    """Write a 2x2 RGBA PNG whose alpha plane is :data:`_RGBA_ALPHAS`."""
    path = os.path.join(directory, "reference-rgba.png")
    rgba = b"".join(bytes((value, value, value)) + bytes((alpha,))
                    for value, alpha in zip(range(0, 40, 10), _RGBA_ALPHAS))
    with open(path, "wb") as handle:
        handle.write(encode_rgba_png(2, 2, rgba))
    return path


def _spy_on_read_png():
    """Patch ``read_png`` to count decodes while still calling through."""
    return mock.patch.object(
        reference_image.png,
        "read_png",
        wraps=reference_image.png.read_png,
    )


class TestReadReferenceCache(unittest.TestCase):
    def test_a_second_read_reuses_the_first_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                first, first_error = reference_image.read_reference(path)
                second, second_error = reference_image.read_reference(path)
        self.assertEqual(1, spy.call_count)
        self.assertIs(first, second)
        self.assertIsNone(first_error)
        self.assertIsNone(second_error)

    def test_alpha_mode_is_part_of_the_cache_key(self):
        # A plain decode has no alpha plane, so it cannot answer a request
        # that asks for transparency: the cache must decode the path again
        # rather than hand back the RGB-only image.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_rgba_reference(tmp)
            with _spy_on_read_png() as spy:
                plain, plain_error = reference_image.read_reference(path)
                with_alpha, alpha_error = reference_image.read_reference(
                    path, alpha=True
                )
        self.assertEqual(2, spy.call_count)
        self.assertIsNone(plain.alpha)
        self.assertEqual(with_alpha.alpha, _RGBA_ALPHAS)
        self.assertIsNone(plain_error)
        self.assertIsNone(alpha_error)

    def test_a_bounded_alpha_decode_keeps_its_alpha_plane(self):
        # Reusing a taller alpha decode for a smaller bound copies the top
        # rows; the alpha plane must be copied to the same bound, or the
        # caller gets an image with no transparency.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_rgba_reference(tmp)
            with _spy_on_read_png() as spy:
                tall, tall_error = reference_image.read_reference(
                    path, alpha=True, max_rows=2
                )
                short, short_error = reference_image.read_reference(
                    path, alpha=True, max_rows=1
                )
        self.assertEqual(1, spy.call_count)
        self.assertEqual((tall.height, short.height), (2, 1))
        self.assertEqual(tall.alpha, _RGBA_ALPHAS)
        self.assertEqual(short.alpha, _RGBA_ALPHAS[:2])
        self.assertIsNone(tall_error)
        self.assertIsNone(short_error)

    def test_a_different_max_rows_is_decoded_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                one, one_error = reference_image.read_reference(
                    path, max_rows=1
                )
                two, two_error = reference_image.read_reference(
                    path, max_rows=2
                )
        self.assertEqual(2, spy.call_count)
        self.assertEqual((one.height, two.height), (1, 2))
        self.assertIsNot(one, two)
        self.assertIsNone(one_error)
        self.assertIsNone(two_error)

    def test_a_larger_cached_decode_serves_a_smaller_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                tall, tall_error = reference_image.read_reference(
                    path, max_rows=2
                )
                short, short_error = reference_image.read_reference(
                    path, max_rows=1
                )
        self.assertEqual(1, spy.call_count)
        self.assertEqual((tall.height, short.height), (2, 1))
        self.assertIsNot(tall, short)
        self.assertIsNone(tall_error)
        self.assertIsNone(short_error)

    def test_a_full_decode_serves_a_bounded_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                full, full_error = reference_image.read_reference(path)
                short, short_error = reference_image.read_reference(
                    path, max_rows=1
                )
        self.assertEqual(1, spy.call_count)
        self.assertEqual((full.height, short.height), (2, 1))
        self.assertIsNone(full_error)
        self.assertIsNone(short_error)

    def test_an_unbounded_request_after_a_bounded_decode_reads_the_whole_image(
        self,
    ):
        # A bounded decode holds only its top rows, so a later unbounded
        # request cannot be served from that cache entry: reusing it would
        # hand every caller a silently truncated reference. Only a decode at
        # least as tall as the image may answer an unbounded request.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                short, short_error = reference_image.read_reference(
                    path, max_rows=1
                )
                full, full_error = reference_image.read_reference(path)
        self.assertEqual(2, spy.call_count)
        self.assertEqual((short.height, full.height), (1, 2))
        self.assertEqual(full.rgb, bytes(12))
        self.assertIsNone(short_error)
        self.assertIsNone(full_error)

    def test_a_bound_past_the_height_is_reused_for_an_equal_request(self):
        # A bound above the image height means the whole image was decoded,
        # so an identical later request must not decode it again.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                first, first_error = reference_image.read_reference(
                    path, max_rows=5
                )
                second, second_error = reference_image.read_reference(
                    path, max_rows=5
                )
        self.assertEqual(1, spy.call_count)
        self.assertEqual((first.height, second.height), (2, 2))
        self.assertIsNone(first_error)
        self.assertIsNone(second_error)

    def test_an_invalid_bound_is_an_error_with_a_cached_decode(self):
        # A cached decode must not let an invalid bound reach ``_bounded``:
        # ``read_png`` would reject it, so the warm path has to as well, and
        # it must not read or decode the file to do so.
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_reference(tmp)
            with _spy_on_read_png() as spy:
                reference_image.read_reference(path)
                for bad in (0, -1, True, 1.5, "2"):
                    self._assert_bound_is_rejected(path, bad)
        self.assertEqual(1, spy.call_count)

    def _assert_bound_is_rejected(self, path, max_rows):
        """Assert a read with the invalid bound *max_rows* fails.

        The bound is rejected without a decode, so the read returns no image
        and a ``PngError`` instead.
        """
        with self.subTest(max_rows=max_rows):
            image, error = reference_image.read_reference(
                path, max_rows=max_rows
            )
            self.assertIsNone(image)
            self.assertIsInstance(error, reference_image.png.PngError)

    def test_a_failed_read_is_cached_like_a_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "absent.png")
            with _spy_on_read_png() as spy:
                first, first_error = reference_image.read_reference(path)
                second, second_error = reference_image.read_reference(path)
        self.assertEqual(1, spy.call_count)
        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertIs(first_error, second_error)
        self.assertIsInstance(first_error, reference_image.png.PngError)


class TestReadReferenceContainment(unittest.TestCase):
    """``read_reference`` refuses a screenshot symlink that escapes the repository.

    A reference screenshot path is contributor-supplied, and a checked-in
    symlink there can point at a private PNG outside the repository. The tests
    decode the target and echo its pixels in assertion diagnostics, so the read
    must refuse the escape before it is decoded -- including when an earlier
    request already cached a decode under the same path.
    """

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "reference.png", encode_png(2, 2, bytes(12))
            )
            with mock.patch.object(reference_image, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    reference_image.read_reference(link)
        self.assertIn(str(link), str(caught.exception))
        self.assertIn("resolves outside", str(caught.exception))

    def test_a_cached_decode_does_not_bypass_the_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            target = root / "actual.png"
            target.write_bytes(encode_png(2, 2, bytes(12)))
            link = root / "reference.png"
            link.symlink_to(target)
            with mock.patch.object(reference_image, "ROOT", root):
                image, error = reference_image.read_reference(link)
                self.assertIsNone(error)
                self.assertEqual((image.width, image.height), (2, 2))
                link.unlink()
                link.symlink_to(tmp / "private.png")
                with self.assertRaises(ValueError) as caught:
                    reference_image.read_reference(link)
        self.assertIn(str(link), str(caught.exception))
        self.assertIn("resolves outside", str(caught.exception))


class TestReferenceScreenshotMixin(unittest.TestCase):
    """The mixin forwards its ``MAX_ROWS`` to the decode.

    ``MAX_ROWS`` bounds the decode of a large Git LFS screenshot to the rows a
    test samples. A class that sets it must get an image no taller than that;
    if ``setUpClass`` dropped it, every pixel assertion would still pass and
    only the decode would silently grow back to the whole screenshot.
    """

    def _case_with(self, path, max_rows):
        """Run the mixin's ``setUpClass`` for a class with this path and bound."""

        class Case(reference_image.ReferenceScreenshotMixin, unittest.TestCase):
            REFERENCE = path
            MAX_ROWS = max_rows

        Case.setUpClass()
        return Case

    def test_max_rows_bounds_the_decoded_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = self._case_with(_write_reference(tmp), 1)
        self.assertIsNone(case.image_error)
        self.assertEqual((case.image.width, case.image.height), (2, 1))

    def test_no_max_rows_decodes_the_whole_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = self._case_with(_write_reference(tmp), None)
        self.assertIsNone(case.image_error)
        self.assertEqual((case.image.width, case.image.height), (2, 2))


class TestSharedFandomBound(unittest.TestCase):
    """The readers of ``desktop_fandom.png`` share one decode bound.

    If the Aurorae inactive reader kept its own smaller bound and ran first,
    the 1250-row desktoptheme readers would find a decode too short and
    re-decode the whole screenshot; sharing the bound keeps the single decode
    independent of discovery order. The desktoptheme readers import
    ``FANDOM_MAX_ROWS`` by construction, so only the Aurorae constant can
    drift.
    """

    def test_the_aurorae_reader_shares_the_fandom_bound(self):
        from support import aurorae_fixtures, desktoptheme_paths

        self.assertEqual(
            aurorae_fixtures.INACTIVE_REFERENCE,
            desktoptheme_paths.FANDOM_REFERENCE,
        )
        self.assertEqual(
            aurorae_fixtures.INACTIVE_REFERENCE_ROWS,
            desktoptheme_paths.FANDOM_MAX_ROWS,
        )


class TestSharedReferenceBounds(unittest.TestCase):
    """The readers and anchor bounds pin each screenshot's shared decode bound.

    ``read_reference`` re-decodes when a later request needs more rows than
    the cached decode holds, so two readers of one screenshot with different
    bounds unfilter it twice, in discovery order. These assertions pin the
    reader classes and module-level anchor bounds to the screenshot's shared
    constant, so a hardcoded literal cannot silently reintroduce a second
    decode -- the Kvantum check-box reader's own 394-row bound did exactly
    that for ``aboutsystem_betawiki.png``.
    """

    def _assert_reader_shares(self, path, bound, *readers):
        for reader in readers:
            self.assertEqual(path, reader.REFERENCE, reader)
            self.assertEqual(bound, reader.MAX_ROWS, reader)

    def test_readers_share_the_archiveorg_bound(self):
        from support.desktoptheme_paths import (
            ARCHIVEORG_MAX_ROWS,
            ARCHIVEORG_REFERENCE,
        )
        from test_colorscheme_reference import (
            DESKTOP_ANCHOR_ROWS,
            REFERENCE_DESKTOP,
        )
        from test_desktoptheme_background import TestBackgroundMatchesReference
        from test_desktoptheme_dialog import TestDialogBackgroundReference
        from test_icon_arrow_reference import TestSubmenuArrowReference

        self._assert_reader_shares(
            ARCHIVEORG_REFERENCE,
            ARCHIVEORG_MAX_ROWS,
            TestBackgroundMatchesReference,
            TestDialogBackgroundReference,
            TestSubmenuArrowReference,
        )
        self.assertEqual(ARCHIVEORG_REFERENCE, REFERENCE_DESKTOP)
        self.assertEqual(ARCHIVEORG_MAX_ROWS, DESKTOP_ANCHOR_ROWS)

    def test_readers_share_the_setup_bound(self):
        from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
        from test_colorscheme_reference import (
            REFERENCE_SCROLLBAR,
            SCROLLBAR_ANCHOR_ROWS,
        )
        from test_desktoptheme_scrollbar import TestScrollbarReference
        from test_kvantum_itemview_reference import TestItemViewReference

        self._assert_reader_shares(
            SETUP_REFERENCE,
            SETUP_MAX_ROWS,
            TestScrollbarReference,
            TestItemViewReference,
        )
        self.assertEqual(SETUP_REFERENCE, REFERENCE_SCROLLBAR)
        self.assertEqual(SETUP_MAX_ROWS, SCROLLBAR_ANCHOR_ROWS)

    def test_readers_share_the_firstboot_bound(self):
        from support.desktoptheme_paths import (
            FIRSTBOOT_MAX_ROWS,
            FIRSTBOOT_REFERENCE,
        )
        from test_colorscheme_reference import (
            FIRSTBOOT_ANCHOR_ROWS,
            REFERENCE_FIRSTBOOT,
        )
        from test_desktoptheme_lineedit import TestLineEditReference

        self._assert_reader_shares(
            FIRSTBOOT_REFERENCE, FIRSTBOOT_MAX_ROWS, TestLineEditReference
        )
        self.assertEqual(FIRSTBOOT_REFERENCE, REFERENCE_FIRSTBOOT)
        self.assertEqual(FIRSTBOOT_MAX_ROWS, FIRSTBOOT_ANCHOR_ROWS)

    def test_readers_share_the_profiler_bound(self):
        from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
        from test_desktoptheme_line import TestLineReference
        from test_render_surface import REFERENCE_BOUNDS

        self._assert_reader_shares(
            PROFILER_REFERENCE, PROFILER_ROWS, TestLineReference
        )
        self.assertEqual(PROFILER_ROWS, REFERENCE_BOUNDS[PROFILER_REFERENCE])

    def test_readers_share_the_aboutsystem_bound(self):
        from support.aurorae_fixtures import REFERENCE, REFERENCE_ROWS
        from test_desktoptheme_dialog import TestDialogBackgroundRaisedReference
        from test_kvantum_checkbox_reference import TestCheckBoxReference
        from test_render_surface import REFERENCE_BOUNDS

        self._assert_reader_shares(
            REFERENCE,
            REFERENCE_ROWS,
            TestCheckBoxReference,
            TestDialogBackgroundRaisedReference,
        )
        self.assertEqual(REFERENCE_ROWS, REFERENCE_BOUNDS[REFERENCE])


if __name__ == "__main__":
    unittest.main()
