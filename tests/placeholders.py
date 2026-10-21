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
"""

from __future__ import annotations

import os
import re
import stat

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
)

# One register table row: ``| `path` | what it stands in for |``.
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*$")


def _is_text_asset(filename):
    """Return True when *filename* is a text format that can hold a marker."""
    return filename in TEXT_NAMES or filename.endswith(TEXT_EXTENSIONS)


def _refuse_non_regular(path):
    """Raise :class:`AssertionError` unless *path* is a regular file.

    ``os.walk`` lists a FIFO or device named like a text asset in the theme
    tree, and ``open()`` on a FIFO blocks until a writer appears while a
    device can stream forever: neither wait has a timeout, so one such entry
    would stall ``make check`` with no diagnostic. Refuse it by name before
    opening it. ``os.stat`` follows a symlink, so a link to a regular file
    inside ``theme/`` is still read, and a dangling link or permission error
    is reported as the same "cannot be read" diagnostic the open would give.
    """
    try:
        mode = os.stat(path).st_mode
    except OSError as exc:
        raise AssertionError(
            escape_controls(f"{path} cannot be read: {exc}")
        ) from exc
    if not stat.S_ISREG(mode):
        raise AssertionError(
            escape_controls(
                f"{path} cannot be read: not a regular file; refusing to "
                "open it"
            )
        )


def _marker_text(path):
    """Return the text after the ``PLACEHOLDER:`` token in *path*, or None.

    The marker is the token plus what it stands in for, in a comment in the
    file's own format; a trailing SVG comment terminator (``-->``) is dropped
    so the returned text is the description alone. A file that is not valid
    UTF-8 text (a binary committed under a text extension, an editor writing
    Latin-1) raises the checker's own :class:`AssertionError` naming *path*,
    instead of escaping as a codec ``UnicodeDecodeError`` that names neither
    the checker nor the file. A file that cannot be read at all -- a dangling
    symlink whose target resolves inside ``theme/``, a permission error --
    raises the same :class:`AssertionError` naming *path*, instead of a bare
    ``OSError`` aborting the check. A non-regular file (a FIFO or device) is
    refused by name without being opened, since opening one can block forever.
    """
    _refuse_non_regular(path)
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                index = line.find(TOKEN)
                if index == -1:
                    continue
                text = line[index + len(TOKEN):].strip()
                if text.endswith("-->"):
                    text = text[:-3].strip()
                return text
    except UnicodeDecodeError as exc:
        raise AssertionError(
            escape_controls(f"{path} is not valid UTF-8 text: {exc}")
        ) from exc
    except OSError as exc:
        raise AssertionError(
            escape_controls(f"{path} cannot be read: {exc}")
        ) from exc
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
            text = _marker_text(path)
            if text is not None:
                found[os.path.relpath(path, root)] = text
    return found


def register_entries(path):
    """Return ``{asset path: what it stands in for}`` from the register table.

    A register that is not valid UTF-8 text raises the checker's own
    :class:`AssertionError` naming *path*, so a stray byte is reported as the
    register's own problem rather than as a codec ``UnicodeDecodeError``. A
    register that cannot be read at all -- a missing file, a directory, a
    permission error -- raises the same :class:`AssertionError` naming *path*,
    instead of a bare ``OSError`` aborting the check. A non-regular register
    (a FIFO or device) is refused by name without being opened, since opening
    one can block forever.
    """
    _refuse_non_regular(path)
    entries = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                match = ROW.match(line)
                if match:
                    entries[match.group(1)] = match.group(2)
    except UnicodeDecodeError as exc:
        raise AssertionError(
            escape_controls(f"{path} is not valid UTF-8 text: {exc}")
        ) from exc
    except OSError as exc:
        raise AssertionError(
            escape_controls(f"{path} cannot be read: {exc}")
        ) from exc
    return entries


def cross_check(root, register):
    """Assert *register* and the markers under *root* name the same assets.

    Returns ``(markers, entries)`` so a caller can assert more; raises
    :class:`AssertionError` naming the first disagreement: a marked file with
    no row, a row whose path is missing, or a row whose file carries no marker.
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
