"""Shared setUp mixin for tests that isolate the cross-process decode cache.

``support.reference_decode_cache`` and ``support.reference_image`` both store
decoded reference planes under the XDG cache home. A test that counts decodes
must neither leave entries in the user's cache nor see an entry a previous
test (or run) wrote for the same content and shape, which would skip the
decode the test counts. ``test_reference_decode_cache`` and
``test_reference_image`` each base three test cases on the mixin, so the
fresh cache home and the environ patch live here once instead of duplicated
in both modules.
"""

import os
import shutil
import tempfile
import unittest.mock


class IsolatedDecodeCacheHome:
    """Point the decode cache at a fresh, empty XDG cache home per test."""

    def setUp(self):
        cache_home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, cache_home, True)
        patcher = unittest.mock.patch.dict(
            os.environ, {"XDG_CACHE_HOME": cache_home})
        patcher.start()
        self.addCleanup(patcher.stop)
        super().setUp()
