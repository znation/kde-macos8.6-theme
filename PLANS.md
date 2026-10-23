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

**Needs review 2026-10-23 by feature: too large for one run**

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

### Platinum cursor theme, part 1/2: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; cursor series part 1/2)

**Needs review 2026-10-23 by feature: too large for one run**

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it under
`PLANS.md`'s last heading `## Done`, adding `— done YYYY-MM-DD` to its `### ` heading, exactly as
the other entries' Plan record paragraphs require (never edit `PLANS-DONE.md`; after the move
`grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`). The final report quotes
the actual output of `grep -l "Generate and ship the Xcursor arrow cursor artifact" PLANS.md
PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`.

**Goal.** The theme ships eight artifacts but no cursor, so a themed Plasma session still shows the
Breeze arrow. Mac OS 8.6 draws a black arrow with a white outline; this part builds that cursor as a
KDE/Xcursor theme artifact — `theme/cursors/org.macos8.desktop/cursors/{left_ptr,arrow,default,top_left_arrow}`
(the last three byte-identical X-name copies of `left_ptr`, images at nominal sizes 16, 24 and 32 in
one Xcursor file) — with a deterministic generator, and nothing else. It does not touch the
`Makefile`, the global theme's `contents/defaults`, README's artifact list or any install or
selection path: the sibling entry will add the opt-in install into the shared
`icons/org.macos8.desktop/` directory (the GTK/Kvantum sharing precedent) and select it with
`cursorTheme` in `contents/defaults`; that part is not in the queue yet and this part does not
depend on it.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows the mouse pointer, so no
reference pixel is sampled and the arrow is our own Platinum-style art drawn from a pixel grid in
the generator, not traced from Apple's artwork (the icon theme's standing rule). Its two colours
are `#000000` face and `#FFFFFF` outline, both already pinned in the colour scheme; the nominal
sizes 16/24/32, the Xcursor binary format, the file name `left_ptr` and the X-name aliases are
X/KDE-required values the reference set does not show. Record that provenance exception in
`docs/invariants.md`. Xcursor files have no image extension, so Git LFS (`.gitattributes`) is
untouched.

**Approach.**
- `tools/png/write.py`: add `encode_rgba_png(width, height, rgba)` beside `encode_png`: the same
  deterministic framing (colour type 6, bit depth 8, every row filter type 0, one IDAT at zlib
  level 9, so identical pixels produce identical bytes) but taking packed RGBA, rejecting anything
  that is not `bytes`/`bytearray` of exactly `width * height * 4` and reusing
  `_validate_dimension` for the bounds. `encode_png`'s behaviour stays byte-identical. Re-export it
  from `tools/png/__init__.py`.
- `tools/png/read.py`: add `decode_rgba(data, max_rows=None)` reusing the existing pipeline but
  keeping alpha: it returns `(width, height, rgba)` with four samples per pixel, alpha 255 where
  the source colour type has no alpha channel (types 0, 2, 3, 4, 6 — the set `_CHANNELS` already
  accepts). It does not touch `Image` or `decode_png`.
- `tools/png/loader.py`: add `read_rgba(path)` that runs `_read_png_data`'s existing file guards
  (non-blocking open, non-regular refusal, `_MAX_FILE_BYTES`, the LFS-pointer diagnostic) and hands
  the bytes to `decode_rgba`.
- `tools/xcursor.py` (new): the Xcursor binary writer, standard library only. Module constants for
  the magic (`b"Xcur"`, 0x58637273), file version 65536, TOC entry types image (0xfffd0002) and
  comment (0xfffe0001, supported on the write side even though the generator writes none), the
  36-byte image chunk header, and `write_cursor(images)` where each image carries `(nominal_size,
  width, height, hotspot_x, hotspot_y, png_bytes)`: the 16-byte file header, one TOC entry per
  image, then each chunk at its declared offset.
