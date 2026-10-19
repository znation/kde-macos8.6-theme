# Fixed bugs

Fixed bugs, newest first, moved here by tumwater from BUGS.md's `## Fixed`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Fixed

### `tests/invariants.py`'s `cross_check` lets an unreadable register escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `docs/invariants.md` is missing, is a directory or is otherwise unreadable,
`cross_check` aborts with a bare `FileNotFoundError`/`OSError` naming neither the checker nor
the register's role; a register whose bytes are not UTF-8 aborts with a bare
`UnicodeDecodeError`. The helper's docstring promises `AssertionError` diagnostics for a bad
register, so a caller cannot catch and report the failure as the register's own problem.

**Reproduction:**
`tests/test_invariants.py::TestHelpers.test_cross_check_rejects_an_unreadable_register` calls
`cross_check` with a missing register path; before the fix it raised `FileNotFoundError`.
`...test_cross_check_rejects_a_non_utf8_register` writes a non-UTF-8 `docs/invariants.md`;
before the fix it raised `UnicodeDecodeError`.

**Cause:** `cross_check` read the register with a bare `open()` outside any handler, unlike
`tests/placeholders.py::register_entries`, which reports the same failure as its own
`AssertionError`.

**Fix:** `cross_check` now reads the register inside a `try` and raises
`AssertionError(f"{register} cannot be read: {exc}")` on `OSError` and
`AssertionError(f"{register} is not valid UTF-8 text: {exc}")` on `UnicodeDecodeError`,
matching the placeholder checker; `parse_rows` still runs on the decoded text.

**Validation gap:** no-fake — the shipped suite had no fixture for an unreadable or non-UTF-8
register, so one had to be written before the failure could be confirmed.

### `tests/support/package_metadata.py` lets an unreadable `metadata.json` escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `load_metadata` opens the file with `open()` outside its `try`, so a
`metadata.json` that cannot be read at all -- a missing file, a dangling symlink, a directory, a
permission error -- escapes as a bare `OSError` (e.g. `FileNotFoundError`) instead of the
helper's own `ValueError`. The three suites that share the mixin (`test_lookandfeel`,
`test_desktoptheme`, `test_wallpaper`) then abort with a read error that names neither the guard
nor the file's role, and a caller guarding on `ValueError` does not catch it.

**Reproduction:**
`tests/test_package_metadata.py::TestLoadMetadata::test_unreadable_file_names_the_path` calls
`load_metadata` on a path whose parent directory does not exist; before the fix it raised
`FileNotFoundError`.

**Cause:** `load_metadata`'s `try` wrapped only `json.load`, with arms for `JSONDecodeError` and
`UnicodeDecodeError`; the `open()` call sat outside it, so an `OSError` from opening (or reading)
the file had no arm.

**Fix:** `load_metadata` now wraps the `open()`/`json.load()` pair in one `try` with an
`OSError` arm that raises `ValueError(f"{path}: cannot be read: {exc}")`, matching the helper's
contract of naming the file for every bad input.

**Validation gap:** no-fake — no fixture supplied an unreadable `metadata.json`, so the `OSError`
path was unobserved; the regression test creates a missing path the suite did not have.

### `tests/placeholders.py` lets an unreadable register escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `register_entries` (and so `cross_check`) reads `PLACEHOLDERS.md` with `open()`
but caught only `UnicodeDecodeError`, so a register that cannot be read -- a missing file, a
directory, a permission error -- escaped as a bare `OSError` naming neither the checker nor the
register's role, aborting the placeholder check instead of the checker's own `AssertionError`.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers::test_register_entries_rejects_an_unreadable_register`
passes a path that does not exist; before the fix it raised `FileNotFoundError`.

**Cause:** `register_entries`' `try` had only a `UnicodeDecodeError` arm; the same `OSError`
arm added to `_marker_text` the previous run was not applied here.

**Fix:** `register_entries` now catches `OSError` alongside `UnicodeDecodeError` and raises
`AssertionError(f"{path} cannot be read: {exc}")`, matching `_marker_text`.

**Validation gap:** no-fake — no fixture supplied an unreadable register, so the `OSError` path
was unobserved; the regression test creates a missing register path the suite did not have.

### `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare `FileNotFoundError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a text asset under `theme/` that is a symlink to a nonexistent
target *inside* `theme/` passes the symlink-escape guard (the resolved path is
contained), but `_marker_text` then opens it and raises a bare
`FileNotFoundError`. The module documents that an unreadable asset fails as
the checker's own `AssertionError` naming the path; instead the run aborts
with an unrelated traceback that does not name the checker.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers::test_markers_rejects_a_dangling_symlink_within_the_theme_root`
builds a synthetic theme root whose `theme/link.svg` points at
`theme/missing.svg` and calls `markers`; before the fix it errored with
`FileNotFoundError` instead of the expected `AssertionError`.

