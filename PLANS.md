# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role):** The
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
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`
but not yet selected); the GTK 3 and GTK 4 Platinum stylesheets under `theme/gtk/` (not yet
installable; part 3/4 is planned below); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them); and a **lock screen** is out of scope
unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered 2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both now have plan entries in the queue.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed; part 3/4 is queued as two entries — the opt-in install (part 1/2) and, blocked on it, the
selection (part 2/2) — and part 4/4 (Firefox `userChrome.css` plus profile preference) is not
planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed but not yet selected); part 2/3 (a
Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) is queued as one entry,
the Lato body face only, because Lato is the only family the package installs. Until part
3/3 lands, KDE, Plasma and Qt applications keep the user's own font; GTK and Firefox
applications keep their own chrome regardless (the queued GTK entries cover GTK, and
Firefox is GTK series part 4/4, not planned).

### GTK opt-in, part 1/2: Install the GTK 3 and GTK 4 Platinum themes opt-in (planned 2026-10-21 by the plan role; GTK series part 3/4)

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge, so
a feature-run diff to `PLANS-DONE.md` is wrong. Before editing, record `grep -n '^## Done$'
PLANS.md`; after the move, `grep -n '^## ' PLANS.md` must print exactly two lines (`## Planned`
and `## Done`) and `grep -n '^### GTK opt-in, part 1/2: Install the GTK 3 and GTK 4
Platinum themes opt-in' PLANS.md` must print exactly one line whose number is greater than the
`## Done` line's. The final report
quotes the actual output of `grep -l "Install the GTK 3 and GTK 4 Platinum themes opt-in" PLANS.md
PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`; never claim a file the diff
does not name.

**Goal.** Parts 1/4 and 2/4 ship `theme/gtk/org.macos8.desktop/index.theme`,
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and
`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, but no make target copies them, so a GTK
application cannot use them without a manual copy. Add an opt-in `gtk` install family, an
`install-gtk` target, and uninstall cleanup, keeping the default `make install` at the families
`INSTALL_PACKAGES` already names and copying no GTK files. This part installs the three files
only; the sibling selection entry below (`requires part 1/2 landed`) adds `make
apply-gtk`/`remove-gtk` and is not part of this diff. This part does not depend on the waiting
Lato font entry.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK theme directory name and its `gtk-3.0/` and
`gtk-4.0/` layout are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop. The sheets' palette is already
grounded through `tests/support/platinum_palette.py`.

**Approach.**
- `Makefile`: add `GTK_ID := org.macos8.desktop`, `GTK_PACKAGE := theme/gtk/$(GTK_ID)` and
  `GTK_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(GTK_ID)`. This is the directory the
  Kvantum package already uses (`.../themes/org.macos8.desktop/Kvantum/`), so the two artifacts
  share a theme directory; do not use `install_package`, which would replace the whole directory
  and delete `Kvantum/`.
- `Makefile`: add `gtk` to `INSTALL_FAMILIES` but not to the default `INSTALL_PACKAGES`; reword
  the comment above them so it says the default installs the families `INSTALL_PACKAGES` names and
  that `gtk` is opt-in. Add a `define install_gtk` after `install_kvantum`: create
  `$(GTK_INSTALL_DIR)/gtk-3.0` and `gtk-4.0`, copy `index.theme`, `gtk-3.0/gtk.css` and
  `gtk-4.0/gtk.css` to the hidden staging siblings `.index.theme.staging`,
  `gtk-3.0/.gtk.css.staging` and `gtk-4.0/.gtk.css.staging` under one EXIT trap that removes all
  three, then rename each into place. A failed copy leaves the previous files untouched and
  removes every staging sibling.
- `Makefile`: gate the `install_gtk` call on `gtk` in `_install`; in `_uninstall` remove the three
  GTK files and those three staging siblings, then `rmdir` `gtk-3.0` and `gtk-4.0` when they are
  empty (`|| true`), leaving `Kvantum/` and every other theme directory alone. Extend the
  shared-parent comment to name the `themes/org.macos8.desktop` sharing.
- `Makefile`: add the public `install-gtk` target (runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`), add it to `.PHONY` and the `help` target list. `make uninstall`
  still removes all installed artifacts.
