"""Shared fixtures and assertions for the fidelity CLI test modules.

``tools/fidelity.py``'s CLI is exercised from several test modules: the verdict
and budget gate, the crop options, the numeric and usage errors, and the
terminal escaping. They build the same small PNG pairs and assert the same
PASS/FAIL and usage-error shapes, so the fixtures and assertions live here once
and each module states only the behaviour it pins.

This module defines no test cases, so ``unittest discover`` never collects it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import CliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image, solid_rgb  # noqa: E402
from tools import fidelity, fidelity_run_family  # noqa: E402


def patched_horizontal_calls(**replacement):
    """Patch the scan callables the horizontal difference-run family scans with.

    ``tools/fidelity.py``'s ``main`` reads each family's scan callables from
    the ``HORIZONTAL_RUN_CALLS`` bundle in its own namespace, so this
    replaces that binding with a copy whose named callables are swapped;
    the keyword names are ``RunFamilyCalls``'s fields (``runs``,
    ``iter_runs``, ``run_count``, ``longest_run``).
    """
    return mock.patch.object(
        fidelity, "HORIZONTAL_RUN_CALLS",
        fidelity_run_family.HORIZONTAL_RUN_CALLS._replace(**replacement))


def patched_column_calls(**replacement):
    """Patch the scan callables the vertical difference-run family scans with.

    See :func:`patched_horizontal_calls`; this patches ``COLUMN_RUN_CALLS``.
    """
    return mock.patch.object(
        fidelity, "COLUMN_RUN_CALLS",
        fidelity_run_family.COLUMN_RUN_CALLS._replace(**replacement))


class FidelityCliTestCase(CliTestCase):
    """Base for a test case that drives ``tools/fidelity.py``.

    Sets ``MAIN`` and ``PROGRAM`` so every subclass runs the CLI in process,
    and adds the shared fixtures (the altered candidate pair, the padded
    surface pair, a solid reference) and the PASS/FAIL and crop-error
    assertions the CLI test modules share.
    """

    MAIN = staticmethod(fidelity.main)
    PROGRAM = "fidelity"

    # One 4x3 candidate-and-blank pair the shared-delta/flags CLI suites
    # drive: the (0, 0) red byte reads delta 10 and the (2, 1) blue byte
    # reads delta 30, both strictly beyond tolerance 9.
    DELTA_PAIR_ROWS = [
        bytes([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        bytes([0, 0, 0, 0, 0, 0, 0, 0, 30, 0, 0, 0]),
        bytes(12),
    ]

    def _delta_pair(self) -> tuple[bytes, bytes]:
        """Return PNG bytes for the shared 4x3 delta pair.

        The candidate carries two over-tolerance bytes (the ``(0, 0)`` red
        10 and the ``(2, 1)`` blue 30) on an all-zero reference, so every
        derived run claims a FAIL. Four CLI suites drive exactly this pair:
        test_fidelity_flags_shared_deltas, test_fidelity_metrics_shared_deltas,
        test_fidelity_pixels_shared_deltas and test_fidelity_spatial_shared_flags.
        """
        return (
            make_png(4, 3, self.DELTA_PAIR_ROWS),
            make_png(4, 3, [bytes(12)] * 3),
        )

    def _write_altered_pair(self, directory: Path) -> tuple[str, str]:
        """Write a 3x3 candidate and a one-pixel-altered copy of it.

        Pixel (1, 0) of the candidate is (20, 0, 60); the altered copy raises
        its green channel to 50, so exactly one of the 27 RGB bytes differs by
        50 while the alpha channels agree (MAE 50/36, differing fraction 1/9).
        Returns the two paths.
        """
        surface, png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
        changed = bytearray(surface.rgb)
        changed[4] = 50
        altered_png = make_png(
            3, 3, [bytes(changed[i : i + 9]) for i in range(0, 27, 9)]
        )
        return (
            self._write(directory, "candidate.png", png),
            self._write(directory, "altered.png", altered_png),
        )

    def _run_png_pair(
        self, candidate_png: bytes, reference_png: bytes, *args: str
    ) -> subprocess.CompletedProcess:
        """Write two PNGs to a temp dir and run the CLI on them.

        *candidate_png* is written as ``candidate.png`` and *reference_png* as
        ``reference.png``.
        """
        tmp = self._tmp_dir()
        candidate = self._write(tmp, "candidate.png", candidate_png)
        reference = self._write(tmp, "reference.png", reference_png)
        return self._run(candidate, reference, *args)

    def _write_padded_surface_pair(self, directory: Path) -> tuple[str, str]:
        """Write a 2x2 surface PNG and a 4x4 reference with a 1px black border.

        The reference embeds the surface at (1, 1), so ``--crop 1,1,2,2``
        selects exactly the surface. Returns the surface path and the
        reference path.
        """
        surface, surface_png = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
        border = bytes([0, 0, 0] * 4)
        rows = [
            border,
            bytes([0, 0, 0] + list(surface.rgb[0:6]) + [0, 0, 0]),
            bytes([0, 0, 0] + list(surface.rgb[6:12]) + [0, 0, 0]),
            border,
        ]
        full_png = make_png(4, 4, rows)
        return (
            self._write(directory, "surface.png", surface_png),
            self._write(directory, "full.png", full_png),
        )

    def _padded_surface_png(self, width, height, ox, oy) -> bytes:
        """Return a *width* x *height* PNG with the 2x2 test surface at ``(ox, oy)``.

        The surface is the same ``rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))``
        the other fixtures use, so a crop selecting it matches a crop of any
        other padded copy; the rest of the image is black.
        """
        def pixel(x, y):
            if ox <= x < ox + 2 and oy <= y < oy + 2:
                return ((x - ox) * 9, (y - oy) * 9, 5)
            return (0, 0, 0)

        return rgb_image(width, height, pixel)[1]

    def _solid_reference(self) -> str:
        """Write a 1x1 black PNG to a fresh temp dir and return its path."""
        _, data = solid_rgb(1, 1)
        return self._write(self._tmp_dir(), "reference.png", data)

    def _assert_pass(self, result: subprocess.CompletedProcess) -> None:
        """Assert *result* is a clean exit-0 pass whose stdout says PASS."""
        self._assert_success(result)
        self.assertIn("PASS", result.stdout)

    def _assert_fail(self, result: subprocess.CompletedProcess) -> None:
        """Assert *result* is an exit-1 fidelity failure whose stdout says FAIL."""
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL", result.stdout)

    def _assert_outside_crop_is_error(self, option: str, filename: str) -> None:
        """Assert a syntactically valid crop past the 2x2 edge is a usage error.

        *option* is ``--candidate-crop`` or ``--crop`` and *filename* names the
        image the option selects, so the two options are exercised the same way.
        """
        tmp = self._tmp_dir()
        _, image = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
        path = self._write(tmp, filename, image)
        result = self._run(path, path, option, "1,1,2,2")
        self._assert_usage_error(result, "falls outside")
