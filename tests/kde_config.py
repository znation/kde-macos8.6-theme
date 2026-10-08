"""Read KDE INI files the way Plasma itself reads them.

Plasma's config format is INI-like but differs from configparser's defaults in
two ways that matter: `%` is not an interpolation character (colour and path
values may contain it literally), and key names are case-sensitive. Reading a
scheme or `defaults` file without these settings silently mangles values.
"""

import configparser


def read(path):
    """Parse the KDE INI file at `path`; returns the ConfigParser."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # KDE keys are case-sensitive.
    with open(path, encoding="utf-8") as handle:
        parser.read_file(handle)
    return parser
