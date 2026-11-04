"""Run the headless render lifecycle after CLI validation."""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from tools.diagnostics import report_error, report_failure
    from tools.png import PngError, read_png
    from tools.process_group import run_logged
    from tools.render_output import publish
    from tools.gtk_user_files import ConfigError
    from tools.render_clients import (
        checkbox_dialog_client,
        combobox_dialog_client,
        gtk_dialog_client,
        menu_dialog_client,
    )
    from tools.render_session import Session, session_command
    from tools.render_setup import (
        CONFIG_FILES,
        install_gtk_selection,
        install_theme,
        link_kvantum_themes,
        write_kvantum_selection,
        write_session_configs,
    )
    from tools.repo_root import ROOT
else:  # run directly from render_surface.py
    from diagnostics import report_error, report_failure
    from png import PngError, read_png
    from process_group import run_logged
    from render_output import publish
    from gtk_user_files import ConfigError
    from render_clients import (
        checkbox_dialog_client,
        combobox_dialog_client,
        gtk_dialog_client,
        menu_dialog_client,
    )
    from render_session import Session, session_command
    from render_setup import (
        CONFIG_FILES,
        install_gtk_selection,
        install_theme,
        link_kvantum_themes,
        write_kvantum_selection,
        write_session_configs,
    )
    from repo_root import ROOT

TOOL = "render_surface"


def _capture_is_unpainted(rgb: bytes) -> bool:
    """Return whether a capture's RGB plane is entirely black."""
    return not any(rgb)


def _dialog_config_files() -> tuple[str, ...]:
    """Config files the dialog render applies, unlike the applet render."""
    return CONFIG_FILES + ("kdeglobals",)


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

        dialog = (
            args.checkbox_dialog or args.combobox_dialog or args.menu_dialog
            or args.gtk_dialog
        )
        try:
            write_session_configs(session, files=_dialog_config_files() if dialog else CONFIG_FILES)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return report_failure(TOOL, f"cannot write the session config: {exc}")

        if args.checkbox_dialog:
            client = list(checkbox_dialog_client(session))
        elif args.combobox_dialog:
            client = list(combobox_dialog_client(session))
        elif args.menu_dialog:
            client = list(menu_dialog_client(session))
        elif args.gtk_dialog:
            client = list(gtk_dialog_client(session))
        else:
            client = ["plasmawindowed", args.applet]
        if dialog:
            try:
                write_kvantum_selection(session)
            except OSError as exc:
                return report_failure(TOOL, f"cannot write the Kvantum selection: {exc}")
            if args.gtk_dialog:
                try:
                    install_gtk_selection(session)
                except (OSError, ConfigError) as exc:
                    return report_failure(
                        TOOL, f"cannot install the GTK selection: {exc}"
                    )

        command = session_command(session, client, args.settle, args.width, args.height, args.timeout)
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
            return report_failure(TOOL, f"capture is not a readable PNG: {exc}", command.log)
        if (image.width, image.height) != (args.width, args.height):
            return report_failure(
                TOOL, f"capture is {image.width}x{image.height}, expected {args.width}x{args.height}", command.log
            )
        if _capture_is_unpainted(image.rgb):
            return report_failure(
                TOOL,
                "capture is entirely black: the window did not paint before "
                f"the {args.settle:g}s settle; retry with a longer --settle",
                command.log,
            )
        try:
            publish(session.surface, output)
        except OSError as exc:
            return report_failure(TOOL, f"cannot write {output}: {exc}")
        return 0
