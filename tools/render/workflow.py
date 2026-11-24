"""Run the headless render lifecycle after CLI validation."""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__.startswith("tools"):
    from tools.diagnostics import report_error, report_failure
    from tools.png import PngError, read_png
    from tools.process_group import run_logged
    from tools.render.output import publish
    from tools.gtk.user_files import ConfigError
    from tools.render.splash_client import splash_client
    from tools.render.dialogs import DIALOG_MODES, DialogMode
    from tools.render.capture_diagnosis import capture_is_unpainted, client_exited_during_capture, log_size, report_render_log
    from tools.render.session import Session, session_command
    from tools.render.window_rules import (
        RULES_FILE,
        write_focus_settle_script,
        write_readiness_settle_script,
        write_window_rules,
    )
    from tools.render.setup import (
        CONFIG_FILES,
        install_gtk_selection,
        install_theme,
        link_kvantum_themes,
        write_desktop_selection,
        write_kvantum_selection,
        write_session_configs,
    )
    from tools.repo_root import ROOT
else:  # run directly from render_surface.py
    from diagnostics import report_error, report_failure
    from png import PngError, read_png
    from process_group import run_logged
    from render.output import publish
    from gtk.user_files import ConfigError
    from render.splash_client import splash_client
    from render.dialogs import DIALOG_MODES, DialogMode
    from render.capture_diagnosis import capture_is_unpainted, client_exited_during_capture, log_size, report_render_log
    from render.session import Session, session_command
    from render.window_rules import (
        RULES_FILE,
        write_focus_settle_script,
        write_readiness_settle_script,
        write_window_rules,
    )
    from render.setup import (
        CONFIG_FILES,
        install_gtk_selection,
        install_theme,
        link_kvantum_themes,
        write_desktop_selection,
        write_kvantum_selection,
        write_session_configs,
    )
    from repo_root import ROOT

TOOL = "render_surface"


def _dialog_config_files() -> tuple[str, ...]:
    """Config files the dialog and desktop renders apply, unlike the applet."""
    return CONFIG_FILES + ("kdeglobals",)


def _selected_dialog_mode(args: argparse.Namespace) -> DialogMode | None:
    """Return the dialog mode whose flag was set, or None for the applet."""
    for mode in DIALOG_MODES:
        if getattr(args, mode.attr):
            return mode
    return None


def _client_command(args: argparse.Namespace, session: Session) -> list[str]:
    """Return the client command for the dialog flag set, else the applet."""
    if args.splash:
        # The look-and-feel's own splash paints the client itself; no applet
        # or dialog client.
        return list(splash_client(session))
    if args.desktop:
        # The shell draws the menu bar itself; no applet or dialog client.
        return ["plasmashell"]
    for mode in DIALOG_MODES:
        if getattr(args, mode.attr):
            return list(mode.client(session))
    return ["plasmawindowed", args.applet]


def _select_dialog_theme(session: Session, args: argparse.Namespace) -> int | None:
    """Select the theme for a dialog render; return a failure report, or None.

    Every dialog mode writes the Kvantum selection; a mode whose client runs
    zenity also installs the GTK selection.
    """
    try:
        write_kvantum_selection(session)
    except OSError as exc:
        return report_failure(TOOL, f"cannot write the Kvantum selection: {exc}")
    if any(
        getattr(args, mode.attr)
        for mode in DIALOG_MODES
        if mode.client_tool == "zenity"
    ):
        try:
            install_gtk_selection(session)
        except (OSError, ConfigError) as exc:
            return report_failure(
                TOOL, f"cannot install the GTK selection: {exc}"
            )
    return None


