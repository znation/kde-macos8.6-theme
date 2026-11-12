"""Invoke the desktop cursor selector."""

from __future__ import annotations

import shutil

if __package__:
    from tools import cursor_link
    from tools.diagnostics import report_missing_tool, report_note, scratch_directory
    from tools.repo_root import ROOT
    from tools.required_command import run_required
else:  # run directly through apply_cursor.py
    import cursor_link
    from diagnostics import report_missing_tool, report_note, scratch_directory
    from repo_root import ROOT
    from required_command import run_required

TOOL = "apply_cursor"
SELECT_TOOL = "plasma-apply-cursortheme"
CURSOR_THEME = cursor_link.CURSOR_THEME
COMMAND_TIMEOUT = 60.0


def select(env: dict[str, str], optional: bool) -> int:
    """Select the theme, optionally reporting a missing desktop selector."""
    if optional and shutil.which(SELECT_TOOL) is None:
        report_note(
            TOOL,
            f"{SELECT_TOOL} is not on PATH; the pointer set is installed and "
            "linked, but select it in your desktop's cursor settings",
        )
        return 0
    missing = report_missing_tool(TOOL, [SELECT_TOOL])
    if missing is not None:
        return missing
    with scratch_directory(TOOL, "apply-cursor-") as scratch:
        if scratch is None:
            return 2
        status = run_required(
            TOOL,
            [SELECT_TOOL, CURSOR_THEME],
            env,
            scratch / f"{SELECT_TOOL}.log",
            COMMAND_TIMEOUT,
            ROOT,
        )
        return 0 if status is None else status
