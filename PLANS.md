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
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style art (a black-face, white-outline arrow not
traced from Apple's artwork) with its provenance exception recorded in its entry and
`docs/invariants.md`; **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them); and a **lock screen** is out of scope
unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered 2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both now have plan entries in the queue.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed; part 3/4 is queued as three entries — the opt-in install (parts 1/3 and 2/3) and,
blocked on them, the selection (part 3/3) — and part 4/4 (Firefox `userChrome.css` plus profile
preference) is not planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed but not yet selected); part 2/3 (a
Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) is queued as one entry,
the Lato body face only, because Lato is the only family the package installs. Until part
3/3 lands, KDE, Plasma and Qt applications keep the user's own font; GTK and Firefox
applications keep their own chrome regardless (the queued GTK entries cover GTK, and
Firefox is GTK series part 4/4, not planned).

### GTK opt-in, part 3/3: Select the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-21 by the plan role; rewritten 2026-10-23 by the plan role; parts 1/3 and 2/3 landed)

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
3/3: Select the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one line
whose number is greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select the
installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of
`git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 3/4 installs the GTK 3 and GTK 4 sheets under
`$XDG_DATA_HOME/themes/org.macos8.desktop`, but nothing selects them, so GTK applications still
draw their system theme. Add `make apply-gtk` and `make remove-gtk` plus `tools/apply_gtk.py`:
set `gtk-theme-name=org.macos8.desktop` in both GTK settings files and give libadwaita
applications the GTK 4 sheet as user CSS. Parts 1/3 and 2/3 landed the opt-in install family and
the installed file layout; this entry does not reimplement them. It does not add Firefox chrome, which remains
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
  `XDG_CONFIG_HOME` each fall back to `$HOME/.config`; and the diagnostic pins
  `test_missing_data_home_names_xdg_data_home` and
  `test_missing_config_home_names_xdg_config_home` each call `main` with the variable unset or
  relative and `HOME` unusable, then, after `assert_failed` from `support.process_assertions`,
  assert `result.stderr` contains `XDG_DATA_HOME` or `XDG_CONFIG_HOME` respectively -- a bare
  exit-code assertion does not pin the diagnostic. Add `TestMakeApplyGtk` mirroring
  `tests/test_apply_theme.py`'s `TestMakeApply`, with all five pins as named methods, each also
  asserting its exact diagnostic or output substring, never the return code alone:
  `test_dry_run_shows_install_before_the_script` (`run_make(["-n", "apply-gtk"], ...)`) asserts
  `assert_succeeded`, that `result.stdout` contains both `INSTALL_PACKAGES=gtk` and
  `tools/apply_gtk.py`, and that `result.stdout.index("INSTALL_PACKAGES=gtk")` is less than
  `result.stdout.index("tools/apply_gtk.py")`; `test_non_empty_destdir_is_refused` runs
  `run_make(["apply-gtk", "DESTDIR=<temp dir>"], ...)`, asserts `assert_failed`, that
  `result.stderr` contains `DESTDIR must be empty`, and that neither stream names
  `apply_gtk.py`; `test_python_version_is_refused` follows `tests/test_make_check.py`'s
  `TestPythonVersion` (a fake interpreter script written to a temp dir, made executable, passed
  as `PYTHON=<fake>`, that exits non-zero for every invocation) and asserts `result.stderr`
  contains `Python 3.10 or newer` and the fake path; `test_dry_run_shows_remove_script`
  (`run_make(["-n", "remove-gtk"], ...)`) asserts `assert_succeeded` and that `result.stdout`
  contains `tools/apply_gtk.py --remove`; and `test_help_lists_both_targets`
  (`run_make(["help"], ...)`) asserts `assert_succeeded` and that a `result.stdout` line starts
  with ``  apply-gtk `` and a line starts with ``  remove-gtk ``.
  Every refusal assertion on an exit status states its diagnostic substring in the same method:
  `test_missing_sheet_names_make_install_gtk` asserts `result.stderr` contains both
  `make install-gtk` and `gtk-4.0/gtk.css`, and the foreign-`gtk.css` pin asserts the stdout
  note names `gtk.css`. A method that asserts only a return code does not implement its pin.
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
  gtk-4.0/gtk.css>");`; the same command fails and its stderr names `make install-gtk` and
  `gtk-4.0/gtk.css` when the installed sheet is absent.
