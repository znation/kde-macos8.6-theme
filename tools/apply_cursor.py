"""Expose the shipped Xcursor pointer set and select it for the running session.

``make apply`` and ``make apply-cursor`` install the icon theme, which carries
the Platinum pointer set under ``cursors/``, and then run this script. Xcursor
searches ``~/.icons``, not ``$XDG_DATA_HOME/icons``, so the installed theme is
exposed at ``$HOME/.icons/org.macos8.desktop`` as a symlink and selected with
``plasma-apply-cursortheme org.macos8.desktop``. ``make remove-cursor`` runs
the same script with ``--remove``: it deletes only that link, leaving a foreign
path and ``kcminputrc`` untouched. ``--optional`` skips only the selection when
the KDE selector is absent, which is how the aggregate ``make apply`` installs
the pointer set on a desktop it cannot address.

Usage::

    python3 tools/apply_cursor.py [--optional]
    python3 tools/apply_cursor.py --remove

Exit status: 0 when the selection or removal ran, 1 when the selector failed,
2 for a usage error, an unusable ``HOME``, a missing installed theme, a
foreign path at the link target, a selector that cannot be started, a scratch
directory that cannot be created, or another install/uninstall holding the
data-home lock past the timeout, and 128 plus the signal number when a
SIGTERM or SIGHUP ends the run.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools import cursor_link
    from tools import cursor_selection
    from tools import cursor_workflow
    from tools import xdg_homes
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error
    from tools.process_group import exit_on_termination
else:  # run directly: python3 tools/apply_cursor.py
    import cursor_link
    import cursor_selection
    import cursor_workflow
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error
    from process_group import exit_on_termination

TOOL = "apply_cursor"
CURSOR_THEME = cursor_link.CURSOR_THEME
SELECT_TOOL = cursor_selection.SELECT_TOOL
CursorError = cursor_link.CursorError


def resolve_homes(env: dict[str, str]) -> tuple[Path, Path, Path]:
    """Return ``(home, data_home, config_home)`` from *env*.

    ``$HOME`` must be absolute because it is the only fallback for both XDG
    homes; a relative or unset ``HOME`` raises :class:`CursorError` naming it.
    An absolute ``$XDG_DATA_HOME`` or ``$XDG_CONFIG_HOME`` wins, otherwise the
    XDG default below ``$HOME`` is used, as ``make install`` resolves it.
    """
    home = env.get("HOME", "")
    if not os.path.isabs(home):
        state = xdg_homes.unresolved_home_state(home)
        raise CursorError(
            f"HOME is {state}; export an absolute HOME"
        )
    home_path = Path(home)
    # ``HOME`` is absolute, so both XDG fallbacks resolve to a path.
    return home_path, xdg_homes.data_home(env), xdg_homes.config_home(env)


def main(argv: list[str] | None = None) -> int:
    """Run the cursor selection CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Expose the installed Mac OS 8.6 Xcursor pointer set at the "
            "Xcursor path and select it."
        ),
        epilog=(
            "exit status: 0 when the selection or removal ran, 1 when the "
            "selector failed, 2 for a usage error, an unusable HOME, a "
            "missing installed theme, a foreign path at the link target, a "
            "selector that cannot be started, or a scratch directory that "
            "cannot be created, and 128 plus the signal number when a SIGTERM "
            "or SIGHUP ends the run"
        ),
    )
    parser.add_argument(
        "--optional",
        action="store_true",
        help="skip the selection, with a note, when plasma-apply-cursortheme is not on PATH",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our ~/.icons symlink and leave kcminputrc untouched",
    )
    args = parser.parse_args(argv)

    try:
        home, data_home, config_home = resolve_homes(dict(os.environ))
        if args.remove:
            return cursor_workflow.remove(home, data_home, config_home)
        with exit_on_termination():
            return cursor_workflow.apply(home, data_home, dict(os.environ), args.optional)
    except CursorError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