**Cause:** `_marker_text` caught only `UnicodeDecodeError`, so an `OSError`
from `open` (the dangling symlink, or any unreadable asset) escaped the
checker.

**Fix:** `_marker_text` now catches `OSError` alongside `UnicodeDecodeError`
and raises `AssertionError` naming the path (`cannot be read`), matching its
documented contract and the symlink-escape guard's handling.

**Validation gap:** no-fake — confirming it needed a synthetic theme root
carrying a dangling symlink that resolves inside `theme/`, a fixture the suite
did not have.

### `make check`'s `CHECK_PATTERN` guard accepts a pattern with surrounding whitespace that then matches no test module (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make check CHECK_PATTERN=' test_byteops.py '` passed the `require_check_pattern`
guard, which trims leading whitespace only to test for an empty value, but the recipe handed the
untrimmed glob to `unittest discover -p ' test_byteops.py '`. The glob matches no file, so the run
executes nothing: interpreters before 3.12 exit 0 — the silent green suite the guard was added to
prevent — and 3.12 and newer exit 5 with only "NO TESTS RAN".

**Reproduction:** `make -n check` with `CHECK_PATTERN=' test_byteops.py '` printed
`-p ' test_byteops.py '` before the fix.
`tests/test_make_check.py::TestCheckPattern.test_surrounding_whitespace_pattern_is_stripped`
fails on the old recipe and passes on the new one.

**Cause:** the guard trimmed a copy of the value for its emptiness check, but the recipe expanded
`$(CHECK_PATTERN)` itself, so the value validated and the value run could differ by surrounding
whitespace.

**Fix:** the discovery recipe now hands `$(strip $(CHECK_PATTERN))` to `unittest discover`, so the
guard's trimmed value is the value the run uses.

**Validation gap:** no-repro — the untrimmed glob was visible in a `make -n` dry run, but the
silent-green symptom needs an interpreter before 3.12; on the installed 3.13 the same glob fails
loudly with NO TESTS RAN, so the guard's gap was confirmed from the dry run and the version guard
rather than from the failure itself.

