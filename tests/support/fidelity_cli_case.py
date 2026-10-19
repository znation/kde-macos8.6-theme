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

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import CliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image, solid_rgb  # noqa: E402
from tools import fidelity  # noqa: E402


class FidelityCliTestCase(CliTestCase):
    """Base for a test case that drives ``tools/fidelity.py``.

    Sets ``MAIN`` and ``PROGRAM`` so every subclass runs the CLI in process,
    and adds the shared fixtures (the altered candidate pair, the padded
    surface pair, a solid reference) and the PASS/FAIL and crop-error
    assertions the CLI test modules share.
    """

    MAIN = staticmethod(fidelity.main)
    PROGRAM = "fidelity"

    def _write_altered_pair(self, directory: Path) -> tuple[str, str]:
        """Write a 3x3 candidate and a one-pixel-altered copy of it.

        Pixel (1, 0) of the candidate is (20, 0, 60); the altered copy raises
        its green channel to 50, so exactly one of the 27 bytes differs by 50
        (MAE 50/27, differing fraction 1/9). Returns the two paths.
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
        self, candidate_png: bytes, reference_png: bytes
    ) -> subprocess.CompletedProcess:
        """Write two PNGs to a temp dir and run the CLI on them.

        *candidate_png* is written as ``candidate.png`` and *reference_png* as
        ``reference.png``.
        """
        tmp = self._tmp_dir()
        candidate = self._write(tmp, "candidate.png", candidate_png)
        reference = self._write(tmp, "reference.png", reference_png)
        return self._run(candidate, reference)

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
