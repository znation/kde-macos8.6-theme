"""Read KDE INI files the way Plasma itself reads them.

Plasma's config format is INI-like but differs from configparser's defaults in
six ways that matter: `%` is not an interpolation character (colour and path
values may contain it literally), key names are case-sensitive, a leading
UTF-8 BOM is stripped rather than left in the first line, each line is trimmed
before parsing, `=` is the only key/value delimiter (a colon-delimited line is
an invalid entry KDE skips, not a key), and a later duplicate key overrides an
earlier one. Reading a scheme or `defaults` file without these settings
mangles values or makes configparser reject a file KDE accepts.
"""

import configparser
import io

from support import containment
from support.repo_root import ROOT


def _parseable_lines(handle):
    """Yield KDE-trimmed lines, dropping entries KDE skips as invalid.

    KDE trims each line before parsing it. A non-comment, non-heading line
    with no ``=`` is an invalid entry that KDE logs and ignores; configparser
    would instead reject the whole file. A colon-delimited line
    (``ColorScheme:MacOS8``) is one of those entries: ``=`` is the only
    delimiter KDE accepts, so dropping it keeps the colon from becoming a key
    value the other readers never see. A line that opens a heading but never
    closes it (``[General``) is likewise invalid: KDE ignores the line and
    keeps the section that was already open, so dropping it leaves a
    following key in that section. A key before the first heading is not
    invalid: KDE files it in the ``<default>`` root group, so a synthetic
    heading of that name is emitted before the first such key to keep it in
    the parser. An empty heading (``[]``) opens a group of its own; since
    configparser has no empty section name, its key lines are dropped so they
    cannot join the previous group. Only a leading ``#`` is a comment, so a
    ``;`` line is left for configparser's ``comment_prefixes`` (set to ``#``
    alone in `read`) to parse as KDE does.
    """
    mode = "root"
    root_open = False
    for raw in handle:
        line = raw.lstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("["):
            if "]" not in stripped:
                continue
            name = stripped[1:stripped.index("]")]
            if name:
                mode = "section"
                yield line
            else:
                mode = "skip"
            continue
        if "=" not in stripped:
            continue
        if mode == "section":
            yield line
        elif mode == "root":
            if not root_open:
                yield "[<default>]\n"
                root_open = True
            yield line


def read(path):
    """Parse the KDE INI file at `path`; returns the ConfigParser.

    A theme INI is contributor-supplied, and a checked-in symlink can point at
    a private file; `configparser`'s errors echo the offending line, so
    following such a symlink would leak that file's content into a failing
    test's diagnostic. A path that resolves outside the repository is refused
    before it is opened.

    The file is read through the shared containment reader, so a FIFO or
    device is refused instead of blocking, and decoded as ``utf-8-sig``, so a
    leading UTF-8 BOM -- which Qt's reader strips -- does not leave
    configparser looking for a section header that it never finds.
    """
    text = containment.read_text(path, ROOT, encoding="utf-8-sig")
    parser = configparser.ConfigParser(
        interpolation=None,
        delimiters=("=",),
        comment_prefixes=("#",),
        strict=False,
    )
    parser.optionxform = str  # KDE keys are case-sensitive.
    # KDE trims each line before parsing it, so an indented `[General]`
    # still opens `[General]` and an indented key is a key. configparser
    # instead reads a leading-indented line as a continuation of the
    # previous value, so `_parseable_lines` feeds it the lines with that
    # whitespace removed, minus the invalid entries KDE skips.
    parser.read_file(_parseable_lines(io.StringIO(text)), source=str(path))
    return parser