- `tests/support/gtk_fixtures.py` (new): `GTK_ID`, `PACKAGE` and `SHIPPED_FILES` naming
  `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`, so the install test and the selection
  test can share them.
- `tests/test_gtk_install.py` (new, modelled on `tests/test_kvantum_install.py` because the theme
  shares `themes/org.macos8.desktop`): the source package's `shipped_files` equals
  `SHIPPED_FILES`; `make install INSTALL_PACKAGES=gtk` copies all three byte for byte and is
  repeatable; a default `make install` writes no `index.theme` or `gtk-*/gtk.css` but still writes
  `Kvantum/`; a shadowed failing `install` leaves the previous three files intact and removes
  every staging sibling; `make uninstall` removes the three files and staging siblings, leaves a
  sibling `Kvantum/` file and a second theme directory untouched, and repeats successfully.
- `tests/support/installed_paths.py`: add `installed_gtk_theme(destdir)` returning
  `themes/org.macos8.desktop` below the module's `XDG_DATA_HOME`, and name the theme in the
  module docstring.
- `tests/support/theme_install.py`: add the GTK suite to the module docstring's artifact list and
  reword `install`'s docstring so it no longer says the default installs every family (the default
  installs every default family; `gtk` is opt-in).
- `README.md`: add a GTK paragraph after the Kvantum section that names `make install-gtk` (the
  `test_make_help` README check requires the exact target name), the installed path
  `$XDG_DATA_HOME/themes/org.macos8.desktop`, the shared `Kvantum/` directory, that the default
  `make install` copies no GTK files, and that `make uninstall` removes the GTK files. State that
  this part installs the files but does not select them. Do not add the GTK files to the default
  artifact list or change that list's count.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in install pinned to
  `tests/test_gtk_install.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the theme directory layout is GTK-required.

**Files touched.** `Makefile`, `tests/support/gtk_fixtures.py` (new),
`tests/test_gtk_install.py` (new), `tests/support/installed_paths.py`,
`tests/support/theme_install.py`, `README.md`, `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` writes exactly `index.theme`,
  `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` under `<tmp>/share/themes/org.macos8.desktop/` and
  leaves a pre-existing `Kvantum/` file there untouched; the default `make install DESTDIR=<tmp>`
  still writes the default families and leaves all three GTK files absent.
- A shadowed `install` that fails on a GTK copy leaves the previous three files byte-identical and
  no `.staging` sibling; `make uninstall DESTDIR=<tmp>` removes the three GTK files and their
  `.staging` leftovers, leaves `Kvantum/` and a second theme directory untouched, and repeats
  successfully.
- `make check CHECK_TESTS='test_gtk_install test_gtk_theme test_make_help test_theme_install'`
  passes; corrupting a staged copy, removing `gtk` from `INSTALL_FAMILIES`, or adding it to the
  default `INSTALL_PACKAGES` makes the matching test fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move), does not name `PLANS-DONE.md`, and the README's default artifact list does not gain a GTK
  entry or change its count.
- When the work lands, `grep -n '^### GTK opt-in, part 1/2: Install the GTK 3 and GTK 4
  Platinum themes opt-in' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Install the GTK 3 and GTK 4 Platinum themes opt-in' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Install the GTK 3 and GTK 4 Platinum themes opt-in" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the opt-in GTK install family, the Makefile
  staging and the tests, and its `RISK` names the shared `themes/org.macos8.desktop` directory and
  the opt-in default; a report that calls the change only backlog bookkeeping contradicts the
  diff.

