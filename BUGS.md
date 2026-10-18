# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

_None yet._

## Fixed

### `test_placeholders.py` ignores `PLACEHOLDER:` markers in the theme's `.js` and `.desktoprc` files (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `tests/test_placeholders.py` `TEXT_EXTENSIONS` listed only `.svg`, `.qml`,
`.colors`, `.theme`, `.desktop` and `.json`, but `theme/` also ships a JavaScript layout
(`theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`)
and an Aurorae decoration config (`.desktoprc`). A placeholder added in either format would not
be found by `markers()`, so the register cross-check passed with the placeholder silently
untracked — the exact "forget to replace one" failure the register exists to prevent.
**Reproduce:** a scratch theme root holding `theme/layouts/layout.js` and
`theme/aurorae/theme.desktoprc` each carrying `PLACEHOLDER: stands in`; `markers(root)` returned
`{}` before the fix. The new
`test_placeholders.TestHelpers.test_markers_finds_markers_in_every_text_format_the_theme_ships`
recorded `{} != {...}` before the fix and passes after it.
**Fix:** `.js` and `.desktoprc` joined `TEXT_EXTENSIONS`, so markers in both are read and the
register cross-check now covers every text format the shipped theme uses.
**Validation gap:** no-observability — no shipped placeholder uses those two formats, so the
omission produced no failure or diagnostic; it surfaced only by reading `TEXT_EXTENSIONS` against
the theme's file list and confirming with a scratch reproduction.

### `org.macos8.desktop` icon theme still calls its final art "placeholder icons" (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `theme/icons/org.macos8.desktop/index.theme` still read
`Comment=Mac OS 8.6 Platinum placeholder icons`. The earlier change replaced the five placeholder
SVGs with final Platinum-style art, and `PLACEHOLDERS.md` now says "There are no placeholders
left"; the README status calls it "our own Platinum-style art". KDE shows the `Comment` in System
Settings → Icons, so the shipped theme described itself as temporary stand-in art it no longer
contains.
**Reproduce:** `make check CHECK_TESTS='test_icon_theme.TestIndex.test_comment_names_the_final_platinum_art'`
recorded `'Mac OS 8.6 Platinum placeholder icons' != 'Mac OS 8.6 Platinum icon theme'` before the
fix; the test passes after it.
**Fix:** the `Comment` now reads `Mac OS 8.6 Platinum icon theme`, and the new `test_icon_theme`
case pins it so the description cannot drift from the art again.
**Validation gap:** unclear-invariant — no test pinned the theme's description, so establishing that
"placeholder" was wrong meant reconstructing the art-is-final guarantee from `PLACEHOLDERS.md` and
the README first.

### `make render` installs the theme outside its scratch data home when `DESTDIR` is on the outer make command line (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** The earlier fix dropped `DESTDIR` from the environment `tools/render_surface.py`
hands to its child processes, but a caller who runs `make DESTDIR=/stage render` sets `DESTDIR`
as a *command-line* variable, and GNU make exports command-line variables to sub-makes through
`MAKEFLAGS` (`-- DESTDIR=/stage`). The inner `make install XDG_DATA_HOME=<scratch>/data` imported
it, so the Makefile built its paths as `/stage<scratch>/data/...` and the theme landed outside the
scratch data home. The headless session then found no theme and `spectacle` captured an unthemed
window with exit status 0.
**Reproduce:** `make DESTDIR=/stage render` (a real render). Offline, the stub test
execs the real make so it imports `MAKEFLAGS`:
`tests/test_render_surface.py::TestFailurePaths::test_install_ignores_a_destdir_from_the_outer_make_command_line`
recorded `[/...stage]` before the fix and `[]` after.
**Fix:** `_render` also drops `MAKEFLAGS` from the environment it hands to the child processes, so
the child make cannot import the caller's command-line variable overrides. This also keeps the
scratch install from inheriting a jobserver it cannot use.
**Validation gap:** none — the stubbed-tool test harness reproduced it directly once its stub ran
the real make.

