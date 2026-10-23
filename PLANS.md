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
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
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

### Platinum cursor selection: link the shipped cursor into the Xcursor user path and apply it (planned 2026-10-23 by the plan role; follows the landed cursor artifact)

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, but nothing
selects them. Xcursor searches `~/.icons`, `/usr/share/icons` and `/usr/share/pixmaps` (its
`XcursorLibraryPath()` default), not `$XDG_DATA_HOME/icons`: `plasma-apply-cursortheme --list-themes`
and `XcursorLibraryPath()` both ignore a theme copied under `$XDG_DATA_HOME/icons`, and list it when
the same theme is under `~/.icons`. This part adds an opt-in `make apply-cursor` that exposes the
installed icon theme at `$HOME/.icons/org.macos8.desktop` as a symlink and selects it with
`plasma-apply-cursortheme org.macos8.desktop`; `make remove-cursor` removes only that link. `make
install` and `make apply` stay unchanged and select no cursor.

**Approach.**
- `tools/apply_cursor.py` (new CLI, `TOOL = "apply_cursor"`, `CURSOR_THEME =
  "org.macos8.desktop"`, `SELECT_TOOL = "plasma-apply-cursortheme"`, `COMMAND_TIMEOUT = 60.0`).
  It uses `tools.argument_parsing.EscapingArgumentParser` (`--remove`), reports through
  `tools.diagnostics.report_error`/`report_failure`/`report_missing_tool`, runs the selector with
  `tools.process_group.run_logged` into a temporary log, escapes path text with
  `tools.terminal.escape_controls`, and imports `tools.repo_root.ROOT`.
- `resolve_homes(env)` returns `(home, data_home, config_home)`: `$HOME` must be absolute; data home
  is an absolute `$XDG_DATA_HOME` else `$HOME/.local/share`; config home is an absolute
  `$XDG_CONFIG_HOME` else `$HOME/.config` (only for the removal note). A missing or relative `HOME`
  exits 2 naming it.
- `installed_theme(data_home)` is `$XDG_DATA_HOME/icons/org.macos8.desktop`; it must contain a
  regular `index.theme` and a regular `cursors/left_ptr`, else exit 2 naming the path. That file is
  the icon theme's own `index.theme`, so the symlinked directory is also a valid cursor theme (the
  KDE cursor model lists it by the directory name `org.macos8.desktop`).
- Install: the target path is `$HOME/.icons/org.macos8.desktop`. A missing `~/.icons` is created; an
  existing symlink to the installed theme is success (a repeat install changes nothing); any other
  existing path (a foreign symlink, a real directory or a file) is refused with exit 2 naming it and
  is not touched; a `~/.icons` that exists but is not a directory is refused the same way. A new link
  is created with `os.symlink(str(installed_theme), str(target))`.
  Then `plasma-apply-cursortheme org.macos8.desktop` runs with the inherited environment; a missing
  tool exits 2 through `report_missing_tool`, a timeout or non-zero exit returns `report_failure`
  (status 1) with the log tail.
- Remove (`--remove`): unlink the target only when it is a symlink whose link text is the installed
  theme path (a dangling link to a since-uninstalled theme counts as ours); a real directory, a file
  or a symlink elsewhere is left alone with a note and exit 0, like `remove-gtk` leaving a foreign
  file. Do not edit `kcminputrc`; if its `[Mouse] cursorTheme` still names `org.macos8.desktop`,
  print a note naming `plasma-apply-cursortheme breeze_cursors` as the reset. Leave `~/.icons`
  itself in place.
- `Makefile`: add `apply-cursor` and `remove-cursor` to `.PHONY` and `make help`. `apply-cursor`
  refuses a non-empty `DESTDIR` (like `apply`/`apply-gtk`), then runs
  `$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme` followed by
  `$(PYTHON) tools/apply_cursor.py`, behind `require_python`/`require_python_version`.
  `remove-cursor` runs `$(PYTHON) tools/apply_cursor.py --remove` behind the same Python guards.
- `README.md`: replace the cursor paragraph's "Nothing selects it yet." with the opt-in commands,
  the `$HOME/.icons/org.macos8.desktop` symlink, the selection name, the restart note (the selector
  says a restart is needed for the new pointer to display correctly), and the removal note. Add no
  new `?=` variable.
- `docs/invariants.md`: add one row under `## icons`: the opt-in link/selection exposes the shipped
  arrow at the Xcursor path and selects it, refuses a foreign path, and removal reverses only our
  link, leaving a foreign path and `kcminputrc` untouched; pinned to
  `tests/test_apply_cursor.py::TestInstall`, `::TestRemove` and `::TestSelection`. The provenance
  exception records that no reference screenshot shows a pointer, and that the `~/.icons` path, the
  theme name and the selector are Xcursor/KDE-required values.
- `PLANS.md`'s scope-drift paragraph changes its "nothing selects it yet" phrase to name `make
  apply-cursor`/`make remove-cursor` once this lands; the historical "not planned yet" wording in
  `PLANS-DONE.md` is left alone.

**Files touched.** `tools/apply_cursor.py` (new), `tests/test_apply_cursor.py` (new), `Makefile`,
`README.md`, `docs/invariants.md` and `PLANS.md` (this entry and the scope-drift sentences). Do not
edit `PLANS-DONE.md`, the cursor generator, any `theme/` file, or the installed-theme layout.

**Acceptance criteria.**
- `tests/test_apply_cursor.py` pins: an absolute `HOME` is required (unset and relative refused by
  name); the data-home fallback; a missing installed theme, `index.theme` or `cursors/left_ptr` is
  refused by name; install creates `$HOME/.icons/org.macos8.desktop` as a symlink to the installed
  icon theme, a repeat install succeeds, and a foreign symlink, real directory or file is refused
  without being changed; the selector is invoked as `plasma-apply-cursortheme org.macos8.desktop`,
  a missing selector exits 2 naming it, and a non-zero selector exits 1 with its log tail; removal
  unlinks only our symlink (including a dangling one), leaves a foreign path and `.icons` in place,
  succeeds when repeated, and prints the `kcminputrc` note only when the selection still names
  `org.macos8.desktop`. Changing the link target, deleting the installed-theme check or dropping
  the foreign-path guard makes the matching test fail.
- The Makefile tests pin `apply-cursor`'s dry run (`INSTALL_PACKAGES=icon-theme` before
  `tools/apply_cursor.py`), its `DESTDIR` refusal, and the Python-version refusal; `make help` lists
  both targets and README names `make apply-cursor` and `make remove-cursor`.
- `make check CHECK_TESTS=test_apply_cursor` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## icons` row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

## Done
