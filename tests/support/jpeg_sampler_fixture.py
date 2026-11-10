"""The deterministic JPEG fixture the sampler's JPEG branch is pinned against.

Generated 2026-11-10: a 32x24 P6 PPM quilt of eight-by-eight blocks in twelve
distinct RGB triples ((220,20,30),(30,220,40),(50,90,200),(230,230,10),
(10,120,130),(180,100,30),(120,10,180),(70,200,120),(200,200,200),(40,40,40),
(150,50,90),(90,150,20)), converted once with ``convert quilt.ppm quilt.jpg``
on ImageMagick 7.1.1-43 Q16 x86_64. The JPEG artifact, like the reference
set's own JPEG screenshots, is measured evidence, not a computed value: the
QUILT_* constants below record the decoded values the completed sampler
reported on that one conversion on this host, so no test ever runs
ImageMagick at check time.
"""

from __future__ import annotations

import base64

_QUILT_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQg"
    "KCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwk"
    "LEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAA"
    "RCAAYACADAREAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAACAcJ/8QAFBABAAAAAAAAAAA"
    "AAAAAAAAAAP/EABkBAAMBAQEAAAAAAAAAAAAAAAcICQAEBv/EABQRAQAAAAAAAAAAAAAAAAA"
    "AAAD/2gAMAwEAAhEDEQA/AIEGShBShihEOioBiGmCGo+sx1ZSdKWT9RAb1MHCeBH09yAewM2"
    "xUZl2dA+qwWQp7//Z"
)

QUILT_JPEG: bytes = base64.b64decode(_QUILT_JPEG_B64)

# The decoded image's own geometry, same numbers the fixture encodes.
QUILT_WIDTH = 32
QUILT_HEIGHT = 24

# The sampled region (8, 8) 3x2 is entirely inside the block at grid
# position (1, 1): its decoded face is uniform, so every coordinate reports
# this triple and hex.
QUILT_BLOCK_TRIPLE = (180, 100, 31)
QUILT_BLOCK_HEX = "#B4641F"

# --histogram over region (0, 0) 16x8: the blocks at grid positions (0, 0)
# and (1, 0) decode to one color each, 64 pixels per block additionally
# spanning the blend-free columns. Result rows in the sampler's print order.
QUILT_HISTOGRAM_ROWS = (
    "31,220,40  #1FDC28  count=64",
    "220,20,30  #DC141E  count=64",
    "total colors: 2",
    "omitted pixels: 0",
)

# --runs down the image's first column (region (0, 0) 1x24): three runs of
# eight pixels, one per block, separated at the block bounds.
QUILT_RUN_ROWS = (
    "region (0, 0) 1x24:",
    "axis: vertical",
    "(0, 0): 220,20,30  #DC141E  length=8",
    "(0, 8): 9,120,131  #097883  length=8",
    "(0, 16): 200,200,200  #C8C8C8  length=8",
)

# --find-color #B4641F over region (10, 10) 8x8: the block face blends JPEG
# artifacts into neighbours outside the pinned rows, so 36 of the 64 pixels
# match exactly and the row-major first three matches sit where recorded.
QUILT_FIND_HEX = "#B4641F"
QUILT_FIND_COUNT = 36
QUILT_FIND_BOUNDS = "bounds: 10,10,6,6"
QUILT_FIND_TOTALS = (
    "matching pixels: 3",
    "omitted pixels: 33",
    "pixel (10, 10)",
    "pixel (11, 10)",
    "pixel (12, 10)",
)
