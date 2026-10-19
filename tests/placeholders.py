"""Read PLACEHOLDERS.md and the shipped theme's placeholder markers.

The user answered 2026-10-18 that the theme's own artwork was to ship as
placeholders for now and that every one must be tracked "so we don't forget to
replace them all eventually". A placeholder asset carries the literal token
``PLACEHOLDER:`` in a comment in its own file format, naming what it stands in
for; the register ``PLACEHOLDERS.md`` holds one table row per asset.
:func:`markers` reads the markers under ``theme/`` and :func:`register_entries`
reads the register, and :func:`cross_check` fails when the two disagree: a
marked file with no row, a row whose path is missing, or a row whose file
carries no marker.

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
    so the returned text is the description alone.
    """
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            index = line.find(TOKEN)
            if index == -1:
                continue
            text = line[index + len(TOKEN):].strip()
            if text.endswith("-->"):
                text = text[:-3].strip()
            return text
    return None


def markers(root):
    """Return ``{relative path: marker text}`` for the placeholders under *root*.

    Walks ``<root>/theme`` for text assets and returns one entry per file that
    carries the ``PLACEHOLDER:`` token; a file without the token is not a
    placeholder and is omitted. ``PLACEHOLDERS.md`` is skipped so the register
    itself is never mistaken for a placeholder asset.
    """
    found = {}
    for dirpath, _, filenames in os.walk(os.path.join(root, THEME_DIR)):
        for filename in filenames:
            if filename == "PLACEHOLDERS.md" or not _is_text_asset(filename):
                continue
            path = os.path.join(dirpath, filename)
            text = _marker_text(path)
            if text is not None:
                found[os.path.relpath(path, root)] = text
    return found


def register_entries(path):
    """Return ``{asset path: what it stands in for}`` from the register table."""
    entries = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            match = ROW.match(line)
            if match:
                entries[match.group(1)] = match.group(2)
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