### GTK opt-in, part 2/2: Select the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-21 by the plan role; requires part 1/2 landed)

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
2/2: Select the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one line
whose number is greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select the
installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of
`git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 3/4 installs the GTK 3 and GTK 4 sheets under
`$XDG_DATA_HOME/themes/org.macos8.desktop`, but nothing selects them, so GTK applications still
draw their system theme. Add `make apply-gtk` and `make remove-gtk` plus `tools/apply_gtk.py`:
set `gtk-theme-name=org.macos8.desktop` in both GTK settings files and give libadwaita
applications the GTK 4 sheet as user CSS. This entry requires part 1/2 landed (the opt-in install family
and installed file layout); do not reimplement them. It does not add Firefox chrome, which remains
GTK series part 4/4 and is not planned here.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK settings path, the `gtk-theme-name` key and the
libadwaita user-CSS path are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop.

**Approach.**
- `Makefile`: add public targets `apply-gtk` (refuses a non-empty `DESTDIR`, requires Python with
  both `require_python` and `require_python_version`, runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`, then `$(PYTHON) tools/apply_gtk.py`) and `remove-gtk` (requires
  Python the same way, runs `$(PYTHON) tools/apply_gtk.py --remove`). Add them to `.PHONY` and to
  `help`'s target list. Keep `install-gtk` unchanged.
- `tools/apply_gtk.py` (new): follow `tools/apply_theme.py`'s direct-or-package import block,
  `EscapingArgumentParser`, `report_error`, `report_failure` and `escape_controls`. Put the
  fallback in two module-level helpers so both are directly testable: `_config_home(env)` returns
  an absolute `$XDG_CONFIG_HOME`, else an absolute `$HOME/.config`, else `None`; `_data_home(env)`
  returns an absolute `$XDG_DATA_HOME`, else an absolute `$HOME/.local/share`, else `None`. `main`
  passes `os.environ` to both and, when either is `None`, exits 2 through `report_error` naming
  the ineffective variable and saying to set `XDG_DATA_HOME`/`XDG_CONFIG_HOME` or an absolute
  `HOME` -- the same resolution and refusal as the Makefile's `require_data_home`. Resolve both
  homes before requiring the installed sheet, so the refusal is testable without an install.
  Constants: `TOOL = "apply_gtk"`, `GTK_ID = "org.macos8.desktop"`, the marker comment
  `/* org.macos8.desktop GTK 4 user CSS */`, and the installed CSS path built from the resolved
  data home.
- `tools/apply_gtk.py`: for apply, require the installed
  `themes/org.macos8.desktop/gtk-4.0/gtk.css` (exit 1 naming `make install-gtk` when absent); in
  `$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` set
  `gtk-theme-name=org.macos8.desktop` in `[Settings]`, preserving every other line, stripping a
  leading UTF-8 BOM only for matching and writing it back, replacing the last `gtk-theme-name`
  line in the section or inserting one after the `[Settings]` header, and appending `[Settings]`
  when it is absent; write both files through a `.staging` sibling and `os.replace`. Write
  `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` as the marker line followed by
  `@import url("<installed gtk-4.0/gtk.css as a file URI>");` (use `Path.as_uri()`), but leave an
  existing `gtk.css` whose first line is not the marker untouched and print a note. For `--remove`,
  delete the marker `gtk.css`, and delete only `gtk-theme-name` lines in `[Settings]` whose value
  is `org.macos8.desktop`, leaving foreign values and files. Both modes print a note that running
  GTK applications must be restarted.
- `tests/test_gtk_apply.py` (new): drive `tools.apply_gtk.main` with `XDG_CONFIG_HOME` and `HOME`
  pointed at a temp directory. Pin: apply writes both settings files with `[Settings]` and our
  `gtk-theme-name`; it preserves an existing `gtk-font-name` line and a comment; it replaces an
  existing `gtk-theme-name`; it appends `[Settings]` when absent; it creates the marker `gtk.css`
  whose second line imports the installed sheet as a file URI; it exits 1 naming `make install-gtk`
  when the installed sheet is missing; a foreign `gtk.css` is left byte-identical with a note;
  `--remove` removes our key and marker and leaves a foreign key and file. Add `TestHomeResolution`
  that patches the environment for `main` and pins every helper branch: an absolute
  `XDG_DATA_HOME` is used even with `HOME` unset (with `XDG_CONFIG_HOME` absolute); an empty and a
  relative `XDG_DATA_HOME` each fall back to `$HOME/.local/share`; an empty and a relative
  `XDG_CONFIG_HOME` each fall back to `$HOME/.config`; and `main` exits 2 with a diagnostic naming
  `XDG_DATA_HOME` when that value is not absolute and `HOME` is unset or relative, and likewise for
  `XDG_CONFIG_HOME`. Add `TestMakeApplyGtk` for the target order (`install` before the script), the
  non-empty-`DESTDIR` refusal, the Python-version guard, `make -n remove-gtk`, and `make help`
  listing both targets.
