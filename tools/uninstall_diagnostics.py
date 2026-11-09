"""The ``uninstall`` recipe's config-file selection diagnostics.

``make uninstall`` removes the installed theme files and then reads the
running user's config-home files, without editing anything, to name the reset
for every selection ``make apply`` published that still names an id this theme
removed: a selection left behind keeps naming theme files the removal deleted,
so the application silently falls back to a default without a diagnostic, and
the warning names the reset command instead. These are diagnostics only -- they
must not edit any file, and an absent file, an unreadable one or a foreign
selection stays silent.

The parse state every diagnostic builds on -- the config-home resolution, the
bounded read and the INI scanning -- lives in
:mod:`uninstall_config` and keeps the semantics
``tests/support/kde_ini_corpus.py`` pins through ``tests/test_kde_ini_parity.py``.
The handlers for the live config files live in
:mod:`uninstall_live_diagnostics`, the handlers for the
``kdedefaults`` layer in :mod:`uninstall_defaults_diagnostics`; this module is
the command line and the ordered coordinator.

``tests/test_*_uninstall_diagnostic.py`` pin every message's exact wording;
a message here must not change without changing its test.
"""

from __future__ import annotations

import os
import sys

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.terminal import escape_controls
    from tools.uninstall_config import config_home
    from tools.uninstall_defaults_diagnostics import (
        kdedefaults_kdeglobals_messages,
        kdedefaults_kwinrc_messages,
        kdedefaults_plasmarc_messages,
        ksplashrc_messages,
        package_messages,
    )
    from tools.uninstall_live_diagnostics import (
        gtk_messages,
        kdeglobals_messages,
        kcminputrc_messages,
        kwinrc_messages,
        kvantum_messages,
        plasmarc_messages,
    )
else:  # imported from a directly run tool
    from argument_parsing import EscapingArgumentParser
    from terminal import escape_controls
    from uninstall_config import config_home
    from uninstall_defaults_diagnostics import (
        kdedefaults_kdeglobals_messages,
        kdedefaults_kwinrc_messages,
        kdedefaults_plasmarc_messages,
        ksplashrc_messages,
        package_messages,
    )
    from uninstall_live_diagnostics import (
        gtk_messages,
        kdeglobals_messages,
        kcminputrc_messages,
        kwinrc_messages,
        kvantum_messages,
        plasmarc_messages,
    )


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

    Every handler covers one config surface; the calls keep the exact order
    the recipe's scan always printed: the live files first, then the
    defaults layer the look-and-feel apply wrote.
    """
    return [
        *kdeglobals_messages(config_home, scheme_id, icon_theme_id, lnf_id),
        *gtk_messages(config_home, gtk_id, css_marker),
        *kvantum_messages(config_home, kvantum_id),
        *plasmarc_messages(config_home, dtheme_id),
        *kcminputrc_messages(config_home, icon_theme_id),
        *kwinrc_messages(config_home, aurorae_id),
        *ksplashrc_messages(config_home, lnf_id),
        *package_messages(config_home, lnf_id),
        *kdedefaults_kdeglobals_messages(config_home, icon_theme_id),
        *kdedefaults_kwinrc_messages(config_home, aurorae_id),
        *kdedefaults_plasmarc_messages(config_home, dtheme_id),
    ]


def main(argv: list[str] | None = None) -> int:
    """Print the diagnostics for the running environment; always succeed."""
    parser = EscapingArgumentParser(
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
            # The diagnostics contract routes contributor-supplied text
            # (the ids on the command line, the config-home path from the
            # environment, and the offsets the handlers embed in a
            # message) through the terminal escaper before it reaches
            # stderr; a control character in any of them must never drive
            # this operator's terminal directly.
            print(escape_controls(message), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