### README lists three tools `make render` needs, but `REQUIRED_TOOLS` has six (found by the qa role 2026-10-17) — fixed 2026-10-17 by the bugfix role

README "Installing" says `make render` "needs `kwin_wayland`, `spectacle` and `plasmawindowed` and exits 2
naming the first missing tool". `tools/render_surface.py` (`REQUIRED_TOOLS`, near line 48) also requires `dbus-run-session`
and `plasma-apply-colorscheme` (and `make`); the README does not name them.

Reproduce (from the repo root; the scratch PATH holds only python3, env, sh, make and timeout, so every
required tool is missing and the diagnostic names the first one the script checks):

    S=$(mktemp -d); mkdir $S/bin
    for t in python3 env sh make timeout; do ln -s "$(command -v $t)" $S/bin/$t; done
    PATH=$S/bin make render RENDER_OUTPUT=$S/x.png; echo rc=$?

Expected per the README: the three named tools are the whole prerequisite list.
Actual: exit 2 with `render_surface: error: required tool not found on PATH: dbus-run-session`.
A machine with the three documented tools but no `dbus-run-session` or `plasma-apply-colorscheme` is told
to install tools the docs never named. Fix: name them in the README sentence.

Fixed: README now names all five tools beyond `make`; `tests/test_readme_commands.py`
`test_readme_names_every_tool_make_render_requires` derives the list from `REQUIRED_TOOLS`.

**Validation gap:** none — the bug was confirmed by reading the README against `REQUIRED_TOOLS`, and the new test failed before the edit.

### `make install` fails with a shell syntax error when `XDG_DATA_HOME` or `DESTDIR` contains an apostrophe (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role)

**Symptom:** `make install XDG_DATA_HOME="$d/it's"` exited 2 with `Syntax error: Unterminated quoted string` (or, for the package steps, a `mv` to a mangled path), after creating the empty data home. A home directory such as `O'Brien` hits this.
**Reproduce:** `make install XDG_DATA_HOME="/var/tmp/x/it's"`; `make uninstall` was unaffected because its words are double-quoted.
**Fix:** the `staging=`/`old=` assignments in `_install` and the `install_package` macro are double-quoted like the rest of the recipes, and the package trap reads a `final` shell variable instead of embedding `$(3)/$(1)` inside its single-quoted body.
**Not covered:** a double quote, backtick or backslash in the path still breaks the recipes (every path word is double-quoted); not fixed here.
**Tests:** `TestWhitespaceInInstallPaths.test_install_and_uninstall_under_a_path_with_an_apostrophe` in `tests/test_theme_install.py`; it failed before the fix.
**Validation gap:** none — the existing install harness reproduced it once given an apostrophe path.

### `make render` runs the whole render before reporting an unwritable output, and cannot write an output path starting with `-` (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role)

**Symptom:** `tools/render_surface.py` only tried to write `OUTPUT` after the `make install` and the
headless session (up to the 90s timeout). `make render RENDER_OUTPUT=` (empty), an output that is a
directory, or one in a missing directory therefore failed with `cannot write ...` only after the
full render. `make render RENDER_OUTPUT=-x.png` passed `"-x.png"` to the tool, which argparse read
as an option and rejected with "the following arguments are required: output".
**Reproduce:** `make render RENDER_OUTPUT=` ran the render, then exited 1 with `cannot write <cwd>: [Errno 21] Is a directory`.
**Fix:** `main` checks the output path right after the tool lookup (`_output_problem`: a directory,
a missing parent directory, or an unwritable parent) and exits 2 with a `cannot write` diagnostic
before any scratch or install; the Makefile passes `--` before the output path.
**Tests:** `TestFailurePaths.test_unwritable_output_is_refused_before_installing` and
`test_make_render_passes_a_dash_leading_output_as_a_path` in `tests/test_render_surface.py`; both failed before the fix.
**Validation gap:** none — the stubbed-tool harness and `make -n` reproduced both.

### `make render` installs the theme outside its scratch data home when `DESTDIR` is set in the environment (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role)

