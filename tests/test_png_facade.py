"""Tests for ``tools/png/__init__.py`` -- the codec's public facade.

The codec's pieces are split by concern across ``image.py``, ``read.py`` and
``write.py``, and the package's ``__init__.py`` re-exports the public names so
a consumer imports them from ``tools.png`` regardless of which submodule
defines them. Nothing pinned that contract: a rename in a submodule, or a name
dropped from ``__all__``, left the facade quietly wrong while every direct
submodule import kept working. These tests pin the public names, the submodule
each comes from, and the names ``__all__`` advertises.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png  # noqa: E402
from tools.png import image, read, write  # noqa: E402

# The public interface the facade's docstring documents and ``__all__``
# advertises, each with the submodule object it must re-export.
PUBLIC_NAMES = {
    "Image": image.Image,
    "PngError": image.PngError,
    "decode_png": read.decode_png,
    "encode_png": write.encode_png,
    "pixel_at": image.pixel_at,
    "read_png": read.read_png,
}


class TestFacade(unittest.TestCase):
    def test_all_advertises_the_public_names(self):
        # `from tools.png import *` exposes exactly `__all__`, so a name in the
        # docstring but missing here (or vice versa) is an inconsistent public
        # interface. Both directions are checked by comparing sets.
        self.assertEqual(set(png.__all__), set(PUBLIC_NAMES))

    def test_every_public_name_is_the_defining_submodules_object(self):
        # A re-export must be the same object, not a second copy or a wrapper:
        # callers compare PngError from the facade with the one decode_png
        # raises, and pass a facade-built Image into read/write helpers.
        for name, obj in PUBLIC_NAMES.items():
            with self.subTest(name=name):
                self.assertIs(getattr(png, name), obj)

    def test_all_lists_each_public_name_once(self):
        self.assertEqual(len(png.__all__), len(set(png.__all__)))


if __name__ == "__main__":
    unittest.main()