- `README.md`: extend the GTK paragraph from part 3/4 with `make apply-gtk` and `make remove-gtk`
  (the `test_make_help` README check requires the exact target names), both `gtk-theme-name`
  settings keys, the libadwaita `gtk-4.0/gtk.css` marker/import, the need to restart GTK
  applications, and that KDE users can also choose the theme in System Settings -> Application
  Style -> GNOME/GTK Application Style. State that `make remove-gtk` is what clears the selection.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in selection pinned
  to `tests/test_gtk_apply.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the settings keys and user-CSS path are GTK-required.

**Files touched.** `Makefile`, `tools/apply_gtk.py` (new), `tests/test_gtk_apply.py` (new),
`README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record).
Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make apply-gtk` with `XDG_DATA_HOME`, `XDG_CONFIG_HOME` and `HOME` under a temp root writes
  `[Settings]`/`gtk-theme-name=org.macos8.desktop` to `gtk-3.0/settings.ini` and
  `gtk-4.0/settings.ini`, preserves an unrelated key and comment, and writes a `gtk-4.0/gtk.css`
  whose first line is the marker and whose second line is `@import url("file://<installed
  gtk-4.0/gtk.css>");`; the same command exits 1 naming `make install-gtk` when the installed
  sheet is absent.
- `make remove-gtk` removes only our `gtk-theme-name` line and marker `gtk.css`; a foreign value
  in `gtk-3.0/settings.ini` and a foreign `gtk-4.0/gtk.css` survive byte for byte.
- `make check CHECK_TESTS='test_gtk_apply test_make_help'` passes; corrupting the settings edit,
  the marker check or a home helper makes the matching test fail; `tests/invariants.py` accepts
  the new row and `make check` is green.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestHomeResolution`; making either helper skip
  the `HOME` fallback, accept a relative value, or return a path when both candidates are
  unusable makes a case fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 2/2: Select the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Select the installed GTK 3 and GTK 4 Platinum themes' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Select the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the GTK selection tool and Makefile targets,
  and its `RISK` names the GTK settings files and libadwaita user CSS; a report that calls the
  change only backlog bookkeeping contradicts the diff.

### Select the Lato body face in KDE, Plasma and Qt applications (planned 2026-10-22 by the plan role; UI font series part 3/3, body face only)

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### Select the Lato body
face in KDE, Plasma and Qt applications' PLANS.md` must print exactly one line whose number is
greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select
the Lato body face in KDE, Plasma and Qt applications" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 landed the Lato package and `make install` copies it, but the global theme's
`contents/defaults` names no font, so KDE, Plasma and Qt applications keep the user's font
(README's Status line calls the package "installed but not yet selected"). Make the global theme
select the installed `Lato` family for the general, menu, toolbar and smallest-readable fonts and
for window titles, at KDE's default point sizes, by adding those keys to `contents/defaults` —
the same declarative mechanism that already selects the colour scheme, icons, decoration and
Kvantum style. This is the body face of part 3/3 only: part 2/3 (a Chicago-style menu face) has no
confirmed redistribution licence and is not planned, so the menu bar and window titles wear Lato
for now and the part that vendors a Chicago-style face will update `menuFont`/`activeFont` then.
Monospaced text (`fixed`) keeps the user's fixed font because the package ships no monospace
face. No `Makefile`, `tools/` or install behaviour changes: `make install` still only copies the
family, and `make apply` selects it by re-applying the global theme.

**Reference grounding.** No reference pixel is sampled: Lato is this theme's substitute for
Charcoal (`theme/fonts/org.macos8.desktop/PROVENANCE.md`), and the point sizes are KDE's defaults
(10 for `font`, `menuFont`, `toolBarFont` and `activeFont`; 8 for `smallestReadableFont`), not a
metric measured in a screenshot. Record both as provenance exceptions in `docs/invariants.md`;
matching the reference's 12px body text would need a rendered comparison, which this part does
not claim.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: in `[kdeglobals][General]`, after
  `ColorScheme=MacOS8`, add `font=Lato,10`, `menuFont=Lato,10`, `toolBarFont=Lato,10` and
  `smallestReadableFont=Lato,8`; add a new `[kdeglobals][WM]` section between it and
  `[kdeglobals][Icons]` holding `activeFont=Lato,10`. Leave every other group, key and byte
  identical.
- `tests/test_lookandfeel.py`: add `WM_SECTION = "kdeglobals][WM"` beside the other section
  constants; in `TestDefaults.test_the_expected_sections_and_keys_are_set` put `WM_SECTION` after
  `DEFAULTS_SECTION`, extend the `DEFAULTS_SECTION` options to `["ColorScheme", "font",
  "menuFont", "toolBarFont", "smallestReadableFont"]` in file order, and expect
  `["activeFont"]` for `WM_SECTION`. Add
  `TestDefaults.test_fonts_name_the_installed_lato_family`: for each of the five
  (section, key) pairs, split the value at the first comma, assert the family is exactly
  `Lato`, assert the remaining point size parses as a positive integer, and assert
  `smallestReadableFont` is not larger than `font`. The test reads the shipped file only; it runs
  no KDE tool.
- `theme/fonts/org.macos8.desktop/PROVENANCE.md`: replace the `## Selection` paragraph's "it does
  not select it ... later part" with the selection this part adds (the five roles, KDE default
  sizes, monospace left alone, the Chicago-style face still pending part 2/3).
- `tests/test_fonts.py`: reword the module docstring's "but does not select it in KDE/Plasma/Qt"
  to say the global theme's defaults select the family; no assertion in the file changes.
- `README.md`: in the Status line change "installed but not yet selected" to "selected by the
  global theme"; in the Installing font sentence replace "this part installs the family but does
  not select it" with the five selected roles and KDE's default sizes, that monospaced text keeps
  the user's fixed font, and that menus and window titles use Lato until a Chicago-style face
  lands; in the `make apply` paragraph replace "(the Lato font package is installed but, like
  `make install`, not selected)" with a statement that `make apply` re-applies the global theme,
  which selects Lato, while a bare `make install` only copies it. Leave the artifact count
  (eight) and the target list unchanged.
