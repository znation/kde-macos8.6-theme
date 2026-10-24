"""Install the Firefox Platinum chrome into one opt-in Firefox profile.

``make install-firefox`` copies the standalone ``userChrome.css`` into a
profile's ``chrome/`` directory and adds the preference that makes Firefox
read it; ``make remove-firefox`` removes exactly those two changes. The
profile is named with ``--profile``/``FIREFOX_PROFILE`` or, without either,
resolved from ``installs.ini`` and ``profiles.ini`` under
``$HOME/.mozilla/firefox``. Profile discovery lives in
``tools/firefox_profile.py`` and the ``user.js`` marker-block transform in
``tools/firefox_user_js.py``.

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
    from tools.atomic_write import write_atomically
    from tools.containment import open_regular_binary, read_bytes
    from tools.diagnostics import report_error, report_failure
    from tools.firefox_profile import ConfigError, resolve_profile
    from tools.firefox_user_js import first_line, remove_user_js, set_user_js
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/install_firefox.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from containment import open_regular_binary, read_bytes
    from diagnostics import report_error, report_failure
    from firefox_profile import ConfigError, resolve_profile
    from firefox_user_js import first_line, remove_user_js, set_user_js
    from repo_root import ROOT
    from terminal import escape_controls

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"
# A profile file is read only to compare its first line or to append one
# marker block, so a real userChrome.css/user.js is a few kilobytes. The path
# is the user's and can name something arbitrarily large (a generated user.js
# or a wrong file dropped in the profile); a plain read() would allocate the
# whole file, and a MemoryError is not an OSError, so it would escape as a
# traceback instead of the documented exit-2 diagnostic. Bound the read the
# way containment, reference_validation and local_hook bound theirs.
_MAX_PROFILE_FILE_BYTES = 1 << 20


def _note(message: str) -> None:
    """Print ``install_firefox: note: <message>`` on stdout."""
    print(f"{TOOL}: note: {escape_controls(message)}")


def _read_text(path: Path) -> str | None:
    """Return *path*'s UTF-8 text, or ``None`` when it does not exist.

    The file is opened through the shared regular-file reader, so a FIFO or
    device at the path is refused by name instead of blocking the install on
    an open that waits for a writer, and the check inspects the opened
    descriptor. A directory, a non-regular file, an unreadable file and
    invalid UTF-8 are reported by name as a :class:`ConfigError` rather than
    escaping as a traceback. At most one byte past
    ``_MAX_PROFILE_FILE_BYTES`` is read, so an oversize profile file is
    refused by name instead of being loaded whole.
    """
    try:
        with open_regular_binary(path) as handle:
            data = handle.read(_MAX_PROFILE_FILE_BYTES + 1)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    if len(data) > _MAX_PROFILE_FILE_BYTES:
        raise ConfigError(
            f"{path} is larger than the {_MAX_PROFILE_FILE_BYTES}-byte limit "
            "this installer reads; refusing to load it whole"
        )
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc


def _write_bytes(path: Path, data: bytes) -> None:
    """Publish *data* at *path*, reporting a write failure by path."""
    try:
        write_atomically(path, lambda handle: handle.write(data))
    except OSError as exc:
        raise ConfigError(f"cannot write {path}: {exc}") from exc


def _write_text(path: Path, text: str) -> None:
    """Publish *text* as UTF-8 at *path*, reporting a write failure by path."""
    _write_bytes(path, text.encode("utf-8"))


def _paths(profile: Path) -> tuple[Path, Path]:
    """Return the profile's ``userChrome.css`` and ``user.js`` paths."""
    return profile / "chrome" / "userChrome.css", profile / "user.js"


def _apply(profile: Path) -> int:
    """Install the sheet and preference into *profile*.

    An empty ``userChrome.css`` holds nothing to preserve, so it is adopted
    (overwritten with our sheet) rather than refused as a foreign sheet.
    """
    try:
        sheet = read_bytes(Path(ROOT) / SHEET, ROOT)
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {Path(ROOT) / SHEET}: {exc}") from exc
    sheet_path, js_path = _paths(profile)
    existing_sheet = _read_text(sheet_path)
    if existing_sheet and first_line(existing_sheet) != CSS_MARKER:
        return report_failure(
            TOOL,
            f"{sheet_path} is not our userChrome.css; leaving it untouched",
        )
    existing_js = _read_text(js_path)
    updated_js = set_user_js(existing_js or "")
    if len(updated_js.encode("utf-8")) > _MAX_PROFILE_FILE_BYTES:
        raise ConfigError(
            f"{js_path} would grow past the {_MAX_PROFILE_FILE_BYTES}-byte "
            "limit this installer reads; refusing to write it"
        )
    try:
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {sheet_path.parent}: {exc}") from exc
    _write_bytes(sheet_path, sheet)
    _write_text(js_path, updated_js)
    _note(f"installed the Firefox Platinum chrome into {profile}")
    return 0


def _remove(profile: Path) -> int:
    """Remove our sheet and preference block from *profile*."""
    sheet_path, js_path = _paths(profile)
    existing_sheet = _read_text(sheet_path)
    existing_js = _read_text(js_path)
    if existing_sheet is not None and first_line(existing_sheet) == CSS_MARKER:
        try:
            sheet_path.unlink()
        except OSError as exc:
            raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    if existing_js is not None:
        updated = remove_user_js(existing_js)
        if updated != existing_js:
            _write_text(js_path, updated)
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
