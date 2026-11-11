"""The ``uninstall`` recipe's diagnostics-only config scanner.

``make uninstall`` reads the running user's config-home files, without
editing anything, to name the reset for every selection ``make apply``
published that still names an id this theme removed. This module holds the
shared parse state every uninstall diagnostic builds on: the config-home
resolution the recipe resolved, the bounded read config files get, and the
INI scanning the ini diagnostics share. These are diagnostics only -- they
must not edit any file, and an absent file, an unreadable one or a foreign
selection stays silent.

The config home is resolved the way the recipe resolved it: an absolute
``XDG_CONFIG_HOME`` wins; an unset, empty or relative one falls back to
``$HOME/.config``; with neither the diagnostics run nowhere.

The ini files the diagnostics read -- ``kdeglobals``,
``Kvantum/kvantum.kvconfig``, ``plasmarc``, ``kcminputrc``, ``kwinrc``,
``kdedefaults/ksplashrc``, ``kdedefaults/kdeglobals``,
``kdedefaults/kwinrc``, ``kdedefaults/plasmarc`` and either
``settings.ini`` -- are read with :func:`read_selected_values`, which keeps
the semantics the recipe's inline awks used that
``tests/support/kde_ini_corpus.py`` pins through ``tests/test_kde_ini_parity.py``:
a leading UTF-8 BOM on the first line is stripped, each line is trimmed before
parsing, a trimmed line opening with ``[`` and closing with ``]`` opens the
bracketed section, a line whose first character is ``#`` or ``;`` is a comment
and never a key, the first ``=`` splits key and value with the key and the
value trimmed, and the last value read for a ``(section, key)`` wins. The
``gtk-theme-name`` diagnostic alone reports a match latched from any
``[Settings]`` line, as its awk did: a later foreign value never unmarks an
earlier one of ours.
"""

from __future__ import annotations

from collections.abc import Iterator

if __package__:
    from tools.containment import open_regular_binary
    from tools.text_lines import strip_bom
    from tools.xdg_homes import config_home as resolve_config_home
else:  # imported from a directly run tool
    from containment import open_regular_binary
    from text_lines import strip_bom
    from xdg_homes import config_home as resolve_config_home

_WHITESPACE = " \t\r\n\f\v"


def config_home(env: dict[str, str]) -> str | None:
    """Resolve the config home the recipe resolved, or ``None`` for none.

    An absolute ``XDG_CONFIG_HOME`` wins; an unset, empty or relative one
    falls back to ``$HOME/.config``; with no absolute file root at all there
    is nothing to read and nothing to warn about. The rule itself is
    :func:`tools.xdg_homes.config_home`'s, the one resolver every tool shares;
    this wrapper only re-states it as the plain string the diagnostics join
    their config-file paths onto.
    """
    resolved = resolve_config_home(env)
    return str(resolved) if resolved is not None else None


# A config file is a small settings file the running user owns, so the
# diagnostics-only reader applies the same 1 MiB cap every other bounded read
# here applies (``reference_sources``' sources.txt, ``theme_defaults``' defaults
# file, ``gtk_user_files``' settings and CSS, the Firefox profile files):
# a file bigger than that is unreadable for these warnings' purposes instead
# of being loaded whole.
_MAX_CONFIG_BYTES = 1 << 20


def read_text(path: str) -> str | None:
    """Return the file's text, or ``None`` when absent, unreadable or over the cap.

    Unmappable bytes are kept as surrogate escapes so a foreign file is not
    silently empty; an unmapped value never matches one of the ids. At most
    one byte past the cap is read, so a config file grown (or left corrupt by
    another tool) larger than :data:`_MAX_CONFIG_BYTES` cannot exhaust memory
    inside this diagnostics-only reader, which must always succeed; at the
    cap exactly the file is read whole and parsed. An over-cap file is
    unreadable in the sense the module contract pins -- its selections are
    left silent -- because reading a prefix and parsing it could compare a
    selection against a value the cap cut short and misreport one that the
    whole file would have named differently.

    The path is opened through :func:`containment.open_regular_binary`, as
    every other bounded reader here opens its files: the check runs on the
    opened descriptor, so a regular file swapped for a FIFO between a path
    check and the open of a blocking ``open()`` cannot hang the run waiting
    for a writer that never comes, and a FIFO or device is left unread and
    silent like any other unreadable file.
    """
    try:
        with open_regular_binary(path) as handle:
            data = handle.read(_MAX_CONFIG_BYTES + 1)
    except (OSError, ValueError):
        return None
    if len(data) > _MAX_CONFIG_BYTES:
        return None
    return data.decode("utf-8", errors="surrogateescape")


def _ini_entries(text: str) -> Iterator[tuple[str | None, str, str]]:
    """Yield each key line's ``(section, key, value)`` after trimming.

    One parse of the shared corpus rules (see the module docstring), so every
    consumer filters the same key lines: a key line before any section yields
    a ``None`` section the per-section consumers drop.
    """
    section: str | None = None
    first = True
    for raw in text.splitlines():
        if first:
            first = False
            raw = strip_bom(raw)
        line = raw.strip(_WHITESPACE)
        if len(line) >= 2 and line[0] == "[" and line[-1] == "]":
            section = line[1:-1].strip(_WHITESPACE)
            continue
        if not line or line[0] in "#;":
            continue
        separator = line.find("=")
        if separator <= 0:
            continue
        key = line[:separator].rstrip(_WHITESPACE)
        yield (section, key, line[separator + 1 :].strip(_WHITESPACE))


def read_selected_values(
    text: str, wanted: dict[str, tuple[str, ...]]
) -> dict[tuple[str, str], str]:
    """Return the ``wanted`` sections' last ``(section, key)`` values.

    *wanted* maps a section name to the keys to keep; a key outside its
    section's tuple is dropped. See the module docstring for the parse rules.
    """
    values: dict[tuple[str, str], str] = {}
    for section, key, value in _ini_entries(text):
        if section in wanted and key in wanted[section]:
            values[(section, key)] = value
    return values


def read_selected_values_at(
    path: str, wanted: dict[str, tuple[str, ...]]
) -> dict[tuple[str, str], str]:
    """Read and select INI values at *path*, returning empty when unavailable."""
    text = read_text(path)
    return read_selected_values(text, wanted) if text is not None else {}


def latched_match(text: str, section: str, key: str, expected: str) -> bool:
    """Report whether any ``[section] key=<expected>`` line stands.

    The GTK settings diagnostic latched its match on each line: an early
    ``gtk-theme-name`` of ours marks the file even when a later line renames
    the selection again -- only ``[section]`` lines set it, and a section
    switch or a later duplicate never unmarks it. The last-wins lookup rule
    the :func:`read_selected_values` diagnostics share does not hold here, so
    this scans the shared parse for any matching entry instead of keeping one
    value.
    """
    return any(
        entry_section == section and entry_key == key and value == expected
        for entry_section, entry_key, value in _ini_entries(text)
    )


def flat_text(text: str) -> str:
    """Return the text with the first line's BOM stripped and lines trimmed.

    ``kdedefaults/package`` is a flat name, so its scanner concatenates the
    trimmed lines with nothing between them, as its awk did. A BOM patch on a
    later line is a real byte there and breaks the name, as with the awk.
    """
    body = strip_bom(text)
    return "".join(line.strip(_WHITESPACE) for line in body.split("\n"))
