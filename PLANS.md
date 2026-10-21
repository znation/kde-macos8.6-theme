# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-19 by the clean role; plan status updated 2026-10-21 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
the GTK 3 and GTK 4 Platinum stylesheets under `theme/gtk/` (not yet installable; part 3/4 is
planned below); and the render and fidelity tooling
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
landed, part 3/4 (the opt-in install and selection) is planned below, and part 4/4 (Firefox
`userChrome.css` plus profile preference) is not planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and is planned below; part 2/3 (a Chicago-style menu face, whose
redistribution licence is still unresolved) and part 3/3 (selecting the installed families in
KDE/Plasma/Qt) are not planned yet. Until those parts land, the menu bar and dialog text keep the
user's desktop font, and GTK and Firefox applications keep their own chrome.

### Vendor the Lato body font and install it (planned 2026-10-21 by the plan role; part 1/3)

**Plan record.** This entry is finished only when it sits under `PLANS.md`'s existing `## Done`
heading, the file's last heading, with a closing date added to its `### ` heading. Follow the
feature role's step 6 literally: cut it from `## Planned`, paste it as the first entry under
`## Done`, and leave both `## ` headings unchanged (`grep -n '^## ' PLANS.md` prints exactly
`## Planned` and `## Done` before and after). Do **not** edit `PLANS-DONE.md`: that file is
tumwater's archive and must have no diff. The run's final `VERIFIED` line must quote the actual
output of `grep -l "Vendor the Lato body font" PLANS.md PLANS-DONE.md`, which is exactly
`PLANS.md`; a claim that the entry is in `PLANS-DONE.md` is false. If the entry cannot be moved to
`## Done`, leave it under `## Planned` and report that instead of editing `PLANS-DONE.md`.

**Goal.** QUESTIONS.md's font answer (2026-10-19) directs the theme to vendor a Chicago/Charcoal-style
font, but no `theme/fonts` directory exists and `make install` copies no font. Ship Lato Regular and
Bold (SIL OFL 1.1, already installed on this machine, so no network fetch) as the Charcoal-style
body face under a new `theme/fonts/org.macos8.desktop` artifact, installed to
`$XDG_DATA_HOME/fonts/org.macos8.desktop`, so a later selection part can name the `Lato` family.
This is part 1/3 of the UI-font series: it vendors and installs the body face only. Part 2/3 will
vendor a Chicago-style menu face once a redistribution licence is confirmed (the ChicagoFLF
provenance is still unresolved, so it is deliberately not shipped here); part 3/3 will select the
installed families in KDE/Plasma/Qt. Neither sibling is in the queue yet, and this part does not
depend on them.

**Reference grounding.** `aboutsystem_betawiki.png`'s dialog body draws Charcoal's narrower
humanist forms at 12px, but the theme ships no Apple font and samples no font pixel: Lato is this
theme's substitute for Charcoal, and `PROVENANCE.md` records it as an approximation rather than a
reference anchor. The two screenshot crops (the menu bar in `desktop_betawiki.png` and the
`System` dialog body in `aboutsystem_betawiki.png`) are recorded there as context for the later
Chicago/selection parts, not copied.

**Approach.**
- Add `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` and `Lato-Bold.ttf`, copied byte for byte
  from `/usr/share/fonts/truetype/lato/` (657,212 and 657,188 bytes; `.gitattributes` leaves
  `.ttf` out of Git LFS, so they are committed directly). Add `LICENSE-Lato.txt`, a byte-for-byte
  copy of `/usr/share/doc/fonts-lato/copyright`: its `Files: *` stanza carries the upstream
  copyright line and the complete OFL-1.1 body, while its trailing `Files: debian/*` stanza is
  Debian packaging GPL-2+ text that does not cover the fonts. `PROVENANCE.md` records the local
  source paths, the upstream source (`http://www.latofonts.com`, Debian package `fonts-lato`), the
  SHA-256 digests of all three files, the internal family name `Lato`, the `debian/*` stanza's
  scope, and why the face is an approximation of Charcoal.