- `make remove-gtk` removes only our `gtk-theme-name` line and marker `gtk.css`; a foreign value
  in `gtk-3.0/settings.ini` and a foreign `gtk-4.0/gtk.css` survive byte for byte.
- `make check CHECK_TESTS='test_gtk_apply test_make_help'` passes; corrupting the settings edit,
  the marker check or a home helper makes the matching test fail; `tests/invariants.py` accepts
  the new row and `make check` is green.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestHomeResolution`; making either helper skip
  the `HOME` fallback, accept a relative value, or return a path when both candidates are
  unusable makes a case fail.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestMakeApplyGtk`; dropping any of its five
  named pins, or asserting a refusal pin only by return code while its named diagnostic
  substring (`DESTDIR must be empty`, `Python 3.10 or newer`, `tools/apply_gtk.py --remove`)
  goes unasserted, does not implement the pin above: mutating the matched message string in
  `tools/apply_gtk.py` or the Makefile recipes -- dropping `make install-gtk` from the
  missing-sheet error, `XDG_DATA_HOME`/`XDG_CONFIG_HOME` from a home refusal, or renaming an
  `apply-gtk`/`remove-gtk` help line -- makes the matching assertion fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 3/3: Select the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Select the installed GTK 3 and GTK 4 Platinum themes' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Select the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the GTK selection tool and Makefile targets,
  and its `RISK` names the GTK settings files and libadwaita user CSS; a report that calls the
  change only backlog bookkeeping contradicts the diff.

### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png (planned 2026-10-23 by the plan role; split from the too-large "Generate and ship the Xcursor arrow cursor artifact" entry)

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md` must print exactly one line, whose
whose number is greater than the `## Done` line's. The final report quotes the actual output of
`grep -l "RGBA PNG encode, decode and read in tools/png" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** The cursor series needs PNG frames that keep alpha: part 2/3 ("requires part 1/3 landed")
decodes Xcursor image chunks that embed RGBA PNG, and part 3/3 generates them.
`tools/png` today only round-trips opaque pixels (`encode_png`, `decode_png`, `read_png`;
`tools/png/read.py` reduces everything through `_to_rgb`). Add `encode_rgba_png`, `decode_rgba` and
`read_rgba` beside the existing pipeline, in the same one-responsibility style, leaving every
existing function byte-identical and every existing caller untouched. Nothing in the repository
consumes the new names yet — that is deliberate ground-laying, not a finished feature, and the
later parts' headings name them. This part is independent of (and runs alongside) the queued GTK
opt-in parts 1/3–3/3.

**Reference grounding.** Codec plumbing carries no visual value and samples no pixel; the pixels
the later cursor parts pin come from part 3/3's own grid and carry its provenance exception. No
new KDE-required value appears in this part.

**Approach.**
- `tools/png/write.py`: add `encode_rgba_png(width, height, rgba)` beside `encode_png`: the same
  deterministic framing (colour type 6, bit depth 8, every row filter type 0, one IDAT at zlib
  level 9, so identical pixels produce identical bytes) but taking packed RGBA, rejecting anything
  that is not `bytes`/`bytearray` of exactly `width * height * 4` and reusing
  `_validate_dimension` for the bounds, each diagnostic naming the offending argument.
  `encode_png`'s behaviour and output stay byte-identical; nothing else in the module changes.
- `tools/png/read.py`: add `decode_rgba(data, max_rows=None)` that reuses the existing pipeline
  (`_CHANNELS`, `_validate_max_rows`, `_parse_ihdr`, `_check_pixel_limit`, `_collect_chunks` and
  the scanline unfiltering) but keeps four samples per pixel and bypasses `_to_rgb`'s palette
  reduction: it returns `(width, height, rgba)`, and its alpha is 255 wherever the source colour
  type has no alpha channel (every type in `_CHANNELS` — 0, 2, 3, 4 and 6). It touches neither
  `Image` nor `decode_png`.
- `tools/png/loader.py`: add `read_rgba(path)` that runs the existing `_read_png_data` file guards
  (non-blocking open, non-regular refusal, `_MAX_FILE_BYTES`, the LFS-pointer diagnostic) and hands
  the bytes to `decode_rgba`. `read_png` and `read_png_size` are untouched.
- `tools/png/__init__.py`: extend the module docstring's name list, the `__all__` list and the
  `from .…` imports with the three new public names, in the established order.
- `tests/test_png_rgba.py` (new, modelled on the codec tests): `encode_rgba_png` round-trips
  through `read_rgba` and `decode_rgba` byte for byte at every alpha value 0..255 in a small image;
  the encoded IHDR declares colour type 6; two runs with the same pixels produce identical bytes;
  a too-short or too-long RGBA buffer, a rejected dimension and a 3-bytes-per-pixel buffer raise
  `ValueError` naming the argument (reuse `tests/support/rejection_assertions.py`); `decode_rgba`
  on a colour-type-2 and a colour-type-3 fixture built with `tests/support/png_fixtures.py`'s
  `make_png` (the decoder tests' own builder) returns alpha 255 everywhere; and `encode_png`'s
  output for a small sample image is recorded as a literal in the test, so the RGBA work cannot
  disturb it.
- `docs/invariants.md`: in the existing `## tooling` section add one row — the RGBA PNG codec
  round-trips alpha byte for byte and leaves `encode_png`'s output unchanged — pinned to
  `tests/test_png_rgba.py`, column 3 `none`.