**Symptom:** `tools/render_surface.py` runs `make install XDG_DATA_HOME=<scratch>/data` with the
caller's environment. The Makefile builds its install paths as `$(DESTDIR)$(XDG_DATA_HOME)/...`
and make imports environment variables, so an exported `DESTDIR` put the theme under
`$DESTDIR<scratch>/data`. The headless session then looked in `<scratch>/data`, found no theme,
and `spectacle` captured an unthemed window with exit status 0.
**Reproduce:** `DESTDIR=/stage make -n install XDG_DATA_HOME=/var/tmp/x` prints paths under
`/stage/var/tmp/x`; `tests/test_render_surface.py::TestFailurePaths::test_install_ignores_a_destdir_from_the_environment`
failed with the stub `make` seeing `DESTDIR` before the fix.
**Fix:** `_render` drops `DESTDIR` from the environment it hands to the child processes, as it
already drops `WAYLAND_DISPLAY` and `DISPLAY`.
**Validation gap:** none — the stubbed-tool test harness reproduced it directly.

### Splash progress bar pins the panel face and the empty track as its track and fill colours (found by the plan role 2026-10-17; fixed 2026-10-17 by the bugfix role)

**Symptom:** `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml` draws the boot
progress bar with `trackColor: "#DDDDDD"` and a grey `fillColor: "#ADADAD"`.
`tests/test_splash_reference.py::test_progress_colours_match_reference` pins `TRACK` from
`(135,96)` and `FILL` from `(120,100)` of `macos8.6-screenshots/boot2_betawiki.png`. But sampling
the bar's rows shows `(135,96)` is the panel face above the bar (y=94..97 holds the "Starting Up"
text; x=134 reads `#DDDDDD` at y=93..96), and the bar itself is y=99..102. In that bar, the
`#ADADAD` at `(120,100)` is the *unfilled* track. The filled portion is the lavender run at
x=101..105, for example `(155,155,234)` = `#9B9BEA` at `(102,100)` and `(120,120,209)` = `#7878D1`
at `(102,101)`. So the splash shows a grey bar filling with grey, where Mac OS 8.6 fills a grey
track with lavender.

**How to reproduce:** `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 100 98
--width 10 --height 6` shows the lavender fill at x=101..105, and `python3 tools/sample.py
macos8.6-screenshots/boot2_betawiki.png 134 92 --height 13` shows `#DDDDDD` at y=93..96 above
the `#9A9A9A`/`#ADADAD`/`#B8B8B8` bar rows y=99..102.

**Suspected cause:** The splash plan took "pixels darker than `#DDDDDD`" as the progress well and
read the grey in it as the fill, without spotting the 5-column lavender fill at the bar's left end.

**Next step:** Re-pin the splash's track to `#ADADAD` at `(120,100)` and its fill to `#9B9BEA` at
`(102,100)`, update `Splash.qml` and the splash tests together, and re-check the
progress-well rectangle against rows y=99..102. The PLANS.md entry "Mac OS 8.6 Platinum progress
bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme" pins the same pixels, and
neither change depends on the other.

**Fixed:** `Splash.qml` now paints `trackColor: "#ADADAD"` (the unfilled track at `(120,100)`) and `fillColor: "#9B9BEA"` (the lavender fill at `(102,100)`). The track rectangle is `(101,99,38,4)`: `test_grid_geometry` now re-derives it from the pixels darker than `#C8C8C8` in rows y=98..104, below the "Starting Up" text, where the old rectangle `(101,94,38,9)` included that text's rows. The fill-width binding to `stage` is unchanged. The PLANS.md progress-bar widget entry pins the same pixels and is independent of this fix.

**Validation gap:** none — the existing splash tests re-sample the reference, so re-pointing them at the correct pixels failed against the old QML and passes against the new.

### Test suite fails with 43 failures and 3 errors (found 2026-10-16; fixed 2026-10-17 by the bugfix role)

