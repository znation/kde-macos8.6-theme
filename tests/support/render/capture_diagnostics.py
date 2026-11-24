"""Preserving a failed gate's capture outside the batch's scratch-tree sweep.

A failed render's capture would vanish with the scratch tree the batch's
exit sweep removes, so :func:`preserve_capture` copies it into a
timestamped diagnostics directory under this run's ``TMPDIR`` and prunes
the root to its newest directories. The skip guards, the pixel-reading
mixin, the render session batch and the dialog-gate scaffolding live in
the sibling modules (``skip_guards.py``, ``pixel_pins.py``,
``renders.py`` and ``gates.py``).
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
from unittest import mock

# Where a failed gate's capture survives the scratch-tree sweep: the
# diagnostics root sits outside every scratch directory the batch's exit
# sweep removes, and keeping only the newest timestamped directories bounds
# the space parallel workers and repeated runs spend on captures.
DIAGNOSTICS_DIRECTORY = "platinum-render-diagnostics"
DIAGNOSTIC_DIRECTORIES_KEPT = 8


def diagnostics_root():
    """Return the capture-diagnostics root under this run's ``TMPDIR``."""
    return os.path.join(os.environ.get("TMPDIR", "/tmp"), DIAGNOSTICS_DIRECTORY)


def preserve_capture(kind, directory, filename):
    """Copy the capture at *directory*/*filename* into the diagnostics root.

    The scratch tree is removed at interpreter exit, so a gate failure's
    capture would vanish with it; this copies the PNG byte for byte into
    ``<TMPDIR>/platinum-render-diagnostics/<UTC timestamp>-<pid>-<kind>/``
    under the capture's own filename and returns the copy's path. A ``None``
    return is itself a diagnostic the quarantined gate entries ask for: a
    finished render with no capture says the capture never happened. The
    diagnostics root is pruned to its newest
    :data:`DIAGNOSTIC_DIRECTORIES_KEPT` timestamped directories, and no copy
    or prune error may mask the gate's own failure, so every fault here
    falls back to ``None``.
    """
    try:
        capture = os.path.join(directory, filename)
        if not os.path.isfile(capture):
            return None
        root = diagnostics_root()
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        target_directory = os.path.join(root, f"{stamp}-{os.getpid()}-{kind}")
        os.makedirs(target_directory, exist_ok=True)
        target = os.path.join(target_directory, filename)
        shutil.copyfile(capture, target)
        _prune_diagnostics(root)
        return target
    except Exception:
        return None


def _prune_diagnostics(root):
    """Remove every diagnostics directory but the newest kept count."""
    names = sorted(os.listdir(root))
    for name in names[:-DIAGNOSTIC_DIRECTORIES_KEPT]:
        shutil.rmtree(os.path.join(root, name), ignore_errors=True)


class DiagnosticsRootSteering:
    """Give a preservation probe a diagnostics root only it can reach.

    The four test classes that drive :func:`preserve_capture` directly
    (three in ``test_render_gate_messages`` and the finish-failure class in
    ``test_render_gates_batch``) steer the root into a scratch parent by
    pointing ``TMPDIR`` at it, so pruning assertions see only directories
    the probe seeded and a concurrent run's live diagnostics directory is
    never touched. Mix it in before ``unittest.TestCase`` and start the
    subclass's ``setUp`` with ``super().setUp()``; the probe then reads
    :attr:`root` (the path :func:`diagnostics_root` returns).
    """

    def setUp(self):
        parent = tempfile.mkdtemp(prefix="preservation-root-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"TMPDIR": parent})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = diagnostics_root()