**Files touched.** `tools/png/write.py`, `tools/png/read.py`, `tools/png/loader.py`,
`tools/png/__init__.py`, `tests/test_png_rgba.py` (new), `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `encode_rgba_png` followed by `read_rgba` returns the original RGBA bytes, at every alpha 0..255
  in the round-trip test; the encoded IHDR declares colour type 6; two runs with the same pixels
  produce identical bytes; an off-size buffer, a bad dimension or a 3-bytes-per-pixel buffer raises
  `ValueError` naming its argument; a colour-type-2 and a colour-type-3 PNG decode with alpha 255
  everywhere; `encode_png`'s pinned sample output is byte-identical to before this change, and no
  existing test changes its expectations.
- `make check` is green with the new module included; corrupting any of the pins above (encoding a
  wrong alpha row, dropping a guard, changing the framing) fails the matching test,
  `tests/invariants.py` accepts the new row, and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and neither `PLANS-DONE.md` nor any `theme/` path.
- When the work lands, `grep -n '^### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md`
  prints exactly one line whose number is greater than the `## Done` line's, and
  `grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png'
  PLANS-DONE.md` exits 1 with no output.

### Platinum cursor theme, part 2/3: Xcursor binary writer and test-side parser (planned 2026-10-23 by the plan role; "requires part 1/3 landed")

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -F 'Xcursor binary writer and test-side parser' PLANS.md` must print exactly one line, whose
number is greater than the `## Done` line's. The final report quotes the actual output of
`grep -l "Xcursor binary writer and test-side parser" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`)
and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 (the cursor series' part 1/3, not the GTK opt-in entry of the same number) added
the RGBA PNG codec. This part adds the Xcursor binary container the cursor artifact needs, as a
standard-library writer and an independent test-side parser that cross-checks it, and nothing else:
no generator, no committed files, no Makefile, no README, no selection. The generator, the
committed artifact and the registration are part 3/3 ("requires part 2/3 landed").

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a pointer, so no reference
pixel is sampled here; the Xcursor binary format — the magic (`b"Xcur"`, 0x58637273), file version
65536, TOC entry types image (0xfffd0002) and comment (0xfffe0001) and the 36-byte image chunk
header — is an X/KDE-required container the reference set does not show, provenance first recorded
here and carried into the `## cursors` section part 3/3 adds.

**Approach.**
- `tools/xcursor.py` (new): the Xcursor binary writer, standard library only. Module constants for
  the magic, the version, the two TOC entry types, the image chunk header length and the fixed
  sizes of the file header and TOC entry; `write_cursor(images)` taking one record per frame of
  `(nominal_size, width, height, hotspot_x, hotspot_y, png_bytes)`: validate every numeric field
  and reject anything that would overflow or misalign a chunk with a `ValueError` naming it; write
  the 16-byte file header, one 12-byte TOC entry per image, then each image chunk at its declared
  offset, so re-running with the same records produces byte-identical output.
- `tests/support/xcursor.py` (new): the test-side parser, deliberately independent of the writer —
  validate the file header (magic, declared size, version 65536, `ntoc` matching the TOC read),
  read the TOC (an unknown entry type is tolerated, the supported names are the two constants),
  slice each image chunk at its declared offset, and return each image's record with its PNG
  payload decoded through `read_rgba` (part 1/3).
- `tests/test_xcursor.py` (new): round-trip synthetic frames at 1x1, 2x2, 3x3 and 4x4 with hotspots
  at their tips: `write_cursor` → `tests/support/xcursor.py` → per-frame `encode_rgba_png`
  payloads compared byte for byte and every numeric field re-checked; two runs with the same
  records produce identical bytes; a comment-type record (the writer-side constant) is written and
  tolerated by the parser; truncated files, a corrupted TOC count, an out-of-range hotspot and a
  size-0 dimension are rejected, naming the argument (reuse
  `tests/support/rejection_assertions.py`).
- `docs/invariants.md`: nothing yet — the `## cursors` section belongs to part 3/3, which pins the
  shipped artifact; this part's guarantees are carried by `tests/test_xcursor.py` alone.

**Files touched.** `tools/xcursor.py` (new), `tests/support/xcursor.py` (new),
`tests/test_xcursor.py` (new), and `PLANS.md` (the entry moves to `## Done`; see Plan record).
Do not edit `PLANS-DONE.md`; touch no `theme/` path, no README and no `docs/invariants.md`.

**Acceptance criteria.**
- The round-trip test shows `write_cursor` → parser → `read_rgba` agreeing byte for byte on every
  payload and every numeric field at all four synthetic sizes; two runs with the same records
  produce byte-identical output; the malformed inputs above are rejected with diagnostics naming
  the argument; the parser's header checks (magic, version 65536, `ntoc`) reject a hand-corrupted
  copy at each of those fields.
- `make check` is green with the new modules included; removing a guard, offsetting a chunk or
  changing a constant makes the matching test fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and neither `PLANS-DONE.md` nor any `theme/` path.
- When the work lands, `grep -n '^### Xcursor binary writer and test-side parser' PLANS.md` prints
  exactly one line whose number is greater than the `## Done` line's, and
  `grep -F 'Xcursor binary writer and test-side parser' PLANS-DONE.md` exits 1 with no output.

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; "requires part 2/3 landed")

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -n '^### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor
artifact' PLANS.md` must print exactly one line whose number is greater than the `## Done` line's.
The final report quotes the actual output of `grep -l "Generate and ship the Xcursor arrow cursor
artifact" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`; never claim
a file the diff does not name.