- `Makefile`: add `FONT_ID := org.macos8.desktop`, `FONT_PACKAGE := theme/fonts/$(FONT_ID)` and
  `FONT_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/fonts`; add `fonts` to `INSTALL_FAMILIES` and to
  the default `INSTALL_PACKAGES`; in `_install` create `$(FONT_INSTALL_DIR)` and copy the package
  with the existing `install_package` swap; in `_uninstall` remove
  `$(FONT_INSTALL_DIR)/$(FONT_ID)` together with its `.staging` and `.old` siblings. Update the
  `help` line's default family list (the default is compared against the `?=` value by
  `tests/test_make_help.py`). Update the two family comments: the `INSTALL_FAMILIES` comment's
  `all seven` becomes `all eight`, and `_uninstall`'s shared-parent-directory comment lists
  `fonts` with the other families.
- `tests/support/installed_paths.py`: add `installed_fonts_dir(destdir)` returning the `fonts`
  directory under `$DESTDIR`'s data home, built from the module's `XDG_DATA_HOME` constant like
  the other helpers, and `installed_font_package(destdir, package_id)` returning its `package_id`
  child, matching the Makefile paths; add the font package to the module docstring's list of
  installed artifacts.
- `tests/support/install_lifecycle_cases.py`: add the font suite to the module docstring's family
  list and change the `MAKE_PACKAGES` comment's `instead of all seven` to `instead of all eight`.
  `tests/support/install_failure_cases.py`: change the same `instead of all seven` comment to
  `instead of all eight` (the font package uses the shared staging swap, so the family count it
  describes gains one). `tests/support/theme_install.py`: add the font package to its module
  docstring's list of installable artifact suites.
- `tests/test_fonts.py` (new): `TestFontFiles` parses each TTF's sfnt `name` table (name ID 1 and
  2) with `struct` and asserts the family is `Lato` and the subfamily is `Regular`/`Bold`; pins the
  SHA-256 of both TTFs and of `LICENSE-Lato.txt` and asserts `PROVENANCE.md` names all three
  digests; asserts `LICENSE-Lato.txt` contains `License: OFL-1.1`, the copyright line
  `(c) 2010-2011, Łukasz Dziedzic` and the OFL clause heading `PERMISSION & CONDITIONS` (the file
  has no `SIL OPEN FONT LICENSE` heading, so do not assert that phrase). `TestFontsInstall`
  subclasses `InstallLifecycleCases` with `MAKE_PACKAGES = "fonts"`,
  `PACKAGE_DIR = "theme/fonts/org.macos8.desktop"`, `INSTALLED_FILES` naming the four files, and
  `installed_parent`/`installed_package_dir` overridden to the new helpers, so it gets the
  byte-for-byte, registry-coverage, repeat-install and uninstall-leftover checks once. Add
  `test_uninstall_leaves_a_sibling_font_family`, which creates `$fonts/other-family` before the
  uninstall and asserts it survives.
- `tests/test_theme_install.py`: in `TestWhitespaceInInstallPaths`, add
  `installed_paths.installed_font_package(destdir, package)` to the `directories` list checked
  before and after the round trip, and change both `seven artifacts` docstrings to eight. In
  `TestInstallPackages.test_one_family_installs_only_that_family`, add
  `installed_paths.installed_fonts_dir(tmp)` to `other_dirs` so installing `color-scheme` leaves
  `fonts/` absent.
- `README.md`: change each of the four `seven artifacts` sentences -- the Status line, the
  Installing paragraph, the uninstall paragraph and the `make apply` paragraph -- to eight, and add
  the `org.macos8.desktop` Lato font package to each list with its
  `$XDG_DATA_HOME/fonts/org.macos8.desktop` path, its OFL-1.1 licence and the note that this part
  installs the family but does not select it. In the uninstall paragraph, add `fonts/` to the
  shared-directory list. Leave the Status paragraph's archive sentence (`... fixed bugs are
  archived in BUGS-FIXED.md.`) byte-identical: it is out of scope for this part, and mentioning
  `PLANS-DONE.md` here would contradict the Plan record above.
- `docs/invariants.md`: add a `## fonts` section between `## desktoptheme` and `## gtk` (every
  `theme/` subsystem needs one) with a row for the shipped Lato family/digests pinned to
  `tests/test_fonts.py::TestFontFiles` and a row for the install/uninstall lifecycle pinned to
  `tests/test_fonts.py::TestFontsInstall`, with the provenance exception stating that Lato is a
  Charcoal substitute, not a sampled reference face.

