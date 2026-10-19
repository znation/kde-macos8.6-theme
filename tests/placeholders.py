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

from support.repo_root import ROOT

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
# is also a rejection mutation in ``tests/support/checker_mutations.py``; the
# guard in ``tests/test_checker_mutations.py`` fails when a name here has no
# mutation (or a mutation names a boundary that is not here).
REJECTION_SHAPES = (
    "marker-without-row",
    "row-without-file",
    "row-without-marker",
)

# One register table row: ``| `path` | what it stands in for |``.
ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|\s*$")


def _is_text_asset(filename):
    """Return True when *filename* is a text format that can hold a marker."""
    return filename in TEXT_NAMES or filename.endswith(TEXT_EXTENSIONS)


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
    ``OSError`` aborting the check.
    """
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
        raise AssertionError(f"{path} is not valid UTF-8 text: {exc}") from exc
    except OSError as exc:
        raise AssertionError(f"{path} cannot be read: {exc}") from exc
    return None


def _resolves_within(directory, path):
    """Return True when *path* resolves to a location inside *directory*.

    ``theme/`` is contributor-supplied, and a checked-in symlink can point
    anywhere on the machine: a symlink in ``theme/`` named like a text asset,
    aimed at a private file, would make the checker read that file's lines as
    a placeholder marker and hand its text to a failing assertion's
    diagnostic. Resolving both paths
    keeps every read inside the theme directory even when a symlink tries to
    leave it. A resolution that fails is not assumed to be contained: an
    ``OSError`` (a filesystem failure) and a ``RuntimeError`` (a symlink loop)
    both make this return False, so the caller reports the path instead of the
    exception aborting the check.
    """
    try:
        resolved = os.path.realpath(path)
        base = os.path.realpath(directory)
    except (OSError, RuntimeError):
        return False
    return resolved == base or resolved.startswith(base + os.sep)


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
            if not _resolves_within(theme_dir, path):
                raise AssertionError(
                    f"{path} points outside {theme_dir} (a symlink escape)"
                )
            text = _marker_text(path)
            if text is not None:
                found[os.path.relpath(path, root)] = text
    return found


def register_entries(path):
    """Return ``{asset path: what it stands in for}`` from the register table.

    A register that is not valid UTF-8 text raises the checker's own
    :class:`AssertionError` naming *path*, so a stray byte is reported as the
    register's own problem rather than as a codec ``UnicodeDecodeError``.
    """
    entries = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                match = ROW.match(line)
                if match:
                    entries[match.group(1)] = match.group(2)
    except UnicodeDecodeError as exc:
        raise AssertionError(f"{path} is not valid UTF-8 text: {exc}") from exc
    return entries


def cross_check(root, register):
    """Assert *register* and the markers under *root* name the same assets.

    Returns ``(markers, entries)`` so a caller can assert more; raises
    :class:`AssertionError` naming the first disagreement: a marked file with
    no row, a row whose path is missing, or a row whose file carries no marker.
    """
    found = markers(root)
    entries = register_entries(register)
    for asset in sorted(found):
        if asset not in entries:
            raise AssertionError(
                f"{asset} carries a {TOKEN} marker but has no row in {register}"
            )
    for asset in sorted(entries):
        if not os.path.isfile(os.path.join(root, asset)):
            raise AssertionError(f"{register} lists {asset}, which does not exist")
        if asset not in found:
            raise AssertionError(
                f"{register} lists {asset}, which carries no {TOKEN} marker"
            )
    return found, entries
