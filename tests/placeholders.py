"""Read PLACEHOLDERS.md and the shipped theme's placeholder markers.

The user answered 2026-10-18 that the theme's own artwork was to ship as
placeholders for now and that every one must be tracked "so we don't forget to
replace them all eventually". A placeholder asset carries the literal token
``PLACEHOLDER:`` in a comment in its own file format, naming what it stands in
for; the register ``PLACEHOLDERS.md`` holds one table row per asset.
:func:`markers` reads the markers under ``theme/`` and :func:`register_entries`
reads the register, and :func:`cross_check` fails when the two disagree: a
marked file with no row, a row whose path is missing, a row whose file
carries no marker, a file or the register that is not valid UTF-8 text, or a
text asset whose symlink resolves outside ``theme/``.

``tests/test_placeholders.py`` drives these checks.

A register that lists one asset twice is refused by name with both rows'
descriptions, instead of the last row silently replacing the first.
"""

from __future__ import annotations

import os
import re

from support import containment
from support.repo_root import ROOT
from tools.terminal import escape_controls

TOKEN = "PLACEHOLDER:"
REGISTER = os.path.join(ROOT, "PLACEHOLDERS.md")
THEME_DIR = "theme"
# The text formats a placeholder asset can use. Binary assets (the ``.png``
# wallpapers, the gzipped ``.svgz`` decoration) cannot carry a comment marker.
TEXT_EXTENSIONS = (
    ".svg",
    ".qml",
    ".colors",
    ".theme",
    ".desktop",
    ".desktoprc",
    ".json",
    ".js",
    ".kvconfig",
)
TEXT_NAMES = ("index.theme", "defaults")

# The register/marker disagreements :func:`cross_check` must reject. Each name
# is also a rejection mutation in ``tests/support/placeholders_mutations.py``; the
# guard in ``tests/test_checker_mutations.py`` fails when a name here has no
# mutation (or a mutation names a boundary that is not here).
REJECTION_SHAPES = (
    "marker-without-row",
    "row-without-file",
    "row-without-marker",
    "unreadable-register",
    "dangling-symlink-inside-theme",
    "duplicate-register-row",
)

# One register table row: ``| `path` | what it stands in for |``.
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*$")


def _is_text_asset(filename):
    """Return True when *filename* is a text format that can hold a marker."""
    return filename in TEXT_NAMES or filename.endswith(TEXT_EXTENSIONS)