**Symptom:** Running `make check` reports `Ran 712 tests in 9.646s FAILED (failures=43, errors=3)`. The failures and errors are all in `test_desktoptheme_tabbar.py`, affecting the tabbar widget's SVG assertions.

**How to reproduce:** `cd /home/zach/kde-macos8.6-theme/.tumwater/worktrees/_slot-1 && make check`.

The specific failures are:
- 43 failures in `test_tabbar_closed_edges_are_raised` (all slices and all directions) due to edge band pixel mismatches
- 3 errors in `test_tabbar_colours`, `test_tabbar_corners`, and `test_tabbar_installed` due to missing helper methods and undefined functions

**Cause and fix (2026-10-17):** The tests were half-written, and the artwork they check was
wrong too, which the fixed tests exposed. `widgets/tabbar.svg` painted a black outline on the open
inner edge of every tab, painted black over the highlight or shadow bands of the south, east and
west tabs, and drew corners that matched neither the raised nor the band-extended tables in the
tab-bar plan. `tests/test_desktoptheme_tabbar.py` was rewritten to the plan's rules: closed edges
carry the `face_edge_bands("#DDDDDD", "raised")` bands, the open edge is solid `#DDDDDD`, the two
fully raised corners are `face_corners` and each mixed corner extends the adjoining raised edge's
band; the palette check uses `assert_fill_palette` and the install check imports
`assert_files_identical` and `install`. `tabbar.svg`'s 36 slices were regenerated to match.
The regression is `test_tabbar_closed_edges_are_raised`, `test_tabbar_inner_edges_are_open` and
`test_tabbar_corners`, which failed against the old artwork.

**Validation gap:** none — the existing suite reproduced and confirmed it; the failing assertions named each wrong slice.

### Uninstalling the scheme while it is selected leaves KDE warning `Could not find color scheme "MacOS8"` (found 2026-10-09; fixed 2026-10-09)

**Symptom:** A KDE/Qt app started from a terminal prints
`Could not find color scheme "MacOS8" falling back to BreezeLight` and runs with BreezeLight
instead of the selected scheme. The user hit it in an unrelated terminal session.

**How to reproduce:** `make install`; select the scheme directly with
`plasma-apply-colorscheme MacOS8` (or apply the global theme), which writes
`[General] ColorScheme=MacOS8` to the user's `kdeglobals`; `make uninstall`; then start a KDE app —
it warns and falls back. Observed on this machine: `~/.config/kdeglobals` `[General]` has
`ColorScheme=MacOS8` while `~/.local/share/color-schemes/` is empty and `/usr/share/color-schemes/`
has no `MacOS8.colors`.

**Suspected cause:** `make uninstall` removes the installed `MacOS8.colors` (and the packages) but
leaves the `[General] ColorScheme=MacOS8` selection in the user's `kdeglobals`. KDE resolves the
stored id to `<id>.colors`, finds no file, and falls back to BreezeLight on each start without
rewriting the stale key; `uninstall` is documented to remove only the artifacts `install` copied,
so it never touches the user's config.

**Next step:** Decide the lifecycle fix. Options: (a) have `make uninstall` read
`$XDG_CONFIG_HOME/kdeglobals` (default `$HOME/.config/kdeglobals`) and, when `[General]
ColorScheme=MacOS8` still selects the removed scheme, print a clear warning naming the reset
command (`plasma-apply-colorscheme BreezeLight`), without editing the file; (b) document the
dangling-selection hazard in README.md's Installing section; (c) reset the key automatically
(touches user config — riskiest). Recommend (a) plus (b). Add a test: the existing
`TestRestartRoundTrip.test_applied_id_survives_restart` in `tests/test_colorscheme_install.py`
covers only the installed case, not the post-uninstall dangling one; a new case can drive
`make uninstall` against a throwaway `XDG_CONFIG_HOME` whose `kdeglobals` selects `MacOS8` and
assert the warning is printed.