**Files touched.** `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` (new),
`theme/fonts/org.macos8.desktop/Lato-Bold.ttf` (new),
`theme/fonts/org.macos8.desktop/LICENSE-Lato.txt` (new),
`theme/fonts/org.macos8.desktop/PROVENANCE.md` (new), `Makefile`,
`tests/support/installed_paths.py`, `tests/support/install_lifecycle_cases.py`,
`tests/support/install_failure_cases.py`, `tests/support/theme_install.py`,
`tests/test_fonts.py` (new), `tests/test_theme_install.py`, `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit
`PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=fonts DESTDIR=<tmp>` writes exactly the four files above under
  `$XDG_DATA_HOME/fonts/org.macos8.desktop/`; a default `make install DESTDIR=<tmp>` writes them
  too; `make uninstall` removes that directory and its `.staging`/`.old` leftovers while leaving a
  sibling font family's directory in place (pinned by
  `tests/test_fonts.py::TestFontsInstall.test_uninstall_leaves_a_sibling_font_family`).
- `make check CHECK_TESTS=test_fonts` passes; removing either TTF, changing a byte, renaming the
  family or subfamily in the font, editing `LICENSE-Lato.txt`, or dropping a digest from
  `PROVENANCE.md` makes it fail.
- `tests/invariants.py` accepts `theme/fonts` with its `## fonts` section, and
  `make check CHECK_TESTS=test_theme_install test_make_help` passes with the new family.
- `grep -n seven README.md Makefile tests/support/install_lifecycle_cases.py
  tests/support/install_failure_cases.py tests/test_theme_install.py` finds no artifact-count
  text, and the README Status paragraph's archive sentence still reads exactly `Open work is
  tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions
  needed); fixed bugs are archived in BUGS-FIXED.md.` (a diff that rewrites it fails this plan).
- `git diff --name-status` names only the files listed under "Files touched"; an edit outside that
  list is out of scope for this part.
- When the work lands, `grep -n '^### Vendor the Lato body font and install it' PLANS.md` prints
  exactly one line whose number is greater than the `## Done` line's; `grep -F 'Vendor the Lato
  body font' PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`; and `git diff --name-status` does not name `PLANS-DONE.md`. The final
  report quotes the actual output of `grep -l "Vendor the Lato body font" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`).
- No `kdeglobals` write, global-theme `contents/defaults` change, `tools/apply_*` change, GTK,
  Firefox or README archive-sentence change is made in this part; `make check` is green.

### Install the GTK 3 and GTK 4 Platinum themes opt-in and select them (planned 2026-10-21 by the plan role; GTK series part 3/4)

**Plan record.** This entry is finished only when it sits under `PLANS.md`'s existing `## Done`
heading, the file's last heading, with a closing date added to its `### ` heading. Follow the
feature role's step 6 literally: cut it from `## Planned`, paste it as the first entry under
`## Done`, and leave both `## ` headings unchanged (`grep -n '^## ' PLANS.md` prints exactly
`## Planned` and `## Done` before and after). Do **not** edit `PLANS-DONE.md`: that file is
tumwater's archive and must have no diff. The run's final `VERIFIED` line must quote the actual
output of `grep -l "Install the GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`, which is
exactly `PLANS.md`; a claim that the entry is in `PLANS-DONE.md` is false. If the entry cannot be
moved to `## Done`, leave it under `## Planned` and report that instead of editing
`PLANS-DONE.md`.