def _read_text(path, root):
    """Return *path*'s text through the shared bounded containment reader.

    The guard opens the path non-blocking and ``fstat``s that same descriptor,
    so a FIFO or device is refused by name without a stat-then-open race, and
    a contributor-supplied file past its 1 MiB cap is refused instead of being
    loaded whole. Its failures are reported as the checker's own
    :class:`AssertionError` naming *path*: a non-UTF-8 file keeps the "not
    valid UTF-8" diagnostic, and an unreadable, non-regular or oversize file
    is a "cannot be read" one.
    """
    try:
        return containment.read_text(path, root, encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise AssertionError(
            escape_controls(f"{path} is not valid UTF-8 text: {exc}")
        ) from exc
    except (OSError, ValueError) as exc:
        raise AssertionError(
            escape_controls(f"{path} cannot be read: {exc}")
        ) from exc


def _marker_text(path, root):
    """Return the text after the ``PLACEHOLDER:`` token in *path*, or None.

    The marker is the token plus what it stands in for, in a comment in the
    file's own format; a trailing SVG comment terminator (``-->``) is dropped
    so the returned text is the description alone. A file that is not valid
    UTF-8 text (a binary committed under a text extension, an editor writing
    Latin-1) raises the checker's own :class:`AssertionError` naming *path*,
    instead of escaping as a codec ``UnicodeDecodeError`` that names neither
    the checker nor the file. A file that cannot be read at all -- a dangling
    symlink whose target resolves inside ``theme/``, a permission error, a
    non-regular file (a FIFO or device) or one past the guard's 1 MiB cap --
    raises the same :class:`AssertionError` naming *path*, instead of a bare
    ``OSError``, a block, or an unbounded read aborting the check.
    """
    text = _read_text(path, root)
    for line in text.split("\n"):
        index = line.find(TOKEN)
        if index == -1:
            continue
        marker = line[index + len(TOKEN):].strip()
        if marker.endswith("-->"):
            marker = marker[:-3].strip()
        return marker
    return None


def markers(root):
    """Return ``{relative path: marker text}`` for the placeholders under *root*.

    Walks ``<root>/theme`` for text assets and returns one entry per file that
    carries the ``PLACEHOLDER:`` token; a file without the token is not a
    placeholder and is omitted. ``PLACEHOLDERS.md`` is skipped so the register
    itself is never mistaken for a placeholder asset. A text asset whose
    symlink resolves outside ``<root>/theme`` raises the checker's own
    :class:`AssertionError` naming the path, so a checked-in symlink cannot
    make the read leave the theme tree.
    """
    found = {}
    theme_dir = os.path.join(root, THEME_DIR)
    for dirpath, _, filenames in os.walk(theme_dir):
        for filename in filenames:
            if filename == "PLACEHOLDERS.md" or not _is_text_asset(filename):
                continue
            path = os.path.join(dirpath, filename)
            if not containment.resolves_within(theme_dir, path):
                raise AssertionError(
                    escape_controls(
                        f"{path} points outside {theme_dir} (a symlink escape)"
                    )
                )
            text = _marker_text(path, theme_dir)
            if text is not None:
                found[os.path.relpath(path, root)] = text
    return found


def register_entries(path):
    """Return ``{asset path: what it stands in for}`` from the register table.

    A register that is not valid UTF-8 text raises the checker's own
    :class:`AssertionError` naming *path*, so a stray byte is reported as the
    register's own problem rather than as a codec ``UnicodeDecodeError``. A
    register that cannot be read at all -- a missing file, a directory, a
    permission error, a non-regular file (a FIFO or device) or one past the
    guard's 1 MiB cap -- raises the same :class:`AssertionError` naming
    *path*, instead of a bare ``OSError``, a block, or an unbounded read
    aborting the check. A register that lists one asset twice raises the same
    :class:`AssertionError` naming *path*, the asset and both rows'
    descriptions, instead of the last row silently replacing the first in the
    returned dict.
    """
    # The register's own directory is the containment root, so a symlink at
    # *path* that resolves elsewhere is refused before it is read.
    root = os.path.dirname(os.path.abspath(path))
    entries = {}
    for line in _read_text(path, root).split("\n"):
        match = ROW.match(line)
        if match:
            asset, description = match.group(1), match.group(2)
            if asset in entries:
                raise AssertionError(
                    escape_controls(
                        f"{path} has a duplicate row for {asset}: the first "
                        f"row says {entries[asset]!r}, this one says "
                        f"{description!r}; one asset gets one row"
                    )
                )
            entries[asset] = description
    return entries


def cross_check(root, register):
    """Assert *register* and the markers under *root* name the same assets.

    Returns ``(markers, entries)`` so a caller can assert more; raises
    :class:`AssertionError` naming the first disagreement: a marked file with
    no row, a row whose path is missing, a row whose file carries no marker,
    or a register that lists one asset twice.
    A checked-in symlink at *register* that resolves outside *root* raises
    ``ValueError`` before it is read, so its rows are never echoed in the
    diagnostic.
    """
    found = markers(root)
    containment.require_within_repo(register, root)
    entries = register_entries(register)
    for asset in sorted(found):
        if asset not in entries:
            raise AssertionError(
                escape_controls(
                    f"{asset} carries a {TOKEN} marker but has no row in "
                    f"{register}"
                )
            )
    for asset in sorted(entries):
        if not os.path.isfile(os.path.join(root, asset)):
            raise AssertionError(
                escape_controls(
                    f"{register} lists {asset}, which does not exist"
                )
            )
        if asset not in found:
            raise AssertionError(
                escape_controls(
                    f"{register} lists {asset}, which carries no {TOKEN} marker"
                )
            )
    return found, entries