**Fix:** Adopted (a) plus (b). `_uninstall` now reads `$XDG_CONFIG_HOME/kdeglobals` (default
`$HOME/.config/kdeglobals`, ignoring an empty or relative `XDG_CONFIG_HOME`) and, when its
`[General] ColorScheme` still names the removed scheme id, prints a warning naming
`plasma-apply-colorscheme BreezeLight`; it never edits the config. README's Installing section
documents the dangling selection. Two cases in `tests/test_colorscheme_install.py` drive
`make uninstall` with a throwaway `XDG_CONFIG_HOME` and assert the warning appears for
`ColorScheme=MacOS8` (leaving the file unchanged) and stays quiet for another selection.

**Validation gap:** real-run-needed — the KDE-side fallback (`Could not find color scheme`) needs a
real KDE app start to observe, so the regression test pins our warning rather than KDE's.

### Palette anchors are not re-derivable from the reference screenshots (structural risk, found 2026-10-07; fixed 2026-10-08)

**Symptom:** `tests/test_colorscheme_reference.py`'s `TestReferenceAnchors` ties the menu-bar face
(`Window`/`Button`/`Header`), view background and chrome foreground to pixels of
`desktop_archiveorg8.6hd.png`, and the selection background to a pixel of `firstboot_betawiki.png`,
but the tooltip anchor (`255,255,204`) had no reference pixel: in `macos8.6-screenshots/` that
colour occurs only as anti-aliasing fragments — diagonal edges and a few small glyph-like clusters
— never as a balloon, so there was no pixel to re-derive it from.

**How to reproduce:** Decode every PNG in `macos8.6-screenshots/` with `tools/png.py` and search
for `255,255,204`. The largest connected region is a 185-pixel diagonal edge at (966–984, 289–311)
in `desktop_betawiki.png` and `firstboot_betawiki.png`, plus small glyph clusters near (388–397,
77–88) in `firstboot_betawiki.png` — no balloon. Decoding the JPEGs (via a converter, since
`tools/png.py` cannot read them) and searching likewise finds no pale-yellow balloon.

**Suspected cause:** The palette was sampled by hand with ImageMagick while planning; the tooltip
token has no recorded sample point, and none of the collected reference screenshots happens to show
a tooltip.

**Resolution (2026-10-08).** No retail Mac OS 8.6 tooltip/balloon screenshot could be sourced
(BetaWiki's archived Mac OS 8.6 page holds only the already-collected images; the archive.org item
behind `desktop_archiveorg8.6hd.png` holds a single screenshot). The scheme header had claimed
every palette anchor was sampled, which was false for the tooltip. Following the recommendation in
QUESTIONS.md, that claim was dropped: `[Colors:Tooltip]` is now documented in
`theme/color-schemes/MacOS8.colors` and `tests/test_colorscheme.py` as a KDE-required semantic role
whose value comes from the classic Platinum palette, with no Mac OS 8.6 reference in the set; the
color-scheme implementation note in `PLANS.md` records the same, and `TestProvenanceNote` pins the
header's exception. The value stays pinned in `TestAnchors`; it is just no longer presented as
reference-derived.

**Validation gap:** no-observability — the ungrounded tooltip anchor passed the suite's
hard-coded assertion, so the gap surfaced only by decoding the reference set by hand.

### Selection palette anchor is not re-derivable (found 2026-10-07; fixed 2026-10-08)

**Symptom:** `TestAnchors` pinned the selection anchor (`206,206,255`) to a hard-coded string and
no test read a reference pixel for it, so a wrong value passed unnoticed. The value had been
sampled from `opendialog_macrumors86.jpg`, a lossy JPEG the repository cannot decode.

**How to reproduce:** Point `TestReferenceAnchors` at the Setup Assistant list selection in the
retail `firstboot_betawiki.png` (its fill at `(200, 63)`). With the scheme at `206,206,255` the
test fails: `(204, 204, 255) != (206, 206, 255)`.

**Suspected cause:** JPEG chroma loss shifted the hand-sampled value; the lossless retail PNGs
(`firstboot_betawiki.png`, `setup_betawiki.png`) show the selection fill as `204,204,255`.

