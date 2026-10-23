# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
the `org.macos8.desktop` Kvantum widget style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style art (a black-face, white-outline arrow not
traced from Apple's artwork), it has landed inside the icon theme package with its provenance
exception recorded in `docs/invariants.md`, and nothing selects it yet; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) is queued in `## Planned`. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which is queued in `## Planned`).

### Retire the `unclear-invariant` validation gap with an invariant-register ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: unclear-invariant` tag, 17 Fixed entries)

**Goal.** Seventeen Fixed entries in BUGS-FIXED.md carry `gap: unclear-invariant` — each bug
could be confirmed only after reconstructing what the code was supposed to guarantee first.
`docs/invariants.md` already has rows for the KDE INI rules, the PNG IDAT trailer, the
`INSTALL_PACKAGES` guard, the icon theme, the palette anchors and the fidelity gate, but it has
no row for `tools/url_check.py`'s RFC 3986 rules, the render session's config-search-path
isolation or the lineedit corner tiles, and nothing ties an archived record to its register row.
Retire the tag with a ledger that maps each record to the register row and the test that pins
it, and a count cap so a new `unclear-invariant` tag fails the suite until its invariant is
recorded.

**Cited entries.** BUGS-FIXED.md lines recording `gap: unclear-invariant` (17 entries): the PNG
IDAT-trailer invariant, three KDE config-reader rules, the render session's `XDG_CONFIG_DIRS`
isolation, the lineedit corner geometry, the eight `tools/url_check.py` RFC 3986 cases, and the
three older one-line records (icon-theme placeholder naming, the selection palette anchor and
the objective fidelity check).

**Approach.**
- `tests/support/validation_gaps.py`: add `UNCLEAR_INVARIANT_BASELINE = 17` and one
  `UNCLEAR_INVARIANT_REPRODUCTIONS` entry per mechanism, matching both the prose and the older
  one-line record forms. Give each entry the register row's guarantee text in addition to its
  test reference, and add an `unclear_invariant(records)` selector plus a tag-aware lookup that
  returns `None` for an unmatched record, mirroring the `no-observability` ledger without
  changing its entries.
- `tests/test_validation_gaps.py`: add `TestUnclearInvariantLedger` asserting that every
  archived `unclear-invariant` record maps to an entry; that each entry's test reference passes
  `tests/invariants.check_reference`; that each entry's guarantee text occurs in a row
  `tests/invariants.parse_rows` returns from `docs/invariants.md`; that each entry covers a
  shipped record; and that the record count does not exceed 17.
- `docs/invariants.md`: add the three missing tooling rows — `tools/url_check.py`'s RFC 3986
  well-formedness pinned to `tests/test_url_check.py`, the render session's
  `XDG_CONFIG_DIRS` isolation pinned to
  `tests/test_render_surface.py::TestFailurePaths::test_session_ignores_a_config_search_path_from_the_environment`,
  and the lineedit corner tiles pinned to
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference`
  — and extend the existing validation-gap ledger row to name both tags.
- `PLANS.md`: this entry moves under `## Done` when the work is done.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`,
`docs/invariants.md` and `PLANS.md` (this entry). Do not edit `PLANS-DONE.md` or any `theme/`
path; the invariants are already recorded, so no shipped artwork or config changes.

**Acceptance criteria.**
- `tests/test_validation_gaps.py::TestUnclearInvariantLedger` passes, and deleting a ledger
  entry, pointing one at an absent register row or a non-existent test, or adding an
  `unclear-invariant` record without an entry makes the matching assertion fail.
- `make check` is green; `tests/invariants.py` accepts the new and extended `## tooling` rows.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`.

### Firefox Platinum chrome, part 2/2: Install the stylesheet and preference into a Firefox profile (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the stylesheet; "requires part 1/2 landed")

**Goal.** Part 1/2 landed `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, but no
target puts it where Firefox reads it. This part makes the sheet usable for one opt-in profile:
`make install-firefox` copies the sheet into the profile's `chrome/userChrome.css` and adds the
marker-delimited `toolkit.legacyUserProfileCustomizations.stylesheets=true` preference to its
`user.js`, and `make remove-firefox` removes exactly those two changes. It is opt-in like the GTK
targets: `make install` and `make apply` stay unchanged and install no Firefox files.

