"""Install the Firefox Platinum chrome into one opt-in Firefox profile.

``make install-firefox`` copies the standalone ``userChrome.css`` into a
profile's ``chrome/`` directory and adds the preference that makes Firefox
read it; ``make remove-firefox`` removes exactly those two changes. The
profile is named with ``--profile``/``FIREFOX_PROFILE`` or, without either,
resolved from ``installs.ini`` and ``profiles.ini`` under
``$HOME/.mozilla/firefox``. Profile discovery lives in
``tools/firefox_profile.py``, the profile files' bounded read and atomic
write in ``tools/firefox_user_files.py``, and the ``user.js`` marker-block
transform in ``tools/firefox_user_js.py``.

Usage::

    python3 tools/install_firefox.py [--profile PATH]
    python3 tools/install_firefox.py --remove [--profile PATH]

Exit status: 0 when the install or removal ran, 1 when a foreign
``userChrome.css`` is left untouched, 2 for a usage error, an unresolvable
profile, or a file that cannot be read or written.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.containment import read_bytes
    from tools.diagnostics import report_error, report_failure, report_note
    from tools.firefox_profile import resolve_profile
    from tools.firefox_user_files import (
        MAX_PROFILE_FILE_BYTES,
        ConfigError,
        read_profile_text,
        user_chrome_path,
        user_js_path,
        write_profile_bytes,
        write_profile_text,
    )
    from tools.firefox_user_js import first_line, remove_user_js, set_user_js
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/install_firefox.py
    from argument_parsing import EscapingArgumentParser
    from containment import read_bytes
    from diagnostics import report_error, report_failure, report_note
    from firefox_profile import resolve_profile
    from firefox_user_files import (
        MAX_PROFILE_FILE_BYTES,
        ConfigError,
        read_profile_text,
        user_chrome_path,
        user_js_path,
        write_profile_bytes,
        write_profile_text,
    )
    from firefox_user_js import first_line, remove_user_js, set_user_js
    from repo_root import ROOT

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"


def _note(message: str) -> None:
    """Print ``install_firefox: note: <message>`` on stdout."""
    report_note(TOOL, message)


def _apply(profile: Path) -> int:
    """Install the sheet and preference into *profile*.

    An empty ``userChrome.css`` holds nothing to preserve, so it is adopted
    (overwritten with our sheet) rather than refused as a foreign sheet.
    """
    try:
        sheet = read_bytes(Path(ROOT) / SHEET, ROOT)
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {Path(ROOT) / SHEET}: {exc}") from exc
    sheet_path, js_path = user_chrome_path(profile), user_js_path(profile)
    existing_sheet = read_profile_text(sheet_path)
    if existing_sheet and first_line(existing_sheet) != CSS_MARKER:
        return report_failure(
            TOOL,
            f"{sheet_path} is not our userChrome.css; leaving it untouched",
        )
    existing_js = read_profile_text(js_path)
    updated_js = set_user_js(existing_js or "")
    if len(updated_js.encode("utf-8")) > MAX_PROFILE_FILE_BYTES:
        raise ConfigError(
            f"{js_path} would grow past the {MAX_PROFILE_FILE_BYTES}-byte "
            "limit this installer reads; refusing to write it"
        )
    try:
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {sheet_path.parent}: {exc}") from exc
    write_profile_bytes(sheet_path, sheet)
    write_profile_text(js_path, updated_js)
    _note(f"installed the Firefox Platinum chrome into {profile}")
    return 0


def _remove(profile: Path) -> int:
    """Remove our sheet and preference block from *profile*."""
    sheet_path, js_path = user_chrome_path(profile), user_js_path(profile)
    existing_sheet = read_profile_text(sheet_path)
    existing_js = read_profile_text(js_path)
    if existing_sheet is not None and first_line(existing_sheet) == CSS_MARKER:
        try:
            sheet_path.unlink()
        except OSError as exc:
            raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    if existing_js is not None:
        updated = remove_user_js(existing_js)
        if updated != existing_js:
            write_profile_text(js_path, updated)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the Firefox profile install CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Install or remove the Mac OS 8.6 Firefox Platinum userChrome.css "
            "in one Firefox profile."
        ),
        epilog=(
            "exit status: 0 when the install or removal ran, 1 when a foreign "
            "userChrome.css is left untouched, 2 for a usage error, an "
            "unresolvable profile, or a file that cannot be read or written"
        ),
    )
    parser.add_argument(
        "--profile",
        metavar="PATH",
        help="absolute Firefox profile directory (default: FIREFOX_PROFILE "
        "or the active profile under $HOME/.mozilla/firefox)",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our userChrome.css and user.js preference block",
    )
    args = parser.parse_args(argv)

    try:
        profile = resolve_profile(args.profile, os.environ)
        if args.remove:
            return _remove(profile)
        return _apply(profile)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