**Goal.** The theme ships eight artifacts but no cursor, so a themed Plasma session still shows the
Breeze arrow. Mac OS 8.6 draws a black arrow with a white outline; this part builds that cursor as
a KDE/Xcursor theme artifact — `theme/icons/org.macos8.desktop/cursors/{left_ptr,arrow,default,top_left_arrow}`
(the last three byte-identical X-name copies of `left_ptr`, images at nominal sizes 16, 24 and 32
in one Xcursor file) — with a deterministic generator, and ships it inside the
`org.macos8.desktop` icon theme package, whose `make install` family already installs that whole
tree (so install and uninstall need no Makefile change) and whose directory is one of the paths the
XDG icon-spec lookup searches for `cursors/`. It touches no install or selection path: `make
uninstall` already removes the tree with its family, and the selection (`cursorTheme` in the global
terminal's `contents/defaults`) is not planned yet and is not part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows the mouse pointer, so no
reference pixel is sampled and the arrow is our own Platinum-style art drawn from a pixel grid in
the generator, not traced from Apple's artwork (the icon theme's standing rule). Its two colours
are `#000000` face and `#FFFFFF` outline, both already pinned in the colour scheme; the nominal
sizes 16/24/32, the Xcursor binary format, the file name `left_ptr` and the X-name aliases are
X/KDE-required values the reference set does not show. Record that provenance exception in
`docs/invariants.md`. Xcursor files have no image extension, so Git LFS (`.gitattributes`) is
untouched. The files ride the icon theme artifact, so README's artifact count stays at eight
(status wording untouched); part 3/3 only extends their reader-facing description in the
"Installing" section.