**Approach.**
- `tools/install_firefox.py` (new CLI, `TOOL = "install_firefox"`). It takes `--profile PATH` and
  `--remove`, parses with `tools.argument_parsing.EscapingArgumentParser`, reports through
  `tools.diagnostics.report_error`/`report_failure`, and escapes path text with
  `tools.terminal.escape_controls`. Constants name the source
  (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`), the CSS first-line marker
  (`/* org.macos8.desktop Firefox chrome, standalone userChrome.css`), the `user.js` marker
  (`// org.macos8.desktop Firefox Platinum userChrome`) and the exact pref line
  `user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);`.
- `resolve_profile(explicit, env)`: an explicit `--profile` (or `FIREFOX_PROFILE` when the flag is
  absent, which also lets the script run directly) must be an absolute existing directory, else
  exit 2. Otherwise `HOME` must be absolute and the profile root is `$HOME/.mozilla/firefox`.
  Build candidates in this order: the first `Default=` under an `[Install…]` section of
  `installs.ini`; the first `[Profile…]` section of `profiles.ini` whose `Default=1`; the first
  `[Profile…]` section with a `Path`. Read the INI files with `configparser` and
  `interpolation=None`, resolve a `Path` relative to the root unless `IsRelative=0`, and take the
  first candidate whose directory exists. When none exists, exit 2 with a diagnostic naming the
  root and the candidates tried.
- Install (`_apply(profile)`): read the shipped sheet through
  `tools.containment.read_bytes(SHEET, ROOT)`, then read an existing
  `<profile>/chrome/userChrome.css` before writing anything. An existing file whose first line is
  not the CSS marker is foreign: report with `report_failure` (status 1) naming its path and write
  nothing. Otherwise create `<profile>/chrome`, publish the sheet with
  `tools.atomic_write.write_atomically` (byte-for-byte), and publish `<profile>/user.js` with the
  same writer.
- `set_user_js(text)` and `remove_user_js(text)` are pure text transforms. They preserve every
  foreign line and that line's own CRLF/CR/LF ending, and a missing final newline. Install removes
  any earlier marker line plus the exact pref line immediately after it, then appends the marker
  and pref at the end, terminating an unterminated last line first and using the file's dominant
  ending (a new file uses `\n`), so a repeat install leaves exactly one block and our line follows
  any foreign setting of the same pref. Removal deletes only that marker-plus-pref pair and leaves
  a foreign `user_pref` for the same name untouched; it leaves an emptied `user.js` and the
  `chrome/` directory in place rather than deleting a file it cannot prove it created.
- Remove (`_remove(profile)`): delete `<profile>/chrome/userChrome.css` only when its first line
  is the CSS marker, then rewrite `user.js` with `remove_user_js`. A foreign file, a foreign pref
  line, and a repeated remove are all no-ops; an unreadable file or failed write exits 2 naming
  the path.
- `Makefile`: add `install-firefox` and `remove-firefox` to `.PHONY` and `make help`, each behind
  `require_python`/`require_python_version`, running
  `$(PYTHON) tools/install_firefox.py $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")`
  (with `--remove` for removal). Add a `FIREFOX_PROFILE=path` help line naming the default
  (the active profile under `$HOME/.mozilla/firefox`); do not add a `?=` variable. No DESTDIR
  guard or data-home lock is needed because neither target writes the installed theme tree.
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: replace the header sentence saying no
  Makefile target installs it with the two target names and the profile rule; keep the provenance
  text, the preference name and every rule and hex value unchanged.
- `README.md`: replace the Firefox paragraph with the opt-in install/remove commands, profile
  resolution and `FIREFOX_PROFILE`, the restart note, and the existing
  `browser.tabs.inTitlebar=0` explanation; keep the artifact count and `tumwater:status` text.
  `PLANS.md`'s scope-drift paragraph changes its two "not planned yet" phrases for part 2/2 to
  "is queued in `## Planned`".
- `docs/invariants.md`: add one row under `## firefox`: the opt-in install copies the sheet
  byte-for-byte, adds only the marker-delimited pref while preserving foreign lines and endings,
  refuses a foreign `userChrome.css`, and removal reverses only those two changes — pinned to
  `tests/test_firefox_install.py::TestInstall` and `::TestRemove`.

**Files touched.** `tools/install_firefox.py` (new), `tests/test_firefox_install.py` (new),
`Makefile`, `README.md`, `docs/invariants.md`, `theme/firefox/org.macos8.desktop/chrome/userChrome.css`
(header only) and `PLANS.md` (this entry and the scope-drift sentences). Do not edit `PLANS-DONE.md`,
any `theme/gtk/` path or any installed-theme directory layout.

**Acceptance criteria.**
- `tests/test_firefox_install.py` pins: explicit and `FIREFOX_PROFILE` profile resolution, an
  `installs.ini` default, a `profiles.ini` `Default=1` and first-profile fallback, relative and
  absolute `Path`, and a named refusal when `HOME` is unusable or no candidate exists; install
  writes a byte-identical sheet and exactly one marker-plus-pref block; a foreign
  `userChrome.css` is refused with nothing written; a repeat install does not duplicate the block;
  foreign `user.js` lines, a foreign pref with the same name, CRLF endings and a missing final
  newline survive install and removal; removal deletes only our sheet and marker block and a
  repeated removal succeeds. Deleting the marker, changing the pref value, or dropping the foreign
  line assertion makes the matching test fail.
- `make check CHECK_TESTS=test_firefox_install` passes, then `make check` is green;
  `tests/invariants.py` accepts the new `## firefox` row. `tests/test_make_help.py` finds both new
  targets in `.PHONY`, `make help` and README, and the `FIREFOX_PROFILE` help line resolves to a
  variable the Makefile expands.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

## Done
