"""Decode a render gate's capture PNG once per gate class.

Each render gate owns one PNG its capture wrote and reads it from many
pixel tests; decoding it per read would re-decode the same file, so the
first read caches the decoded image on the gate's class.

This mixin serves the three gates that share the plain decode-once
behaviour: ``DialogGate`` (``support/render/gates.py``), ``TestRender``
(``tests/test_render_surface.py``, the applet render) and
``TestSplashRender`` (``tests/test_render_splash_gate.py``).
``TestDesktopRender`` keeps its own ``candidate_image`` — it hardens a
missing capture into an ``AssertionError`` naming the render output
instead of the read error this mixin lets through — and its exit check
is one combined test, so it inherits neither method.
"""

from __future__ import annotations

from tools.png import read_png
from support.render.renders import render_output_note


class CachedCandidatePng:
    """Mixin for gates that own one rendered PNG capture.

    ``setUpClass`` must set ``returncode``, ``stdout`` and ``stderr`` from
    the render, ``output`` to the capture's path, and ``_candidate`` to
    ``None``. The mixin then provides:

    - ``candidate_image``: decode the capture once and reuse the decoded
      image for every later read. A failed render leaves the output absent
      and the first read raises ``PngError`` naming the path, just as it
      did before: for a missing file the message carries the underlying
      ``FileNotFoundError``, for an unreadable one the read failure.
    - ``test_exits_zero``: the render's exit status is 0, with a failure
      message built from both streams — a failed render's session-log tail
      lands on stdout and stderr may print nothing, so quoting stderr
      alone would report a bare ``0 != 1``.
    """

    @classmethod
    def candidate_image(cls):
        """Return the render output decoded once, reused by every read."""
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def test_exits_zero(self):
        self.assertEqual(
            0,
            self.returncode,
            render_output_note(self.stdout, self.stderr) or None,
        )
