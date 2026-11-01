"""Install the Firefox Platinum chrome into one Firefox profile.

``make apply`` runs this with ``--optional`` so the active profile gets the
chrome when one exists; ``make install-firefox`` copies the standalone
``userChrome.css`` and ``userContent.css`` into a named profile's ``chrome/``
directory and adds the preference that makes Firefox read them;
``make remove-firefox`` removes exactly those three changes. The profile is
named with ``--profile``/``FIREFOX_PROFILE`` or, without either, resolved from
``installs.ini`` and ``profiles.ini`` under ``$HOME/.mozilla/firefox``.
Profile discovery lives in ``tools/firefox_profile.py``, the profile files'
bounded read and atomic write in ``tools/firefox_user_files.py``, and the
``user.js`` marker-block transform in ``tools/firefox_user_js.py``. Profile
file installation and removal live in ``tools/firefox_profile_actions.py``;
install publication and rollback live in ``tools/firefox_transaction.py``.
The bounded-wait profile lock shared with the GTK tools lives in
``tools/file_lock.py``.

Usage::

    python3 tools/install_firefox.py [--profile PATH]
    python3 tools/install_firefox.py --optional [--profile PATH]
    python3 tools/install_firefox.py --remove [--profile PATH]

Exit status: 0 when the install, removal or optional skip ran, 1 when a
foreign ``userChrome.css`` or ``userContent.css`` is left untouched, 2 for a
usage error, an unresolvable profile, another run holding the profile lock
past the timeout, a profile directory that cannot be locked, or a file that
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
    from tools.diagnostics import report_error, report_note
    from tools.firefox_profile import resolve_profile
    from tools.firefox_profile_actions import (
        CONTENT_CSS_MARKER,
        CONTENT_SHEET,
        CSS_MARKER,
        SHEET,
        SHEETS,
        apply_profile,
        remove_profile,
    )
    from tools.firefox_user_files import ConfigError
    from tools.file_lock import exclusive_flock
else:  # run directly: python3 tools/install_firefox.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_note
    from firefox_profile import resolve_profile
    from firefox_profile_actions import (
        CONTENT_CSS_MARKER,
        CONTENT_SHEET,
        CSS_MARKER,
        SHEET,
        SHEETS,
        apply_profile,
        remove_profile,
    )
    from firefox_user_files import ConfigError
    from file_lock import exclusive_flock

TOOL = "install_firefox"
__all__ = [
    "CONTENT_CSS_MARKER",
    "CONTENT_SHEET",
    "CSS_MARKER",
    "SHEET",
    "SHEETS",
    "main",
]

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


def main(argv: list[str] | None = None) -> int:
    """Run the Firefox profile install CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Install or remove the Mac OS 8.6 Firefox Platinum userChrome.css "
            "and userContent.css in one Firefox profile."
        ),
        epilog=(
            "exit status: 0 when the install, removal or optional skip ran, 1 "
            "when a foreign userChrome.css or userContent.css is left "
            "untouched, 2 for a usage error, an unresolvable profile, another "
            "run holding the profile lock past the timeout, a profile "
            "directory that cannot be locked, or a file that cannot be read "
            "or written"
        ),
    )
    parser.add_argument(
        "--profile",
        metavar="PATH",
        help="absolute Firefox profile directory (default: FIREFOX_PROFILE "
        "or the active profile under $HOME/.mozilla/firefox)",
    )
    parser.add_argument(
        "--optional",
        action="store_true",
        help="skip with a note when no Firefox profile is discovered",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our userChrome.css, userContent.css and user.js preference block",
    )
    args = parser.parse_args(argv)

    try:
        profile = resolve_profile(
            args.profile, os.environ, optional=args.optional
        )
        if profile is None:
            _note(
                "no Firefox profile found; skipping the Firefox chrome step"
            )
            return 0
        with _profile_lock(profile):
            if args.remove:
                return remove_profile(profile)
            return apply_profile(profile)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
