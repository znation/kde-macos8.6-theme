"""Shared fixtures and independent readers for committed cursor artifacts."""

from support import xcursor as xcursor_reader
from tools import make_cursors

PACKAGE = make_cursors.ROOT / make_cursors.PACKAGE_DIR
CURSORS = PACKAGE / make_cursors.CURSORS_DIR
SIZES = (16, 24, 32)
HOTSPOTS = {
    "left_ptr": {16: (1, 1), 24: (2, 2), 32: (3, 3)},
    "xterm": {16: (7, 7), 24: (11, 11), 32: (15, 15)},
    "hand2": {16: (7, 2), 24: (10, 3), 32: (14, 4)},
    "watch": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "fleur": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_hor": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_ver": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_fdiag": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_bdiag": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "crosshair": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "not-allowed": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "dnd-copy": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "grab": {16: (7, 12), 24: (11, 18), 32: (14, 24)},
    "grabbing": {16: (7, 12), 24: (11, 18), 32: (14, 24)},
    "help": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "progress": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "pencil": {16: (2, 14), 24: (3, 21), 32: (4, 28)},
    "zoom-in": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "zoom-out": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "context-menu": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
}
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def _pixel(rgba, width, x, y):
    """Return pixel (*x*, *y*) of packed *rgba* as an RGBA tuple."""
    start = (y * width + x) * 4
    return tuple(rgba[start : start + 4])


def _read_cursor(path):
    """Read *path* through the independent test-side reader."""
    return xcursor_reader.read_cursor(path)