- `tools/make_cursors.py` (new): follow `tools/make_wallpaper.py`'s direct-or-package import block,
  `require_within_repo` containment guard and `report_error` diagnostics. It holds the 16x16 arrow
  pixel grid as ASCII rows (`#` black face, `.` white outline, space transparent) with the tip at
  (1,1), scales it nearest-neighbour to 16, 24 and 32 (hotspot scaled by the same mapping), encodes
  each frame with `encode_rgba_png`, writes `left_ptr` with `write_cursor` and the three aliases as
  byte-identical copies, into the repository's `theme/cursors/org.macos8.desktop/cursors/`. The
  output is deterministic, so re-running it rewrites identical bytes; it refuses an output directory
  that resolves outside the repository, naming the path.
- Committed artifacts: the four generated files under
  `theme/cursors/org.macos8.desktop/cursors/` (small binaries, regular git blobs, no LFS filter).
- `tests/test_png_rgba.py` (new, modelled on the existing codec tests): `encode_rgba_png`
  round-trips through `read_rgba` byte for byte at every alpha value 0..255 in a small image; the
  encoded IHDR declares colour type 6; a rejected byte count and a rejected dimension raise
  `ValueError` naming the argument; a 3-byte-per-pixel buffer is refused; and `encode_png`'s output
  for a sample RGB image is byte-identical before and after this change (pinned against a literal
  recorded in the test, so the RGBA work cannot disturb it).
- `tests/support/xcursor.py` (new): the test-side Xcursor parser — validate the file header
  (magic, declared size, version 65536, `ntoc`), read the TOC, slice each image chunk, and return
  each image's PNG payload decoded with `read_rgba`.
- `tests/test_cursors_theme.py` (new): run the generator into a temp directory (twice, asserting
  byte-identical output), parse the committed `left_ptr` with the test-side parser, and pin: exactly
  one image chunk per nominal size in {16, 24, 32}; each chunk's PNG payload decodes with RGBA and
  its width/height equal its nominal size; the 16px frame's hotspot is (1,1) and its tip pixel
  (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and (15,15) transparent
  (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are byte-identical to
  `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the hotspot fails the
  matching assertion.
- `docs/invariants.md`: add a `## cursors` section with one row — the arrow draws the black face
  and white outline at nominal sizes 16/24/32 with the hotspot at the tip — pinned to
  `tests/test_cursors_theme.py`, carrying the provenance exception above.

**Files touched.** `tools/png/write.py`, `tools/png/read.py`, `tools/png/loader.py`,
`tools/png/__init__.py`, `tools/xcursor.py` (new), `tools/make_cursors.py` (new),
`theme/cursors/org.macos8.desktop/cursors/` (four new generated files), `tests/test_png_rgba.py`
(new), `tests/support/xcursor.py` (new), `tests/test_cursors_theme.py` (new),
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record).
`Makefile`, `README.md` and `.gitattributes` are untouched.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/cursors/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- `encode_rgba_png` followed by `read_rgba` returns the original RGBA bytes; the encoded colour
  type is 6; an off-size buffer or a bad dimension raises with a diagnostic naming it; `encode_png`'s
  pinned sample output is byte-identical to before this change.
- The test-side parser accepts the committed `left_ptr` (magic, version 65536, three image chunks)
  and rejects a truncated or hand-corrupted copy; the pinned pixels and hotspots above hold for all
  three nominal sizes (scaled accordingly); the aliases are byte-identical to `left_ptr`.
- `make check` is green with the new modules included; `git diff --name-status` names only the files
  listed under "Files touched" (besides the backlog move) and neither the `Makefile` nor
  `PLANS-DONE.md`.
- When the work lands, `grep -n '^### Platinum cursor theme, part 1/2: Generate and ship the Xcursor
  arrow cursor artifact' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's, and `grep -F 'Generate and ship the Xcursor arrow cursor artifact'
  PLANS-DONE.md` exits 1 with no output.

## Done