**Approach.**
- `tools/make_cursors.py` (new): follow `tools/make_wallpaper.py`'s direct-or-package import block,
  `require_within_repo` containment guard and `report_error` diagnostics. It holds the 16x16 arrow
  pixel grid as ASCII rows (`#` black face, `.` white outline, space transparent) with the tip at
  (1,1), scales it nearest-neighbour to 16, 24 and 32 (hotspot scaled by the same mapping), encodes
  each frame with `encode_rgba_png` and assembles each file with `write_cursor`, writing `left_ptr`
  and the three aliases as byte-identical copies (not symlinks) into the repository's
  `theme/icons/org.macos8.desktop/cursors/`. The output is deterministic, so re-running it
  rewrites identical bytes; it refuses an output directory that resolves outside the repository,
  naming the path.
- Committed artifacts: the four generated files under
  `theme/icons/org.macos8.desktop/cursors/` (small binaries, regular git blobs, no LFS filter).
- `tests/test_cursors_theme.py` (new): run the generator into a temp directory twice, asserting
  byte-identical output; parse the committed `left_ptr` with `tests/support/xcursor.py` (part 2/3)
  and pin: exactly one image chunk per nominal size in {16, 24, 32}; each chunk's PNG payload
  decodes with `read_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its tracked
  set so the tree holds exactly with the four cursor files added; the SVG-level assertions
  (`test_each_icon_is_a_square_svg_of_its_declared_size`, the palette and pins and
  `test_the_geometry_registry_covers_every_shipped_icon`) take the `suffix=".svg"` filter of
  `tests/support/shipped_files.py`'s `shipped_files(root, suffix=None)` so they keep iterating only
  the icons and do not mistake a binary cursor for an icon. The placeholder register and
  `tests/support/package_metadata.py` stay untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add a `## cursors` section with one row — the arrow draws the black face
  and white outline at nominal sizes 16/24/32 with the hotspot at the tip, and the four files are
  byte-identical apart from their names — pinned to `tests/test_cursors_theme.py`, carrying the
  provenance exception above (this is the standing exception window the cursor series uses; no
  screenshot shows a pointer).

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry
moves to `## Done`; see Plan record). The `Makefile` and `.gitattributes` are untouched; do not
edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; the pinned
  pixels and hotspots hold for all three nominal sizes (scaled accordingly); the aliases are
  byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size from the
  generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin holds with the four cursor files (removing one, or
  editing the committed grid's colours, fails the matching test), and every SVG-level icon
  assertion keeps iterating only the icons because of its `suffix=".svg"` filter from
  `tests/support/shipped_files.py`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## cursors` row; `git diff --name-status` names only the files listed under "Files touched"
  (besides the backlog move) and neither the `Makefile` nor `PLANS-DONE.md`.
- When the work lands, `grep -n '^### Platinum cursor theme, part 3/3: Generate and ship the Xcursor
  arrow cursor artifact' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's, and `grep -F 'Generate and ship the Xcursor arrow cursor artifact'
  PLANS-DONE.md` exits 1 with no output.

### Retire the `no-observability` validation gap with test-side observability (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-observability` tag, 20 Fixed entries)

**Goal.** Twenty Fixed entries in BUGS-FIXED.md carry `gap: no-observability` — failures that left no trace the suite could see, so the bug could not be confirmed until instrumentation was added. Retire the tag by adding test-side observability helpers (trace capture, structured failure logging) that make such failures reproducible offline, so new bugs in those areas are confirmable without a real run.

**Cited entries.** BUGS-FIXED.md lines recording `gap: no-observability` (20 entries), including the aurorae reader FIFO, containment guard, config-reading quirks, and invariants/placeholders register rows.

**Acceptance criteria.** `make check` is green; the promoted tag's count stops growing.

## Done
