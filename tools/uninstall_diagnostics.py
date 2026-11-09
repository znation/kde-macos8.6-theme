"""The ``uninstall`` recipe's config-file selection diagnostics.

``make uninstall`` removes the installed theme files and then reads the
running user's config-home files, without editing anything, to name the reset
for every selection ``make apply`` published that still names an id this theme
removed: a selection left behind keeps naming theme files the removal deleted,
so the application silently falls back to a default without a diagnostic, and
the warning names the reset command instead. These are diagnostics only -- they
must not edit any file, and an absent file, an unreadable one or a foreign
selection stays silent.

The config home is resolved the way the recipe resolved it: an absolute
``XDG_CONFIG_HOME`` wins; an unset, empty or relative one falls back to
``$HOME/.config``; with neither the diagnostics run nowhere.

The ini files -- ``kdeglobals``, ``Kvantum/kvantum.kvconfig``, ``plasmarc``,
``kcminputrc``, ``kwinrc``, ``kdedefaults/ksplashrc``,
``kdedefaults/kdeglobals``, ``kdedefaults/kwinrc``, ``kdedefaults/plasmarc``
and either ``settings.ini`` -- are read with :func:`read_selected_values`,
which keeps the semantics the recipe's inline awks used that
``tests/support/kde_ini_corpus.py`` pins through ``tests/test_kde_ini_parity.py``:
a leading UTF-8 BOM on the first line is stripped, each line is trimmed before
parsing, a trimmed line opening with ``[`` and closing with ``]`` opens the
bracketed section, a line whose first character is ``#`` or ``;`` is a comment
and never a key, the first ``=`` splits key and value with the key and the
value trimmed, and the last value read for a ``(section, key)`` wins. The
``gtk-theme-name`` diagnostic alone reports a match latched from any
``[Settings]`` line, as its awk did: a later foreign value never unmarks an
earlier one of ours.

``tests/test_*_uninstall_diagnostic.py`` pin every message's exact wording;
a message here must not change without changing its test.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
import os
import sys

if __package__:
    from tools.containment import open_regular_binary
else:  # imported from a directly run tool
    from containment import open_regular_binary

_BOM = "\ufeff"
_WHITESPACE = " \t\r\n\f\v"


def config_home(env: dict[str, str]) -> str | None:
    """Resolve the config home the recipe resolved, or ``None`` for none.

    An absolute ``XDG_CONFIG_HOME`` wins; an unset, empty or relative one
    falls back to ``$HOME/.config``; with no absolute file root at all there
    is nothing to read and nothing to warn about.
    """
    config_home = env.get("XDG_CONFIG_HOME", "")
    if not config_home.startswith("/"):
        config_home = ""
    if not config_home:
        home = env.get("HOME", "")
        if home.startswith("/"):
            config_home = os.path.join(home, ".config")
    return config_home or None


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
            if raw.startswith(_BOM):
                raw = raw[len(_BOM) :]
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


def _flat_text(text: str) -> str:
    """Return the text with the first line's BOM stripped and lines trimmed.

    ``kdedefaults/package`` is a flat name, so its scanner concatenates the
    trimmed lines with nothing between them, as its awk did. A BOM patch on a
    later line is a real byte there and breaks the name, as with the awk.
    """
    body = text[len(_BOM) :] if text.startswith(_BOM) else text
    return "".join(line.strip(_WHITESPACE) for line in body.split("\n"))


def _font_diagnostics(kde: dict[tuple[str, str], str], path: str) -> list[str]:
    """The five Lato warnings, one per selection the apply published."""
    diagnoses = (
        (
            ("General", "font"),
            "the font selection [General] font=Lato,10",
            "--group General --key font --delete",
            "Lato,10",
        ),
        (
            ("General", "menuFont"),
            "the font selection [General] menuFont=Lato,10",
            "--group General --key menuFont --delete",
            "Lato,10",
        ),
        (
            ("General", "toolBarFont"),
            "the font selection [General] toolBarFont=Lato,10",
            "--group General --key toolBarFont --delete",
            "Lato,10",
        ),
        (
            ("General", "smallestReadableFont"),
            "the font selection [General] smallestReadableFont=Lato,8",
            "--group General --key smallestReadableFont --delete",
            "Lato,8",
        ),
        (
            ("WM", "activeFont"),
            "the font selection [WM] activeFont=Lato,10",
            "--group WM --key activeFont --delete",
            "Lato,10",
        ),
    )
    out = []
    for (section, key), wording, reset_tail, published in diagnoses:
        if kde.get((section, key)) != published:
            continue
        out.append(
            f"uninstall: {wording} the look-and-feel apply wrote is still"
            f" in {path} after removal; KDE and Qt keep naming the Lato face"
            " the removal deleted and fall back to a default where no other"
            " copy of the family remains installed. Reset it with:"
            f" kwriteconfig6 --file kdeglobals {reset_tail}"
        )
    return out


def diagnostics(
    config_home: str,
    scheme_id: str,
    icon_theme_id: str,
    kvantum_id: str,
    gtk_id: str,
    dtheme_id: str,
    lnf_id: str,
    aurorae_id: str,
    css_marker: str,
) -> list[str]:
    """Return the diagnostics to print, in the recipe's order.

    Every argument names a selection id the apply published.
    """
    messages: list[str] = []

    kde_globals = os.path.join(config_home, "kdeglobals")
    kde_text = read_text(kde_globals)
    if kde_text is not None:
        kde = read_selected_values(
            kde_text,
            {
                "General": (
                    "ColorScheme",
                    "widgetStyle",
                    "font",
                    "menuFont",
                    "toolBarFont",
                    "smallestReadableFont",
                ),
                "WM": ("activeFont",),
                "KDE": ("widgetStyle", "LookAndFeelPackage"),
                "Icons": ("Theme",),
            },
        )
        scheme = kde.get(("General", "ColorScheme"))
        if scheme is not None and scheme == scheme_id:
            messages.append(
                f"uninstall: color scheme {scheme_id} is still selected in"
                f" {kde_globals} after removal; if KDE cannot resolve it, it"
                " falls back to BreezeLight on the next start. Reset it with:"
                " plasma-apply-colorscheme BreezeLight"
            )
        if kde.get(("KDE", "widgetStyle")) == "kvantum":
            messages.append(
                "uninstall: the widget-style selection the look-and-feel"
                " apply wrote ([KDE] widgetStyle=kvantum) is still in"
                f" {kde_globals} after removal; every Qt start keeps"
                " selecting the style that key names whether or not it still"
                " resolves. Reset it with: kwriteconfig6 --file kdeglobals"
                " --group KDE --key widgetStyle --delete"
            )
        if kde.get(("Icons", "Theme")) == icon_theme_id:
            messages.append(
                "uninstall: the icon-theme selection the look-and-feel apply"
                f" wrote ([Icons] Theme={icon_theme_id}) is still in"
                f" {kde_globals} after removal; KDE and Qt applications"
                " cannot load the removed icon theme and keep the default"
                " icons. Reset it with: kwriteconfig6 --file kdeglobals"
                " --group Icons --key Theme --delete"
            )
        messages.extend(_font_diagnostics(kde, kde_globals))
        if kde.get(("KDE", "LookAndFeelPackage")) == lnf_id:
            messages.append(
                "uninstall: the global theme the look-and-feel apply step"
                f" selected ([KDE] LookAndFeelPackage={lnf_id}) is still in"
                f" {kde_globals} after removal; Plasma keeps naming the"
                " removed global theme and draws the stock look-and-feel on"
                " the next start. Reset it with: kwriteconfig6 --file"
                " kdeglobals --group KDE --key LookAndFeelPackage --delete"
            )

    chosen = ""
    for ini in (
        os.path.join(config_home, "gtk-3.0", "settings.ini"),
        os.path.join(config_home, "gtk-4.0", "settings.ini"),
    ):
        ini_text = read_text(ini)
        if ini_text is not None and latched_match(
            ini_text, "Settings", "gtk-theme-name", gtk_id
        ):
            chosen = f"{chosen} {ini}"
    css = os.path.join(config_home, "gtk-4.0", "gtk.css")
    # The marker is ASCII, so the same bounded read_text scan the ini files
    # get finds it in the decoded text byte-for-byte; a shared-cap reader
    # cannot read this path while skipping the cap the ini reads have.
    css_text = read_text(css)
    css_first_line = css_text.splitlines()[0] if css_text else ""
    if css_first_line.removeprefix(_BOM).startswith(css_marker):
        chosen = f"{chosen} {css}"
    if chosen:
        messages.append(
            f"uninstall: a GTK selection still names {gtk_id} after removal"
            f" in{chosen}; GTK applications cannot load the removed theme"
            " and keep their default style. Clear it with: make remove-gtk"
        )

    kvconfig = os.path.join(config_home, "Kvantum", "kvantum.kvconfig")
    kvconfig_text = read_text(kvconfig)
    if kvconfig_text is not None:
        kvantum = read_selected_values(kvconfig_text, {"General": ("theme",)})
        if kvantum.get(("General", "theme")) == kvantum_id:
            messages.append(
                f"uninstall: the Kvantum selection still names {kvantum_id}"
                f" after removal in {kvconfig}; Kvantum applications cannot"
                " load the removed theme and keep their default style."
                " Clear it with: make remove-kvantum"
            )

    plasmarc = os.path.join(config_home, "plasmarc")
    plasmarc_text = read_text(plasmarc)
    if plasmarc_text is not None:
        desktop = read_selected_values(plasmarc_text, {"Theme": ("name",)})
        if desktop.get(("Theme", "name")) == dtheme_id:
            messages.append(
                "uninstall: the desktop theme selection still names"
                f" {dtheme_id} after removal in {plasmarc}; Plasma cannot"
                " load the removed desktop theme and keeps the default"
                " style. Reset it with: plasma-apply-desktoptheme breeze"
            )

    kcminputrc = os.path.join(config_home, "kcminputrc")
    kcminputrc_text = read_text(kcminputrc)
    if kcminputrc_text is not None:
        mouse = read_selected_values(kcminputrc_text, {"Mouse": ("cursorTheme",)})
        if mouse.get(("Mouse", "cursorTheme")) == icon_theme_id:
            messages.append(
                "uninstall: the pointer selection still names"
                f" {icon_theme_id} after removal in {kcminputrc}; Xcursor"
                " applications cannot load the removed cursor theme and"
                " keep the default pointer. Reset it with:"
                " plasma-apply-cursortheme breeze_cursors"
            )

    kwinrc = os.path.join(config_home, "kwinrc")
    kwinrc_text = read_text(kwinrc)
    if kwinrc_text is not None:
        deco = read_selected_values(
            kwinrc_text,
            {"org.kde.kdecoration2": ("ButtonsOnLeft", "ButtonsOnRight", "library", "theme")},
        )
        curtain = deco.get(("org.kde.kdecoration2", "ButtonsOnLeft"))
        if curtain == "X" and deco.get(
            ("org.kde.kdecoration2", "ButtonsOnRight")
        ) == "AL":
            messages.append(
                "uninstall: the window-button layout"
                " [ButtonsOnLeft=X, ButtonsOnRight=AL] that make apply wrote"
                f" is still in {kwinrc}; KWin keeps that layout under the"
                " default decoration after removal. Reset it with:"
                " kwriteconfig6 --file kwinrc --group org.kde.kdecoration2"
                " --key ButtonsOnLeft --delete && kwriteconfig6 --file"
                " kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight"
                " --delete"
            )
        library = deco.get(("org.kde.kdecoration2", "library"))
        theme = deco.get(("org.kde.kdecoration2", "theme"))
        if library == "org.kde.kwin.aurorae" and theme == aurorae_id:
            messages.append(
                "uninstall: the window-decoration selection"
                f" [library=org.kde.kwin.aurorae, theme={aurorae_id}] that"
                f" the look-and-feel apply wrote is still in {kwinrc};"
                " KWin cannot load the removed"
                f" kwin/decorations/{aurorae_id} decoration package and"
                " keeps a default window decoration. Reset it with:"
                " kwriteconfig6 --file kwinrc --group org.kde.kdecoration2"
                " --key library --delete && kwriteconfig6 --file kwinrc"
                " --group org.kde.kdecoration2 --key theme --delete"
            )
        if theme == aurorae_id:
            messages.append(
                "uninstall: the window-decoration selection still names"
                f" {aurorae_id} after removal in {kwinrc};"
                " KWin cannot load the removed"
                f" kwin/decorations/{aurorae_id} decoration package and"
                " keeps the default style. Reset it with: kwriteconfig6"
                " --file kwinrc --group org.kde.kdecoration2 --key theme"
                " --delete && kwriteconfig6 --file kwinrc --group"
                " org.kde.kdecoration2 --key library --delete"
            )

    ksplash = os.path.join(config_home, "kdedefaults", "ksplashrc")
    ksplash_text = read_text(ksplash)
    if ksplash_text is not None:
        splash = read_selected_values(ksplash_text, {"KSplash": ("Theme",)})
        if splash.get(("KSplash", "Theme")) == lnf_id:
            messages.append(
                "uninstall: the splash selection the look-and-feel apply"
                f" left in defaults still names {lnf_id} after removal in"
                f" {ksplash}; the start splash cannot load the removed"
                " SplashQML and keeps the platform default splash. Reset it"
                f" with: kwriteconfig6 --file {ksplash} --group KSplash"
                " --key Theme --delete"
            )

    package = os.path.join(config_home, "kdedefaults", "package")
    package_text = read_text(package)
    if package_text is not None and _flat_text(package_text) == lnf_id:
        messages.append(
            "uninstall: the look-and-feel package default the look-and-feel"
            f" apply left in defaults still names {lnf_id} after removal in"
            f" {package}; the defaults file the apply wrote names the"
            f' removed look-and-feel package. Reset it with: rm "{package}"'
        )

    df_kdeglobals = os.path.join(config_home, "kdedefaults", "kdeglobals")
    df_text = read_text(df_kdeglobals)
    if df_text is not None:
        df = read_selected_values(
            df_text, {"KDE": ("widgetStyle",), "Icons": ("Theme",)}
        )
        if df.get(("KDE", "widgetStyle")) == "kvantum":
            messages.append(
                "uninstall: the widget-style selection the look-and-feel"
                " apply left in defaults ([KDE] widgetStyle=kvantum) is"
                f" still in {df_kdeglobals} after removal; when the live key"
                " is absent or reset away, the defaults layer re-selects the"
                " style that key names. Reset it with: kwriteconfig6 --file"
                f" {df_kdeglobals} --group KDE --key widgetStyle --delete"
            )
        if df.get(("Icons", "Theme")) == icon_theme_id:
            messages.append(
                "uninstall: the icon-theme selection the look-and-feel apply"
                f" left in defaults ([Icons] Theme={icon_theme_id}) is still"
                f" in {df_kdeglobals} after removal; when the live key is"
                " absent or reset away, the defaults layer re-selects the"
                " removed icon theme and KDE and Qt applications keep the"
                " default icons. Reset it with: kwriteconfig6 --file"
                f" {df_kdeglobals} --group Icons --key Theme --delete"
            )

    df_kwinrc = os.path.join(config_home, "kdedefaults", "kwinrc")
    df_winrc_text = read_text(df_kwinrc)
    if df_winrc_text is not None:
        df = read_selected_values(
            df_winrc_text, {"org.kde.kdecoration2": ("library", "theme")}
        )
        if df.get(("org.kde.kdecoration2", "library")) == (
            "org.kde.kwin.aurorae"
        ) and df.get(("org.kde.kdecoration2", "theme")) == aurorae_id:
            messages.append(
                "uninstall: the window-decoration selection"
                " [library=org.kde.kwin.aurorae,"
                f" theme={aurorae_id}] that the"
                " look-and-feel apply left in defaults is still in"
                f" {df_kwinrc}; when the live keys are absent or reset away,"
                " the defaults layer re-selects the removed"
                f" kwin/decorations/{aurorae_id} decoration package"
                " and KWin keeps a default window decoration. Reset it with:"
                f" kwriteconfig6 --file {df_kwinrc} --group"
                " org.kde.kdecoration2 --key library --delete &&"
                f" kwriteconfig6 --file {df_kwinrc} --group"
                " org.kde.kdecoration2 --key theme --delete"
            )

    df_plasmarc = os.path.join(config_home, "kdedefaults", "plasmarc")
    df_plasmarc_text = read_text(df_plasmarc)
    if df_plasmarc_text is not None:
        df = read_selected_values(df_plasmarc_text, {"Theme": ("name",)})
        if df.get(("Theme", "name")) == dtheme_id:
            messages.append(
                "uninstall: the desktop theme selection the look-and-feel"
                " apply left in defaults still names"
                f" {dtheme_id} after removal in {df_plasmarc}; when the live"
                " key is absent or reset away, the defaults layer re-selects"
                " the removed desktop theme. Reset it with: kwriteconfig6"
                f" --file {df_plasmarc} --group Theme --key name --delete"
            )

    return messages


def main(argv: list[str] | None = None) -> int:
    """Print the diagnostics for the running environment; always succeed."""
    parser = argparse.ArgumentParser(
        description="print the uninstall recipe's selection diagnostics"
    )
    parser.add_argument("--scheme-id", required=True)
    parser.add_argument("--icon-id", required=True)
    parser.add_argument("--kvantum-id", required=True)
    parser.add_argument("--gtk-id", required=True)
    parser.add_argument("--desktop-id", required=True)
    parser.add_argument("--lnf-id", required=True)
    parser.add_argument("--aurorae-id", required=True)
    parser.add_argument("--css-marker", required=True)
    args = parser.parse_args(argv)
    root = config_home(dict(os.environ))
    if root is not None:
        messages = diagnostics(
            root,
            args.scheme_id,
            args.icon_id,
            args.kvantum_id,
            args.gtk_id,
            args.desktop_id,
            args.lnf_id,
            args.aurorae_id,
            args.css_marker,
        )
        for message in messages:
            print(message, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