**Fix:** Corrected `[Colors:Selection] BackgroundNormal`/`BackgroundAlternate` to `204,204,255` in
`theme/color-schemes/MacOS8.colors`, updated `TestAnchors`, and added
`TestReferenceAnchors.test_selection_background`, which decodes `firstboot_betawiki.png` with
`tools/png.py` and asserts the selection fill at `(200, 63)`. The tooltip token is not a sampled
anchor (see the Fixed palette-anchor entry above).

**Validation gap:** unclear-invariant — confirming the bug meant deciding which reference was
authoritative, because the lossless retail PNG (`204,204,255`) disagreed with the value hand-sampled
from the lossy JPEG (`206,206,255`).

### `--tolerance` does not gate the fidelity exit status; README documents no pass threshold (found 2026-10-07; fixed 2026-10-07)

**Symptom:** README's "Fidelity checking" section says the tool exits non-zero "when the result is
outside the requested tolerance" and documents only `--crop`. Requesting a tolerance with
`--tolerance N` on a candidate whose worst channel delta is exactly `N` still exits 1 (FAIL),
because the verdict also requires `mae <= --max-mae` and `frac_differing <= --max-frac`, both
defaulting to 0 and neither mentioned in the README. The tool's own `--help` epilog ("0 within
tolerance") has the same contradiction, so a first-time user cannot make a within-tolerance
comparison pass from the documentation alone.

**How to reproduce:**

```
cd <repo>
python3 - <<'PY'
import sys; sys.path[:0] = ['.', 'tests']
from support.png_fixtures import make_png, rgb_image
ref, ref_png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
open('/tmp/ref.png', 'wb').write(ref_png)
c = bytearray(ref.rgb); c[4] = 50  # pixel (1,0) green: 0 -> 50
open('/tmp/cand.png', 'wb').write(make_png(3, 3, [bytes(c[i:i+9]) for i in range(0, 27, 9)]))
PY
python3 tools/fidelity.py /tmp/cand.png /tmp/ref.png --tolerance 50
```

Expected: exit 0 (PASS) — the worst channel delta, 50, is within the requested `--tolerance 50`
and the tool reports `differing pixels: 0 / 9`. Actual: exit 1 (FAIL), printing
`FAIL: max-mae=0.0000 max-frac=0.000000 tolerance=50`.

**Suspected cause:** `main` computes `ok = metrics.mae <= args.max_mae and
metrics.frac_differing <= args.max_frac`; `--tolerance` only feeds `compare(tolerance=...)`, which
affects the differing-pixel count, not `mae`. The README and the help epilog present `--tolerance`
as the pass/fail knob when it is not.

**Fix:** `--max-mae` and `--max-frac` now default to unset (`None`) instead of 0, and the verdict
is the conjunction of the budgets the caller actually set; with neither set it falls back to the
strictest gate, no pixel differing by more than `--tolerance` (so the default stays byte-exact, and
`--tolerance` alone now gates as the README promised). The verdict line prints `unset` for an
unset budget, and the README's Fidelity section and the `--help` epilog document the rule.
`tests/test_fidelity_cli.py` adds `TestCli.test_tolerance_is_the_default_gate` (a candidate whose worst
delta equals `--tolerance` passes and one above it fails) and
`TestCli.test_explicit_budget_replaces_default_gate` (`--max-mae` alone is the criterion); both
fail before the change and pass after. A coverage pass (2026-10-08) added
`TestCli.test_max_frac_budget_is_the_verdict` (`--max-frac` alone is the criterion; its generous
case fails before the fix) and `TestCli.test_both_budgets_must_be_met` (with both budgets set,
either unmet budget fails the run, pinning the conjunction rather than `any()`).

**Validation gap:** none — the existing suite had no case for it, but a deterministic scratch repro
built from the shipped `png_fixtures` confirmed the failure offline, so nothing was missing.

### `plasma-apply-colorscheme` writes a scheme ID that does not survive a restart (found 2026-10-07; fixed 2026-10-07)

