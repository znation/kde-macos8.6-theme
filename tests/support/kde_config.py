"""Read KDE INI files the way Plasma itself reads them.

Plasma's config format is INI-like but differs from configparser's defaults in
four ways that matter: `%` is not an interpolation character (colour and path
values may contain it literally), key names are case-sensitive, a leading
UTF-8 BOM is stripped rather than left in the first line, and each line is
trimmed before parsing, so leading whitespace never makes a section header a
value continuation or a key part of the previous value. Reading a scheme or
`defaults` file without these settings mangles values or makes configparser
reject the first section.
"""

import configparser

from support import containment
from support.repo_root import ROOT


def read(path):
    """Parse the KDE INI file at `path`; returns the ConfigParser.

    A theme INI is contributor-supplied, and a checked-in symlink can point at
    a private file; `configparser`'s errors echo the offending line, so
    following such a symlink would leak that file's content into a failing
    test's diagnostic. A path that resolves outside the repository is refused
    before it is opened.

    The file is decoded as ``utf-8-sig``, so a leading UTF-8 BOM -- which Qt's
    reader strips -- does not leave configparser looking for a section header
    that it never finds.
    """
    containment.require_within_repo(path, ROOT)
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # KDE keys are case-sensitive.
    with open(path, encoding="utf-8-sig") as handle:
        # KDE trims each line before parsing it, so an indented `[General]`
        # still opens `[General]` and an indented key is a key. configparser
        # instead reads a leading-indented line as a continuation of the
        # previous value, so feed it the lines with that whitespace removed.
        parser.read_file(
            (line.lstrip() for line in handle), source=str(path)
        )
    return parser