### `make uninstall`'s color-scheme warning reads the first duplicate `ColorScheme` key, not the last (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `[General]` in `$XDG_CONFIG_HOME/kdeglobals` repeats the `ColorScheme` key,
`make uninstall`'s warning about a still-selected scheme is decided by the **first** line. KDE
(like `configparser`) lets the **last** key win, so a file holding `ColorScheme=BreezeLight`
then `ColorScheme=MacOS8` leaves KDE on `MacOS8` while uninstall stays silent; the reverse
order leaves KDE on `BreezeLight` while uninstall warns wrongly. The diagnostic claims to read
kdeglobals "the way KDE reads it", so a wrong or missing warning is a real, if low-severity,
gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_the_last_duplicate_selection`
and `::test_make_uninstall_does_not_warn_for_an_overridden_selection` write a two-line
`ColorScheme` kdeglobals and run `make uninstall`; before the fix the first missed its warning
and the second emitted a false one.

**Cause:** the uninstall recipe's `awk` matched the first `ColorScheme=` in `[General]` and
called `exit` immediately, so it never saw a later override.

**Fix:** the `awk` now records every match and prints the last non-empty one from its `END`
block, matching KDE's last-key-wins semantics.

**Validation gap:** unclear-invariant — no test or doc stated which duplicate key KDE's config
reader honours, so that last-key-wins invariant had to be established before the parser could
be pinned to it.

### `tools/render_surface.py` leaks the caller's `XDG_CONFIG_DIRS` into the throwaway render session (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** the render session built by `tools/render_surface.py` still resolves config
through the caller's `XDG_CONFIG_DIRS`, so a host session's `kdeglobals`/`kwinrc` (or a scheme
already applied there) can change the rendered surface even though the run installs into a
scratch `XDG_DATA_HOME` and writes `kwinrc`/`plasmarc` into a scratch `XDG_CONFIG_HOME`. This
is the same non-hermeticity that made `plasma-apply-desktoptheme` a no-op in the sibling
`TestApplyDesktopTheme` bug.

**Reproduction:** `tests/test_render_surface.py::TestFailurePaths.test_session_ignores_a_config_search_path_from_the_environment`
sets `XDG_CONFIG_DIRS` to an ambient directory and has the `dbus-run-session` stub echo the
variable it was given; before the fix it recorded the ambient path.

**Cause:** `_render` copied `os.environ` into the child env and dropped only
`WAYLAND_DISPLAY`, `DISPLAY`, `DESTDIR` and `MAKEFLAGS`, so `XDG_CONFIG_DIRS` passed through
to `plasma-apply-colorscheme` and the session.

**Fix:** drop `XDG_CONFIG_DIRS` from the child env too, so the session uses the system default
search path and never the caller's config directories.

**Validation gap:** unclear-invariant — the module promised the user's configuration is never
touched but never said the XDG config search path was part of that, so the isolation guarantee
had to be established before it could be pinned.

### `tests/test_desktoptheme.py::TestApplyDesktopTheme` fails when `XDG_CONFIG_DIRS` already names a session theme (found by the feature role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make check` errors in `test_apply_lists_and_selects_the_theme` with
`FileNotFoundError: [Errno 2] No such file or directory: '<tmp>/config/plasmarc'`.
`plasma-apply-desktoptheme org.macos8.desktop` exits 0 but prints `The requested theme
"org.macos8.desktop" is already set as the theme for the current Plasma session.` and writes no
`plasmarc`, so the test's `read_kde_config` call raises.

**Reproduction:** With `XDG_CONFIG_DIRS` naming a directory whose `plasmarc` already sets
`[Theme] name=org.macos8.desktop` (this session exports
`XDG_CONFIG_DIRS=/home/zach/.config/kdedefaults:/etc/xdg:...`, and
`~/.config/kdedefaults/plasmarc` holds that value), run `make check
CHECK_TESTS='test_desktoptheme.TestApplyDesktopTheme'`. Seeding the test's isolated
`$XDG_CONFIG_HOME/plasmarc` with a different theme (`[Theme] name=breeze-dark`) makes the apply
write the file and the test pass; so does clearing `XDG_CONFIG_DIRS`.

**Cause:** `plasma-apply-desktoptheme` reads the current session theme from the config search
path, which includes `XDG_CONFIG_DIRS`. The test overrides `XDG_DATA_HOME` and `XDG_CONFIG_HOME`
but not `XDG_CONFIG_DIRS`, so the real user's `kdedefaults/plasmarc` still reports the theme as
already selected and the apply is a no-op. Overriding `HOME` and `XDG_CONFIG_HOME` alone does not
isolate it.

**Fix:** `TestApplyDesktopTheme` now runs the apply through `_apply_isolated`, which points
`XDG_CONFIG_DIRS` at an empty directory inside the test's `tmp`, and
`test_apply_ignores_a_session_theme_in_the_config_search_path` plants a session-theme `plasmarc`
in the ambient `XDG_CONFIG_DIRS` to pin that isolation.

**Validation gap:** no-repro — the failure depended on the developer's ambient `XDG_CONFIG_DIRS`
naming the theme, so confirming it needed a planted session-theme config dir to make the leak
deterministic.

### `widgets/lineedit.svg` corner tiles miss the reference field's outline and top-right notch (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** The `base` corner tiles of `theme/desktop-themes/org.macos8.desktop/widgets/lineedit.svg` did not reproduce the Mac OS 8.6 text field's corners in `macos8.6-screenshots/firstboot_betawiki.png`. Three pixels differed from the reference: the bottom-left and bottom-right corner tiles painted the #000000 outline's bottom pixel (canvas `(1,2)`) as #FFFFFF, so the outline stopped one row short of the field's bottom edge (reference `(29,351)` and `(430,351)` are #000000); and the top-right tile painted its outer pixel (canvas `(2,0)`) as #999999 where the reference `(431,58)` is the window face #CCCCCC, because the top shadow stops one pixel short of the outer highlight.