**Symptom:** `plasma-apply-colorscheme MacOS8` — the ID the tool lists for the
then-named dotted scheme file — reports success and writes `[General]
ColorScheme=MacOS8` into `kdeglobals`. On the next load KDE resolves that value to
`MacOS8.colors`, which does not exist, so the scheme silently falls back to BreezeLight. The value
that resolves to the shipped file is `MacOS8.6`.

**How to reproduce:** With `XDG_DATA_HOME` pointing at a data dir holding the scheme file under
its old dotted name, set the temp `XDG_CONFIG_HOME`'s `kdeglobals` to
`[General] ColorScheme=MacOS8` and run `plasma-apply-colorscheme` with no argument: it prints
`Could not find color scheme "MacOS8" falling back to BreezeLight`. Repeat with
`ColorScheme=MacOS8.6`: it resolves. Applying via the CLI looks correct in the running session, so
the breakage appears only at the next start.

**Suspected cause:** The tool derives a scheme's CLI id from the filename up to the first dot
(`MacOS8`), while its resolver turns the `ColorScheme` config value into `<value>.colors`. A
filename containing a dot therefore has a CLI id that no longer names the file.

**Fix:** Renamed the scheme file from its old dotted name to `MacOS8.colors` and set its `[General]
ColorScheme=MacOS8`, so the filename stem KDE lists as the CLI id equals the value it writes into
`kdeglobals` and resolves back to the file. Updated the `Makefile` install target, the install-path
assertion in `tests/test_colorscheme_install.py`, the README Installing section, and the look-and-feel
plan's `ColorScheme`. `tests/test_colorscheme.py` adds
`test_cli_id_matches_filename_and_config_value` (asserts the filename stem equals `[General]
ColorScheme` and that `<stem>.colors` exists), and `tests/test_colorscheme_install.py` adds
`TestRestartRoundTrip.test_applied_id_survives_restart` (applies the listed id in a temp
`XDG_DATA_HOME`/`XDG_CONFIG_HOME`, then runs `plasma-apply-colorscheme` with no argument and fails
if it prints `Could not find`); both fail against the dotted filename and pass after the rename.

**Validation gap:** real-run-needed — the breakage appears only on the next load, and no existing
test exercised KDE's scheme resolver, so confirming it required a bounded run of the real
`plasma-apply-colorscheme` against a temp config (now covered by the round-trip test).

### No objective fidelity check for "pixel-perfect" (structural risk, found 2026-10-07; fixed 2026-10-07)

**Symptom:** The initial prompt asks for theming "as close as possible to pixel-perfect," but the
repo could not measure a rendered surface against its Mac OS 8.6 reference image. Any loop could
claim a surface matches and no reviewer could confirm or reject the claim.

**How to reproduce:** Ask for the current fidelity of any surface (menu bar, title bar, scrollbar).
There was no render path, no capture step and no comparison, so the only possible answer was
qualitative.

**Suspected cause:** No visual-fidelity harness existed. The repo held the reference screenshots and
their provenance, but no code compared a captured surface against the retail-labelled images in
`macos8.6-screenshots/`.

**Fix:** The fidelity tooling decodes PNG candidates and references (8-bit, non-interlaced, color
types 0/2/3/4/6) with only the standard library, crops a reference to a surface region, and reports
objective metrics — mean absolute error, RMSE, worst per-channel delta, and differing-pixel
fraction — exiting non-zero when the result is outside the requested tolerance. `tools/png.py`
holds the decoder, `tools/fidelity_metrics.py` the comparison math, and `tools/fidelity.py` the CLI.
`tests/test_png_decode.py` covers decoding (palette plus every PNG filter type);
`tests/test_fidelity_metrics.py` covers the metrics and cropping, and
`tests/test_fidelity_cli.py` covers the CLI pass/fail paths. Producing the candidate PNG (the Plasma
render step) is still missing and is tracked as its own Open entry above.

**Validation gap:** unclear-invariant — "pixel-perfect" had no numeric definition and the repo had
no comparison path, so the objective metric and threshold had to be defined before the gap could be
confirmed.
