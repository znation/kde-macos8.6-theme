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
    from tools.symlink_refusal import refuse_symlink
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
    from symlink_refusal import refuse_symlink

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"


def _note(message: str) -> None:
    """Print ``install_firefox: note: <message>`` on stdout."""
    report_note(TOOL, message)


def _is_our_sheet(text: str) -> bool:
    """Return whether *text*'s first line is our marker.

    A UTF-8 BOM is valid in CSS and some editors add one, so it must not hide
    the marker and make our own installed sheet look foreign.
    """
    return first_line(text).removeprefix("\ufeff") == CSS_MARKER


def _restore_file(path: Path, previous: str | None) -> None:
    """Put *previous* back at *path*, or remove a file an install created.

    A file that did not exist before the failed install is removed; an
    existing one is written back through the same atomic write used for the
    install. A restore failure is reported by path alongside the write
    failure that caused it.
    """
    if previous is None:
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise ConfigError(f"cannot restore {path}: {exc}") from exc
        return
    write_profile_text(path, previous)


def _restore_user_js(path: Path, previous: str | None, published: str) -> None:
    """Put *previous* back at *path* when the failed write published *published*.

    The atomic writer can publish the new text and still raise (an interrupt
    delivered after the rename), so the filesystem, not a flag set after the
    write returns, decides whether the preference block is present. When the
    read-back is not the text the failed write tried to publish, the write
    never took effect and the file is left as it was.
    """
    if previous != published and read_profile_text(path) == published:
        _restore_file(path, previous)


def _apply(profile: Path) -> int:
    """Install the sheet and preference into *profile*.

    An empty ``userChrome.css`` holds nothing to preserve, so it is adopted
    (overwritten with our sheet) rather than refused as a foreign sheet.
    The sheet is published first; any failure or interrupt after that point
    starts the rollback, which restores the previous sheet and ``user.js``
    (or removes either file the install created) so a failed write does not
    leave half the pair behind. A restore that itself fails is reported
    alongside the original error instead of masking it.
    """
    try:
        sheet = read_bytes(Path(ROOT) / SHEET, ROOT)
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {Path(ROOT) / SHEET}: {exc}") from exc
    sheet_path, js_path = user_chrome_path(profile), user_js_path(profile)
    existing_sheet = read_profile_text(sheet_path)
    if existing_sheet and not _is_our_sheet(existing_sheet):
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
    # Both files are written, so a symlinked path is refused before the
    # chrome directory or either file is touched. The reads above still run
    # first, so an unreadable link is reported by its own read error.
    refuse_symlink(sheet_path, "write", ConfigError)
    refuse_symlink(js_path, "write", ConfigError)
    try:
        sheet_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {sheet_path.parent}: {exc}") from exc
    try:
        write_profile_bytes(sheet_path, sheet)
        write_profile_text(js_path, updated_js)
    except BaseException as exc:
        # There is no flag to miss: the read-back says whether the user.js
        # write published before it raised, and any failure or interrupt
        # after the sheet write starts restores the sheet, including one
        # delivered after the rename took effect but before the call returned.
        rollback_errors = []
        try:
            _restore_file(sheet_path, existing_sheet)
        except ConfigError as rollback:
            rollback_errors.append(str(rollback))
        try:
            _restore_user_js(js_path, existing_js, updated_js)
        except ConfigError as rollback:
            rollback_errors.append(str(rollback))
        if rollback_errors:
            raise ConfigError(
                f"{exc}; {'; '.join(rollback_errors)}"
            ) from exc
        raise
    _note(f"installed the Firefox Platinum chrome into {profile}")
    return 0


def _remove(profile: Path) -> int:
    """Remove our sheet and preference block from *profile*.

    The user.js rewrite happens before the sheet is deleted, so a failed
    rewrite leaves both files untouched. If the removal raises while the
    sheet is still present, including an interrupt before or during the
    unlink, the previous user.js is written back; if the sheet was already
    unlinked, the completed rewrite is kept. A rewrite back that itself fails
    is reported alongside the original error.
    """
    sheet_path, js_path = user_chrome_path(profile), user_js_path(profile)
    existing_sheet = read_profile_text(sheet_path)
    existing_js = read_profile_text(js_path)
    remove_sheet = (
        existing_sheet is not None and _is_our_sheet(existing_sheet)
    )
    updated = None if existing_js is None else remove_user_js(existing_js)
    rewrite_js = updated is not None and updated != existing_js
    # Check every planned change before making any: a symlinked path is the
    # user's link, so refuse it instead of deleting or replacing it.
    if remove_sheet:
        refuse_symlink(sheet_path, "remove", ConfigError)
    if rewrite_js:
        refuse_symlink(js_path, "remove", ConfigError)
    # Rewrite user.js first, then delete the sheet. Roll the rewrite back on
    # any failure after it, including an interrupt, so a failed removal does
    # not leave a preference block for a sheet that is still present.
    try:
        if rewrite_js:
            write_profile_text(js_path, updated)
        if remove_sheet:
            try:
                sheet_path.unlink()
            except OSError as exc:
                raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    except BaseException as exc:
        # The filesystem, not a flag set after the calls, says whether the
        # user.js rewrite still needs putting back: when the sheet is gone
        # the rewrite is the completed removal, and when it remains the pair
        # is half-applied. An interrupt after either step is covered.
        if rewrite_js and sheet_path.exists():
            try:
                write_profile_text(js_path, existing_js)
            except ConfigError as rollback:
                raise ConfigError(f"{exc}; {rollback}") from exc
        raise
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