**Goal.** Parts 1/4 and 2/4 ship `theme/gtk/org.macos8.desktop/index.theme`,
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and
`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, but no make target copies them, so a GTK
application cannot use them without a manual copy. Add an opt-in `gtk` install family, an
`install-gtk` target, and `apply-gtk`/`remove-gtk` helpers that select the theme in the GTK
settings and give libadwaita applications the GTK 4 sheet as user CSS. The default `make
install` is unchanged: it installs every family `INSTALL_PACKAGES` already names and copies no
GTK files. This is part 3/4 of the
GTK and Firefox series; part 4/4 adds the Firefox chrome and is not planned yet. This part does
not depend on the waiting Lato font entry.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. The sheets'
palette is already reference-grounded through `tests/support/platinum_palette.py` and their
geometry is this theme's adaptation; this part adds no visual value and samples no pixel. The
GTK theme directory name, the `gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` `gtk-theme-name`
key and the `gtk-4.0/gtk.css` user-CSS path are GTK-required values the reference set does not
show; record that in `docs/invariants.md` rather than claiming a GTK reference crop.

**Approach.**
- `Makefile`: add `GTK_ID := org.macos8.desktop`, `GTK_PACKAGE := theme/gtk/$(GTK_ID)` and
  `GTK_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(GTK_ID)`. `GTK_INSTALL_DIR` is the
  same directory the Kvantum package already uses (`.../themes/org.macos8.desktop/Kvantum/`), so
  the two artifacts share a theme directory; do not use `install_package`, which would replace
  the whole directory and delete the Kvantum files.
- `Makefile`: add `gtk` to `INSTALL_FAMILIES` but **not** to the default `INSTALL_PACKAGES`; the
  comment above `INSTALL_FAMILIES` says the default installs every family, so reword it to say
  the default installs the families `INSTALL_PACKAGES` names and that `gtk` is opt-in. Add a
  `define install_gtk` after
  `install_kvantum`: create `$(GTK_INSTALL_DIR)/gtk-3.0` and `$(GTK_INSTALL_DIR)/gtk-4.0`, copy
  `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` to the hidden staging siblings
  `.index.theme.staging`, `gtk-3.0/.gtk.css.staging` and `gtk-4.0/.gtk.css.staging` (one EXIT
  trap removes all three), then rename each into place. A failed copy leaves the previous files
  untouched and removes every staging sibling.
- `Makefile`: gate the `install_gtk` call on `gtk` in `_install`; in `_uninstall` remove only the
  three GTK files and those three staging siblings, then `rmdir` `gtk-3.0` and `gtk-4.0` when they
  are empty (`|| true`), leaving `Kvantum/` and every other theme directory alone. Extend the
  shared-parent comment to name the `themes/org.macos8.desktop` sharing.
- `Makefile`: add public targets `install-gtk` (runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`), `apply-gtk` (refuses a non-empty `DESTDIR`, requires Python with
  both `require_python` and `require_python_version`, runs the same nested install, then
  `$(PYTHON) tools/apply_gtk.py`) and `remove-gtk` (requires Python the same way, runs
  `$(PYTHON) tools/apply_gtk.py --remove`). Add them to `.PHONY` and to `help`'s target list.
  `install-gtk` is the opt-in install; `make uninstall` still removes all installed artifacts.
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
  `/* org.macos8.desktop GTK 4 user CSS */`, and the shipped/installed CSS path built from the
  resolved data home. For apply: require the installed `themes/org.macos8.desktop/gtk-4.0/gtk.css`
  (exit 1 naming `make install-gtk` when absent); in `$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and
  `gtk-4.0/settings.ini` set `gtk-theme-name=org.macos8.desktop` in `[Settings]`, preserving every
  other line, stripping a leading UTF-8 BOM only for matching and writing it back, replacing the
  last `gtk-theme-name` line in the section or inserting one after the `[Settings]` header, and
  appending `[Settings]` when it is absent; write both files through a `.staging` sibling and
  `os.replace`. Write `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` as the marker line followed by
  `@import url("<installed gtk-4.0/gtk.css as a file URI>");` (use `Path.as_uri()`), but leave an
  existing `gtk.css` whose first line is not the marker untouched and print a note. For `--remove`:
  delete the marker `gtk.css`, and delete only `gtk-theme-name` lines in `[Settings]` whose value
  is `org.macos8.desktop`, leaving foreign values and files. Both modes print a note that running
  GTK applications must be restarted.
- `theme/gtk/org.macos8.desktop/index.theme`: change `Comment` to `Standalone Platinum controls
  for GTK 3 and GTK 4 applications`; `tests/test_gtk_theme.py::TestGtkTheme.test_index_theme`
  pins that exact string, so update it with the file.
- `tests/support/gtk_fixtures.py` (new): `GTK_ID`, `PACKAGE` and `SHIPPED_FILES` naming
  `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`, so the two GTK test modules share them.
- `tests/test_gtk_install.py` (new, modelled on `tests/test_kvantum_install.py` because the theme
  shares `themes/org.macos8.desktop`): the source package's `shipped_files` equals
  `SHIPPED_FILES`; `make install INSTALL_PACKAGES=gtk` copies all three byte for byte and is
  repeatable; a default `make install` writes no `index.theme` or `gtk-*/gtk.css` but still writes
  `Kvantum/`; a shadowed failing `install` leaves the previous three files intact and removes every
  staging sibling; `make uninstall` removes the three files and staging siblings, leaves a sibling
  `Kvantum/` file and a second theme directory untouched, and a repeated uninstall succeeds.
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
  listing all three targets.
- `tests/support/installed_paths.py`: add `installed_gtk_theme(destdir)` returning
  `themes/org.macos8.desktop` below the module's `XDG_DATA_HOME`, and name the GTK theme in the
  module docstring; `tests/support/theme_install.py` names the GTK suite in the module docstring's
  artifact list and rewords `install`'s docstring so it no longer says the default installs every
  family (the default installs the seven default families; `gtk` is opt-in);
  `tests/support/install_lifecycle_cases.py` names the GTK suite in its module docstring.
- `README.md`: add a GTK paragraph after the Kvantum section that names `make install-gtk`,
  `make apply-gtk` and `make remove-gtk` (the `test_make_help` README check requires the exact
  target names), the installed path `$XDG_DATA_HOME/themes/org.macos8.desktop`, the shared
  `Kvantum/` directory, both `gtk-theme-name` settings keys, the libadwaita `gtk-4.0/gtk.css`
  marker/import, the need to restart GTK applications, and that KDE users can also choose the
  theme in System Settings -> Application Style -> GNOME/GTK Application Style. State that the
  default `make install` copies no GTK files and that `make uninstall` removes the GTK files but
  `make remove-gtk` is what clears the selection. Do not add the GTK files to the default
  artifact list; write the default's artifact count as it stands when this part lands, because
  another waiting plan may extend it.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in install and
  selection pinned to `tests/test_gtk_install.py`, `tests/test_gtk_apply.py` and
  `tests/test_gtk_theme.py::TestGtkTheme.test_index_theme`, with the provenance exception that no
  reference screenshot shows a GTK widget and that the theme name and settings paths are
  GTK-required values.

**Files touched.** `Makefile`, `theme/gtk/org.macos8.desktop/index.theme`, `tools/apply_gtk.py`
(new), `tests/support/gtk_fixtures.py` (new), `tests/test_gtk_install.py` (new),
`tests/test_gtk_apply.py` (new), `tests/test_gtk_theme.py`, `tests/support/installed_paths.py`,
`tests/support/theme_install.py`, `tests/support/install_lifecycle_cases.py`, `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit
`PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` writes exactly `index.theme`,
  `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` under `<tmp>/share/themes/org.macos8.desktop/` and
  leaves a pre-existing `Kvantum/` file there untouched; the default `make install DESTDIR=<tmp>`
  still writes the default families and leaves all three GTK files absent.
