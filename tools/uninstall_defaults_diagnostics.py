"""The uninstall diagnostics for the defaults layer the apply left behind.

One handler per defaults-file surface ``make apply`` wrote under
``kdedefaults``: ``ksplashrc``, the flat ``package`` name and the
``kdeglobals``, ``kwinrc`` and ``plasmarc`` mirrors. Each handler takes the
config root and the ids it needs, reads through the shared scanner in
:mod:`uninstall_config` and returns only its own warnings; the coordinator in
:mod:`uninstall_diagnostics` calls them in the recipe's order, after every
live-config handler.
"""

from __future__ import annotations

import os

if __package__:
    from tools.uninstall_config import (
        flat_text,
        read_selected_values_at,
        read_text,
    )
else:  # imported from a directly run tool
    from uninstall_config import flat_text, read_selected_values_at, read_text


def ksplashrc_messages(config_home: str, lnf_id: str) -> list[str]:
    """The splash selection the look-and-feel apply left in defaults."""
    path = os.path.join(config_home, "kdedefaults", "ksplashrc")
    splash = read_selected_values_at(path, {"KSplash": ("Theme",)})
    if splash.get(("KSplash", "Theme")) == lnf_id:
        return [
            "uninstall: the splash selection the look-and-feel apply"
            f" left in defaults still names {lnf_id} after removal in"
            f" {path}; the start splash cannot load the removed"
            " SplashQML and keeps the platform default splash. Reset it"
            f' with: kwriteconfig6 --file "{path}" --group KSplash'
            " --key Theme --delete"
        ]
    return []


def package_messages(config_home: str, lnf_id: str) -> list[str]:
    """The flat look-and-feel package name in ``kdedefaults/package``."""
    path = os.path.join(config_home, "kdedefaults", "package")
    text = read_text(path)
    if text is not None and flat_text(text) == lnf_id:
        return [
            "uninstall: the look-and-feel package default the look-and-feel"
            f" apply left in defaults still names {lnf_id} after removal in"
            f" {path}; the defaults file the apply wrote names the"
            f' removed look-and-feel package. Reset it with: rm "{path}"'
        ]
    return []


def kdedefaults_kdeglobals_messages(config_home: str, icon_theme_id: str) -> list[str]:
    """The ``kdedefaults/kdeglobals`` mirror's style and icon selections."""
    path = os.path.join(config_home, "kdedefaults", "kdeglobals")
    defaults = read_selected_values_at(
        path, {"KDE": ("widgetStyle",), "Icons": ("Theme",)}
    )
    messages: list[str] = []
    if defaults.get(("KDE", "widgetStyle")) == "kvantum":
        messages.append(
            "uninstall: the widget-style selection the look-and-feel"
            " apply left in defaults ([KDE] widgetStyle=kvantum) is"
            f" still in {path} after removal; when the live key"
            " is absent or reset away, the defaults layer re-selects the"
            " style that key names. Reset it with: kwriteconfig6"
            f' --file "{path}" --group KDE --key widgetStyle --delete'
        )
    if defaults.get(("Icons", "Theme")) == icon_theme_id:
        messages.append(
            "uninstall: the icon-theme selection the look-and-feel apply"
            f" left in defaults ([Icons] Theme={icon_theme_id}) is still"
            f" in {path} after removal; when the live key is"
            " absent or reset away, the defaults layer re-selects the"
            " removed icon theme and KDE and Qt applications keep the"
            " default icons. Reset it with: kwriteconfig6"
            f' --file "{path}" --group Icons --key Theme --delete'
        )
    return messages


def kdedefaults_kwinrc_messages(config_home: str, aurorae_id: str) -> list[str]:
    """The ``kdedefaults/kwinrc`` mirror's aurorae decoration selection."""
    path = os.path.join(config_home, "kdedefaults", "kwinrc")
    defaults = read_selected_values_at(
        path, {"org.kde.kdecoration2": ("library", "theme")}
    )
    if defaults.get(("org.kde.kdecoration2", "library")) == (
        "org.kde.kwin.aurorae"
    ) and defaults.get(("org.kde.kdecoration2", "theme")) == aurorae_id:
        return [
            "uninstall: the window-decoration selection"
            " [library=org.kde.kwin.aurorae,"
            f" theme={aurorae_id}] that the"
            " look-and-feel apply left in defaults is still in"
            f" {path}; when the live keys are absent or reset away,"
            " the defaults layer re-selects the removed"
            f" kwin/decorations/{aurorae_id} decoration package"
            " and KWin keeps a default window decoration. Reset it with:"
            f' kwriteconfig6 --file "{path}" --group'
            " org.kde.kdecoration2 --key library --delete &&"
            f' kwriteconfig6 --file "{path}" --group'
            " org.kde.kdecoration2 --key theme --delete"
        ]
    return []


def kdedefaults_plasmarc_messages(config_home: str, dtheme_id: str) -> list[str]:
    """The ``kdedefaults/plasmarc`` mirror's desktop theme selection."""
    path = os.path.join(config_home, "kdedefaults", "plasmarc")
    defaults = read_selected_values_at(path, {"Theme": ("name",)})
    if defaults.get(("Theme", "name")) == dtheme_id:
        return [
            "uninstall: the desktop theme selection the look-and-feel"
            " apply left in defaults still names"
            f" {dtheme_id} after removal in {path}; when the live"
            " key is absent or reset away, the defaults layer re-selects"
            " the removed desktop theme. Reset it with: kwriteconfig6"
            f' --file "{path}" --group Theme --key name --delete'
        ]
    return []