def render(args: argparse.Namespace) -> int:
    """Run the already-validated render options through capture and publish."""
    output = Path(args.output).absolute()
    try:
        session = Session.create()
    except OSError as exc:
        return report_error(TOOL, f"cannot create a scratch session directory: {exc}")
    with session:
        try:
            status, install_log = install_theme(session)
        except OSError as exc:
            return report_error(TOOL, f"cannot run make: {exc}")
        if status != 0:
            reason = "timed out" if status is None else f"exited {status}"
            return report_failure(TOOL, f"make install {reason}", install_log)

        problem, path = link_kvantum_themes(session)
        if problem is not None:
            return report_error(TOOL, f"cannot link {path}: {problem}")

        mode = _selected_dialog_mode(args)
        desktop = args.desktop
        # A splash run keeps the applet's own session configs: the splash
        # reads no selection (the client argument is the session-local
        # installed package path), so no Kvantum or GTK selection, no desktop
        # selection and no window-rules file are written for it.
        try:
            write_session_configs(
                session,
                files=_dialog_config_files() if (mode or desktop) else CONFIG_FILES,
            )
            # The scratch config home gets the theme defaults the dialog
            # applies, plus the mode's own extra config files. kwinrulesrc is
            # not one of the theme defaults (the defaults writer refuses a
            # file no [<file>][<group>] section defines), so the rules file
            # the mode names is written beside them from its own writer.
            if mode is not None and RULES_FILE in mode.extra_config_files:
                write_window_rules(session)
            if desktop:
                # The shell only builds the themed menu bar when the scratch
                # session selects the look-and-feel, so the selection is
                # written beside the session configs.
                write_desktop_selection(session)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return report_failure(TOOL, f"cannot write the session config: {exc}")

        client = _client_command(args, session)
        if mode is not None:
            failure = _select_dialog_theme(session, args)
            if failure is not None:
                return failure

        # The two-window mode settles the pair's focus state in-session: the
        # newest-window activation is a race under the parallel check's
        # load, so the session re-runs the focus-settle KWin script until
        # the capture has returned instead of trusting the newest window.
        focus_script = (
            str(write_focus_settle_script(session))
            if mode is not None and mode.focus_settle else None
        )
        # The splash's first mapped frame is an intermediate animation stage,
        # and the desktop's plasmashell window maps before its wallpaper
        # paints, so a readiness end would capture the bar over a black
        # field. Those two keep their measured ceilings instead of ending on
        # the first windowAdded. The two-window mode gets the pair script,
        # which ends only once both titled windows are in the gate's state.
        pair = mode is not None and mode.focus_settle
        readiness_script = (
            None
            if args.splash or args.desktop
            else str(write_readiness_settle_script(session, pair=pair))
        )
        command = session_command(
            session, client, args.settle, args.width, args.height, args.timeout,
            focus_script, readiness_script,
        )
        try:
            status = run_logged(command.argv, session.environment, command.log, command.timeout, ROOT)
        except OSError as exc:
            return report_error(TOOL, f"cannot run dbus-run-session: {exc}")
        if status is None:
            return report_failure(TOOL, f"render timed out after {args.timeout:g}s", command.log)
        if status != 0:
            return report_failure(TOOL, f"render session exited {status}", command.log)

        try:
            image = read_png(str(session.surface))
        except (PngError, OSError) as exc:
            detail = ""
            if not session.surface.exists():
                # The session exited 0 (every other status returned above), so
                # a missing capture means the session finished without writing
                # it. Name that state and the log size, so the failure says
                # whether the session logged anything before it ended.
                detail = (
                    f"; the session exited 0 and wrote no capture at "
                    f"{session.surface} (render log {log_size(command.log)})"
                )
            return report_failure(
                TOOL, f"capture is not a readable PNG: {exc}{detail}", command.log
            )
        if (image.width, image.height) != (args.width, args.height):
            return report_failure(
                TOOL, f"capture is {image.width}x{image.height}, expected {args.width}x{args.height}", command.log
            )
        if capture_is_unpainted(image.rgb):
            if client_exited_during_capture(command.log):
                return report_failure(
                    TOOL,
                    "capture is entirely black: the client exited during the "
                    "capture, after the settle passed its liveness check, so "
                    "its window was gone before the frame was taken",
                    command.log,
                )
            return report_failure(
                TOOL,
                "capture is entirely black: the window did not paint before "
                f"the {args.settle:g}s settle; retry with a longer --settle",
                command.log,
            )
        report_render_log(command.log, TOOL)
        try:
            publish(session.surface, output)
        except (OSError, ValueError) as exc:
            # ValueError names a non-regular capture source (the open guard's
            # FIFO or device refusal), so it joins the OSError copy failures
            # as a reported failed render rather than a traceback.
            return report_failure(TOOL, f"cannot write {output}: {exc}")
        return 0
