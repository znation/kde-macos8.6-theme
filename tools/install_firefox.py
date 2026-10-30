"""Install the Firefox Platinum chrome into one opt-in Firefox profile.

``make install-firefox`` copies the standalone ``userChrome.css`` and
``userContent.css`` into a profile's ``chrome/`` directory and adds the
preference that makes Firefox read them; ``make remove-firefox`` removes
exactly those three changes. The profile is named with
``--profile``/``FIREFOX_PROFILE`` or, without either, resolved from
``installs.ini`` and ``profiles.ini`` under ``$HOME/.mozilla/firefox``.
Profile discovery lives in ``tools/firefox_profile.py``, the profile files'
bounded read and atomic write in ``tools/firefox_user_files.py``, and the
``user.js`` marker-block transform in ``tools/firefox_user_js.py``. The
bounded-wait profile lock shared with the GTK tools lives in
``tools/file_lock.py``.

Usage::

    python3 tools/install_firefox.py [--profile PATH]
    python3 tools/install_firefox.py --remove [--profile PATH]

Exit status: 0 when the install or removal ran, 1 when a foreign
``userChrome.css`` or ``userContent.css`` is left untouched, 2 for a usage
error, an unresolvable profile, another run holding the profile lock past
the timeout, a profile directory that cannot be locked, or a file that
cannot be read or written. Install and removal serialize on a lock over the
profile directory, so a concurrent pair cannot publish a preference block
without the sheets it selects (or delete the sheets while the block stays).
"""

from __future__ import annotations

import contextlib
import os
import sys
from collections.abc import Iterator
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
        user_content_path,
        user_js_path,
        write_profile_bytes,
        write_profile_text,
    )
    from tools.file_lock import exclusive_flock
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
        user_content_path,
        user_js_path,
        write_profile_bytes,
        write_profile_text,
    )
    from file_lock import exclusive_flock
    from firefox_user_js import first_line, remove_user_js, set_user_js
    from repo_root import ROOT
    from symlink_refusal import refuse_symlink

TOOL = "install_firefox"
SHEET = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"
CSS_MARKER = "/* org.macos8.desktop Firefox chrome, standalone userChrome.css"
CONTENT_SHEET = "theme/firefox/org.macos8.desktop/chrome/userContent.css"
CONTENT_CSS_MARKER = (
    "/* org.macos8.desktop Firefox content, standalone userContent.css"
)

# The shipped sheet, its first-line marker and its profile destination, in
# the order the install publishes them and the removal deletes them.
SHEETS = (
    (SHEET, CSS_MARKER, user_chrome_path),
    (CONTENT_SHEET, CONTENT_CSS_MARKER, user_content_path),
)

# A whole install or removal is short (a few small files), so a second run
# normally waits well under a second for the first to finish. The bound only
# exists so a holder stopped with SIGSTOP cannot block every later run
# forever; it matches the GTK selection lock's default.
LOCK_TIMEOUT = 60.0


def _note(message: str) -> None:
    """Print ``install_firefox: note: <message>`` on stdout."""
    report_note(TOOL, message)


@contextlib.contextmanager
def _profile_lock(profile: Path) -> Iterator[None]:
    """Serialize install and removal on a lock over *profile*'s directory.

    Both runs read the sheets and ``user.js``, edit that text, and write the
    result; without a lock an install can publish its sheets after a removal
    cleared them, or a removal can clear ``user.js`` after an install added
    the block, leaving the preference beside no sheet or a sheet with no
    preference. Locking the profile directory itself means both runs contend
    on one inode (resolved through a symlinked profile), and the lock adds no
    lock file to the profile and is released by the kernel when the process
    dies, SIGKILL included.

    The profile is required to exist before this lock is taken, so there is
    no containing directory to create. A lock held for longer than
    ``LOCK_TIMEOUT`` raises :class:`ConfigError` naming the profile, rather
    than waiting forever on a stopped holder or racing it.
    """
    with exclusive_flock(
        profile,
        "for the Firefox install",
        f"another install-firefox/remove-firefox to finish with {profile}",
        timeout=LOCK_TIMEOUT,
        error=ConfigError,
    ):
        yield


