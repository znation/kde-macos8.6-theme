"""The two image pairs the fidelity shared-delta suites pin against.

``tools/fidelity.py`` derives one channel-delta pass per run and hands the
strings to the spatial flag scan, the pixel reports and ``compare``; the
four ``test_fidelity_*_shared_deltas`` and ``_shared_flags`` modules pin
that shared pass against the same two image pairs, so the pairs live here
once and each module states only the behaviour it pins.

The RGB pair is 4x2: the candidate carries one red byte 10 at pixel (0, 0)
and one blue byte 30 at pixel (2, 1) against an all-zero reference, so
each candidate byte's delta is its own value, the delta list has three
strings, and tolerance 9 keeps exactly the two over-tolerance pixels.

The RGBA pair is 3x2: the candidate carries alpha and its byte 0 at
(0, 0) sits against an RGB-only reference whose absent plane reads opaque
255, so the compared alpha adds a fourth delta string whose only nonzero
byte is 255 and tolerance 100 differs at exactly that pixel.

Each suite re-derives its report values from these bytes in its own test
docstrings and assertions; this module defines no test cases, so
``unittest discover`` never collects it.
"""

from __future__ import annotations

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.png import Image  # noqa: E402

CANDIDATE_RGB = bytearray(24)
CANDIDATE_RGB[0] = 10            # (0, 0) red
CANDIDATE_RGB[3 * 6 + 2] = 30    # (2, 1) blue
RGB_PAIR = (Image(4, 2, bytes(CANDIDATE_RGB)), Image(4, 2, bytes(24)))

ALPHA_CANDIDATE_RGB = bytearray(18)
ALPHA_CANDIDATE_RGB[0] = 40      # (0, 0) alpha, against opaque 255
ALPHA_CANDIDATE = Image(
    3, 2, bytes(ALPHA_CANDIDATE_RGB), bytes([0, 255, 255, 255, 255, 255]),
)
RGBA_PAIR = (ALPHA_CANDIDATE, Image(3, 2, bytes(18)))
