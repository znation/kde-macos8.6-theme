"""Shared fixtures for the tools/check_references.py test modules.

The checker is a script rather than an installed package, so these helpers
load it from its path and build throwaway reference directories for it to
check. ``test_check_references_io``, ``test_check_references_validation`` and
``test_check_references_cli`` each import the pieces they use, so the loading
and fixture construction live here once instead of in each module.
"""

import contextlib
import importlib.util
import os
import sys
import tempfile
import unittest.mock
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
CHECKER = os.path.join(ROOT, "tools", "check_references.py")


def load_checker():
    """Load ``tools/check_references.py`` as a module for the tests to call.

    The checker is a script rather than an installed package, so it is loaded
    from its path with importlib instead of imported by name.
    """
    spec = importlib.util.spec_from_file_location("check_references", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def reference_set(module, sources, files=()):
    """Yield a temporary reference directory built from the given content.

    ``sources`` is the sources.txt content, encoded as UTF-8 when passed as
    text; ``files`` pairs a path relative to the directory with the bytes to
    write, creating intermediate directories. The directory is removed when
    the context exits.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / module.SOURCES_NAME).write_bytes(
            sources.encode("utf-8") if isinstance(sources, str) else sources
        )
        for name, content in dict(files).items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        yield root


@contextlib.contextmanager
def symlinked_reference(module, link_name, target, sources=None):
    """Yield a reference directory holding one symlink that escapes it.

    ``target`` is the bytes of a file created beside the directory, and the
    symlink named ``link_name`` inside it points at that file. ``sources``,
    when given, is the sources.txt content written inside the directory (so
    the caller can declare the escaping link); when omitted, no sources.txt
    is written and ``link_name`` may itself be the symlinked sources.txt.
    The directory and its sibling target are removed when the context exits.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ref = root / "ref"
        ref.mkdir()
        outside = root / "outside"
        outside.write_bytes(target)
        if sources is not None:
            (ref / module.SOURCES_NAME).write_bytes(sources.encode("utf-8"))
        os.symlink(outside, ref / link_name)
        yield ref


def check_references_in(module, sources, files=()):
    """Return check_references' problems for a temporary reference set."""
    with reference_set(module, sources, files) as root:
        return module.check_references(root)


@contextlib.contextmanager
def path_method_raises(method, path, error_type, errno, message):
    """Patch ``Path.<method>`` to fail for ``path`` and delegate otherwise.

    The checker reads, lists, and resolves paths throughout a run, so a test
    drives a single filesystem failure -- an unreadable file, an unlistable
    directory, an unresolvable path -- by making only that path raise. Every
    other path still reaches the real ``Path`` method, leaving the rest of
    the check working.
    """
    real = getattr(Path, method)

    def raises_for(self, *args, **kwargs):
        if self == path:
            raise error_type(errno, message, str(self))
        return real(self, *args, **kwargs)

    with unittest.mock.patch.object(Path, method, raises_for):
        yield