**Reproduction:** `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 29 351`, `... 430 351` (both #000000) and `... 431 58` (#CCCCCC); the pre-fix artwork rendered #FFFFFF and #999999 there. `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference` now re-derives all six corner pixels, and `TestLineEdit::test_lineedit_corner_bevels_turn_the_corner` fails against the old artwork.

**Cause:** `sunken_outside_face_corners` and the SVG corner groups were drawn from the edge bands alone, which is self-consistent but puts the bottom outline one row short and fills the top-right outer corner with the shadow. The existing corner test pinned that wrong table, and the reference test only sampled three border runs, so the whole suite passed.

**Validation gap:** unclear-invariant — the in-repo corner table was self-consistent with the artwork, so confirming the bug meant reconstructing the field's intended corner geometry from the reference screenshot's corner pixels before the test could assert it.

### `tools/url_check.py` accepts a malformed path, query or fragment as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://example.test/%`, `https://example.test/a%2`,
`https://example.test/a<b>` and `https://example.test/a?q=%`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of
them as a well-formed absolute URL. RFC 3986 requires a `%` to introduce
exactly two hex digits and limits a path to `pchar` (plus `/`), a query and a
fragment to `pchar` (plus `/` and `?`), so each is malformed while the
provenance check reported it clean.

**How to reproduce:**
`python3 -c "from tools.url_check import is_absolute_url; print(is_absolute_url('https://example.test/%'))"`
printed `True` before the fix and prints `False` after.

**Cause:** `url_problem` validated the scheme, whitespace and authority but
never the path, query or fragment after them, even though its docstring
claims to return why a URL is not a well-formed absolute URL.

**Fix:** After the authority checks, `url_problem` splits the remainder into
path, query and fragment and holds each to its RFC 3986 character set
(`_is_path`, `_is_query_or_fragment`), so a bare percent or a raw character
no `pchar` allows is rejected.

**Test:** `tests/test_url_check.py::TestPathQueryFragmentCharacters` gained
`test_path_query_fragment_characters_are_accepted` and
`test_malformed_path_query_fragment_characters_are_rejected`; the class
failed on the malformed cases before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring claimed well-formedness
but named only the scheme and authority rules, so I had to reconstruct that
the path, query and fragment were meant to be covered before I could confirm
the acceptance was a bug and not intended scope.

### `tools/url_check.py` rejects an uppercase IPvFuture host as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `"must bracket an IPv6 or IPvFuture
address"` for `https://[V1.a]/x`, so the checker reported a well-formed RFC 3986
IPvFuture as a malformed citation. RFC 3986's ABNF imports RFC 5234's
case-insensitive literals, so the leading `v` of `IPvFuture = "v" 1*HEXDIG "."
1*( unreserved / sub-delims / ":" )` may be either case.

**How to reproduce:**
`python3 -c "from tools.url_check import is_absolute_url; print(is_absolute_url('https://[V1.a]/x'))"`
printed `False` before the fix; `https://[v1.a]/x` printed `True`.

**Cause:** `_IPV_FUTURE` was compiled as
`re.compile(r"v[0-9A-Fa-f]+\....")`, whose literal `v` matched only lowercase
while `ipaddress.IPv6Address` then rejected `V1.a`, so the whole bracketed host
failed.

**Fix:** `_IPV_FUTURE` is now `re.compile(r"[vV][0-9A-Fa-f]+\....")`, so the
leading `v` matches either case as the ABNF requires.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained
`https://[V1.a]/x` in `test_valid_ip_literals_are_accepted`; the class failed on
it before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring and the suite stated the
IPvFuture rule but not that ABNF literals are case-insensitive, so I had to
reconstruct that the uppercase form is well formed before I could confirm the
rejection was a bug and not intended.

### `tools/url_check.py` accepts an IPv6 zone identifier as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://[fe80::1%eth0]/x`, `https://[fe80::1%25eth0]/x` and
`https://[::1%eth0]/x`, so `tools/check_references.py` would accept a
`sources.txt` row citing any of them as a well-formed absolute URL. RFC 3986's
`IPv6address` has no zone identifier, so a `%` in a bracketed host is
malformed while the provenance check reported it clean.

**Cause:** `_is_ip_literal` fell through to `ipaddress.IPv6Address`, which
accepts a `%scope` suffix (a zone identifier) that RFC 3986 does not include;
the `_IPV_FUTURE` branch never sees one because its character class has no
`%`.

**Fix:** `_is_ip_literal` rejects a bracketed host holding `%` before it
reaches `ipaddress.IPv6Address`, so neither a raw scope (`fe80::1%eth0`) nor
its percent-encoded form (`fe80::1%25eth0`) passes.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained the three
zone-identifier forms in `test_malformed_bracketed_hosts_are_rejected`; the
class failed on `https://[fe80::1%eth0]/x` before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring named RFC 3986 but
neither it nor the suite said that the standard library's IPv6 parser accepts
zone identifiers the RFC omits, so I had to reconstruct that boundary before I
could confirm the acceptance was a bug and not intended.

### `tools/url_check.py` accepts a malformed userinfo as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://a<b>@example.test/x`, `https://a{b}c@example.test/x`,
`https://host\name@example.test/x`, `https://user@@example.test/x`,
`https://exa%2@example.test/x` and a raw non-ASCII byte before the `@`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of
them as a well-formed absolute URL. RFC 3986 makes userinfo a run of
unreserved characters, pct-encoded octets, sub-delims and colons, so each is
malformed while the provenance check reported it clean.

**Cause:** `_authority_host` took the host as `authority.rsplit("@", 1)[-1]`,
discarding everything before the last `@` without validating it; only the host
after it was checked against the reg-name rule.

**Fix:** `_authority_host` now splits the authority with `rpartition("@")` and
validates the userinfo with `_is_userinfo`, which shares the new
`_is_uri_component` scanner with `_is_reg_name` and adds the colon to its
allowed set. A malformed userinfo is rejected with "must use only userinfo
characters before '@'" before the host is parsed.

**Test:** `tests/test_url_check.py::TestUserinfoCharacters` covers both the
accepted userinfo forms (empty, `user`, `user:pass`, sub-delims, pct-encoded)
and the rejected ones; the class failed on `https://a<b>@example.test/x`
before the fix and passes after.

**Validation gap:** unclear-invariant -- the parser's guarantee for userinfo
was neither documented nor tested, so I had to reconstruct the RFC 3986
userinfo shape from the host rule before I could confirm the acceptance was a
bug and not intended.

### `tools/url_check.py` accepts an empty bracketed host (`file://[]`) as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `file://[]/x`, `file://[]` and
`file://[]:80/x`, so `tools/check_references.py` would accept a `sources.txt`
row citing any of them as a well-formed absolute URL. RFC 3986 makes a
bracketed host an IP-literal, and an empty one (`[]`) is not an IP-literal, so
each is malformed while the provenance check reported it clean.

**Cause:** `_authority_host` treated an empty bracketed host (`host` empty
inside `[...]`) as "no host" and returned no problem; `url_problem` then let it
through because `file` is the one scheme allowed an empty host. The empty-host
allowance, meant for `file:///path`, swallowed the malformed bracketed form.

**Fix:** `_authority_host` now runs the IP-literal check on the bracketed host
unconditionally, so an empty bracketed host is rejected with "must bracket an
IPv6 or IPvFuture address" before the scheme's empty-host rule is consulted.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained the `file://[]`
forms (the class failed on `file://[]/x` before the fix and passes after).

**Validation gap:** unclear-invariant -- the module docstring said `[]` is not a
host, but I had to reconstruct how the `file`-only empty-host allowance bypasses
the bracketed-host check to confirm the acceptance was a bug and not intended.

### `tools/url_check.py` accepts an unbracketed host with non-reg-name characters (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://a<b>c.example/x`,
`https://a{b}c.example/x`, `https://host\name.example/x`,
`https://host"name.example/x`, `https://host|name.example/x`,
`https://exa%2.example/x` and a host holding a raw non-ASCII byte, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. RFC 3986 defines the unbracketed host as a
reg-name -- `*( unreserved / pct-encoded / sub-delims )` -- so each is
malformed while the provenance check reported it clean.

**Cause:** `_authority_host` only required an unbracketed host to be non-empty;
it never examined the host's characters, unlike the port and the bracketed
IP-literal checks beside it.

**Fix:** a new `_is_reg_name` helper accepts RFC 3986 unreserved characters,
sub-delims and `%HH` pct-encoded octets (rejecting a bare or short percent), and
`_authority_host` applies it to the unbracketed host. The empty host
(`file:///path`, `https://:80/p`) stays valid and is still caught by the
existing empty-host check.

**Test:** `tests/test_url_check.py::TestUnbracketedHostCharacters` (a scratch run
of `url_problem` returned `None` for the malformed hosts before the fix; the new
class fails on `https://a<b>c.example/x` before the fix and passes after).

**Validation gap:** unclear-invariant -- the module's docstring stated the
bracketed-host and port rules but never the unbracketed host's character set, so
I had to reconstruct RFC 3986's reg-name form before calling the acceptance a
bug.

### `tools/url_check.py` accepts a non-numeric or doubled port as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://host:80:90/x`,
`https://host:abc/x`, `https://[::1]:80:90/x` and `https://[::1]:abc/x`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. RFC 3986 defines a port as `*DIGIT`, so each is
malformed while the provenance check reports it clean.

**Cause:** `_authority_host` took the unbracketed host as
`hostport.split(":", 1)[0]` and ignored everything after the first colon, and
for a bracketed host it only checked that the character after `]` was a colon;
neither path examined the port's contents.

**Fix:** a new `_is_port` helper accepts only ASCII digits (an empty port, the
`host:` form, stays valid because `*DIGIT` allows zero digits), and
`_authority_host` applies it to the port after both an unbracketed host and a
bracketed one. The host and empty-host messages are unchanged.

**Test:** `tests/test_url_check.py::TestAuthorityPorts` (a scratch run of
`url_problem` returned `None` for the four malformed URLs before the fix; the
class passes after).

**Validation gap:** unclear-invariant — the module never stated the port rule,
so I had to reconstruct RFC 3986's `*DIGIT` form before I could call the
acceptance a bug.

### `test_url_check.py` fails to import when run as the only `CHECK_TESTS` module (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `make check CHECK_TESTS='test_url_check'` exited 2 with
`ModuleNotFoundError: No module named 'tools'` before running any test, so a
contributor could not run this module's tests on its own. The Makefile
documents `CHECK_TESTS` as a supported way to run one module, class or method.

**Cause:** `test_url_check.py` was the only `tests/test_*.py` module whose
first import was `tools.*` rather than `support`; it only ever passed because
unittest discovery imports other modules (which import `support.repo_root`,
the import that puts the repository root on `sys.path`) before it.

**Fix:** `test_url_check.py` now imports `support.repo_root` first, matching
every other test module.

**Test:** `make check CHECK_TESTS='test_url_check'` (the focused run exited 2
with the `ModuleNotFoundError` before the fix and exits 0 after).

**Validation gap:** none — the documented focused-run command reproduced the
failure and confirmed the fix.

### `tools/url_check.py` accepts a malformed bracketed host as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://[]/x`,
`https://[::1/x`, `https://[not-an-ip]/x` and `https://exa[mple].test/x`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. Each names no usable host, so the citation
points nowhere while the provenance check reports it clean.

**Cause:** the host was taken as
`authority.rsplit("@", 1)[-1].split(":", 1)[0]`, which for a bracketed
authority is the literal `[` — truthy, so the empty-host guard never fired and
the bracket contents were never examined.

**Fix:** `_authority_host` parses an RFC 3986 authority: a bracketed host must
be closed and hold an IPv6 or IPvFuture address (`_is_ip_literal`, using the
stdlib `ipaddress`), and an unbracketed host must not carry a bracket. The
empty-host message and the `file://` exemption are unchanged.

**Test:** `tests/test_url_check.py::TestBracketedHosts` (a scratch run of
`url_problem` returned `None` for the four malformed URLs before the fix; the
class passes after).

**Validation gap:** unclear-invariant — the code never stated the bracketed
host rule, so I had to reconstruct RFC 3986's IP-literal form before I could
call the acceptance a bug.

### `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated exception (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** a register row whose test reference contained a NUL byte (the
cell regex `` `([^`]+)` `` matches NUL) made `check_reference` raise
`ValueError: lstat: embedded null character in path` from
`os.path.realpath`, an exception naming neither the register section nor the
reference, so a failing run did not say which row broke the register.
`check_reference` is documented to raise `AssertionError` naming the section
and the first missing piece.

**Cause:** `check_reference` resolved the joined path with
`os.path.realpath(file_path)` before any guard; `realpath` raises `ValueError`
(not `OSError`) for a path with an embedded NUL byte, so the repository-escape
and isfile checks never ran.

**Fix:** `check_reference` now rejects a NUL byte in the reference's path with
`AssertionError` naming the section and the reference, before it reaches
`os.path.realpath`.

**Test:**
`tests/test_invariants.py::TestHelpers::test_cross_check_rejects_a_reference_with_a_nul_byte`
(a scratch run showed the `ValueError` escaping before the fix; the test
errored before the fix and passes after).

**Validation gap:** no-fake -- confirming it needed a synthetic register row
carrying a NUL byte, a fixture the suite did not have.

- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated exception (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 4cb013f; gap: no-fake)
- `tests/invariants.py` accepts a class whose locally defined base only looks like a test case (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit c769e5f; gap: no-observability)
- `tests/invariants.py` accepts a register reference that escapes the repository (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 24eb3a3; gap: no-observability)
- `tests/invariants.py` accepts a method reference into a class that is not a test case (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 4888e9d; gap: no-observability)
- `tests/invariants.py` accepts a register reference to a class with no tests (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 117647d; gap: no-observability)
- `tests/invariants.py` accepts a register reference to a non-test method (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 304545a; gap: no-observability)
- `tests/invariants.py` accepts a register reference with a segment after the method (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 90e6564; gap: no-observability)
- `tests/invariants.py` drops a register row that does not split into three cells (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 91c8968; gap: no-observability)
- `tests/invariants.py` drops a register row whose Test cell has no backticked reference (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit d90e79d; gap: no-observability)
- `tests/invariants.py` drops a register row whose cell contains an escaped pipe (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit ee90205; gap: no-observability)
- `tests/invariants.py` accepts a register reference ending in `::`, pinning a guarantee to no test (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit c87ada1; gap: no-observability)
- `tests/placeholders.py` ignores `PLACEHOLDER:` markers in the theme's `.kvconfig` file (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 16010b3; gap: no-observability)
- `_log_tail_lines` splits a log line on a vertical tab or other exotic break byte (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 7110891)
- `_log_tail_lines` keeps a blank first line when the tail window opens on a `\r\n` newline (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 384a7ac)
- `tests/placeholders.py` ignores `PLACEHOLDER:` markers in the theme's `.js` and `.desktoprc` files (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 21267c2; gap: no-observability)
- `org.macos8.desktop` icon theme still calls its final art "placeholder icons" (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 7cf57e0; gap: unclear-invariant)
- `make render` installs the theme outside its scratch data home when `DESTDIR` is on the outer make command line (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 28132d5)
- README lists three tools `make render` needs, but `REQUIRED_TOOLS` has six (found by the qa role 2026-10-17) — fixed 2026-10-17 by the bugfix role; commit 1ff84a5
- `make install` fails with a shell syntax error when `XDG_DATA_HOME` or `DESTDIR` contains an apostrophe (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit c69c398)
- `make render` runs the whole render before reporting an unwritable output, and cannot write an output path starting with `-` (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit 54ff603)
- `make render` installs the theme outside its scratch data home when `DESTDIR` is set in the environment (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit 6ba6b00)
- Splash progress bar pins the panel face and the empty track as its track and fill colours (found by the plan role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit fb34ec7)
- Test suite fails with 43 failures and 3 errors (found 2026-10-16; fixed 2026-10-17 by the bugfix role; commit 090a345)
- Uninstalling the scheme while it is selected leaves KDE warning `Could not find color scheme "MacOS8"` (found 2026-10-09; fixed 2026-10-09; commit c2b0481; gap: real-run-needed)
- Palette anchors are not re-derivable from the reference screenshots (structural risk, found 2026-10-07; fixed 2026-10-08; commit e723886; gap: no-observability)
- Selection palette anchor is not re-derivable (found 2026-10-07; fixed 2026-10-08; commit df1bedd; gap: unclear-invariant)
- `--tolerance` does not gate the fidelity exit status; README documents no pass threshold (found 2026-10-07; fixed 2026-10-07; commit 14c6530)
- `plasma-apply-colorscheme` writes a scheme ID that does not survive a restart (found 2026-10-07; fixed 2026-10-07; commit aac7aa7; gap: real-run-needed)
- No objective fidelity check for "pixel-perfect" (structural risk, found 2026-10-07; fixed 2026-10-07; commit 2b0b3d5; gap: unclear-invariant)