- `make uninstall DESTDIR=<tmp>` removes those three GTK files and their `.staging` leftovers,
  leaves `Kvantum/` and a second theme directory untouched, and repeats successfully.
- `make apply-gtk` with `XDG_DATA_HOME`, `XDG_CONFIG_HOME` and `HOME` under a temp root writes
  `[Settings]`/`gtk-theme-name=org.macos8.desktop` to `gtk-3.0/settings.ini` and
  `gtk-4.0/settings.ini`, preserves an unrelated key and comment, and writes a `gtk-4.0/gtk.css`
  whose first line is the marker and whose second line is `@import url("file://<installed
  gtk-4.0/gtk.css>");`; the same command exits 1 naming `make install-gtk` when the installed
  sheet is absent.
- `make remove-gtk` removes only our `gtk-theme-name` line and marker `gtk.css`; a foreign value
  in `gtk-3.0/settings.ini` and a foreign `gtk-4.0/gtk.css` survive byte for byte.
- `make check CHECK_TESTS='test_gtk_install test_gtk_apply test_gtk_theme test_gtk4_theme
  test_make_help'` passes, and corrupting the settings edit, the marker check or a staged copy
  makes the matching test fail; `tests/invariants.py` accepts the new row and `make check` is
  green.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestHomeResolution`; making either helper skip
  the `HOME` fallback, accept a relative value, or return a path when both candidates are
  unusable makes a case fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the
  backlog move), does not name `PLANS-DONE.md`, and the README's default artifact list does not
  gain a GTK entry.
- When the work lands, `grep -n '^### Install the GTK 3 and GTK 4 Platinum themes' PLANS.md`
  prints exactly one line whose number is greater than the `## Done` line's; `grep -F 'Install the
  GTK 3 and GTK 4 Platinum themes' PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md`
  prints exactly `## Planned` and `## Done`; and `git diff --name-status` does not name
  `PLANS-DONE.md`. The final report quotes the actual output of `grep -l "Install the GTK 3 and
  GTK 4 Platinum themes" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`).

## Done