def _is_our_sheet(text: str, marker: str) -> bool:
    """Return whether *text*'s first line is *marker*.

    A UTF-8 BOM is valid in CSS and some editors add one, so it must not hide
    the marker and make our own installed sheet look foreign.
    """
    return first_line(text).removeprefix("\ufeff") == marker


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
    """Install both sheets and the preference into *profile*.

    An empty ``userChrome.css`` or ``userContent.css`` holds nothing to
    preserve, so it is adopted (overwritten with our sheet) rather than
    refused as a foreign sheet. Both shipped sheets are read, and every
    destination is checked, before anything is written. The sheets are
    published first, in ``SHEETS`` order; any failure or interrupt after that
    point starts the rollback, which restores the previous sheets and
    ``user.js`` (or removes any file the install created) so a failed write
    does not leave half the set behind. A restore that itself fails is
    reported alongside the original error instead of masking it.
    """
    # The sheet paths are children of chrome/. Refusing only a symlink at
    # userChrome.css/userContent.css would still let a symlinked directory
    # redirect their atomic writes outside the selected profile.
    refuse_symlink(profile / "chrome", "write", ConfigError)
    pending = []
    for source, marker, path_for in SHEETS:
        source_path = Path(ROOT) / source
        try:
            data = read_bytes(source_path, ROOT)
        except (OSError, ValueError) as exc:
            raise ConfigError(f"cannot read {source_path}: {exc}") from exc
        pending.append((source_path, marker, path_for(profile), data))

    destinations = []
    for source_path, marker, sheet_path, data in pending:
        existing_sheet = read_profile_text(sheet_path)
        if existing_sheet and not _is_our_sheet(existing_sheet, marker):
            return report_failure(
                TOOL,
                f"{sheet_path} is not our {source_path.name}; leaving it untouched",
            )
        destinations.append((sheet_path, data, existing_sheet))

    js_path = user_js_path(profile)
    existing_js = read_profile_text(js_path)
    updated_js = set_user_js(existing_js or "")
    if len(updated_js.encode("utf-8")) > MAX_PROFILE_FILE_BYTES:
        raise ConfigError(
            f"{js_path} would grow past the {MAX_PROFILE_FILE_BYTES}-byte "
            "limit this installer reads; refusing to write it"
        )
    # Every file is written, so a symlinked path is refused before the chrome
    # directory or any file is touched. The reads above still run first, so an
    # unreadable link is reported by its own read error.
    for sheet_path, _data, _existing in destinations:
        refuse_symlink(sheet_path, "write", ConfigError)
    refuse_symlink(js_path, "write", ConfigError)
    chrome_dir = destinations[0][0].parent
    try:
        chrome_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {chrome_dir}: {exc}") from exc
    try:
        for sheet_path, data, _existing in destinations:
            write_profile_bytes(sheet_path, data)
        write_profile_text(js_path, updated_js)
    except BaseException as exc:
        # There is no flag to miss: the read-back says whether the user.js
        # write published before it raised, and any failure or interrupt
        # after a sheet write starts restores that sheet, including one
        # delivered after the rename took effect but before the call returned.
        rollback_errors = []
        for sheet_path, _data, existing_sheet in destinations:
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
    """Remove our sheets and preference block from *profile*.

    The user.js rewrite happens before any sheet is deleted, so a failed
    rewrite leaves every file untouched. If the removal raises while any
    owned sheet is still present, including an interrupt before or during an
    unlink, the previous user.js is written back; once every owned sheet is
    gone, the completed rewrite is kept. A rewrite back that itself fails is
    reported alongside the original error.
    """
    # A symlinked chrome/ directory redirects both reads and unlinks outside
    # the selected profile, even when the sheet paths themselves are regular.
    refuse_symlink(profile / "chrome", "remove", ConfigError)
    owned = []
    for _source, marker, path_for in SHEETS:
        sheet_path = path_for(profile)
        existing_sheet = read_profile_text(sheet_path)
        if existing_sheet is not None and _is_our_sheet(existing_sheet, marker):
            owned.append(sheet_path)
    js_path = user_js_path(profile)
    existing_js = read_profile_text(js_path)
    updated = None if existing_js is None else remove_user_js(existing_js)
    rewrite_js = updated is not None and updated != existing_js
    # Check every planned change before making any: a symlinked path is the
    # user's link, so refuse it instead of deleting or replacing it.
    for sheet_path in owned:
        refuse_symlink(sheet_path, "remove", ConfigError)
    if rewrite_js:
        refuse_symlink(js_path, "remove", ConfigError)
    # Rewrite user.js first, then delete the sheets. Roll the rewrite back on
    # any failure after it, including an interrupt, so a failed removal does
    # not leave a preference block for a sheet that is still present.
    try:
        if rewrite_js:
            write_profile_text(js_path, updated)
        for sheet_path in owned:
            try:
                sheet_path.unlink()
            except OSError as exc:
                raise ConfigError(f"cannot remove {sheet_path}: {exc}") from exc
    except BaseException as exc:
        # The filesystem, not a flag set after the calls, says whether the
        # user.js rewrite still needs putting back: when every owned sheet is
        # gone the rewrite is the completed removal, and when any remains the
        # set is half-applied. An interrupt after any step is covered.
        if rewrite_js and any(path.exists() for path in owned):
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
            "and userContent.css in one Firefox profile."
        ),
        epilog=(
            "exit status: 0 when the install or removal ran, 1 when a foreign "
            "userChrome.css or userContent.css is left untouched, 2 for a "
            "usage error, an unresolvable profile, another run holding the "
            "profile lock past the timeout, a profile directory that cannot "
            "be locked, or a file that cannot be read or written"
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
        help="remove our userChrome.css, userContent.css and user.js preference block",
    )
    args = parser.parse_args(argv)

    try:
        profile = resolve_profile(args.profile, os.environ)
        with _profile_lock(profile):
            if args.remove:
                return _remove(profile)
            return _apply(profile)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