- `docs/invariants.md`: extend the `## look-and-feel` row whose guarantee lists what
  `contents/defaults` selects to name the `Lato` font family, and add a `## fonts` row pinned to
  `tests/test_lookandfeel.py::TestDefaults`: the global theme selects the installed Lato family
  for the general, menu, toolbar, smallest-readable and window-title fonts; provenance exception:
  Lato is a Charcoal substitute, the point sizes are KDE defaults, and monospace keeps the user's
  fixed font.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/test_lookandfeel.py`, `theme/fonts/org.macos8.desktop/PROVENANCE.md`,
`tests/test_fonts.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to
`## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- The defaults file holds exactly the five keys above with the `Lato` family and those sizes,
  `make check CHECK_TESTS='test_lookandfeel test_fonts'` passes, and changing `Lato` to another
  family, dropping a key, adding a sixth font role, or making a size zero, negative or
  non-numeric makes the matching `TestDefaults` assertion fail.
- `tests/invariants.py` accepts the extended look-and-feel row and the new fonts row, and
  `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`, `Makefile` or any file under `tools/`; README still
  says eight artifacts and lists no new target.
- When the work lands, `grep -n '^### Select the Lato body face in KDE, Plasma and Qt
  applications' PLANS.md` prints exactly one line whose number is greater than the `## Done`
  line's; `grep -F 'Select the Lato body face in KDE, Plasma and Qt applications' PLANS-DONE.md`
  exits 1 with no output; and `git diff --name-status` does not name `PLANS-DONE.md`. The report's
  `SUMMARY` names the `contents/defaults` font selection and its `RISK` names KDE reading the
  font keys from the theme defaults and the menu/window-title face borrowing Lato until a
  Chicago-style face lands; a report that calls the change only backlog bookkeeping contradicts
  the diff.

## Done
