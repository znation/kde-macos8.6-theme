"""Render a themed Plasma surface headlessly and capture it as a PNG.

Starts a virtual KWin Wayland session with no display server, applies the
Mac OS 8.6 theme inside it, opens the selected mode's client (a Plasma applet
window, a dialog, the shell that draws the menu bar, or the startup splash)
and screenshots the
output, producing the candidate image ``tools/fidelity.py`` compares against a
reference screenshot.

Everything runs against a throwaway scratch root: ``make install`` targets its
``data/`` directory, and the window decoration and desktop theme keys that the
global theme's ``contents/defaults`` names are written to its ``cfg/``. The
user's real configuration and session are never touched, and the scratch root
is removed afterwards.

Usage::

    python3 tools/render_surface.py OUTPUT [--applet ID] [--width W]
        [--height H] [--settle SECONDS] [--timeout SECONDS]
        [--checkbox-dialog | --combobox-dialog | --color-dialog
        | --icon-dialog | --inactive-dialog | --lineedit-dialog
        | --menu-dialog | --radiolist-dialog
        | --calendar-dialog | --progressbar-dialog | --slider-dialog
        | --textbox-dialog | --gtk-dialog | --file-dialog]
        [--desktop] [--splash]

Exit status: 0 when OUTPUT was written, 1 when the render or capture failed,
2 for a usage error, an unwritable OUTPUT, a missing external tool, a missing
applet package, a command
this tool starts directly (``make`` or ``dbus-run-session``) that cannot be
started, or a scratch session directory that cannot be created, and 128 plus
the signal number when a SIGTERM or SIGHUP ends the run.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__:
    from tools.diagnostics import report_error, report_missing_tool
    from tools.process_signals import exit_on_termination
    from tools.render_applet import applet_problem
    from tools.render_output import output_problem
    from tools.render_surface_options import REQUIRED_TOOLS, parse_options
    from tools.render_workflow import render
else:  # run directly: python3 tools/render_surface.py
    from diagnostics import report_error, report_missing_tool
    from process_signals import exit_on_termination
    from render_applet import applet_problem
    from render_output import output_problem
    from render_surface_options import REQUIRED_TOOLS, parse_options
    from render_workflow import render

TOOL = "render_surface"


def main(argv: list[str] | None = None) -> int:
    """Run the render CLI; *argv* is the argument list without a program name."""
    args, requirements = parse_options(argv)
    missing = report_missing_tool(TOOL, requirements)
    if missing is not None:
        return missing
    if requirements == REQUIRED_TOOLS:
        # An applet package is not a command, so report_missing_tool cannot
        # see its absence: the default calculator render would otherwise
        # waste a full scratch session on a capture that never paints and
        # times out. The dialog modes and the desktop capture open their own
        # clients and never touch the applet, so they skip this check.
        applet = applet_problem(args.applet)
        if applet is not None:
            return report_error(TOOL, applet)
    problem = output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return render(args)


if __name__ == "__main__":
    sys.exit(main())
