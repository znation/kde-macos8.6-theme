# Fixed bugs

Fixed bugs, newest first, moved here by tumwater from BUGS.md's `## Fixed`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Fixed

### post-merge review of 87464dad never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `87464dad9485aa5f8f9b7219ca1456b761946107`: `require_uninstall_parents` checks the fixed uninstall destinations before the removal recipe, and `TestUninstallSymlinkParents` verifies a symlinked GTK subdirectory is refused while an outside stylesheet survives. The invariant register points to that regression test.

**Validation gap:** none — the existing regression test reproduces the planted parent symlink and checks the outside file remains.

### post-merge review of 95990634 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `959906348a7fa0c016b882c80af02c7a9811d631`: the GTK 3 sheet reflects only unchecked RTL disclosure arrows with `scaleX(-1)`; the regression test asserts the exact declarations and selector uniqueness while preserving collapsed and checked arrow rules. `docs/invariants.md` records the GTK 3 adaptation and distinguishes the GTK 4 behavior.

**Validation gap:** none — the existing GTK 3 test directly checks the RTL declarations, and the current source and invariant documentation match the reviewed change.

### post-merge review of 1341c439 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `1341c4399ed2cebe5cdb940693c54b6f449aee49`: the shared fixture preserves the previous callers' directory open, exclusive non-blocking flock and cleanup behavior. All three wrappers delegate to that fixture; GTK's distinct config-lock helper remains local.

**Validation gap:** none — the existing apply-lock tests exercise each wrapper's held-lock behavior and cleanup.

### post-merge review of 9681e407 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

Reviewed commit `9681e40787d8cb3f7884d394bcd884e25d0bb2b0`. Its tests cover both installed GTK sheets and refusal when the GTK 3 sheet is missing while GTK 4 exists. The helper checks both sheets before selection and reports the missing path with the repair command; the test assertions match that behavior.

**Validation gap:** none — the review was settled by inspecting the implementation and focused tests, which directly cover the helper's contract.

### post-merge review of dad5b35f never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `dad5b35f27e37625e459ae0b0d8229642a0a4d37`: the GTK 3 stylesheet adds nine disabled self-selected backdrop link selectors with `color: #888888`; its test checks exact declaration sets and uniqueness, derives the inactive-text color from the scheme, and requires the group to follow the enabled self-selected backdrop selectors. The invariant row records the missing GTK reference surface and the installed GTK resource provenance. No defect found in the reviewed change.

**Validation gap:** none — existing declaration and source-order tests confirm the change; rendered GTK pixels remain outside those checks.

### post-merge review of 8ca180d6 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed `8ca180d6c6b838d6989cb03b1096beb2d0dbf6c1`: `_candidate` now rejects a relative `Path` when `IsRelative=0`, while preserving absolute paths and resolving `IsRelative=1` paths under the Firefox root. The regression test exercises a same-working-directory relative path and asserts the diagnostic identifies the malformed flag and path.

**Validation gap:** none — the focused regression test and existing profile-resolution coverage directly check malformed and valid path modes.

### post-merge review of 67a2c172 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `67a2c172ed567098ef0f55d981b400776431f05a` and the current `tools/generated_files.py`. The default writer delegates to `write_bytes_atomically`, and `tests/test_generated_files.py::TestGeneratedFiles::test_default_writer_creates_directory_and_publishes_bytes` exercises the no-injection path, nested directory creation, success status and published bytes. The current suite also covers containment refusal, directory creation failure and a later write failure while retaining earlier files. No defect was found in the reviewed change.

**Validation gap:** none — the committed regression test directly invokes the default writer and asserts its published result.

### post-merge review of b3f5b561 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `b3f5b5617e9abbfe29d60e391bce01c8c3b52d91`: its GTK 3 sheet adds nine disabled self-selected link state selectors with the inactive-text colour, and `TestGtkTheme.test_disabled_selected_inline_link_foregrounds` checks the generated selectors, disabled-text colour, colour-only declarations and ordering after both ordinary disabled and enabled self-selected rules. The invariant records the missing GTK reference surface and platform provenance.

**Validation gap:** none — the existing GTK stylesheet test directly checks the declarations and precedence described by the change.

### post-merge review of d1046956 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The reviewed GTK 4 stylesheet adds six disabled self-selected inline-link selectors with `color: #888888`. The current `TestGtk4Theme.test_disabled_selected_inline_link_foregrounds` derives those states, checks each declaration and uniqueness, and verifies source order after ordinary disabled and enabled self-selected rules. The GTK invariant row records the missing reference surface and derives the value from `[Colors:Button] ForegroundInactive`. The stylesheet matches these checks; no defect found.

**Validation gap:** none — the existing selector and declaration test directly covers the reviewed stylesheet behavior.

### post-merge review of a2f04528 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The post-merge review of commit `a2f045281a4a204bc4e907865ba7974436dbac01` (Share selected inline-link assertions across GTK 3 tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Reviewed the shared helper and all five call sites. Each preserves the prior declaration, selector uniqueness, color, and cascade-order assertions; no defect was found.

**Validation gap:** none — the existing GTK declaration tests exercise the refactored assertions at each call site.

### post-merge review of a7288806 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed `a728880630507ddeb44ff134ad1cf126f78126c4`: the selected-ancestor backdrop selectors cover link, visited and combined link/visited states across base, hover and active. Their declarations set only inactive text grey, and the test verifies selector uniqueness and placement after the competing rules. The invariant records the missing reference surface, palette source and limitation of declaration checks.

**Validation gap:** none — the existing GTK theme test verifies the selectors, declarations and cascade ordering; the change makes no runtime-rendering claim.

### post-merge review of 99b67519 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The review found the change consistent with its GTK 3 contract: all nine disabled selected-ancestor link selectors cover link, visited and combined visited states across base, hover and active states, exclude backdrop links, and declare only the inactive-text color. The test asserts the generated selector set, declarations, uniqueness and ordering after both ordinary disabled and enabled selected-ancestor rules. The invariant records the missing reference surface and palette source.

**Validation gap:** none — the existing GTK test checks the selector set, declarations and cascade order; the review entry tracked a missing verdict rather than a reported behavioral failure.

### post-merge review of 9a6d0021 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed the commit diff and current GTK 4 stylesheet and test. The six disabled selected-ancestor selectors assign inactive text and appear after both ordinary disabled link rules and enabled selected-ancestor rules; the regression test checks selector uniqueness, the shared disabled-text value and cascade ordering. No defect found.

**Validation gap:** none — the existing stylesheet declaration test covers each state, its exact inactive-text declaration, uniqueness and source ordering.

### post-merge review of 85d12175 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The reviewed GTK 3 backdrop selected-ancestor link group covers the nine enabled base, hover and active selectors. Its test checks exact declarations, selector uniqueness, palette-derived black and cascade order; the invariant table records the GTK resource and absent reference surface. The reviewed change adds no keyboard mapping or theme-owned branded UI.

**Validation gap:** none — the review record lacked a verdict, and inspection of the implementation, test and invariant evidence was sufficient to settle it.

### post-merge review of f506bb76 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The post-merge review of commit `f506bb76d19eceb404004ab2e54faaaf08ebb265` (Share the Firefox panel declaration assertion helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** The helper in `tests/support/firefox_chrome_cases.py` iterates the supplied selectors, compares each parsed declaration mapping with `REQUIRED_RULES`, and retains per-selector subtests. The panel call sites preserve the selector-scope assertions while using the shared equality assertion; the existing panel tests and invariant rows still point to those call sites. No behavior defect was found in this test-only refactor.

**Validation gap:** none — the review diff and current helper, call sites and invariant references directly establish that the extracted assertions preserve their prior comparisons.

### post-merge review of 34ca72c4 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Checked the commit's GTK 3 stylesheet change, selector assertions, and invariant entry. The four add-color overlay states declare `#000000`, the regression test checks each state and its equality with the sheet's `window` foreground, and the invariant records the missing reference surface and adaptation source. The current tree retains these declarations and checks.

**Validation gap:** none — the post-merge review was settled by inspecting the changed declarations, regression assertions, and invariant documentation; no behavior defect was found.

### post-merge review of acaedf4e never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

Fix: Checked the refactor against its parent: all four GTK 3 OSD cases still flatten selector groups into a set, assert the expected inventory size, and return that set for the existing scope comparison. The helper preserves that behavior, and the split OSD tests retain the same four count checks.

**Validation gap:** none — the review was hard to confirm only because it was interrupted; the helper and its four callers directly preserve the prior assertions.

### post-merge review of 2c699158 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `2c699158366a181189a5a0485597813534def357`: all four add-color overlay states declare `box-shadow: none`; `test_add_color_box_shadows` pins those states, and the existing image-reset and square-corner checks retain their declarations. The GTK invariant names the missing reference surface, toolkit resource provenance and declaration-test limitation. No defect found in the reviewed change.

**Validation gap:** none — the existing declaration checks cover the change, and source inspection confirmed the invariant and four-state selector group.

### post-merge review of 57a8984e never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed commit `57a8984e37e3074a46798216af2b0bab3caa35bf`: the base `button.color colorswatch:only-child` rule clears the decorative shadow, its exact declaration test pins the reset, the swatch corner selector inventory includes the rule, and the GTK invariant records the missing reference surface and toolkit resource provenance. The change preserves swatch color and geometry and limits its guarantee to declarations.

**Validation gap:** none — the exact declaration and selector inventory tests cover the reviewed stylesheet contract, and the invariant explicitly limits the claim to declarations rather than rendered pixels.

### post-merge review of 085434b9 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The post-merge review of commit `085434b9b0941a66380649c457baeb22eb780888` (Restate GTK 4 OSD scale thumbs with Platinum recipes) found the four OSD slider state declarations use the shared `SCALE_THUMB` paint; the disabled state matches the ordinary disabled border and flat shadow. The focused test asserts the four complete rule dictionaries and selector inventory, while `docs/invariants.md` records the missing reference surface and GTK resource provenance. The broader `make check` noted in the commit's own record passed; no discrepancy was found in the diff.

**Validation gap:** none — the selector and declaration tests cover the change, and the commit records a passing project check.

### post-merge review of 1e91fbe6 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The post-merge review of commit `1e91fbe64d2652d35818f679635dcb7672b0ae6e` (Restate GTK 4 OSD progress and scale paints) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix.** Reviewed the complete commit diff: it adds the ten GTK 4 OSD progress and scale paint arms, a matching `test_osd_progress_scale` assertion for each declaration and the selector inventory, and an invariant note describing the missing reference surface and recipe provenance. The assertions match the stylesheet declarations; the review found no defect to repair.

**Validation gap:** none — the existing GTK 4 stylesheet test pins the added declarations and selector inventory, and the diff review found them consistent.

### post-merge review of dbaee0e4 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Reviewed the complete commit diff and current stylesheet/tests. The selectors restate the GTK 3 stock rounded, borderless scale-popup rules with square borders and the existing Platinum face; the dedicated test checks declarations and selector uniqueness. The change agrees with its recorded GTK invariant and introduces no separate defect.

**Validation gap:** none — the existing selector regression test documents the declarations involved; review confirmation also included direct source comparison.

### post-merge review of d4609435 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The commit diff changes only a blank line in `tests/test_render_surface.py`; despite its subject, it does not remove a button-row assertion or alter behavior. The parent revision already contains the same assertions as the current file. The review record is settled: this commit introduces no code change to fix.

**Validation gap:** none — the committed check was reported passing, and comparing the test file with its parent confirms the whitespace-only diff leaves the assertions unchanged.

### post-merge review of 08224293 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix:** Reviewed the commit's GTK 3 OSD stepper selector arms against the toolkit claims documented in the stylesheet and confirmed the current `test_osd_spinbutton_buttons` pins all twelve expected arms and declaration sets. The vertical active arm alone inverts its bevel; disabled arms omit the outline; vertical arms clear the stock background clip. The reviewed change is consistent with its recorded invariant.

**Validation gap:** none — the existing declaration test directly pins the stepper arms and their values, so the review required no missing reproduction path.

### post-merge review of ea41dae6 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The GTK 3 sheet restates the five stock `.osd button.destructive-action` arms in their original cascade order, including `background-clip: border-box` to clear the stock padding-box clip. Its regression test pins the nine state selectors, expected declarations, and selector scope; the GTK invariant records the overlay guarantee. The inspected diff and current implementation agree.

**Validation gap:** none — the existing GTK declaration test pins each restated arm and its exact selector scope.

### post-merge review of 3471442c never reached a verdict — fixed 2026-11-11 by the bugfix role (found by the review role 2026-11-11)

**Fix.** Reviewed commit `3471442cc23eefd762177498941014b393a81e6c`: the new session tests assert the exact Kvantum config output, replacement of stale selection, agreement with the apply-side theme id, and presence of the shipped package directory. The invariants row names the same test class and contract; no defect was found in the reviewed change.

**Validation gap:** none — the commit added offline tests for the wiring it changes, and code and assertions directly establish the selected id and written config.

### post-merge review of 89db8731 never reached a verdict (found by the review role 2026-11-11) — fixed 2026-11-11 by the bugfix role

The post-merge review of commit `89db87315adf58c524e524be5c3b17d2bd014055` (Land planned GTK 3 OSD suggested-action push-button restatement) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Reviewed the commit's GTK 3 stylesheet restatements, the `test_osd_suggested_action` selector and declaration assertions, the neighboring OSD scope filter, and the invariants update. The sheet and test agree on nine selectors and explicitly clear the stock `background-clip: padding-box` claim with `border-box`; no defect was found.

**Validation gap:** none — the commit's focused assertions and the surrounding scope checks provide direct coverage of the review claims.

### A command-line HOME make function executes before the shell-syntax refusal (found by the coverage role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Fix.** Keep `HOME` out of make's child environments until the raw value passes the parse-time refusal; export the validated value afterwards. The regression test covers the command-line override alongside the existing environment-supplied case.

**Validation gap:** none — the new test reproduced command-line function evaluation and confirmed the refusal leaves its canary absent.

### The split-output command runner can leak its child if its stdin writer thread cannot start (found by the bugfix role 2026-11-11) — fixed 2026-11-11 by the bugfix role

`run_logged_split` started its stdin writer before entering the `try/finally` that kills and reaps the command. If `Thread.start()` raised, the caller saw the startup error but the child remained alive, and its stdin pipe stayed open.

Reproduce by running `run_logged_split` with `stdin_bytes` supplied while making `threading.Thread.start` raise. Before the fix, the runtime error escaped and the child process remained alive.

The writer now starts inside the child's cleanup scope; if it did not start, cleanup closes the pipe after killing and reaping the child.

**Validation gap:** none — the new regression test reproduced the live child before the fix and confirmed it was gone afterward.

### The Kvantum button-reference test still pins the `button-default-indicator` group the reviewer fix removed from the shipped SVG, and the color and icon dialog gates draw a gradient push-button face (found by the plan role 2026-11-11) — fixed 2026-11-11 by the ci role

`make check` failed in two modules. First, `tests/test_kvantum_button_reference.py::TestButtonReference::test_default_button_indicator_keeps_the_face_flat` asserts exactly one `button-default-indicator` group in the shipped `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` and got zero — commit `dfd954379` (the 2026-11-11 reviewer fix for a993c56b) deleted the whole `<g id="button-default-indicator">` block while removing a duplicate `focusRectElement` line, but that commit touched no test, so the landed assertion still counted the removed group. Second, `tests/test_render_surface.py`'s `TestColorDialogRender` and `TestIconDialogRender` failed their two push-button tests each (`test_draws_the_push_button_frame_and_cell`, `test_draws_the_push_button_face_at_the_landed_recipe`): the asserted flat `#DDDDDD` face rows and right-bevel column read a `#E4E4E4`→`#E7E7E7` gradient instead (first differing element 72 of the face row).

The fix restores the `<g id="button-default-indicator">` 7x7 flat-face block to the SVG verbatim as a993c56b landed it. The removal's premise — a duplicate `button-default-indicator` id — was already disproven by the 2026-11-11 reviewer fix `122373b7d` ("the SVG has exactly one such ID at base, HEAD, and now"), and `dfd954379`'s own item 1 says reverting the indicator art turns former ring/wedge pixels black, so the deletion was self-contradictory. Both symptoms share the one root: after the restore, the button-reference test counts the group again, and fresh full `--color-dialog` renders draw the flat `#DDDDDD` face rows again (two consecutive captures byte-identical).

**Validation gap:** none — `make check` reproduces both symptoms directly: the button-reference group count fails at zero and the two dialog gates' flat-face pins fail on the gradient, and the suite's fresh full renders reproduce the gradient face before the restore and the flat face after it.

### The file-dialog gate's header column-layout pins move with the time of day because the seeded files' mtime text drives the Date column's width (found by the feature role 2026-11-11) — fixed 2026-11-11 by the bugfix role

**Symptom.** `tests/test_render_surface.py::TestFileDialogRender` passes at some hours and fails 13 of its landed tests at others. At 13:33–13:41 on this host three consecutive full `--file-dialog` runs agreed byte-for-byte outside the caret strip, but every header column-layout pin sat 7px right of the landed constants: the Size/Date divider columns measured at x=350/351 and x=400/401 instead of the landed x=343/344 and x=393/394, the Size caption inked x=356..377 instead of x=349..371, the Date caption x=407..432 instead of x=400..425, the style-drawn sort arrow x=337..347 instead of x=329..339, and the size-text ink rectangles x=375..393 instead of the landed x=368..386. The failing tests are `test_the_column_header_band_pins_its_face_and_dividers`, `test_the_header_inks_its_captions_and_sort_arrow` and `test_the_list_rows_pin_their_band_faces` (the landed part 1/2 pins); a dry-run of the landed class against the fresh capture fails exactly those 13 (13 subtest failures across the three tests). Earlier today the same gate ran green in `make check` and in isolation, so the layout varies within a single day although the seeded directory is fixed.

**Reproduce.** Render twice at times whose mtime display draws at different widths (e.g. hours apart, or across a narrow-digit boundary in the clock) and compare the header band: `python3 tools/render_surface.py <scratch>/a.png --file-dialog` twice, byte-comparing the header rows 99..122 and the size-text columns against the landed pins. The sidebar (x=6..138) showed no such movement across the measured runs.

**Suspected cause.** The seeded files are `touch()`ed at session start (`tools/render_clients.py`), so their mtime display is the session's wall clock, and KIO sizes the details-view columns from their content: the Date column's width follows the mtime text's rendered width (the theme's Lato digits have a narrow `1`), and the stretch Name column absorbs the difference, shifting the Size/Date dividers, both captions, the sort arrow and the size-text x-positions together. `tools/render_clients.py`'s docstring claimed "the absence of clock-dependent content keep[s] every capture deterministic" — the mtime display is exactly such content.

**Fix.** `tools/render_clients.py`'s `file_dialog_client` seeding now pins both timestamps of each seeded file to a new `FILE_DIALOG_SEED_EPOCH` constant (1104537600, 2005-01-01 00:00:00 UTC) with `os.utime`, so the Date column's rendered text — and with it every header x-position the gate pins — is identical in every session whatever the wall clock says; the docstring's determinism claim now names the pinned mtimes. The landing pins stay untouched: the header band renders against a constant listing, so the existing constants hold. `tests/test_render_surface_units.py::TestSessionCommand::test_pins_the_seeded_file_dialog_files_mtime` asserts each seeded file's mtime equals 1104537600; without the fix it fails with the session's live mtime (measured 1794434520.5653315).

**Validation gap:** none — the gate's first 13-failure evidence only showed at hours whose Date column text renders wider, but the new unit pin reproduces the mechanism deterministically: without the fix it fails on the seeded files' live mtime, with it the suite confirms every capture renders against a constant listing.

### The Kvantum button-reference test still pinned the `button-default-indicator` group the reviewer fix removed from the shipped SVG, the color and icon dialog gates drew a gradient push-button face, and the file-dialog header pins drifted 7px (found by the plan role 2026-11-11) — fixed 2026-11-11 by the ci role

**Symptom.** `make check` failed in two modules. First, `tests/test_kvantum_button_reference.py::TestButtonReference::test_default_button_indicator_keeps_the_face_flat` asserted exactly one `button-default-indicator` group in the shipped `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` and got zero — commit `dfd954379` (the 2026-11-11 reviewer fix for a993c56b) deleted the whole `<g id="button-default-indicator">` block when removing the duplicate 7x7/8x8 markers, but that commit touched no test, so the landed assertion still counted the removed group; no group carried the id any more because `6b882061d` had already dropped the 8x8 art when deduplicating, so the reviewer's "the shipped indicator stays the parent's slot-measured 8x8 art" was factually wrong. Second, `tests/test_render_surface.py`'s `TestColorDialogRender` and `TestIconDialogRender` failed their two push-button tests each (`test_draws_the_push_button_frame_and_cell`, `test_draws_the_push_button_face_at_the_landed_recipe`): the asserted flat `#DDDDDD` face rows and right-bevel column read a `#E4E4E4`→`#E7E7E7` gradient wedge instead — the compiled-in default-button corner art the missing element let Kvantum paint again (a 45° diagonal wedge growing from the button's bottom-right interior corner, measured on the capture). Third, `TestFileDialogRender`'s header band, caption/sort-arrow and row-band tests failed: every pin at or right of the Name column's end (dividers, Size/Date caption bands, sort arrow, size-text rects) sat 7-8px left of the actual render, so the landed pins no longer matched any render this run could produce.

**Cause.** The first two symptoms share one root: removing the element made Kvantum fall back to its compiled-in default-button art, restoring the wedge the 2026-11-03 default-mark fix had replaced with flat face art; the render pins had been derived on 2026-11-10 when the theme still supplied the element. The file-dialog drift is a host-side rendering shift between the landing run's measurement session and this run (the Name column rendered 7px wider; no repository change moves a header column, and the detached 1d617ca82 checkout fails identically, so it predates this run's tree edits).

**Fix.** Restored `<g id="button-default-indicator">` as the 8x8 `#DDDDDD` face patch (the size the 2026-11-03 fixed entry records) at its original slot, and re-pinned `test_default_button_indicator_keeps_the_face_flat` to the 8x8 cell (64 px; a 7x7 or off-by-one pin fails it). Re-derived the drifted `TestFileDialogRender` pins (dividers x=343/344→350/351 and 393/394→400/401, Size caption band 349..371→355..379, Date caption band 400..425→406..433, sort arrow x=329→336, size-text rects and `ROW_TEXT_BANDS` 368..386→375..393) from three consecutive `--file-dialog` renders that agreed byte for byte outside the documented caret strip; an off-by-one arrow pin fails the byte-compare.

**Validation gap:** none — the color-dialog render reproduced the gradient wedge on row 344 (columns 375..380) before the restore and drew the flat face after; the file-dialog render reproduced all four drifted pins before the re-derivation and the re-pinned tests' exact assertions (face pin, arrow byte-map, row-band faces) pass against two agreeing captures.

### The file-dialog landing left the dialog-mode count prose saying thirteen modes and twelve kdialog modes after its fourteenth mode (found by the bugfix role 2026-11-11) — fixed 2026-11-11 by the bugfix role

`tools/render_dialogs.py`'s `DIALOG_MODES` table has held fourteen dialog modes (thirteen
kdialog clients and one zenity client) since the file-dialog render mode's part 1/2 plumbing
landed, but the words that count them still read the pre-landing numbers: `tests/test_render_dialogs.py`'s
module docstring says "the render CLI's thirteen dialog modes", and the per-flag client comment in
`tests/test_render_surface.py`, the workflow-install comment in `tests/test_ci_workflow.py` and the
skip-guard row in `docs/invariants.md` say "kdialog for the twelve kdialog modes". The prose reader
is told the CLI demands one fewer kdialog client than it does.

The guard `tests/test_dialog_gate_count_prose.py` could not see the drift: it derived the kdialog-mode
count from the `Test...DialogRender` gate classes (gate count minus the zenity gate), which equals
the CLI's kdialog-mode count only while every mode has its gate. The file-dialog series lands its
mode in part 1/2 and its pixel gate in part 2/2, so during that window the gate-derived number
under-counts. The guard now derives the kdialog-mode count from the live `DIALOG_MODES` table and
also pins `tests/test_render_dialogs.py`'s mode-count docstring against it; the prose words moved to
fourteen modes and thirteen kdialog modes.

**Validation gap:** no-observability — the drifted prose left no failing trace in the suite, because the count guard's kdialog-mode expectation was derived from the gate classes (twelve) and so confirmed the stale word instead of refuting it.

### An environment-supplied HOME value executes GNU make functions during Makefile parsing (found by the security role 2026-11-02) — fixed 2026-11-02 by the security role

An environment `HOME` whose value carries make syntax is expanded as make syntax when the
Makefile reads `$(HOME)` at parse time, so make functions in it run before any target, guard or
recipe — including under `make -n`, which is supposed to run nothing. Reproduce with

    env HOME='$(shell touch /tmp/canary)' make -n help

which creates `/tmp/canary` (confirmed by an adversarial reviewer on 2026-11-11 with make exit 0
and the canary file present) before `help` prints anything.

**Suspected cause:** `XDG_DATA_HOME := $(if $(filter /%,$(XDG_DATA_HOME_ENV)),$(XDG_DATA_HOME_ENV),$(HOME)/.local/share)`
expands `$(HOME)` while parsing, and GNU make expands environment-origin variables as recursive
variables, so their values are evaluated as make syntax. The `shell_unsafe_chars` guard closes
the shell-quoting route for values pasted into recipe shells; it does not see the raw value of a
variable make has already expanded — the Makefile's own comment on that guard says a value
carrying make `$( )` is expanded by make while the guard reads it, and calls that documented
behaviour outside the shell route the guard closes. The impact is parse-time command execution
from an untrusted environment value that the guards treat as a path.

**Progress 2026-11-11 by the director role:** resolved — the reviewer's 2026-11-11 confirmation
reproduces only against the pre-fix Makefile. Extracting the Makefile as of `166a85cfd^` into a
scratch directory and running the verbatim repro there gives make exit 0 with the canary file
created — exactly the recorded reviewer observation — while the same repro against the fixed
Makefile refuses at parse with exit 2, the Makefile:142 metacharacter diagnostic (echoing the
raw `$(value)` text) and no canary. Commit 166a85cfd (2026-11-02, the security role) captured
`HOME_ENV := $(value HOME)`, rewrote the parse-time fallback to use it, switched
`shell_unsafe_in`/`control_char_in` to raw-value reads, and put `HOME` in the parse-time
refusal list, so make-function text in `HOME` is refused before any recipe, under `make -n`
too; the reviewer repair 1db265ac1 (2026-11-11) closed the diagnostic-echo route for `PYTHON`
and `INSTALL_PACKAGES`. The reviewer's reproduction verified the historical vulnerability was
real, but the fix had already landed before the entry was recorded;
`tests/test_make_refusals.py::TestShellUnsafeInstallPaths::test_make_function_text_in_HOME_is_refused_without_evaluation`
(landed with 166a85cfd) pins the refusal.

**Validation gap:** no-repro — the entry's confirming evidence was gathered against the
pre-166a85cfd Makefile, so the bug no longer reproduced on the tree the entry was recorded
against, and only the historical state reproduced it.

### The hosted CI image lacks ImageMagick's `convert` for JPEG sampler tests (found by the ci role 2026-11-10) — fixed 2026-11-11 by the bugfix role

The newest pushed CI run fails `tests/test_sample_jpeg.py` because its runner cannot find the
external `convert` executable. The test assertion reports:

```text
AssertionError: 2 != 0 : sample: error: cannot decode /tmp/tmpajeftfg7/quilt.jpg: the input is a JPEG image, and decoding it needs ImageMagick's convert, which is not installed
```

The hosted run is https://github.com/znation/kde-macos8.6-theme/actions/runs/42982951246. The
same workflow step passes in this worktree, where `/usr/bin/convert` is installed. The workflow's
render-tool install step does not install ImageMagick, so the hosted dependency gap is not
reproducible as a source or test failure here.

**Progress 2026-11-11 by the director role:** Reproduced the missing-tool failure
without uninstalling host packages: create `repro_dir=$(mktemp -d)`, then run
`env PATH="$repro_dir" /usr/bin/python3 -m unittest discover -s tests -p test_sample_jpeg.py`.
The run exits 1; `TestJpegSampler.test_script_entry_point` reports the same
`AssertionError: 2 != 0` and missing-ImageMagick diagnostic quoted above.
`tools/jpeg_convert.py::convert_jpeg` resolves `convert` with `shutil.which`
and returns that diagnostic when it is absent. `TestJpegSampler` requires real
JPEG conversion; its success cases have no capability skip. The workflow
`.github/workflows/ci.yml` neither installs ImageMagick nor includes `convert`
in its initial capability guard or final executable verification. The local
installed executable therefore masks a reproducible dependency gap, not a reason
to park this report. Route the fix to CI dependency provisioning: ensure a
package providing the literal `convert` command is installed before `make check`,
including when the Plasma tools are already present; verify the executable and
add a workflow regression test for that provisioning path. Keep the JPEG
success tests exercising the real decoder. Leave this entry open for the bugfix role.

**Docker follow-up 2026-11-11 by the director role:** The user installed Docker
and requested a container reproduction. `docker version` finds client 26.1.5,
but daemon access fails with permission denied on `/var/run/docker.sock`.
The socket is owned by `root:docker` with mode `0660`; this role process's
`id` output does not include the docker group. `sudo -n docker version` fails
with `sudo: a password is required`. No container reproduction ran. Once the
role process has daemon access, use a disposable container with the worktree
mounted read-only and Python available but no `convert`, and run
`python3 -m unittest discover -s tests -p test_sample_jpeg.py` from that mount.
Record the image and observed failure; this supplements the confirmed
empty-PATH reproduction above. Keep the CI provisioning fix assigned to the
bugfix role; Docker access does not change its scope.

**Fix 2026-11-11 by the bugfix role:** `.github/workflows/ci.yml` now installs the
`imagemagick` package when `convert` is absent, after the Plasma render-tool step so it
runs on both the already-installed and fresh-install paths, and then verifies the literal
`convert` executable. `tests/test_ci_workflow.py::test_workflow_provisions_and_verifies_imagemagick_convert`
failed on the unfixed workflow and passes with it. The hosted run has not been observed yet;
the `imagemagick` package's provision of `convert` on the hosted image is confirmed only by that
step's own verification when the next hosted run reaches it.

**Validation gap:** real-run-needed — the local host's installed `convert` masked the missing executable, so only the hosted run showed it; the offline bound (the workflow must provision and verify `convert`) is pinned by the workflow test, and the empty-PATH run of `test_sample_jpeg.py` was the local reproduction.

**Docker reproduction 2026-11-11 by the director role:** The daemon access that
blocked the follow-up above is now available; this role process's `id` includes
the docker group and `docker version` reaches the server. In a disposable
`python:3.12-slim` container (Python 3.12.16, no `convert`), with this worktree
mounted read-only at `/worktree:ro`, `python3 -m unittest discover -s tests -p
test_sample_jpeg.py` failed 6 of its 19 tests, and all 6 failure messages carry
the missing-`convert` diagnostic quoted above (13 pass). The same image with the
`imagemagick` package installed passes all 19. This confirms in a clean
environment both the hosted dependency gap and the fix's premise that
provisioning `imagemagick` is sufficient; the hosted CI run itself has still not
been observed.

### The dialog-mode mutual-exclusion refusal says "not both" when three or more dialog modes are given together (found by the bugfix role 2026-11-10) — fixed 2026-11-10 by the bugfix role

**Symptom.** The render CLI refuses any combination of two or more `--*-dialog` mode flags with "the dialog modes open one dialog client each: give one of <flags>, not both" (tools/render_surface.py's mode check). With two flags the wording holds, but every third or further flag joins the same list, so a three-flag argv printed "give one of --checkbox-dialog, --slider-dialog, --gtk-dialog, not both" — a wording that is false about the number it refuses. The sibling two-mode refusal tests pinned only that both flag names appear, never the closing wording or the three-flag case, so the drift was invisible to the suite.

**Reproduce.** `python3 tools/render_surface.py out.png --checkbox-dialog --slider-dialog --gtk-dialog` exits 2 and prints the refusal ending ", not both" above. The new regression test `tests/test_render_surface_units.py::TestArguments::test_the_multi_mode_refusal_wording_holds_for_three_modes` fails on that wording before the fix ("'not more than one' not found in ...") and passes after it.

**Fix.** The refusal now ends "not more than one", which holds for every count above one, so no count-dependent wording remains. The two-mode argv shape is unchanged; the two existing two-mode refusal tests still pass untouched.

**Validation gap:** none — the confirmation needed only a three-flag argv through the CLI's existing usage-error path, nothing external was missing to observe it; what was missing was any test reading that path's wording, and the new three-mode test now pins it.

### The render harness's nested sessions crash-loop xdg-desktop-portal-kde with SIGABRT while the nested Wayland socket is not serving (found by the director role 2026-11-10) — fixed 2026-11-10 by the bugfix role
**Symptom.** On this host (Plasma Wayland login of uid 1000), `coredumpctl -q list --since "2 hours ago"` showed ~640 SIGABRT (Signal 6) coredumps of `/usr/lib/x86_64-linux-gnu/libexec/xdg-desktop-portal-kde` in the window ending 2026-11-10 02:58:14 PST — still firing at 02:58:14 as the user reported, quiet by 03:03. Bursts run roughly one to three dumps per second, and `drkonqi-coredump-launcher` chases every dump in the journal (extra churn; its pid metadata lookups also fail, flooding the log). Every dump's stack is identical: `QGuiApplicationPrivate::createEventDispatcher` → `QMessageLogger::fatal` → `abort` in `QApplicationPrivate::init` at the portal's `_main`, the classic qFatal when the platform plugin cannot connect to a display. Crucially the sampled dumps sit in a `tmux-spawn-…` cgroup scope of `user@1000.service` — descendants of a tmux pane running a role run — not the login portal (that one, a ~4.9-day-old process on the host bus, is stable). The journal carries tens of thousands of portal-kde lines per busy day since October 17, matching the cadence of role render runs, and tens of thousands of coredump payloads this boot.

**Reproduce.** On this host, with the coredump journal readable (`journalctl --user` works for uid 1000), run one dialog render gate (`python3 tools/render_surface.py --color-dialog <out>.png`, documented prerequisites present) and count fresh xdg-desktop-portal-kde SIGABRT entries in `coredumpctl` during the run. The suspected window is the span where `dbus-run-session`'s private bus is up but the nested `kwin_wayland` socket `render-surface` (tools/render_session.py's `SOCKET`) is not yet listening — or has died — while something on that bus (KWin's startup settings-portal call, or a later activation retry) asks for the portal: each activation starts the portal inside the caller's process tree, Qt tries Wayland, QGuiApplication aborts, and D-Bus re-activates, dumping a core per attempt until the socket serves or the run's supervision ends the loop.

**Suspected cause.** The nested session's environment (tools/render_session.py::Session, which drops the host's `DISPLAY`/`WAYLAND_DISPLAY` and exports `WAYLAND_DISPLAY=SOCKET`) is applied at the `dbus-run-session` level and is passed whole to its private bus daemon (tools/render_workflow.py::render calls `process_group.run_logged(command.argv, session.environment, …)`), so every D-Bus-activated service — including xdg-desktop-portal-kde — inherits `WAYLAND_DISPLAY=render-surface` and no `QT_QPA_PLATFORM`. The session script's own `export QT_QPA_PLATFORM=wayland` pins only the client inside the `sh` body, not the activated portal. When the nested KWin socket is not yet listening (before `bind`) or gone (after KWin exits while the bus still lives), the portal's QGuiApplication cannot connect and aborts; nothing pins the portal to a display-free platform, and the re-activation loop turns every attempt into a SIGABRT coredump. Because the crashes are D-Bus-activated descendants of `dbus-run-session`, the end-of-run group kill in tools/process_group.py::run_logged already bounds them per run — the load may be zooming only through repeated runs — but if any private bus outlives its socket without supervision, those kills can never break the loop.

**Fix direction for the bugfix role.** Candidate: in tools/render_session.py::Session's `environment`, set `QT_QPA_PLATFORM=offscreen` for the whole nested bus subtree (the session script still overrides it to `wayland` for the client), so the activated portal never attempts Wayland and serves KWin's settings query from a display-free context; verify empirically that a render run afterwards produces no new xdg-desktop-portal-kde SIGABRT entries in `coredumpctl`, and pin the environment change in the render-surface suite's existing session-environment tests. Do not add any pkill-style name/pattern cleanup (project rule); any teardown must reach only process trees this harness started.

**Validation gap:** real-run-needed — the crash-window confirmation required a real bounded render run against this host's coredump journal (one fresh SIGABRT before the fix, none after); the offline stubs cannot observe D-Bus activation at all.

### The landed --color-dialog gate left the dialog-gate count prose in one test comment, one docstring and the two paired invariants rows saying nine dialog gates and eight kdialog modes (found by the bugfix role 2026-11-10) — fixed 2026-11-10 by the bugfix role

The color-dialog render gate landed in 534650a1d with the shared skip guard already covering its `TestColorDialogRender` (the gate list in `tests/test_render_surface.py` derives nothing from these words), but only some of the prose that counts the gates was updated along with it: `tests/test_render_surface.py`'s skip-guard comment and docstring still read "kdialog for the eight kdialog modes", `tests/test_ci_workflow.py`'s comment still read "the nine dialog gates" listing nine gate classes without `TestColorDialogRender`, and `docs/invariants.md`'s skip-guard row and software-renderer row still read "The nine dialog render gates ... kdialog for the eight kdialog modes" — while the sibling prose in the same lines had already moved to "the ten dialog gates" and "the nine kdialog modes". A reader trusting either stale surface would under-report the dialog surfaces the skip guard covers.

Reproduce by grepping the count prose: `grep -n 'eight kdialog\|nine dialog' tests/test_ci_workflow.py docs/invariants.md tests/test_render_surface.py` shows the stale words beside fresh ones. The new derived guard `tests/test_dialog_gate_count_prose.py` counts the live `Test...DialogRender` gate classes in `tests/test_render_surface.py` and fails on all four stale prose sites before the fix (failures 9≠10 and 8≠9) and passes after.

**Validation gap:** no-observability — the stale counts sat in comments, a docstring and doc prose that no test read, so the drift produced no failure and was found only by a manual grep; the new count guard now fails on any count word that lags the live gate classes.

### The Makefile render-mode parity test never pins the literal-argv `--lineedit-dialog` branch (found by the bugfix role 2026-11-10)

`tests/test_render_make.py::TestRenderMake::test_default_and_explicit_modes_pass_literal_argv`
pins one literal-argv row per `RENDER_MODE` the `render` target's `case` maps — the default,
`calculator` and eight of the nine dialog modes (checkbox, combobox, menu, calendar,
progressbar, slider, textbox, gtk) — but the ninth, `lineedit-dialog`, never got a row when its
gate landed. A mistyped branch therefore ships with the whole module green: shown by
temporarily mapping the branch to `--menu-dialog`, after which `tests.test_render_make` still
passed while `make render RENDER_MODE=lineedit-dialog` would capture the wrong dialog.
Behavior on this host is fine; the gap is the unguarded branch.

Fix: add the ("lineedit-dialog", ["--lineedit-dialog"]) row beside its siblings; re-running the
mistyped contrast shows the new row failing on it and the restored Makefile passing.

**Validation gap:** none — a deterministic mutation contrast reproduces and confirms the gap
(mistyping the branch keeps the suite green before the fix; the new row fails on the mistyped
Makefile and passes on the restored one), so nothing was missing.

### The render CLI's usage docstring omits the landed --calendar-dialog mode (found by the bugfix role 2026-11-10) — fixed 2026-11-10 by the bugfix role

`tools/render_surface.py`'s module docstring Usage block — the CLI contract a
reader sees before any `--help` run — listed its sibling dialog modes
without `--calendar-dialog`, even though the calendar render-gate commit
(93a227df0) registered the flag in the argument parser and updated the
Makefile, argparse help, README and invariants around it. Nobody reading the
docstring learns the calendar mode exists.

Reproduce by comparing the two lists: the argument parser defines nine
run-dialog flags — `--checkbox-dialog`, `--combobox-dialog`,
`--lineedit-dialog`, `--menu-dialog`, `--calendar-dialog`,
`--progressbar-dialog`, `--slider-dialog`, `--textbox-dialog` and
`--gtk-dialog` — while the docstring named eight, with no
`--calendar-dialog` among them. Fixed by adding the flag to the Usage block and by a
regression test (`tests/test_render_surface_units.py::TestArguments`
`test_usage_docstring_names_every_dialog_mode_the_parser_defines`) that
extracts both sets from the source and demands exact equality, so a future
gate that wires Makefile/README but skips the docstring (or outlives its
removal) fails immediately.

**Validation gap:** none — the new source-parsing regression test reproduced
the drift before the fix (parser modes minus docstring modes named
`--calendar-dialog`) and passed after it; the existing suite pinned argparse
help but nothing pinned the docstring, so the gap was one missing guard, not
a missing repro.

### The render CLI suite ran no slider-dialog missing-kdialog test because a copy-pasted def shadowed the name it was filed under (found by the dedupe role 2026-11-10) — fixed 2026-11-10 by the dedupe role

`tests/test_render_surface_units.py::TestArguments` defined
`test_rejects_an_applet_with_the_checkbox_dialog` twice: the first definition (a copy-paste of the
per-mode requires-kdialog recipe) asserted `--slider-dialog`'s missing-tool naming but carried the
checkbox name, and the second definition — the real applet-refusal test — replaced it at import
time, so the first never executed. Every other kdialog dialog mode (lineedit, progressbar,
combobox, menu, checkbox) has a `test_the_<mode>_dialog_requires_kdialog` test; the slider mode's
coverage existed only inside the shadowed, misnamed def, so the suite ran no assertion that
`render_surface.main(("out.png", "--slider-dialog"))` names kdialog when it is absent, while
`tools/render_surface.py`'s `kdialog_flags` branch does require kdialog for that mode.

The fix deletes the shadowed definition and restores its body under the correct name,
`test_the_slider_dialog_requires_kdialog`, placed with the slider group — completing the per-mode
family without changing any production code.
**Validation gap:** none — a per-class duplicate-`def` scan over `tests/test*.py` reproduces the
shadowing, and the renamed test passes against the current CLI.

### The GTK CSS suite ran only the second of two same-named `test_escaped_trailing_value_whitespace_is_preserved` defs (found by the coverage role 2026-11-10) — fixed 2026-11-10 by the coverage role

`tests/test_gtk_css.py::TestRuleBlockSemantics` defined `test_escaped_trailing_value_whitespace_is_preserved`
twice: `767e83a9b` (2026-11-01) added the first definition and `84b7e1cc8` (2026-11-01, later the same
day) added a second with the same name into the same class, so the first was shadowed at import
time and never executed for nine days while `make check` stayed green. A repeated `def` in one
class silently replaces the earlier one — the same shadowing shape the dedupe role removed from
`TestGtk4Theme::test_dim_label_foreground` on 2026-11-09.

The dead definition still passed when run directly, so it was lost to the shadow rather than
outdated. It covered two cases the surviving definition never runs: a two-backslash trailing run
(`token\\   ;` keeps both backslashes; the survivor loops slash counts (1, 3) only) and the plain
unescaped-trailing-whitespace collapse (`token   ; color: red;` and `token   }` reduce the value to
`token`, the trimming half of the invariant row the test shares). The fix deletes the shadowed
definition and folds both cases into the surviving one — slash counts (1, 2, 3), plus an explicit
unescaped-collapse loop — so one test now covers both halves of `docs/invariants.md:346` and the
row's named test reads unchanged.
**Validation gap:** none — a per-class duplicate-`def` scan over `tests/test*.py` reproduces the
shadowing, and running the shadowed definition under a temporary distinct name showed it green;
no other test module defines a same-class duplicate.

### The GTK 3 sheet lost the selected-row swatch ring rule the colorchooser suite pins (found by the plan role 2026-11-10) — fixed 2026-11-10 by the bugfix role

`python3 tests/test_gtk_theme_colorchooser.py` fails two tests: `test_color_swatch_corners`
and `test_selected_row_color_swatch_ring` (`AssertionError: 1 != 0` — the sheet holds zero
`row:selected colorswatch` selectors where the suite pins exactly one with
`box-shadow: 0 0 0 2px ` the sheet's black frame-border ink). The declared `make check` is
red on the tree the pending slider-dialog merge builds from, so that merge's check cannot pass
today. Reproduce from any tree that carries commit `6aedc94d3` by running the module; no other
dialog of the sheet is involved.

Suspected cause: `6aedc94d3` (tumwater(reviewer) 2026-11-10) deduplicated the ring declaration
and deleted the `row:selected colorswatch` rule and its 2026-10-31 provenance comment from
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (the hunk around the landed
`button.color colorswatch:only-child` block, near `colorswatch overlay:hover`), stating a
second identical copy "further down the swatch block" survived — the surviving copy does not
exist in the committed sheet, so the rule vanished instead of collapsing to one copy. A fix
restores one rule plus one dated provenance comment (re-deriving the comment's date or keeping
the 2026-10-31 one) and leaves both tests reading unchanged; whether the sheet text that
re-lands comes from `git show 5b0cb131c` or the pre-`6aedc94d3` state, exactly one rule and
exactly one `docs/invariants.md` selected-row ring row must remain.

Fix: landed 2026-11-10 in `564ccd1d9` — it restores one `row:selected colorswatch` rule with
the kept 2026-10-31 provenance comment after the landed `button.color colorswatch:only-child`
block, and the tree holds exactly one such rule and exactly one selected-row ring row at
`docs/invariants.md:170`.
**Validation gap:** none — the existing `tests/test_gtk_theme_colorchooser.py` suite reproduced
it; removing the restored rule makes both pinned tests fail (`AssertionError: 1 != 0`) and
restoring it turns them green.

### The GTK 3 selected-row colorswatch ring test pins a selector the landed sheet no longer ships (found by the dedupe role 2026-11-10) — fixed 2026-11-10 by the bugfix role

**Symptom:** on a pristine checkout of main, `make check` fails in
`tests/test_gtk_theme_colorchooser.py::TestGtkThemeColorChooser::test_selected_row_color_swatch_ring`:
`self.selectors.count("row:selected colorswatch")` is 0, and
`GtkSheetRuleCases.assert_color_swatch_corners` also fails for the same selector.

**Repro:** `make check`; also `cd tests && python3 test_gtk_theme_colorchooser.py` (both fail with 2
failures in that module, verified 2026-11-10 with no local edits).

**Suspected cause:** the sheet
(`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`) contains no `row:selected colorswatch` arm at all,
so the test's pin (`{"box-shadow": "0 0 0 2px #000000"}` at line 54) matches nothing. Reviewer commit
6aedc94d3 (2026-11-10, "tumwater(reviewer): Fix 5b0cb131") removed the sheet's copy as an alleged
"duplicate CSS rule", believing an identical rule existed further down the swatch block — but the
shipped sheet has no other copy (checked by grep, 2026-11-10), so the removal deleted the only
declaration the test and the corner inventory look for.

Already resolved before this run: commit 564ccd1d9 (2026-11-10) restored the
`row:selected colorswatch` arm (`box-shadow: 0 0 0 2px #000000`, with the platform-adaptation
provenance comment) at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:724`. Verified 2026-11-10: all
15 tests in `tests/test_gtk_theme_colorchooser.py` pass, no code edit needed.

**Validation gap:** none — the module's tests reproduced and confirmed the missing selector, then confirmed the restored arm on main's HEAD; nothing was missing.

### The invariants register names a missing render-gate test (found by the dedupe role 2026-11-09) — fixed 2026-11-09 by the bugfix role

`make check` red on a clean worktree: the kvantum invariants row `docs/invariants.md:596`
registers `tests/test_render_surface.py::TestMenuDialogRender::test_draws_the_list_field_sunken_border_runs`,
but no such method exists in that file (it names only `test_draws_the_item_view_frame_and_white_interior`
under that class). Both `test_invariants_seed_is_valid` and `test_invariants_mutations` in
`tests/test_checker_mutations.py` fail on it. The open PLANS.md entry "Kvantum line-edit dialog
render gate" (planned 2026-11-09) describes this gate; the register row was written as if the
gate had already landed, so the mismatch predates and is unrelated to this run's diff (which
touches only `tools/sample_match_runs.py`). Fix when the plan's gate lands, or correct the
register row's test reference to the gate actually shipped.

The register citation was corrected by commit 519ef843c to the gate actually shipped
(`TestMenuDialogRender::test_item_view_frame_matches_its_measured_border_runs`); no new edit was
needed. Verified on the 2026-11-09 worktree: `tests/test_checker_mutations` (10 tests) and
`tests/test_invariants` (46 tests) pass, and the register cross-check reports no errors.

**Validation gap:** none — the two checker tests reproduced and confirmed the stale citation; nothing was missing.

### the render tests' KWin session cannot allocate its capture buffers under the workflow's llvmpipe env (found by the ci role 2026-11-09) — fixed 2026-11-09 by the feature role

`make check` at main's tip `3a380abe20b939b96004b32fd07ddc3e5d9bf49f` fails `tests/test_render_surface.py` with 32 errors and 5 failures: every KWin virtual render session (`tools/render_session.py`: plain `kwin_wayland --virtual`) fails with `KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied`, so the session produces no capture and the tests that read the rendered PNG get `cannot read ... dialog.png: [Errno 2] No such file or directory`.

Reproduce with the workflow job env on this host:

    QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 MESA_LOADER_DRIVER_OVERRIDE=llvmpipe \
      make check CHECK_TESTS=test_render_surface

Suspected cause: commit `a005ece42` added `MESA_LOADER_DRIVER_OVERRIDE: llvmpipe` (and `LIBGL_ALWAYS_SOFTWARE: '1'`) to `.github/workflows/ci.yml`'s job env for the GPU-less hosted runner. On this host (kernel `6.12.115+deb13.1-amd64`, a real GPU is present): with `LIBGL_ALWAYS_SOFTWARE=1` alone the virtual session is clean, but adding `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe` drives Mesa's KMS/GBM dumb-buffer path, and the kernel refuses dumb-buffer creation on the render node while permitting it on the primary node — verified with a direct `drmModeCreateDumb`-equivalent ioctl probe: `/dev/dri/card0` succeeds, `/dev/dri/renderD128` returns `Permission denied`. KWin then logs `kmsro: driver missing`, `Failed to open drm node: ""`, and the dumb-buffer denial, and spectacle's `CaptureScreen` on `Virtual-0` gets no reply.

A local-only fix inside project code (unsetting the override in the session or the check target) would silence the env for the runner-run `make check` too, defeating the env the runner still needs and whose runner-side value was never observed: the hosted run at `18ded7fe` failed at the install step before tests, so the forced-llvmpipe KWin path has never executed on the runner. The workflow files are out of the ci role's scope by this team's charter, so this filing routes to the bugfix or plan role: either drop the override from the workflow's env or read why it is needed on the runner and give the session an env it can steer there only.

Worked output from the reproduce run:

    AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/tumwater-run-Q0oLZO/render-surface-d99iuox1/surface.png: [Errno 2] No such file or directory: '/tmp/tumwater-run-Q0oLZO/render-surface-d99iuox1/surface.png'
      An error occurred while taking a screenshot.
      KWin screenshot request failed:
      Did not receive a reply. Possible causes include: the remote application did not send a reply, the message bus security policy blocked the reply, the reply timeout expired, or the network connection was broken.
      Potentially relevant information:
      - Method: CaptureScreen
      - Method specific arguments: "Virtual-0"
      
      render-session: capture status 0
      KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied
      render-session: client reaped

Fix: the settled change removes the `MESA_LOADER_DRIVER_OVERRIDE: llvmpipe` line from `.github/workflows/ci.yml`'s check job env and keeps only `LIBGL_ALWAYS_SOFTWARE: '1'`, which alone forces a software EGL driver for the nested KWin virtual session; the reproduce contrast above was re-run with the override stripped (`QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check CHECK_TESTS=test_render_surface`) and the module completes with no KMS dumb-buffer error, the capture gates skipping with the software-renderer reason. The absence is pinned by `tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_runs_the_suite_on_the_headless_qt_platform`'s new `assertNotRegex` assertions on both `MESA_LOADER_DRIVER_OVERRIDE:` and `GALLIUM_DRIVER:` assignments, and `docs/invariants.md`'s two `## tooling` rows reword the forced-llvmpipe wording and record the local contrast's provenance. The fix is filed as the plan entry "CI workflow: drop the forced llvmpipe driver override the KWin render sessions cannot survive on a GPU host", done 2026-11-09 by the feature role (archived under PLANS-DONE.md).

**Validation gap:** real-run-needed — the local reproduce contrast is settled, but the hosted runner's virtual session under the remaining env (`LIBGL_ALWAYS_SOFTWARE=1` alone) was never observed (the hosted run `18ded7fe` failed at the install step before any test); it stays unobserved until the next hosted run that reaches the suite, as recorded in the workflow comment and the invariants row's provenance cell. (Originally tagged the bespoke `runner-side`, a tag in no ledger; re-tagged to the closest header tag — no offline path observed the hosted session — in the change that pinned the archive's tag vocabulary.)

### post-merge review of 6d3e4ac9 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `6d3e4ac986708de6cb4d2667391599905877d92f` (Pin the Kvantum check indicator to the 14x14 canvas via %General check_size=14) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix.** Read the commit's diff on main and checked each piece against the current tree: the `[%General]` `check_size=14` pin in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` is present with its provenance comment; `tests/support/kvantum_config_spec.py` pins `check_size: "14"` under `VALUE_KEYS["%General"]`; `tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference::test_config_draws_the_indicator_at_the_canvas_size` derives the canvas side from the shipped SVG (14 = `SHIPPED_SIZE`) and asserts the resolved config value matches; `tests/support/validation_gaps.py` carries the `check-box-indicator-resample` real-run reproduction with `REAL_RUN_NEEDED_BASELINE` raised to 6; and `docs/invariants.md` carries the rendered-indicator guarantee row with its Kvantum 1.1.4 provenance. Nothing to fix: the commit landed correctly. Re-ran both touched test modules (`tests.test_kvantum_checkbox_reference`, `tests.test_kvantum_config`) — all tests pass.

**Validation gap:** none — the landing's own suite pins every facet this settlement checked; nothing was missing.

### post-merge review of 9abbd3d7 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9abbd3d758e1b8bc3498199e4c601915b84b2c62` (Pin the check log-cap's breakless-window and CRLF branches) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Verdict: landed correct, nothing to fix.** Checked the commit's diff against the current code: `tools/check_parallel_results.py::_bounded_log_text` realizes the breakless-window arm exactly as the new `test_a_window_without_any_line_break_is_shown_whole` pins it (no `\n` in the window leaves it whole at 65536 shown, so the leading `check:` note names 100000 − 65536 = 34464 hidden bytes, nothing dropped), and it realizes the CRLF arm exactly as `test_crlf_worker_log_lines_end_before_the_line_breaks` pins it (`tools/text_lines.py::split_lines` folds `\r\n` and bare `\r` into one line per record before `escape_controls` replays the tail, so no literal carriage return survives); both new tests exist in `tests/test_check_parallel.py::TestCoordinator` and `docs/invariants.md`'s tooling row was updated to name them.

**Validation gap:** none — the commit's own two new coordinator tests reproduce and confirm both pinned branches offline.

### post-merge review of b02a1811 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `b02a18113d564a1c870f6af5a56aa99a53f5ec07` (Factor the dotted focus-outline assertion in tests/test_gtk_theme.py into one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Verdict: landed correct, nothing to fix.** Read the commit's diff (`git show b02a1811`) and the landed tree at main's tip: it is a pure tests/test_gtk_theme.py refactor that adds one class helper carrying the literal `1px dotted` outline dict plus the three-property copy-from-anchor loop, and converts all thirteen repeated blocks — twelve with the default `button:focus` anchor, `spinbutton.vertical:focus` anchored to `spinbutton:focus:not(.vertical)` and `radiobutton:focus` anchored to `checkbutton:focus`, preserving each original comparison. After the later suite split the helper lives hoisted in `tests/support/gtk_rule_cases.py` (line 282) with the same signature and docstring, and the thirteen calls span the split suites (three in `test_gtk_theme.py`, four in `test_gtk_theme_views.py`, six in `test_gtk_theme_controls.py`); the two declared remaining inline cases (`test_scale_focus_outline`, `test_button_focus_outline`) stay inline with their extra properties, and the only other `1px dotted` literals in the suite area are the scale trough rule, the GTK 4 user-sheet restatement pins and the OSD sheet restatement — the sheet's own CSS literals and `gtk_theme_spec`'s `RUBBERBAND` constant are untouched, so no assertion coverage was lost.

**Validation gap:** none — the converted call sites are exercised by the GTK theme suites; `CHECK_TESTS='test_gtk_theme test_gtk_theme_controls test_gtk_theme_views test_gtk_theme_osd' make check` exits 0 with `Ran 184 tests ... OK`.

### post-merge review of 7e872a94 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `7e872a94a111a8b95bcb8be97f140ee17ccd0ec9` (Recolour Firefox chrome and page scrollbars with the Platinum two-face scrollbar-color sweep) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Verdict: landed correct, nothing to fix.** Read the commit's diff (`git show 7e872a94`) and the landed tree at main's tip: `userChrome.css` declares `scrollbar-color: #DDDDDD #EEEEEE !important` inside the landed `:root` variable block (line 841) with the dated provenance comment naming the absent reference surface, the toolkit probe and the two-face limit; `userContent.css` carries the one top-level `:root` rule with the same sweep (line 940) and its provenance comment; `tests/support/firefox_chrome_cases.py` pins the declaration in `REQUIRED_RULES[":root"]` (line 131); `tests/test_firefox_theme_shell.py::TestFirefoxChromeShell::test_root_colors_every_chrome_scrollbar` and `tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_root_colors_the_page_scrollbars` (with the column-zero `:root {` count and the no-`scrollbar-color`-in-any-body guard) are landed; the `## firefox` invariants table carries the two scrollbar rows with provenance cells. Both values match `tests/support/platinum_palette.py`'s `FACE = "#DDDDDD"` and `TROUGH = "#EEEEEE"`, the desktop-theme scrollbar art pinned by `tests/test_desktoptheme_scrollbar.py`. Nothing in the diff contradicts the project's principles: no Apple asset, no new dependency, values grounded in the pinned palette with the missing-reference provenance recorded.

**Validation gap:** none — the pinned suites confirm the landed declarations: `CHECK_TESTS='test_firefox_theme_shell test_firefox_content_theme test_invariants test_desktoptheme_scrollbar test_colorscheme_reference' make check` exits 0 with `Ran 94 tests ... OK`.

### post-merge review of 9e2126ef never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9e2126ef2e5b076d445968fcfce888c15aed63ba` (Cap the parallel check's printed worker logs at a bounded 64 KiB tail with a hidden-bytes note) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Verdict: the landed cap is correct; nothing to fix.** Read the commit's diff on main and the landed tree: `tools/check_parallel_results.py::_bounded_log_text` anchors its read at (file size − 64 KiB) or the file's start, opens the window on a line break, decodes with replacement, puts the hidden-byte note ahead of the section, and feeds every line through `escape_controls`; the exit-5 `NO TESTS RAN` verdict scan runs on the tail that always ends with unittest's summary. `_print_results` still routes every module through it and the `OSError` unreadable-log guard still stands. The landed tree has hardened past the diff's own text since the merge (a later land added the `os.O_NONBLOCK` open and the `stat.S_ISREG` regular-file guard, and the CRLF `replace` chain became the shared `tools/text_lines.py::split_lines`, byte-for-byte the same line splitting), and both later lands are their own review entries. Both pinned tests from the diff live on: `tests/test_check_parallel.py::TestCoordinator::test_a_flooded_log_prints_a_bounded_tail_with_a_hidden_byte_note` and `test_a_flooded_log_keeps_its_end_of_log_summary_verdict`; the module's check (`CHECK_TESTS='test_check_parallel'`) runs those 43 tests with every one passing (exit 0).

**Validation gap:** none — the module's own suite reproduces and confirms the cap offline (flooded-tail printing, hidden-byte note, surviving summary verdict); only the verdict of the never-run review was missing, not any confirmation.

### post-merge review of 55468302 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `55468302d04e3c1c2f11ea19fc43330721c548cb` (Repaint GTK 3 header drop arm with the selection fill, plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff and re-checked the landed tree — the GTK 3 sheet carries the dated adaptation comment and the single grouped twelve-selector rule (`treeview.view button.dnd` and the legacy `header.button.dnd` spelling plus the landed `header button.dnd` chain, each with plain/`:hover`/`:active`/`:selected`) declaring exactly the selection `#CCCCFF` fill with black text, `background-image: none`, no text shadow, no box shadow, no border and zero radius (theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css ~line 810); `grep -c dndtarget` over the sheet returns 0, and the sheet declares no padding in the arm. The pinning tests survive a later relocation into `tests/test_gtk_theme_views.py` (`test_header_drop_indicator`, `test_header_drop_arm_carries_no_padding`, `test_no_dndtarget_node_declared`) guarding the same twelve selectors, and `docs/invariants.md` carries the dnd-arm row under `## gtk`. Nothing is wrong to fix.

**Validation gap:** none — the existing suite reproduced and confirmed it; the landed tests pin every selector and declaration.

### post-merge review of 432fac12 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: read the diff of commit `432fac122f8e696eccf13ee4ffeff409039162d1` (Make the apply-cursor and Firefox HOME refusals name the received HOME value) on main — nothing is wrong, so there is nothing to fix. Both refusals still stand on the landed tree with the wording the diff landed: `tools/apply_cursor.py`'s `resolve_homes` raises `HOME is {state}; export an absolute HOME` and `tools/firefox_profile.py`'s `resolve_profile` raises `HOME is {state} and no Firefox profile was named; …`, where the shared `xdg_homes.unresolved_home_state` (later factoring) keeps an unset or empty value `"unset"` and quotes any other non-absolute value as `'...value...'`. No equal-tier rule or later edit strips it: the only remaining `"unset or not absolute"` wording lives in `apply_gtk`'s own message, left unchanged on purpose per the commit's RISK note. The two test files still pin the new wording, including `test_home_value_reaches_the_diagnostic_escaped` for the control-byte escape; ran them green through the project's check (`make check CHECK_TESTS='test_apply_cursor test_firefox_profile'`, OK, exit 0).

**Validation gap:** none — the recorded tests reproduce and confirm the wording this commit pins; nothing was missing.

### post-merge review of 6ed8830f never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `6ed8830f4906d3b9038ec267337365f5174cd132` (Repaint GTK 4 drag-and-drop drop states with the #CCCCFF selection fill) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: nothing wrong to fix. On the landed tree all three dnd groups reach gtk-4.0/gtk.css unchanged (lines 1398, 1402 and 1410): the icon-view drop border, the three row-drop-target band arms and the nine header `button.dnd` arms (with the six state variants) all declare the pinned `#CCCCFF` selection with black ink, and tests/test_gtk4_theme.py still pins them with the four recorded tests (`test_iconview_drop_border`, `test_row_drop_borders`, `test_header_drop_indicator`, `test_row_drop_directional_arms_undeclared`), which run green against the sheet. No landed rule overrides them: the sheet's other header-button arms (`> header > button`, `:hover`, `:active`, `:last-child`, the sort-indicator spellings) name no `.dnd` token and lose the specificity count, so a dragged-over header button keeps the selection fill. The stock provenance remains recorded in the docs/invariants.md row the commit added.

**Validation gap:** none — the four landed dnd tests reproduce and confirm the sheet's drop-state rules, so the review's only open question, whether the landed commit's claims still hold on main, was answered by running them.

### post-merge review of 2c379b28 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `2c379b28758fb69d225d658c58bc98acf727d6bc` (Refuse control bytes in CHECK_TESTS and CHECK_PARALLEL at make parse time, unecheod) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: checked the landed tree and the commit's declared behavior holds — `make check CHECK_TESTS=$'tests_x\x1b'` refuses at parse (`Makefile:142 *** CHECK_TESTS contains a control character ...`) with the variable named and the 0x1b byte absent from both streams, the legal values still dry-run (`make -n check CHECK_TESTS=test_colorscheme.TestAnchors CHECK_PARALLEL=2` exits 0), and the commit's tests survive in `tests/test_make_refusals.py::TestShellUnsafeCheckVariables` (extended to also pin the double-quote breakout `2c379b28` left to the recipe guards, via the no-slower shared refusal later commit `321bded65` gave both variables in the line-142 `refuse_unsafe_value` foreach — no regression). The landed tree no longer carries the commit's dedicated two-line guard; the shared foreach guard refuses a control byte the same unecheod way, so nothing is wrong to fix.

**Validation gap:** none — the landed suite's `TestShellUnsafeCheckVariables` reproduces the refusal and the scratch parse-time and legal-value runs confirmed the rest.

### post-merge review of 4e97dc86 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `4e97dc86812ef81e5b0af62a959e52bc106ccc4b` (Paint the GTK 3 scrollbar corner junction as the flat #EEEEEE scrollbar band) never reached a verdict: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed commit `4e97dc86`'s diff on main's current tree. The GTK 3 sheet declares exactly two junction rules — `scrolledwindow junction` and `scrolledwindow junction:backdrop`, each pinning `background-color: #EEEEEE` (the landed scrollbar band trough ink), `border-color: transparent` and `border-image: none` — inside an adaptation comment that names the missing reference surface (no collected screenshot shows a GTK scrollbar corner) and the stock `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` inventory it adapts, with no stray `junction:dir` arm; the live tests pin the exact rule shape and the arm's absence, and the docs/invariants.md GTK 3 junction row cross-references them. Nothing wrong to fix.

**Validation gap:** none — the landed suite already pins the junction rules' shape, state coverage and arm absence, confirming the change as landed.

### post-merge review of 1555c1c2 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `1555c1c261debc86fcb890bf4806353af6e5c7c7` (Remove the stray, unreferenced `adwaita3.css` from the repo root) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: the landed state verifies at HEAD. `git show 1555c1c2` on main is a pure deletion — 2055 lines removed from the single file `adwaita3.css` at the repo root, nothing else touched. The file is absent from the worktree (`test -e adwaita3.css` fails), and a case-insensitive tree grep (`grep -RIni adwaita3 .` excluding `.git`) matches nothing that consumes or expects the file: the only hits are this BUGS.md record itself and a historical narrative line in BUGS-FIXED.md recording the removal's provenance — no Makefile target, test, tool or doc references it. The stock Adwaita resource is regenerated from the installed libgtk-3.so by past runs, so no evidence file is needed. Nothing wrong found to fix.

**Validation gap:** none — the settled commit's own `make check` plus today's tree grep confirm the removal left no dangling references.

### post-merge review of 2843fac7 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `2843fac7ecb8824d3dbc79e408ef0ac86593d736` (Remove the dead private wrapper `_link_target` from tools/apply_cursor.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main — a pure 5-line deletion of the private wrapper `_link_target` from tools/apply_cursor.py — and verified it removed nothing in use. A tree-wide grep over tools, tests, docs and the Makefile for `_link_target` matches nothing outside this BUGS.md record, so the wrapper truly had zero callers; tools/apply_cursor.py still imports `cursor_link` and retains `CURSOR_THEME`/`CursorError` plus the `_require_installed` and `_install_link` neighbors above the removed block, and tools/cursor_link.py still defines `link_target` (line 32) with `install_link` and `remove_link` — the callers the commit's WHY names — unchanged. Nothing was wrong; the commit lands as reviewed, verdict reached today by reading the diff instead.

**Validation gap:** none — the existing suite covers apply_cursor.py; the review itself was only blocked, not the verification.

### post-merge review of 514cfd13 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `514cfd137f072b8df4777047d7917807e8c46174` (Extend the GTK 4 linked-group strip to menubutton, colorbutton, fontbutton and tabbutton members) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: the commit landed correctly. It touches only the GTK 4 sheet's linked-group rules (theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css), the pinning tests (tests/test_gtk4_theme.py), the invariants row and the plan move; the landed four-member strip rules keep their exact text and the four new member spellings extend the same trailing-border-strip shape. Re-derived the provenance from the installed stock resource: `gresource extract` of `/org/gnome/Adwaita/styles/base.css` from `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` carries exactly these four wrapped-container member arms at lines 1124–1162 (menubutton, colorbutton, fontbutton, tabbutton), horizontal arms direction-doubled with radius flattening and negative margins, vertical arms as child combinator spellings the sheet translates its `.linked.vertical > ` child selectors to; `appchooserbutton > combobox > box > button.combo` stays out, matching the invariants row's scope note. All selectors survive at HEAD (`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` lines ~2686–2721, tests at tests/test_gtk4_theme.py lines ~5505–5530), and `make check CHECK_PATTERN='test_gtk4_theme.py'` ran OK (244 tests). The recorded adaptation risk — a GTK app nesting one of these containers under `.linked.vertical` unlike the stock's own spellings — is platform behavior the stock resource does not exercise either; nothing in the stock arms contradicts the landed rule text.

**Validation gap:** none — the existing suite (tests/test_gtk4_theme.py) pins every stripped and restored member spelling, and the stock resource re-derivation confirmed the four-arm inventory.

### post-merge review of 9c1b6738 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9c1b673822eb2bed96e47d46d29360a910ef4384` (Pin the parallel check's discovery skip of a symlinked test-module file) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: every landed piece of the commit verifies at HEAD. The commit is test-only plus one invariants wording update (2 files, +22/−1; no production code). The delivered guard stands: `tools/check_parallel_discovery.py` line 49 guards every walked entry with `os.path.islink(path)` and skips it, so the same guard covers package directories and top-level module files, and a symlink at the tests root pointing to an outside module file never becomes a discovered module name. The two pinning tests survive a later merge at the moved path — the organize commit `b7818a495` split `tests/test_check_parallel.py` into per-module suites, and both symlink cases now also live at `tests/test_check_parallel_discovery.py::TestDiscovery::test_symlinked_package_directories_are_not_recursed` and `...::test_a_symlinked_test_module_file_is_not_imported` (the module case builds an outside `test_outside.py`, links it in as `test_linked.py`, and asserts discovery returns only the real `test_ok` module). `docs/invariants.md` line 745 carries the check-parallel row updated to the moved test paths while retaining the commit's wording, "skips symlinked directories and symlinked module files". Ran `make check CHECK_PATTERN='test_check_parallel_discovery.py'` in this worktree: 9 tests ran and passed, including the module-symlink case the commit added. Nothing wrong found to fix.

**Validation gap:** none — the commit's own test reproduces the reached edge offline (a symlinked module file outside the selected tests tree skipped by discovery); nothing was missing.

### post-merge review of 31561db0 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `31561db0f51dd3b83b6c022494d8d6d2003207b3` (Share one helper for each GTK 4 scale-anchored focus assertion) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: the commit is test-only and faithful — it introduces `SCALE_FOCUS`/`SCALE_SLIDER` constants and two helpers (`assert_scale_focus_outline`, `assert_scale_slider_transition`) whose bodies reproduce each displaced assertion verbatim (the same `assert_rule` call plus the same cross-rule comparison, now against the constant), every migrated call site passes the identical selector string the displaced copy keyed, the scale-anchor test `test_scale_focus_outline_color` keeps its original body (comparing against the calendar label, never against itself), and the displaced test count matches the commit subject's (six outline-color tests: button, entry, spinbutton, checkbutton, notebook, switch; five transition tests: button, entry, spinbutton, checkbutton, notebook tab), so no guarantee was weakened and nothing needed fixing. Verified on today's `main`: the helpers sit in `tests/test_gtk4_theme.py` at 919–952 with every call site covered, the docstring-anchored invariants rows for these GTK 4 focus tests in `docs/invariants.md` still name the unchanged test names in that file, and `make check CHECK_TESTS=test_gtk4_theme.TestGtk4Theme` reports the suite OK (239 tests, 1 skipped, exit 0).

**Validation gap:** none — the existing suite reproduced and confirmed it; the migrated tests ran green within the project's check both before and after this settlement.

### post-merge review of cfcbc183 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `cfcbc183c5e182284b601dc81238c2a2f50edf4a` (Clear the stock GTK 3 scroll overshoot glows in the Platinum sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: every landed piece of the commit verifies at HEAD. The commit's plan (Platinum GTK 3 scroll areas: clear the stock overshoot edge glows) is archived at PLANS-DONE.md line 7161 with its "— done 2026-10-30 by the feature role" stamp. The delivered rule stands: `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` lines 1028–1041 hold the one grouped rule listing the eight stock overshoot arm selectors (`scrolledwindow overshoot.top`/`.bottom`/`.left`/`.right` and their `:backdrop` versions) verbatim declaring `background-image: none`. The commit wrote its two tests into `tests/test_gtk_theme.py`; a later merge moved them intact to `tests/test_gtk_theme_scrollbars.py::TestGtkThemeScrollbars::test_overshoot_glows_cleared` and `...::test_overshoot_backdrop_glows_cleared`, and `docs/invariants.md` line 406 names both at the moved path with the eight-arm inventory, its gresource-extraction provenance and the broadway runtime probe. Both tests pass in this worktree under `make check CHECK_TESTS=test_gtk_theme_scrollbars.TestGtkThemeScrollbars` (the run reaches both overshoot tests, prints OK and no FAILED/ERROR line). Nothing wrong found to fix.

**Validation gap:** none — the archive record, sheet rule, pinning tests and invariants row all covered the commit's landing; verifying them needed no new repro.

### post-merge review of 64cd32e1 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `64cd32e1d6ea2719862f5ac0ab15da0f65bbcbaf` (Record an unopenable worker log in check_parallel instead of a traceback) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the commit's landing at HEAD. `tools/check_parallel_workers.py` still carries the OSError handler the commit added — now in the refactored `_fill_workers` starter loop (`tools/check_parallel_workers.py:147-160`, identical behavior and diagnostic wording): a failing `_spawn` log open prints one `check: error: cannot open the worker log for <module>: <os error>` stderr line with the module and OS error run through `escape_controls`, records the module as exit 1 (the same never-started status `_spawn`'s own `could not be started` note produces, whose unreadable-log section `_print_results` then reports), and keeps supervising the rest of the run instead of unwinding `_supervise` as a bare traceback. The two pinning tests the commit added exist and pass — `tests/test_check_parallel.py::TestCoordinator::test_an_unopenable_log_records_its_module_and_keeps_the_run` (unit: exit statuses `{module: 1}`/`{other: 0}` plus the stderr diagnostic) and `...::test_an_unopenable_log_reports_its_module_as_a_failure` (end-to-end through `main`: run exits 1, the diagnostic on stderr, no `Traceback`, and the module's section reported as `worker log could not be read`); `docs/invariants.md` line 745 carries the check-parallel row naming the unopenable-log behavior in `tools/check_parallel_workers.py` and both test names. `escape_controls` is imported in both the package and script contexts (`tools/check_parallel_workers.py:16,21`). Nothing wrong found to fix.

**Validation gap:** none — the commit's two `TestCoordinator` cases reproduce and confirm the fault path offline (a poisoned log path under a missing parent directory); nothing was missing.

### post-merge review of 88ab8202 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `88ab8202ffa3ffbe8df54c01f7ad92eaa87a4673` (Append the verified GTK 3 scroll-edge plan to PLANS.md ## Planned and refresh role notes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: every landed piece of the commit verifies at HEAD. The commit's PLANS.md plan (Platinum GTK 3 scroll areas: clear the stock overshoot edge glows) was implemented and archived — PLANS-DONE.md line 7144 carries it with its "— done 2026-10-30 by the feature role" stamp; the stray evidence extract `adwaita3.css` it also wrote at the repo root was removed by the later organize commit `1555c1c26`. The delivered rule, tests and provenance all stand at HEAD: `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` lines 1028–1041 hold the one grouped rule listing the eight stock overshoot arm selectors (`scrolledwindow overshoot.top`/`.bottom`/`.left`/`.right` and their `:backdrop` versions) verbatim declaring `background-image: none`; both named tests exist and pass — `tests/test_gtk_theme_scrollbars.py::TestGtkThemeScrollbars::test_overshoot_glows_cleared` and `...::test_overshoot_backdrop_glows_cleared` (path differs from the plan's named `tests/test_gtk_theme.py`, an acceptable landing deviation); and `docs/invariants.md` line 406 carries the `## gtk` row naming both tests, the eight-arm inventory, its gresource-extraction provenance and the broadway probe. Nothing wrong found to fix.

**Validation gap:** none — the archive record, sheet rule, named tests and invariants row all covered the commit's landing; verifying them needed no new repro.

### post-merge review of 8ac91c5b never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `8ac91c5b605d34271c716f50501bfef72fa2229f` (Clear stock GTK 4 undershoot and overshoot bands in the Platinum gtk.css) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the commit's landing at HEAD. The six direction-arm undershoot mirrors, the arm-by-arm `columnview`/`treeview`/print/search-popover/emoji-picker/filechooser/row.combo/toolbarview mirrors and the four `scrolledwindow > overshoot.*` glow-clearing rules all sit verbatim in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` lines 1461–1501 declaring `background: none; box-shadow: none` (undershoots) and `background-image: none` (overshoots); `tests/test_gtk4_theme.py` carries `test_undershoot_bands_cleared` and `test_overshoot_fades_cleared` plus the two widened enumeration tests `test_gridview_item_corners` and `test_emoji_picker_cell_corners`; `docs/invariants.md` row on line 404 records the guarantee and names all four test classes. All four pass from `tests/`, and no GTK 3 or PLACEHOLDERS.md scope was touched by the commit.
**Validation gap:** none — the declaration-level suite reproduced and confirmed the clearance; nothing was missing.

### post-merge review of 3b60be19 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: reviewed the commit's landing at HEAD. The Makefile carries both make-level refusals: the CHECK_PATTERN guard sits in the shared `refuse_unsafe_value` list at `Makefile:142` (since extended with `COLOR_SCHEME_NAME`, `CHECK_TESTS` and `CHECK_PARALLEL`) and its separate apostrophe refusal for the single-quoted `-p '$(strip $(CHECK_PATTERN))'` recipe words at `Makefile:150` and `Makefile:488`/`Makefile:490`; the INSTALL_PACKAGES guards sit at `Makefile:212` (control bytes) and `Makefile:213` (shell metacharacters at its unquoted `set -- $(INSTALL_PACKAGES)` position at `Makefile:327`), still checking a caller's value before `INSTALL_PACKAGES ?=` at `Makefile:319` defines the default. The commit's test classes landed intact after migrating between test files (`tests/test_theme_install.py` → `tests/test_make_refusals.py:606` and `tests/test_make_refusals.py:678`); docs/invariants.md row 698 names both variables, both refusal sets and both test classes, so no doc gap is left. Running the named classes passes, and a live probe of both vectors (`make check CHECK_PATTERN='testX"; touch <canary>; echo "'`, `make install INSTALL_PACKAGES='noop; echo'`) refuses at make level with the diagnostics naming the variables and leaves no canary file.

**Validation gap:** none — the existing suite reproduced and confirmed it; nothing was missing.

### post-merge review of 7923474a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `7923474a2cd53d3c75f1efaf851ed5d6331e1f65` (Add `THEME_ROOT` to the Makefile's parse-time refusal of shell-metacharacter make inputs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the commit's landing at HEAD. The parse-time guard list carries `THEME_ROOT` (Makefile:142, extended by later commits — it now also covers `COLOR_SCHEME_NAME`, `CHECK_PATTERN` and the check variables, with the dated comment at Makefile:116-118); `require_theme_links` still pastes the value into the double-quoted recipe words (`[ -L "$(THEME_ROOT)" ]`, `find "$(THEME_ROOT)" ...` at Makefile:338), so the guard is the right protection; the commit's tests survive — migrated intact (including the canary injection test and the HOSTILES sweep) to `tests/test_make_refusals.py:407` as `TestShellUnsafeThemeRoot`, and all four tests pass. The one gap found was in documentation, not code: the sibling variables' invariant row carried every guarded variable and test but never mentioned `THEME_ROOT`, so docs/invariants.md:698 now lists it with its test. The commit landed as ordinary verified-backlog work; nothing else in its scope was missing.

**Validation gap:** none — the existing suite's `TestShellUnsafeThemeRoot` reproduces and confirms the guard's behavior.

### post-merge review of a44691d4 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `a44691d436e063ebd6a9d21d8a68aa7f49e09391` (Give GTK 4 linked groups one shared black border between members in the Platinum sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff and confirmed every landed piece at HEAD — the GTK 4 linked-group strip and `:last-child` restore groups and the two guard rules live in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` (lines 2467 onward, since extended by later commits with the four wrapped-container member spellings), the provenance-header sentence sits before the header's closing `*/` (lines 126-129), and the three tests `test_linked_members_strip_their_trailing_border`, `test_linked_last_member_restores_the_border` and `test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines` are in `tests/test_gtk4_theme.py` (lines 5327-5371), with the matching invariants row at `docs/invariants.md` line 403. Found nothing wrong to fix: the strip/restore/guard mechanism matches the recording in the commit message and the later extensions trace to their own follow-up commits. Ran the three tests in isolation (OK) and the project's full `make check` after verifying, exit 0.

**Validation gap:** none — the existing suite's three declaration tests reproduce every rule the commit added, and the full check covered the rest of the tree.

### post-merge review of 8c3bfb18 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `8c3bfb186a59f2e16c074f888bac7240de54341e` (Land the GTK 3 linked-group shared-border plan and retire its stale Planned queue) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the commit's diff at main and each landed piece at HEAD — the shared-border rules survive at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:1975` (member strips, `:last-child` restores and the `.path-bar`/`stackswitcher` protection group, with the dated provenance comment), the three pins live at `tests/test_gtk_theme_controls.py:1734` (`test_linked_members_strip_their_trailing_border`, `test_linked_last_member_restores_the_border`, `test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines`; moved from `test_gtk_theme.py` in later work and re-listed so in `docs/invariants.md:402`), and the provenance-header sentence and PLANS-DONE.md entry are in place. All three tests pass; `make check` exits 0 with no failed lines. Nothing wrong found; settled as landed-OK.

**Validation gap:** none — the existing suite reproduced and confirmed the landed declarations; nothing was missing.

### post-merge review of 9203bead never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: settled Landed-OK at HEAD. The commit's CSS rule is present as its own selector at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (`spinbutton.vertical:focus` declaring `outline: 1px dotted #000000`, `outline-offset: 0` and `-gtk-outline-radius: 0`, with its dated no-vertical-reference adaptation comment after the horizontal `spinbutton:focus:not(.vertical)` rule), its pin lives at `tests/test_gtk_theme_controls.py::TestGtkThemeControls::test_vertical_spinbutton_focus_outline` — the spin-button outline tests have since moved from `tests/test_gtk_theme.py` to `tests/test_gtk_theme_controls.py`, where the helper-backed `assert_dotted_focus_outline("spinbutton.vertical:focus", anchor="spinbutton:focus:not(.vertical)")` still asserts the three literal declarations and the per-property equality with the landed horizontal rule — and the invariants row (renamed to name `tests/test_gtk_theme_controls.py::TestGtkThemeControls::test_vertical_spinbutton_focus_outline`) sits under `## gtk` in `docs/invariants.md`. Both the vertical and horizontal focused-outline tests pass under unittest, and `make check` exits 0 at this tree. Nothing in the landed change was wrong.

**Validation gap:** none — the existing suite reproduced and confirmed the landed assertions; nothing was missing.

### post-merge review of 85d1a439 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: settled the review by hand on main's tip. The commit's pieces are all landed and verified at HEAD: the dated adaptation comment and `calendar { border: 1px solid #000000; }` rule at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:1796-1801`, the pin `tests/test_gtk_theme.py::TestGtkTheme::test_calendar_outer_border` at line 776 (asserting the exact `calendar` border declaration and its equality with both `frame > border` and `.frame`), and the invariant row at `docs/invariants.md:184`. Ran the focused test (pass); ran `make check` (pass).

**Validation gap:** none — the landed suite already reproduced and confirmed the change; nothing was missing.

### post-merge review of 266c6cdc never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `266c6cdc073ac038f3c04daa63dd3078c1e5f2fc` (Declare GTK 3 tooltip descendant text treatment and complete its plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked the landed state at HEAD — the GTK 3 sheet still carries the dated comment and the `tooltip *` rule declaring `color: #000000` and `text-shadow: none` exactly where the commit added it, immediately after `tooltip.background` and before the menu-separator rule (now `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:584-589`); the parent `tooltip` rule's `color: #000000` it compiles against sits at gtk.css:571-578 intact; the pin survives in the commit's original file, `tests/test_gtk_theme.py::TestGtkTheme::test_tooltip_descendant_text` (now at lines 184-193), still comparing `tooltip *`'s color against `tooltip`'s and its `text-shadow: none` against `treeview.view header button`, which I ran and watched pass alongside `test_no_universal_selector`, whose only universal-selector exception is still `tooltip *` at tests/test_gtk_theme.py:148-151; the shared `GtkSheetRuleCases.test_tooltip` parent-rule pin lives at tests/support/gtk_rule_cases.py:648-650; and the docs/invariants.md `## gtk` row restates the guarantee with the Adwaita-resource provenance and declaration-only scope (docs/invariants.md:335). Nothing in the commit or anything since it landed is wrong.

**Validation gap:** none — the statement is a settled review verdict, not a changed behavior, and the existing suite pins the rule it reviews.

### post-merge review of 5f785744 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `5f785744caf29ad1b862f7a7a410359c323fb91a` (Clear stock background images from the GTK 3 add-color action) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked the landed state at HEAD — the GTK 3 sheet still carries the dated comment and the four-selector `colorswatch#add-color-button overlay`, `:hover`, `:backdrop` and `:backdrop:hover` rule whose `background-image: none` reset the commit added, since extended by later merges (the 2026-10-31 adaptation adds the face `#DDDDDD`, border, foreground and shadow clears around it, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:680-711`); the strict corner helper's optional `extra_declarations` parameter lives at `tests/support/gtk_rule_cases.py:247` with the GTK 3 caller's own module literals; the pin moved in later reorganizations from the commit's `tests/test_gtk_theme.py` to `tests/test_gtk_theme_colorchooser.py::TestGtkThemeColorChooser::test_add_color_background_images`, which I ran and watched pass, alongside `test_color_swatch_corners` there; the GTK 4 caller `tests/test_gtk4_theme.py::TestGtk4Theme::test_color_swatch_corners` keeps its strict expectations with named exceptions; and the docs/invariants.md rows (`test_add_color_background_images` cited at lines ~175 and ~353) restate the guarantee with the Adwaita-resource provenance and declaration-only scope. Nothing in the commit or anything since it landed is wrong.

**Validation gap:** none — the statement is a settled review verdict, not a changed behavior, and the existing suite pins the rule it reviews.

### post-merge review of b1d277b1 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `b1d277b110f890c900d0ee2660f50400218bf3f7` (Add and document the GTK 3 icon-view focus outline) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked the landed state at HEAD — the GTK 3 sheet still carries the dated comment and the `iconview:focus` rule restating exactly `outline: 1px dotted #000000`, `outline-offset: 0` and `-gtk-outline-radius: 0` right after the `treeview.view:focus` block and before the flow-box block; the pin now lives at `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_iconview_focus_outline` via the shared `assert_dotted_focus_outline` helper (anchored to `button:focus`), which I ran and watched pass; `tests/test_gtk_theme_views.py::test_iconview_selected_arms` still finds `iconview:focus` among landed selectors; the docs/invariants.md row restates the rule, the button:focus recipe reuse, the Adwaita dashed-default provenance and the declaration-only scope. Nothing in the commit or anything since it landed is wrong.

**Validation gap:** none — the statement is a settled review verdict, not a changed behavior, and the existing suite pins the rule it reviews.

### an unfounded `_None yet._` placeholder claims PLANS.md `## Planned` holds no entries (found by the bugfix role 2026-11-09) — fixed 2026-11-09 by the bugfix role

`make check` at main's tip `81921233143640c758cd3651a4b3aba129214fb7` fails `tests/test_backlog_placeholders.py` with two failures, both reporting `('## Planned',)` as an unfounded placeholder: the plan commit `b3e9ea01d` appended the GTK 3 scale marked-node geometry entry to `## Planned` without deleting the section's `_None yet._` claim (it sat at main's PLANS.md:8, directly above the new entry at line 10), and both `test_no_placeholder_claims_a_section_that_holds_an_entry` and `test_plans_sections_placeholders_match_their_entries` pin that a placeholder may only claim a genuinely empty section.

Fix: deleted the `_None yet._` line from PLANS.md `## Planned` (now 10 lines up from the queued entry, file unchanged elsewhere in that section).

**Validation gap:** none — the existing suite reproduces and confirms the placeholder contract; the fix deletes one line.

### post-merge review of df50d69f never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `df50d69fe7bcddc7d17ab99e39e8b72cbc894b04` (Add the GTK 3 calendar focus outline and pin its declarations) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked each changed file. The `calendar:focus` rule is verbatim at theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:1804-1811 (dated adaptation comment at 1804-1805, `1px dotted #000000`, `outline-offset: 0`, `-gtk-outline-radius: 0`); `git diff df50d69f..HEAD` on that file never touches the rule itself (nearby diffs are the later `calendar` outer-border rule added just above it and the search/location-bar band comment, other selectors). The test survives in tests/test_gtk_theme.py:784 `test_calendar_focus_outline` — it was refactored to shared helper `assert_dotted_focus_outline` at tests/support/gtk_rule_cases.py:223, which still pins the three literal declarations and compares each with `button:focus` (verbatim at gtk.css:259-263); the docs/invariants.md:185 row already cites that test path. Ran the test standalone (OK).

**Validation gap:** none — the existing suite reproduces and confirms the declaration guarantee the commit pinned.

### post-merge review of d88fb2e3 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `d88fb2e385c916da63386e3ce0e8b6df36c4f593` (Clear stock background images from GTK 3 paned handles) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked each changed file. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` still declares the grouped rule `paned > separator`, `paned > separator:selected`, `paned > separator:backdrop`, `paned > separator.wide` and `paned > separator.wide:backdrop` with the single `background-image: none` declaration (lines 640–645), preceded by the dated missing-reference adaptation comment (lines 637–638) and followed by the landed etched `paned.horizontal`/`paned.vertical` separator arms it exposes; `git diff d88fb2e3..HEAD -- that file` never touches the rule (the nearby diffs are the GTK 4 direction-margin restatement and the paned sidebar rules, inside different selectors). The commit's test moved from `tests/test_gtk_theme.py` to `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_paned_handle_background_images` (line 1034) and still pins `background-image: none` on all five selectors through `assert_rule`, with the etched-pair geometry pinned by the neighbouring `assert_paned_handles` call (line 1032) via the shared helper in `tests/support/gtk_rule_cases.py:316`. The invariant row at `docs/invariants.md:186` already cites the moved test path. Nothing was wrong on main.

**Validation gap:** none — the commit's own test reproduces the five cleared declarations on main; it was run standalone (`python3 -m unittest -v test_gtk_theme_views.TestGtkThemeViews.test_paned_handle_background_images`) and passed.

### post-merge review of 9f35b16a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9f35b16a4ebad0f8b7ce052d9d142c027c2d2a29` (Add an explicit focus outline to GTK 3 expander titles) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked each changed file. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` still declares `expander > title:focus` with `outline: 1px dotted #000000`, `outline-offset: 0` and `-gtk-outline-radius: 0`, preceded by the dated missing-reference adaptation comment (line 880); `git diff 9f35b16a4eb..main -- that file` leaves the rule itself untouched (the surrounding diffs are the disclosure RTL rule above it and the spin-button spelling shift below). The commit's test remains at `tests/test_gtk_theme.py::TestGtkTheme::test_expander_title_focus_outline` (line 217) and now pins the three literal declarations plus the `button:focus` copy through the shared `assert_dotted_focus_outline` helper in `tests/support/gtk_rule_cases.py` (line 223) — a superset of the commit's original assertions. The invariant row at `docs/invariants.md:188` already cites that live test path. Nothing was wrong on main.

**Validation gap:** none — the commit's own test reproduces the outline declarations on main via the shared helper; the focused GTK check (40 tests) and the named test passed on the live tree.

### post-merge review of dd5937a3 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `dd5937a3252314dce97d0a87ef7d46bbfe172c5b` (Add a GTK 3 focus outline for flow-box children) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 9:09 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and checked each changed file. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` still declares `flowbox > flowboxchild:focus` with `outline: 1px dotted #000000`, `outline-offset: 0` and `-gtk-outline-radius: 0`, preceded by the dated missing-reference adaptation comment (line 856). The commit's test moved from `tests/test_gtk_theme.py` to `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_flowbox_child_focus_outline` (line 234), which now pins the three literal declarations plus the `button:focus` copy through the shared `assert_dotted_focus_outline` helper — a superset of the commit's original assertions. The invariant row at `docs/invariants.md:400` already cites the moved test path. Nothing was wrong on main.

**Validation gap:** none — the commit's own test reproduces the outline declarations on main via the moved helper; the focused check (40 tests) passed on the live tree.

### post-merge review of 97f6c248 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Landed-OK fix. Checked the commit's diff against the live tree: `treeview.view:focus` stands verbatim at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:842` with its dotted black 1px outline, zero offset, `-gtk-outline-radius: 0` and the dated-plan's adaptation comment intact (`git diff 97f6c248 -- <that file>` changes nothing in the rule). The commit's own test was reorganized rather than lost: `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_treeview_focus_outline` (line 229) now pins the selector through `tests/support/gtk_rule_cases.py::GtkSheetRuleCases::assert_dotted_focus_outline`, a superset of the commit's inline assertions (the same three declarations, plus the `button:focus` comparison). `docs/invariants.md` already retargeted its GTK 3 `treeview.view:focus` row to the moved test path. Focused run `CHECK_PATTERN='test_gtk_theme_views.py' make check` passed on the worktree tree.

**Validation gap:** none — the commit's own tests reproduce and hold the tree-view focus outline on main, and the focused check run passed on the live tree.

### post-merge review of 9ddcbc8b never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix.** Settled as landed-OK on main. The commit's declaration lives verbatim in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (`list row:focus` with the `1px dotted #000000` outline, zero offset and `-gtk-outline-radius: 0`, not restricted to `.activatable`, reusing `button:focus` per the provenance comment, beside the generic row selection rules); after the suite's later reorganization the test moved to `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_list_row_focus_outline` and was rewritten onto the shared `tests/support/gtk_rule_cases.py::assert_dotted_focus_outline` helper, which pins those literal declarations and the copy from the `button:focus` anchor; the gtk row in `docs/invariants.md` was retargeted to that moved test path and still names the recording. Focused `make check CHECK_PATTERN='test_gtk_theme_views.py'` reported OK for the module, and the full check passed. Nothing renders differently than the declaration claims, so there is nothing to fix.

**Validation gap:** none — the commit's own declaration test reproduces and holds the rule on main (rewritten onto the shared focus-outline helper during later reorganization), and the focused `make check CHECK_PATTERN='test_gtk_theme_views.py'` run passed on the live tree.

### post-merge review of 1e1e9f68 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix.** Settled as landed-OK on main. The commit's declaration lives verbatim at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:417` (`notebook > header > tabs > tab:focus` carrying the `1px dotted #000000` outline, zero offset and `-gtk-outline-radius: 0` reusing `button:focus`, per the provenance comment); after the suite's later reorganization the test stays at `tests/test_gtk_theme.py::TestGtkTheme::test_notebook_tab_focus_outline` and was rewritten onto the shared `tests/support/gtk_rule_cases.py::assert_dotted_focus_outline` helper, which pins those literal declarations and the copy from the `button:focus` anchor; the gtk row in `docs/invariants.md` is unchanged and still names that test path. Focused `make check CHECK_PATTERN='test_gtk_theme.py'` reported OK for the module, and the full check passed. Nothing renders differently than the declaration claims, so there is nothing to fix.

**Validation gap:** none — the commit's own declaration test reproduces and holds the rule on main (rewritten onto the shared focus-outline helper during later reorganization), and the focused `make check CHECK_PATTERN='test_gtk_theme.py'` run passed on the live tree.

### post-merge review of e2b655ac never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix.** Settled as landed-OK on main. The commit's declaration lives verbatim at `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css:307` (`spinbutton:focus:not(.vertical)` with the 1px dotted black outline, zero offset and `-gtk-outline-radius: 0` reusing `button:focus`, per the provenance comment); the test survived the suite's later reorganization and moved to `tests/test_gtk_theme_controls.py::TestGtkThemeControls::test_horizontal_spinbutton_focus_outline` on the shared `assert_dotted_focus_outline` helper, and the invariant row in `docs/invariants.md` was retargeted to that moved path; a later commit added a `spinbutton.vertical:focus` twin with the same declarations. Focused `make check CHECK_PATTERN='test_gtk_theme*.py'` reported OK for every module, and the full check passed. Nothing renders differently than the declaration claims, so there is nothing to fix.

**Validation gap:** none — the commit's own declaration tests reproduce and hold the rule on main, moving to the shared focus-outline helper during later reorganization, and the focused `make check CHECK_PATTERN='test_gtk_theme*.py'` modules and the full check all passed on the live tree.

### post-merge review of 6bebcd43 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix.** The commit's work is landed-OK on main. Its test `TestSpawnDefenses.test_an_unexpected_popen_error_restores_deferred_signals` survived the later refactor that moved signal deferral out of `tools/check_parallel_workers.py::_spawn` into `tools/process_group.py::_popen_deferred`: in the live tree the test mocks `process_group._defer_signals` (side effect yields the termination-then-interrupt previous-handlers lists), `process_group._restore_termination` and `process_group._replay_deferred`, and asserts that an unexpected `Popen` error takes the deferred-spawn except path restoring termination then interruption and replaying the empty deferred list before re-raising. That is exactly what `tools/process_group.py::_popen_deferred` does on `BaseException` (restore the termination handlers, restore the interrupt handlers, replay the deferrals, re-raise), and `_spawn` converts only `OSError` to its `_NeverStarted` path, so the mocked `RuntimeError` propagates to the test. `git merge-base --is-ancestor 6bebcd43 main` confirms the commit is on main; the review never reached a verdict, so this entry settles it: the commit's landed state checks out.

**Validation gap:** none — the focused test_check_parallel*.py check run reproduces the defended behavior offline against the refactored helpers and passes.

### post-merge review of 37a806fc never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `37a806fc8fb732d5f3391e73321fe4e672315d29` (Skip symlinked package directories during test discovery) never reached a verdict: fix did not merge: merge_conflict. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix.** Settled as landed-OK by re-reviewing the commit on main against the live tree: the commit is an ancestor of main and its three changes are all in the tree. `tools/check_parallel_discovery.py` skips every `os.path.islink` entry in the discovery walk, with the outside-the-tree import rationale in the comment; `tests/test_check_parallel.py::TestDiscovery::test_symlinked_package_directories_are_not_recursed` builds an outside package beside a scratch tests dir, links it in, and asserts empty discovery; and the coordinator row in `docs/invariants.md` names the symlink skip and points at that pinning test. A later landed sibling in the same class, `TestsDiscovery::test_a_symlinked_test_module_file_is_not_imported`, extends the guard to symlinked module files. Focused run `make check CHECK_PATTERN='test_check_parallel*.py'` exits 0 with that test passing and no FAILED or ERROR line in its log.

**Validation gap:** none — the commit's own discovery regression reproduces and confirms the guard offline, and the follow-up module-file test re-confirms it after the coordinator split.

### post-merge review of c1325a54 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `c1325a54c20a2aae1d9efaac0251fa9934a1c7ec` (Split the parallel check coordinator by responsibility) never reached a verdict: fix did not merge: merge_conflict. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix.** The commit's landed work is live on main and settled as landed-OK. The split is intact and has grown further since: `tools/check_parallel_discovery.py` holds `discover_modules` and `_log_paths`, `tools/check_parallel_workers.py` holds `_NeverStarted`, `_Worker`, `_spawn` and `_supervise`, and `tools/check_parallel_results.py` holds `_plural` and `_print_results`, with no forwarding definitions left in `tools/check_parallel.py` (grep of `def _supervise`/`def _print_results`/`def discover_modules`/`def _log_paths`/class definitions over `tools/check_parallel*.py` matched only the defining modules); the coordinator imports those modules for both the package and direct-script entry paths, and the focused check run executed it directly (`python3 tools/check_parallel.py -p 'test_check_parallel*.py'`) without error. The tests import and patch the extracted helpers at their defining modules (`check_parallel_discovery.discover_modules`, `check_parallel_discovery._log_paths`, `check_parallel_workers._supervise`, `check_parallel_workers._NeverStarted`, `check_parallel_workers.os/subprocess` patch targets) and patch the coordinator's own imported bindings only where the coordinator-contract cases must steer it, and a later-landed `tools/check_parallel_order.py` module plus a newer `docs/invariants.md` tooling row identify guarantees by module (row naming `check_parallel_discovery.py`, `check_parallel_workers.py`, `check_parallel_results.py` and the order module), so nothing stale or missing remained to fix.

**Validation gap:** none — the existing coordinator tests reproduce and confirm the split behavior at its new module paths; the focused `make check CHECK_PATTERN='test_check_parallel*.py'` run (3 modules, 3 workers) passed on the live tree.

### post-merge review of 144131fd never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `144131fdd29d45e711c58140dde54c311e13cc2c` (Complete and record original artwork placeholder tracking) never reached a verdict: fix did not merge: merge_conflict. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. Commit `144131fd` is merged on main (`git merge-base --is-ancestor` holds) and its work is in the live tree, since reorganized: the done entry sits at `PLANS-DONE.md:8057` with the plan removed from `PLANS.md`; the shipped SVG artwork under `theme/icons/org.macos8.desktop` and the splash logo all carry `<!-- PLACEHOLDER: … -->` markers with matching PLACEHOLDERS.md rows (splash logo row at `PLACEHOLDERS.md:18`); the invariants row the diff added names the tracked tests at `docs/invariants.md:725` (`tests/test_splash_logo.py::TestLogo::test_logo_is_tracked_as_a_placeholder`, `tests/test_placeholders.py`); and the validation-gap mapping change survives in `tests/support/validation_gaps/unclear_invariant.py:268`, where the `icon-placeholder-art` unclear-invariant entry now needles `icon theme` and names `tests/test_icon_theme.py::TestIndex::test_placeholder_register_matches_the_icon_art` (the implicit string concat there yields the intended full dotted test id). The underlying behavior is green: `make check CHECK_PATTERN='test_icon_theme.py'` (19 tests OK, includes the register-matches-icon-art test), `CHECK_PATTERN='test_splash_logo.py'` (3 tests OK, includes `test_logo_is_tracked_as_a_placeholder`) and `CHECK_PATTERN='test_placeholders.py'` (23 tests OK, the parser and duplicate-row refusals all pass). Nothing in the commit's scope is wrong on main, so there was nothing to fix.

**Validation gap:** none — the focused icon-theme, splash-logo and placeholder module runs reproduced and confirmed the landing of the placeholder tracking.

### post-merge review of 0caac668 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `0caac66850897b63f8bf7e33c1971902c94ec097` (Escape control characters in parallel-check diagnostics) never reached a verdict: fix did not merge: merge_conflict. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

No defect. Commit `0caac668` is merged on main (`git merge-base --is-ancestor` holds) and its capability is live, since strengthened by the later coordinator split: `tools/check_parallel.py` imports `escape_controls` from `tools/terminal.py` on both import branches and escapes `options.pattern` in the run banner (`tools/check_parallel.py:90`), while the commit's two usage refusals (a missing `--tests-dir` directory and a pattern that matches no module) now ride the shared `report_error` diagnostic, which escapes the whole message itself (`tools/diagnostics.py:79`), instead of the inline `escape_controls` calls the commit added — the same guarantee through a stronger path. The regression test `tests/test_check_parallel.py::TestCoordinator::test_pattern_control_characters_are_escaped_in_diagnostic` is intact in the tree (moved to line 842 by insertion-only hunks), `docs/invariants.md`'s rewritten parallel-check register row still lists that test among the cases it pins, and the diagnostic contract behind `report_error` records the control-character escaping in `tools/diagnostics.py`'s module doc and invariant rows. Focused runs `make check CHECK_TESTS='test_check_parallel'` (62 tests OK) and `make check CHECK_TESTS='test_make_check'` (36 tests OK) pass; nothing in the commit's scope needed repair.

**Validation gap:** none — the committed escaping regression test itself reproduced and confirmed the behavior, passing in the focused module run.

### post-merge review of a3f6ce0f never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: settled by reading commit `a3f6ce0f` (Paint GTK 3 application notifications with the Platinum band) on main, where it is an ancestor. The diff's `.app-notification` / `.app-notification.frame` band rules, their `:backdrop` twins and the `> border` reset are present in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (lines 1597–1615), with the border reset preceding the etched bottom border and the reuses of the landed infobar palette and etched edge; the two declaration tests `test_app_notification_band` and `test_app_notification_frame_border` and the `GTK 3 application notifications` row of docs/invariants.md are landed as the diff shows; and `make check CHECK_TESTS='test_gtk_theme'` passes (74 tests, OK). Nothing in the commit needs repair.

**Validation gap:** none — the commit's own declaration tests reproduce and hold every claim on main, and they were re-run green this run.

### The archive accepts validation-gap tags no ledger covers, so a bespoke tag evades every ledger cap and the newest Fixed record already does it (`runner-side`) (found by the steward role 2026-11-09) — fixed 2026-11-09 by the bugfix role

`BUGS.md`'s opening lines record exactly seven tags (`none`, `no-repro`, `no-fake`, `real-run-needed`, `no-observability`, `slow-check`, `unclear-invariant`), the roles' shared tag contract uses no others ("when nothing fits exactly, use the closest tag and say so — never invent a tag"), and the ledger modules treat those tags as complete. The archive carries an eighth: the capture-buffer entry's Fixed record (fixed 2026-11-09 by the feature role) reads `**Validation gap:** runner-side — …`, a tag in no ledger. Verified `runner-side` is unique in `BUGS.md` and `BUGS-FIXED.md` combined; every other archived tag is ledger-backed.

Why the discipline cannot catch it: `tests/support/validation_gaps/reader.py` (lines 18–19, `PROSE_GAP` and `BULLET_GAP`) parses any lowercase tag word, and the ledger suite enforces entry matching, guarantee pinning and the non-growth baseline only for the six tags in `tests/support/validation_gaps/ledgers.py::LEDGERS`. A foreign tag borrows no ledger entry (`tests/test_validation_gaps.py::TestReproductionLookup::test_a_foreign_tag_borrows_no_ledger_entry`), consumes no baseline and is never capped, so the caps fail closed only where a ledger exists. That test's own comment anticipated this — "Every shipped tag now has a ledger, so the foreign tag here is one that no ledger covers yet (rename it again if such a tag ever becomes a real concern)" — and the concern arrived on 2026-11-09.

Risk: any Fixed record can carry a bespoke tag and so ship with no reproduction entry and no bounded count, `validation_gaps.reproduction_for` refuses it (the record pinning that refusal is the foreign-tag test), and a tally of the archive sees the tag name but no ledger can ever match it — including the steward's promotion query, which decides when a recurring tag earns retirement infrastructure. Today the escape is a single record, so closing it is cheap; it grows costlier with each new bespoke-tag record.

Reproduce offline: `grep -n 'Validation gap:.*runner-side' BUGS.md BUGS-FIXED.md` names the record — the archive's only one — and a tag tally over both archive files exceeds the six `LEDGERS` keys by exactly that tag.

Repair routes to the bugfix role (the ledger and its tests are source, outside the steward's markdown-only scope). First, pin the vocabulary with a source-side test: every record `validation_gaps.read_gaps` finds in `BUGS.md`/`BUGS-FIXED.md` carries one of the seven header tags, so a future bespoke tag fails instead of sailing through. Then settle the demonstrated record: either re-tag `runner-side` to its closest allowed tag (`real-run-needed` fits — no offline path observed the hosted session; a real bounded run was required) and give it a `real-run-needed` ledger entry naming an offline reproduction of the failure, raising `REAL_RUN_NEEDED_BASELINE` by one in the same change, or leave it named and record a reasoned exception in the reader's tests if no offline reproduction exists.


Fix: the repair followed the re-tag route. `tests/test_validation_gaps.py::TestArchiveVocabulary` now pins the vocabulary — every record `validation_gaps.read_gaps` finds in `BUGS.md`/`BUGS-FIXED.md` must carry one of the seven header tags, and `LEDGERS` must cover every header tag but `none` — so a future bespoke tag fails the suite in the commit that adds it; the test was written first and named exactly this record (BUGS.md's `runner-side` line) as it failed. The demonstrated record was re-tagged to `real-run-needed` (the wording already matched: no offline path observed the hosted session), and the ledger gained the `render-session-capture-buffer-denial` entry naming `tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_runs_the_suite_on_the_headless_qt_platform` — the offline test that refuses driver-name overrides in the workflow env — with `REAL_RUN_NEEDED_BASELINE` raised to 12 in the same change. `docs/invariants.md`'s tooling row records the closed vocabulary and names the new test.

**Validation gap:** none — the new archive-vocabulary test itself is the reproduction: it read the shipped archives and failed on exactly this record before the re-tag, and passed after.

### post-merge review of 572fb8c0 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `572fb8c022f925bf7fca2ff209da2f3f7bdf5d53` (Fix garbled about:support provenance sentence in userContent.css) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit's diff adds the `@-moz-document url("about:support")` block plus the header provenance paragraph to `theme/firefox/org.macos8.desktop/chrome/userContent.css`, and its fix is in the live tree: the formerly fused clause now reads as two complete sentences — "The page body, its h1/h2 headings, the loaded-about paragraphs and the .action-box card stay Firefox's." and "The `#contents table` selector matches all 26 tables aboutSupport.js builds inside div#contents …" — with every test-required provenance token (aboutSupport.xhtml and .js, the ten button ids, `#codec-table`, widgets/lineedit.svg, `@-moz-document url("about:support")`, "platform colour adaptation 2026-10-27") still present; docs/invariants.md's about:support row agrees with the sheet and names the test module. The rules' selectors and pinned palette are enforced by `tests/test_firefox_content_support.py::TestFirefoxSupportTheme` and `tests/test_firefox_content_theme.py::TestFirefoxContentTheme` (the split the later 9ad1de128 organize run recorded), and the ESR-only claims (26 tables, light DOM) carry their recorded headless-run provenance per the platform-adaptation principle; no CSS rule, selector or palette value in the sheet itself needed repair, so there was nothing to fix.

**Validation gap:** none — the focused support/theme module run (19 tests, OK) reproduced and confirmed the fix as landed.

### post-merge review of 9bdf3f1d never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9bdf3f1d83383a371ac5ee30cf3114fb2a8e631b` (Refuse a FLOCK_TIMEOUT carrying a recipe-shell metacharacter at make level) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix — settled as no defect. Commit `9bdf3f1d` is merged on main (`git merge-base --is-ancestor` holds), and the guard it added is live in the tree, since refactored: `Makefile:142` still lists FLOCK_TIMEOUT in the `$(foreach …$(call refuse_unsafe_value,…)` refusal set, built from `refuse_unsafe_value` at `Makefile:103` with the same refusal diagnostics. Live probe: `make -n install 'FLOCK_TIMEOUT=x"; evil; "'` fails at parse time — `Makefile:142: *** FLOCK_TIMEOUT contains a shell metacharacter ('"' in 'x"; evil; "'); …'` with no recipe shell executed — while `make -n install FLOCK_TIMEOUT=5` still yields the digit-guard prefix `set -- "5"` unchanged. The commit's test still exists, since moved: `tests/test_make_refusals.py` `test_each_metacharacter_is_refused_in_FLOCK_TIMEOUT` (all four metacharacter subtests) passes under `make check CHECK_TESTS='test_make_refusals'`, and the doc strings at `Makefile:43–46`, `README.md` and `docs/invariants.md` present in the diff match the live text. Nothing in the commit's scope is wrong on main.

**Validation gap:** none — the existing refusal tests and the live `make -n` probes reproduced and confirmed the committed behavior.

### post-merge review of ad6e0b13 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `ad6e0b134f2b9e3b1bc97575a2abea33c5d75084` (Add two synthetic-tree tests naming the scanner's untested dotted-candidate forms) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

No defect. The commit is on main and touches only `tests/test_no_unused_imports.py`. Its two tests are byte-identical to the live tree (`git diff ad6e0b13` against the region, moved to lines 351/387 by later insertion-only hunks that do not touch them), the scanner spelling they pin is still in `tests/support/unused_imports.py::_dotted_candidates` (repository dotted name, import-root mid form, bare stem), and the focused check on `test_no_unused_imports.py` passes — so the tests fail if a scanner change drops the mid or stem candidate forms, and nothing else changed.

**Validation gap:** none — the existing suite reproduces and pins the scanner's candidate forms; nothing was missing.

### post-merge review of 5d0ebdbf never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Settled as no defect. Read the commit's diff on main and verified it against the live tree: the commit only moves an assertion loop out of four Library suites in `tests/test_firefox_theme_library.py` into the new `FirefoxChromeTestCase.assert_arms_match_required` helper in `tests/support/firefox_chrome_cases.py`; the helper's body (`subTest(selector=arm)`, `assertEqual(self.rules[arm], REQUIRED_RULES[arm])`, per-value `endswith("!important")`) is identical to all four replaced loops, it resolves the unqualified `REQUIRED_RULES` in the same `tests/support/firefox_chrome_cases.py` globals the test module imports, and no arm list changed. The two deliberately different sites were left untouched as the commit says (the search field's `property=` subTests and the tree-rules exclusion test), and `grep` confirms `endswith("!important")` now appears only in the helper and those two sites. Focused check: `make check CHECK_PATTERN='test_firefox_theme_library.py'` ran OK (22 tests, including all six `TestFirefoxLibrary*` classes the helper serves).

**Validation gap:** none — the converted Library suites' own assertions cover the helper's equivalence directly, so nothing was missing from confirmation.

### post-merge review of 30be8108 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `30be81086b83ef084215c41c10f8db3819500da4` (Land Library part 6/6: Platinum details-pane fields, menulist, tag selector) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

No defect: settled as a review. Checked the commit's touched files against the live tree — `theme/firefox/org.macos8.desktop/chrome/userChrome.css` still carries all nine `#detailsPane`-scoped arms byte-for-byte at its lines 1540–1568, four line-edit fields, the folder menulist's face and hover arms and the tag selector's face, row and selected-row arms, and the provenance header's narrowed sentences leave no `and the details pane` occurrence in the sheet (`grep` count 0). The only live-tree differences from the commit are later refactors of `tests/support/firefox_chrome_cases.py` (the 5d0ebdbf helper aliases `FIELD_FACE`, `BUTTON_FACE`, `BUTTON_HOVER`, whose byte values equal the recipes this commit wrote) and a wording tweak in `tests/test_firefox_theme_library.py`'s docstring — the details-pane rules and tests are otherwise untouched. Ran `make check CHECK_PATTERN='test_firefox_theme_*.py'`: all five Firefox chrome suites (library, panels, popups, shell, page_info) pass, including `TestFirefoxLibraryDetailsPaneChrome`'s byte-for-byte arm matching and `TestFirefoxChromeShell.test_required_rules`' whole-sheet sweep against the shared `REQUIRED_RULES` table, which exercises the commit's nine entries even after the helper refactor; exit 0.

**Validation gap:** none — the existing suite already reproduced and confirmed the byte-recipes (the nine details-pane arms are pinned byte-for-byte against the shared table by the landed tests); nothing was missing.

### post-merge review of c8ca2ac4 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix:** settled as no defect. Read `git show c8ca2ac4` on main and checked every arm against the live tree: the escape-aware `at_rule_bodies` scan loop (the `escaped` token with its comment) survives intact in `tests/support/firefox_content_cases.py`, where the scanner has since moved, and `TestAtRuleBodies` in `tests/test_firefox_content_theme.py` still imports and exercises that live scanner; the `firefox-content-at-rule-escaped-quote` ledger entry survives in `tests/support/validation_gaps/no_fake.py` (the package has since split into a package directory and `NO_FAKE_BASELINE` has grown with later records, but this record is still present and keyed). Ran the commit's own probe on the touched modules: `make check CHECK_PATTERN='test_firefox_content_theme.py'` and `make check CHECK_PATTERN='test_validation_gaps.py'`, both exit 0 with all their tests OK, including the escaped-quote body test and the no-fake ledger test. Nothing to fix.

**Validation gap:** none — the commit's own tests still run against the live scanner and pass; nothing was missing.

### post-merge review of 9d13d194 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The review never reached a verdict because the reviewer hit its usage limit, so I settled it by reading the diff of `9d13d194f2ab742e9afbce37a6b2710cdfdb211a` (Paint Library downloads list and Clear button as Platinum (part 5/6)) on main and verifying each touched file against the live tree: all five Library downloads arms — the `#placesViewsBox richlistbox#downloadsListBox` face, its square-row and selected-row arms and the `toolbar#placesToolbar toolbarbutton#clearDownloadsButton` base and hover arms — are present unchanged in `theme/firefox/org.macos8.desktop/chrome/userChrome.css`; their byte-recipes match the `REQUIRED_RULES` entries in `tests/support/firefox_chrome_cases.py` (built from the pinned palette constants `WHITE`/`BLACK`/`GREY`/`FACE`/`SELECTION` and `BUTTON_BEVEL` in `tests/support/platinum_palette.py` and `tests/support/gtk_theme_spec.py`) via the shared helper asserted by `TestFirefoxLibraryDownloadsChrome` in `tests/test_firefox_theme_library.py`; the whole-sheet `downloadsListBox` enumeration there stays consistent with `TestFirefoxPanelRows`' `#downloadsPanel`-scoped enumeration in `tests/test_firefox_theme_panels.py`; `docs/invariants.md` carries the cross-referenced downloads-view row; and the header's shortened provenance sentences match the sheet comment text. The focused probe `make check CHECK_PATTERN='test_firefox_theme_*'` ran 19 tests OK (rc=0): nothing to fix.
**Validation gap:** none — the existing suite reproduced and confirmed it; nothing was missing.

### post-merge review of bb60d757 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `bb60d757dd6e6d5733d09559eb968f230d7824be` (paint the Firefox Library toolbar band and menu titles Platinum) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit's diff was read against the live tree. The three landed sheet arms (`toolbar#placesToolbar`, `menubar#placesMenu > menu`, `menubar#placesMenu > menu[open]`) are intact at the end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (the later Library parts of the series appended below them without touching these), the three matching `REQUIRED_RULES` entries live in `tests/support/firefox_chrome_cases.py`, and the palette constants they spell the recipes with match the shipped hexes (`FACE #DDDDDD`, `BLACK #000000`, `ETCH_DARK #888888`, `WHITE #FFFFFF`, `SELECTION #CCCCFF` in `tests/support/platinum_palette.py`); the header's provenance paragraph mentions the toolbar band and its menu titles as the tests require, the `TestFirefoxLibraryToolbarChrome` scoping/provenance tests live in `tests/test_firefox_theme_library.py`, and the two shell-suite menubar-title exclusions the commit made are intact in `tests/test_firefox_theme_shell.py` — they drop only `placesMenu`-scoped rules by id, so any unscoped bare menu-title rule would still land in the assertion set and fail it. The commit's own probe ran green today: `make check CHECK_PATTERN='test_firefox_theme_*.py'` — 19 tests, OK, exit 0, including the byte-match of each `toolbar#placesToolbar`/menu-title arm against its pinned `REQUIRED_RULES` recipe.

**Validation gap:** none — the scoping and byte-recipe tests the commit itself added fail loudly on any drift or stray match in the live sheet.

### post-merge review of b5528367 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `b55283673f4e43a3d318127107a1fe99cd1b6161` (Guard COLOR_SCHEME and keep it out of the id-derivation shell string) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: no defect. Re-read the commit's diff on main and verified every piece against the live tree: the parse-time guard now refuses a shell metacharacter in `COLOR_SCHEME`, `COLOR_SCHEME_NAME` and `COLOR_SCHEME_ID` (Makefile `refuse_unsafe_value` list, since extended with more variables and control-byte refusals), the id derivation still passes the basename to its shell through the exported environment (`name="$$COLOR_SCHEME_NAME"`) and resolves an apostrophe-carrying override correctly (`COLOR_SCHEME="theme/x.z'.colors"` yields `COLOR_SCHEME_ID=x`), a dry-run `make -n uninstall` with the commit's own apostrophe canary value creates no file, the tests moved into `tests/test_make_refusals.py` (`TestShellUnsafeColorScheme`, `TestShellUnsafeColorSchemeName`) and pass in the suite, and docs/invariants.md row ~693 pins the whole guarantee.

**Validation gap:** none — the commit's own canary refusal, the surviving derivation and the moved test classes were all re-verified against the live tree.

### post-merge review of a1dbce37 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `a1dbce3771c394be8536a65c6b330dd97975c1fc` (Paint preferences panes' fields and menulists Platinum (plan part 8)) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. Settled as no defect.

Fix: Verified the commit's diff on main against the live tree. The five new `#mainPrefPane` arms (enabled text field, menulist, and the menulist's `:hover` and `[open="true"]` states) are intact in `theme/firefox/org.macos8.desktop/chrome/userContent.css`; the four pinned recipes and the field/menulist population arms now live in `tests/support/firefox_content_cases.py` with `TestFirefoxPreferencesFieldsTheme` in `tests/test_firefox_content_preferences.py` (moved by later test refactorings); `docs/invariants.md`'s about:preferences fields-and-menulists row pins the palette and provenance. Nothing over-matches per the test population arms: the entries scope to `#mainPrefPane` and `:not([disabled])`, leaving the disabled `#fxaSyncComputerName`, dropdown menupopups and sub-dialogs Firefox's, and no selector or palette drift was introduced by the later merges. `cd tests && python3 -m unittest test_firefox_content_preferences` passes and `make check` ran green (rc=0, no FAILED or ERROR lines).

**Validation gap:** none — the existing suite reproduced and confirmed it; nothing was missing.

### post-merge review of 4710a8fc never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `4710a8fc84723d375e1852c27f9da11417bda88c` (Treat `__all__.extend`/`append` re-exports as entry sources in the unused-import scanner) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit's diff was read against the live tree: the `__all__`-growing-call allowance in `tests/support/unused_imports.py` is intact and only fires on `append`/`extend`/`insert` calls on the bare name `__all__` (assignments and augmented assignments unchanged); all three scanner fixtures the commit added live in `tests/test_no_unused_imports.py` (`test_an_all_extend_call_re_exports_the_import`, `test_an_all_append_call_re_exports_the_import`, `test_an_all_remove_call_keeps_the_flag`) and the module passes (36 tests, OK); the `unused-imports-all-extend-call` no-fake ledger record survived the `tests/support/validation_gaps/` package split and points at that test; `docs/invariants.md` line for the unused-import guarantee names the widened allowance. A scratch synthetic tree reproduced the commit's claimed behavior on main today: `__all__.extend(["os"])` keeps the import, while `__all__.remove("os")` and a bare `os = None` write both still flag.

**Validation gap:** none — the scanner's fixture suite and the repo-wide tree-clean assertion fail loudly on a stale allowance.

### post-merge review of 787a809a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `787a809a70ca20a8b050d86a7b18134bd7828e34` (Rename the four word-swapped test modules to mirror the tool modules they cover) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit's rename is intact on main: all five renamed paths exist (`tests/test_apply_gtk.py`, `tests/test_apply_gtk_errors.py`, `tests/test_apply_gtk_locks.py`, `tests/test_install_firefox.py`, `tests/support/apply_gtk_case.py`); a tree-wide grep over the worktree (everything but `.git`, PLANS-DONE.md and BUGS-FIXED.md) for `test_gtk_apply`, `test_firefox_install`, `gtk_apply_case` and `GtkApplyCase` finds no live reference, so docstrings, docs/invariants.md and the validation-gap ledger point at the current names (the leading ledger strings resolve to `tests/test_apply_gtk.py`, `tests/test_apply_gtk_errors.py`, `tests/test_install_firefox.py` — the ledger regression test in the check would fail on a dangling string); the renamed modules collect and pass — `make check` green, rc=0, no failures, all 313 test modules ran.

**Validation gap:** none — the suite's own references (invariants register, validation-gap ledger, cross-referencing docstrings) fail loudly on a stale module name, and the check confirmed every one was repointed.

### post-merge review of 525cfa27 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `525cfa27600dbc359f5a68852d3739aa48a40b58` (Fix two stale Firefox test-module docstrings whose scope lists lag the series parts landed today) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the full diff on main — no defect. Both docstring claims were true when written and are true of the text now on main: the two touched docstrings (`tests/test_firefox_content_theme.py`, `tests/test_firefox_theme_library.py`) were rewritten again by later landings (`9ad1de128` split the Firefox content tests into shared and per-page modules, `67c95d4f6` corrected the stale scope summaries), so the commit's exact wording is gone, but every claim of the live text was verified against the module it describes. `test_firefox_content_theme.py`'s docstring matches the module's tests (marker, at-rule enumeration, exact palette, hygiene, downloads list rules) and its cross-references resolve — `tests/support/firefox_content_cases.py` exists and `tests/test_firefox_content_{config,preferences,support,networking,telemetry}.py` all exist; `test_firefox_theme_library.py`'s docstring matches the module's test classes (places trees, column-header band, toolbar band and menu titles, search box, downloads list and Clear button, details pane fields/rows/tag selector). The docstrings of the other Firefox test modules (config, networking, preferences, support, telemetry, profile, page_info, panels, popups, shell) state the same split-page scoping, so the commit's "no other module has the same staleness" claim still holds. Both touched modules run green via `make check CHECK_PATTERN=...`.

**Validation gap:** none — the every-claim-against-live-tree check above reproduced the commit's own verification; nothing was missing.

### post-merge review of 2eafd38b never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `2eafd38bef0f2f9942ae7f3613f57c070676e5e5` (Extend the Makefile's recipe-shell metacharacter guard to FIREFOX_PROFILE) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit's guarantee stands on main and was then widened, not weakened: the Makefile's parse-time guard now drives `refuse_unsafe_value` over `DESTDIR XDG_DATA_HOME_ENV HOME FIREFOX_PROFILE FLOCK_TIMEOUT RENDER_OUTPUT COLOR_SCHEME COLOR_SCHEME_NAME COLOR_SCHEME_ID CHECK_PATTERN THEME_ROOT CHECK_TESTS CHECK_PARALLEL` (Makefile line 142), so a `FIREFOX_PROFILE` carrying `"`, `$`, a backtick or a backslash is still refused at make level before any recipe, with the diagnostic naming the variable; the four recipe words `--profile "$(FIREFOX_PROFILE)"` (Makefile 592, 641, 647) and the guard's covered-character set are unchanged from the commit, and docs/invariants.md line 693 records the refusal under the `TestShellUnsafeFirefoxProfile` test. The only drift from the commit's VERIFIED text is the test's home: the class lives in tests/test_make_refusals.py (lines 135-201), moved there by a later refactor that consolidated the parse-time guards, and it pins all four metacharacters on both `install-firefox` and `remove-firefox`, the canary probe (`p"; touch "canary"; echo "` — no canary file after the refusal), and the space-legal `--profile "<path>"` verbatim pass-through (`make -n`).

**Validation gap:** none — the suite's `TestShellUnsafeFirefoxProfile` reproduced and confirmed the guarantee as landed.

### post-merge review of 9bf7b08b never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9bf7b08be6e17f53725ea6e1bd5445d2469bdc12` (Correct column-header provenance: four hidden columns, replaced bottom shadow) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit is prose-provenance rewording plus the new Library column-header arms in theme/firefox/org.macos8.desktop/chrome/userChrome.css. Checked against the live tree and the installed Firefox: the provenance paragraph's “seven sortable treecol columns (four starting hidden="true")” matches `unzip -p /usr/lib/firefox-esr/browser/omni.ja chrome/browser/content/browser/places/places.xhtml` (7 treecols under `id="placeContentColumns"`, 4 carrying `hidden="true"`), and every tree.css paint-chain claim matches `/usr/lib/firefox-esr/omni.ja chrome/toolkit/skin/classic/global/tree/tree.css`: `min-height: max(24px, 1.3em)`, `padding: 0 4px`, `-moz-ColHeader`/`-moz-ColHeaderText` face text, `border-inline-start: 1px solid ThreeDLightShadow` (the divider the arms keep — they declare only background-color/color/border-radius/box-shadow), `box-shadow: inset 0 -1px ThreeDLightShadow` (the inset bottom shadow the arms' box-shadow replaces) and the `-moz-ColHeaderHover`/`-moz-ColHeaderActive` washes alongside `treecol:where([ordinal="1"])` (the divider omission). No “three starting” or “keep … bottom shadow” wording remains in the touched files, and no later commit reworded these spans.

**Validation gap:** none — the suite reproduced and confirmed it; nothing was missing.

### post-merge review of 4b284034 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `4b284034b4ef77ca4b60d63a219c172df5ba4db8` (Refuse a DESTDIR, XDG_DATA_HOME or HOME carrying a recipe-shell metacharacter at make level) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: reviewed the commit's diff against the live tree and found it sound, with the guard since extended (it now also covers `FLOCK_TIMEOUT`, `FIREFOX_PROFILE`, `CHECK_PATTERN` and the other recipe-word variables, per docs/invariants.md:692) and its tests reorganised, not lost — `TestShellUnsafeInstallPaths` now lives in `tests/test_make_refusals.py`. Read the guard in `Makefile` (`shell_unsafe_chars`/`shell_unsafe_in`/`metachar_refusal`, Makefile:77-103) and confirmed its rationale: those values are expanded into double-quoted recipe words where exactly a double quote, `$`, a backtick and a backslash are shell syntax, while spaces and apostrophes stay inert. Ran `make check CHECK_PATTERN='test_make_refusals.py'` (rc=0) and reproduced the commit's manual claim at main's tip: a hostile `"; touch canary; "` `DESTDIR` is refused at parse with rc=2, the diagnostic names the variable, the offending character and the value, and no canary file is created.

**Validation gap:** none — the reorganised suite (`tests/test_make_refusals.py::TestShellUnsafeInstallPaths`) and a manual hostile-`DESTDIR` run reproduced and confirmed the behaviour.

### post-merge review of 064efd1f never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `064efd1f0563a9902ad072df26ba8e3f8b1abea2` (Paint about:preferences XUL radios as the Platinum face and dot) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: audited the commit's diff against the live tree and found nothing wrong. The two userContent.css rules survive verbatim — the unchecked `#mainPrefPane radio:not([disabled]) .radio-check` white face with the 1px black circular ring and the `[selected]` data-URI dot, both `!important`, inside the `about:preferences` block, the dot's black written `rgb(0, 0, 0)` so `TestFirefoxContentTheme::test_palette_is_exact` keeps its exact literal set, with the provenance header comment travelling in the same block. The five `TestFirefoxPreferencesRadioTheme` tests survive intact after the test-module reorganisation into `tests/test_firefox_content_preferences.py` (sheet recipe, pane scoping, pinned palette, dot URI pinning the checkmarks.svg `radiobutton` circle, provenance header), and the invariants row stands at docs/invariants.md. Running the committing tests on the live tree with `make check CHECK_PATTERN='test_firefox_content_preferences.py'` passes with no FAILED line.

**Validation gap:** none — the suite's own `TestFirefoxPreferencesRadioTheme` declaration checks plus `test_palette_is_exact` reproduced and confirmed every claim the diff makes.

### post-merge review of 243b57ce never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `243b57ceada718117f4b649f9dc672c81f80450c` (Add AugAssign `__all__` tests to the unused-import scanner suite) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: the commit is test-only and sound. The live tree at `tests/test_no_unused_imports.py:131` (`test_an_all_augassign_entry_re_exports_the_import`) and `:221` (`test_an_augassign_to_another_name_keeps_the_flag`) carries both added tests verbatim, and the allowance arm they exercise stands at `tests/support/unused_imports.py:117` (the `ast.AugAssign` elif feeding the `__all__`-target check) — the naked-name control still leaves the flag standing, the extend case still re-exports. `make check CHECK_PATTERN='test_no_unused_imports.py'` runs the module with both tests included and passes. Nothing wrong found.

**Validation gap:** none — the existing suite reproduced and confirmed it; nothing was missing.

### post-merge review of 9b709858 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9b70985879c1b765602adc504933a99ec703d997` (Paint the Firefox Library search box as the Platinum line edit) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit painted the Library toolbar's `moz-input-search#searchFilter` as the Platinum line edit through the five `--input-text-*`/`--icon-color` tokens, byte-identical (checked side by side) to the landed userContent.css `moz-input-search#searchInput` recipe. The live tree holds the host rule at `theme/firefox/org.macos8.desktop/chrome/userChrome.css` line 1448 with its provenance paragraph at lines 617–620 (later Library merges appended further rules after it with no conflict), the matching `REQUIRED_RULES["moz-input-search#searchFilter"]` pin in `tests/support/firefox_chrome_cases.py` line 544, the `SEARCH_RULE` Library test asserting it in `tests/test_firefox_theme_library.py`, and the bookmark-panel sheet-wide token check's `name != "moz-input-search#searchFilter"` exemption in `tests/test_firefox_theme_panels.py` line 553 (the panels check would otherwise count a line edit inside the library sheet region as a new panel input). The committing suites (`test_firefox_theme_library`, `test_firefox_theme_panels`, `test_firefox_theme_shell`) pass on the live tree, and they reuse the already-landed `#searchInput` pin so the twin stays in lock-step.

**Validation gap:** none — the rule, its pin, its test and the panels exemption were re-derived from the live tree and the committing suites were rerun; the original review's only gap was that it never ran.

### post-merge review of 9cec3cca never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9cec3ccada22331cc378d4a505a4952f57e2f638` (Share the Firefox test suite's write/unlink-failure fixtures as case helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. The commit added `fail_unlink_to` beside `fail_write_to` in `tests/support/firefox_profile_case.py` (the unlink twin with the same `Path(path) == target` comparison and pass-through `*args`/`**kwargs` as the inline closures it replaced) and converted three `test_firefox_install.py` sites to the shared helpers; none of the converted tests' assertions needs the closure's OSError wording — each pins only the tool's own `cannot write`/`cannot restore`/`cannot remove <path>` stderr messages and file outcomes (checked by reading the converted sites). The four inline closures the commit deliberately left are in the live tree still — three counted/publish-then-raise `flaky_write` copies in `tests/test_install_firefox.py` (the file was later renamed) and one unrelated `write_bytes_atomically` signature site in `tests/test_make_cursors.py` — each with behavior `fail_write_to` cannot express. The Firefox suites (`test_install_firefox`, `test_firefox_profile`, 102 tests) pass on the live tree.

**Validation gap:** none — the pass-through and remaining-closures claims were re-derived from the live tree and the suites were rerun; the original review's only gap was that it never ran.

### post-merge review of 0ae727c4 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `0ae727c4d8ead6b2dcd25a37a57f7cd5df7a36d1` (Sort the unused-import scanner's findings by path, line and name as its docstring documents) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. `git show 0ae727c4` (sort the scanner's findings by path, line, name) checked against the live tree: `tests/support/unused_imports.py` builds `(relative_path, node.lineno, name)` tuples and returns `sorted(findings)` mapped back to `path:line: unused import name` strings, matching the docstring's "sorted by path, then line" promise (the name is only a within-line tiebreaker); the comment's premise holds — `_scan_module` collects a module's imports through `ast.walk` (BFS), so a block-nested import really would trail later top-level ones unsorted; sorting whole-path string-wise preserves the sorted file-walk order the docstring cites. The commit's regression test `test_findings_are_sorted_by_path_then_line` still exists and, with all of `test_no_unused_imports`, passes on the live tree.

**Validation gap:** none — the commit's own ordering regression test reproduced and confirmed the behavior, so no confirmation step was missing.

### post-merge review of 86d18b48 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `86d18b48ffae886baa78caf6e85ccde71c36c19b` (Drop the bare `from . import name` scanner registration as untrue) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. `git show 86d18b48` (drop the unused-import scanner's bare `from . import name` registration) checked against the live tree: `tests/support/unused_imports.py` registers each `ImportFrom` through `_resolved_module()` with no extra bare-form key, so a bare `from . import thing` adds only `("pkg", "thing")` and cannot keep `pkg/thing.py`'s own import alive; both regression tests from the commit still exist (`test_a_package_facade_re_export_keeps_the_submodule_import`, `test_a_bare_relative_import_does_not_bless_the_submodules_import`) and pass on the live tree; the `no-fake` ledger entry `unused-imports-facade-reexport` survived the later packaging split of `tests/support/validation_gaps.py` into `tests/support/validation_gaps/`; the later reviewer merge `725c8d42f` did not remove the commit's registration.

**Validation gap:** none — the already-landed regression tests reproduced and confirmed the behavior, so no confirmation step was missing.

### post-merge review of 8b9a994e never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `8b9a994ea69a16ca70a09c7f193e96e5a3e051c4` (Paint about:preferences XUL check boxes as Platinum squares; fix PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: no defect found. The commit appended two rules to the `about:preferences` at-rule in `theme/firefox/org.macos8.desktop/chrome/userContent.css` — the `#DDDDDD`/1px-black/white-`#888888`-bevel face for `#mainPrefPane checkbox:not([disabled]) .checkbox-check` and the checked box's data-URI SVG glyph (black written `rgb(0, 0, 0)`, keeping `test_palette_is_exact` exact) — plus their pins and a docs/invariants.md row. Checked against the live tree: both rules still stand (userContent.css lines 580 and 588) byte-identical to the commit's diff; the data-URI's decoded path `M 3.5 8.5 L 6.5 11.5 L 12.5 5.5` (2px black, square cap, miter join, 16×16) matches the shipped `theme/desktoptheme/org.macos8.desktop/widgets/checkmarks.svg` `checkbox` glyph, and the invariants row still names the pin set. The later dedupe merge (`0111acd46`) moved the tests from the commit's `TestFirefoxPreferencesCheckboxTheme` in `tests/test_firefox_content_theme.py` to `tests/test_firefox_content_preferences.py` with shared recipes in `tests/support/firefox_content_cases.py` (CHECKBOX_FACE/CHECKBOX_GLYPH/CHECKBOX_GLYPH_URI, the same selectors and URI); `python3 -m unittest test_firefox_content_preferences` from `tests/` runs them all OK. The PLANS.md bookkeeping the commit message claims (moving the landed places-trees entry under `## Done`) was verified by the later 4c097fb2 settlement; nothing in the diff harms the scope, palette or keyboard principles.

**Validation gap:** none — the committing test class reproduces and confirms every pin, and the migrated suite still runs it.

### post-merge review of 4c097fb2 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `4c097fb2c34df6879ad6d63e1ef2915f449c18d6` (Paint Firefox Library places trees as the Platinum list field) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no defect. `git show 4c097fb2` checked against the live tree: the landing appends five ordered rule blocks (`#placesList`/`#placeContent` field face, both trees' shared hover transparent bevel rule, shared selected-row `#CCCCFF`, shared cell-text black, and the single content-tree `multicol, odd` stripe floated back — nine selectors) to `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, byte-matching `tests/support/firefox_chrome_cases.py`'s `REQUIRED_RULES` entries (verified by reading both files at the appended region), which is the landed `#metatree`/`#imagetree` Page Info recipe as the plan states; the selector names name only the two places trees (`tree#placesList`, `tree#placeContent`, both `placesTree` members in `places.xhtml`) so nothing else in the Library window takes the field paint. The provenance paragraph added to the sheet header and the `docs/invariants.md` `## firefox` row present as a platform colour adaptation with no reference screenshot for the Library window, naming the greps' absent reference surface, and adjust no palette value. The commit's tests live in `tests/test_firefox_theme_library.py::TestFirefoxLibraryChrome` with the shared `REQUIRED_RULES` extended, `make check CHECK_TESTS="test_firefox_theme_library test_firefox_theme_shell test_firefox_theme_page_info test_firefox_theme_panels test_firefox_theme_popups"` ran OK on this worktree. Later parts of the same series landed on top (search field, column headers, downloads list, details pane) without conflicting with part 1's nine rules — the appended blocks remain exact.

**Validation gap:** none — the landed suite reproduces and pins the paint (the scoping and exact-declaration tests fail on any drift in the nine selectors or their values), and the commit's own `make check` attests the placement.

### post-merge review of 500f9fde never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `500f9fde6ec0d6e06ad49052a384a78ac145539f` (Unused-import scanner now counts only Load-context reads) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** no defect found. Checked `git show 500f9fde` against the live tree: the read-only surprise is intact — `tests/support/unused_imports.py`'s `_scan_module()` still counts only `ast.Name` nodes whose `ctx` is `ast.Load` (assignment, loop, walrus and `del` targets fall through the `__all__` branch harmlessly, their `targets` list stays empty and the loop `continue`s), and a `os = os.sep` Load keeps the import. Later merges gently extended it: `86d18b48f` dropped the untrue `from . import name` registration, `0ae727c4d` sorted the findings, `4710a8fc8` treated `__all__.extend`/`append/insert` re-exports as entry sources, and reviewer fix `725c8d42f` added further assignment and noqa false-negative repairs — all within the Load-only read-board. Both of the commit's fixtures survive in `tests/test_no_unused_imports.py` (`test_a_reassignment_of_the_imported_name_keeps_the_flag`, `test_a_del_of_the_imported_name_keeps_the_flag`, plus the later loop-and-walrus fixture), and the no-fake ledger carries the `unused-imports-reassignment-as-read` reproduction under `tests/support/validation_gaps/` (packaged since the original `tests/support/validation_gaps.py` was split).

**Validation gap:** none — the focused `make check CHECK_TESTS=test_no_unused_imports` (36 tests, OK) reproduces and pins the settled behavior.

### post-merge review of 22feeb3c never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `22feeb3c5460430d08c3db584af8e758ba8b1849` (Hold the data-home lock across apply-cursor's installed-theme check, ~/.icons link and selection) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** no defect found. Checked `git show 22feeb3c` against the live tree: the commit's behavior survives two later merges — `apply_cursor.py` no longer carries the lock itself, because `938d4ac36` (Serialize cursor removal with apply on the data-home lock) moved it into `tools/cursor_workflow.py`, where `apply()` still checks `cursor_link.require_installed` before taking `installed_data_lock` on the data home, re-checks the theme under the lock, keeps it through `install_link` and `selection`, and uses the same bounded `LOCK_TIMEOUT = 60.0` via `tools/file_lock.exclusive_flock`; `remove()` also takes the lock (the later commit's extension), and the exit-status docstring still names the data-home lock. The commit's tests survive as `tests/test_apply_cursor_locks.py` (`TestDataHomeLock`, four tests, OK) and the `docs/invariants.md` cursor-selection row pins the lock guarantee with that test reference.
**Validation gap:** none — the existing replay of `tests/test_apply_cursor_locks.py` reproduced the settled guarantee and only the verdict was missing.

### post-merge review of d2cd2c6b never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `d2cd2c6b6b26d7e985307c07250006c9fb483688` (Paint about:preferences pane buttons as Platinum push buttons) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix.** Settled as no defect by re-reviewing the commit against the live tree. The two `#mainPrefPane button:not(.arrowhead):not([disabled])`/`:hover` rules in `theme/firefox/org.macos8.desktop/chrome/userContent.css` (lines ~566–580) match the commit's diff byte-for-byte: `#DDDDDD` face, black text, 1px black outline, `border-radius: 0`, `inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` bevel on the base rule, and flat `#CCCCFF` with `box-shadow: none` on hover — the same recipe the commit's tests pin for userChrome's push buttons. Scope is intact: both selectors stay `#mainPrefPane`-prefixed, exclude the six `.arrowhead` disclosure arrows, exclude `[disabled]`, and leave the `#dialogTemplate` overlay, sidebar, `categories` and button geometry untouched. The two `TestFirefoxPreferencesPushButtonsTheme`-era rules the commit added to `tests/test_firefox_content_theme.py` live after the file split in `tests/test_firefox_content_preferences.py::TestFirefoxPreferencesPushButtonsTheme` and the `docs/invariants.md` row points at that post-split home; the pane intent, header-provenance naming and pinned palette (`FACE`, `BUTTON_SHADOW`, `SELECTION`, `WHITE`, `BLACK`) hold. The plan bookkeeping in the commit (PLANS.md entry moved to PLANS-DONE.md with the appended done stamp) checks out in the archives. Dependency on no reference screenshot is recorded in the invariants row (platform colour adaptation). No defect found.

**Validation gap:** none — the commit's own declaration tests (now in `test_firefox_content_preferences.py`) reproduce and confirm the rules, and the bar is a CSS declaration match, not a rendered pixel, so nothing was missing beyond a Firefox render.

### post-merge review of f49ae710 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `f49ae710ff1b16367b0a9df2e8e7552b19679e48` (Fix the unused-import scanner dropping annotated `__all__` assignments) never reached a verdict.

**Fix:** settled as no-defect. Re-read the commit's diff and verified every claim against the current tree, which has moved on since Oct 27: the one-line scanner fix (`elif isinstance(node, ast.AnnAssign) and node.value is not None: targets = [node.target]`) is present in `_scan_module()` at `tests/support/unused_imports.py:119`, correctly guarded so a bare `__all__: list[str]` declaration (no value, no strings) still contributes nothing to the re-export allowance; the two fixtures the commit added survive as `tests/test_no_unused_imports.py::TestNoUnusedImports::test_an_annotated_all_entry_re_exports_the_import` and `::test_an_annotated_all_declaration_without_a_value_keeps_the_flag`; and the required no-fake ledger record survives the later split of `tests/support/validation_gaps.py` into a package as `unused-imports-annotated-all` in `tests/support/validation_gaps/no_fake.py` (the ledger file the diff named no longer exists at that path). All 36 tests in `tests.test_no_unused_imports` pass under `make check CHECK_TESTS=test_no_unused_imports.TestNoUnusedImports`.

**Validation gap:** none — the commit's own two fixtures reproduce and confirm the annotated-`__all__` behavior; only the verdict was missing.

### post-merge review of 273bb60a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `273bb60ae3842c349afc18e6f7dd0666af2704a9` (Hand DESTDIR to the apply refusals via `export` + `$$DESTDIR`, not expansion) never reached a verdict.

**Fix:** settled as no-defect. Re-read the commit diff and re-verified every claim against the current tree, which has moved on since Oct 27: the per-target refusals are now factored into one shared `refuse_destdir` macro (Makefile line ~419) that reads `$$DESTDIR` from the exported value and names it verbatim in the diagnostic; `export DESTDIR` still sits near the Makefile top; the macro covers all four apply targets (`apply`, `apply-plasma`, `apply-gtk`, `apply-cursor` — confirmed by grep), so every caller-chosen staging value reaches the refusal as an environment read, never as make expansion. An outside-the-suite probe with a hostile `"; touch <canary>"` value ran no injected command (scratch dir stayed empty); the tree additionally refuses any metacharacter-carrying DESTDIR at make parse time (`refuse_unsafe_value`, Makefile line ~139, DESTDIR in the guarded list), a later hardening that makes the canary doubly unreachable. The canary tests the commit added survive in `tests/test_apply_theme.py::TestMakeApply::test_a_hostile_DESTDIR_value_is_refused_without_running_its_shell` and the `tests/support/apply_target_cases.py` mixin used by `TestMakeApplyGtk` and `TestMakeApplyCursor` (reworded by that hardening to expect the parse-time refusal; both they and the plain nonempty-DESTDIR refusal tests pass). No tool reads DESTDIR from the child environment except `tools/render_session.py`, which drops it along with WAYLAND_DISPLAY/DISPLAY/MAKEFLAGS before spawning the session — grep over `tools/` confirms it is the only match.

**Validation gap:** none — the commit's own canary tests reproduce and confirm the injection refusal; only the verdict was missing.

### post-merge review of 9ea1e0e5 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Settled as no-defect. The commit only adds a test pinning read_gaps' prose-wins-over-bullet precedence, and the current tree matches its claims: the pinned test `test_a_prose_line_with_a_trailing_bullet_tag_is_read_once_as_prose` exists in tests/test_validation_gaps.py, and the scanner (now the package at tests/support/validation_gaps/reader.py, not the single tests/support/validation_gaps.py file the diff names) matches PROSE_GAP first and `continue`s past the BULLET_GAP search, so a hybrid prose-plus-bullet line yields exactly one prose record with the prose tag. `python3 -m unittest test_validation_gaps` run from tests/ passes.

**Validation gap:** none — the existing suite reproduced and confirmed the pinned precedence behavior; nothing was missing.

### post-merge review of 759593cd never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Settled as no-defect. Read the commit's diff on main and verified every claim in the current tree: the about:preferences search-field rule (`moz-input-search#searchInput` setting only the five `--input-text-*`/`--icon-color` custom properties with `!important`) is present in `theme/firefox/org.macos8.desktop/chrome/userContent.css` inside the existing `@-moz-document url("about:preferences")` block; the suite lives on since the merge in `tests/support/firefox_content_cases.py` (`SEARCH`/`REQUIRED_PREFERENCES_RULES`, same five token declarations in order) with the four `TestFirefoxPreferencesSearchTheme` tests in `tests/test_firefox_content_preferences.py`; and the matching `docs/invariants.md` firefox row names the current test module. The later surface-button infill (`#mainPrefPane button` rules) after the search rule in the same block is later merges' work, not this commit's. `tests/test_firefox_content_preferences.py` and `tests/test_firefox_content_theme.py` pass.

**Validation gap:** none — the existing suite (rule exact-set, token-scoping, provenance and palette tests) reproduces and confirms everything the commit claimed.

### post-merge review of a7ebee69 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

No defect: the commit's split is intact and its claims hold in the current tree — the modules were since renamed (`test_gtk_apply.py` → `tests/test_apply_gtk.py`, fault and lock arms → `tests/test_apply_gtk_errors.py` and `tests/test_apply_gtk_locks.py`, shared fixture → `tests/support/apply_gtk_case.py` keeping the required `ApplyGtkTestCase` name), and no stale `test_gtk_apply`/`gtk_apply_case` reference remains in tests/ or tools/; docs/invariants.md rows 360–362 and tests/support/validation_gaps.py point at the current names, and all three renamed modules pass together.
**Validation gap:** none — the suite covered the split itself; only the post-merge verdict was missing.

### post-merge review of 07818902 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `07818902d67a2c08ee786523758d08611bb82956` (Revise the clock.svg plan: fix SVG counts, hand-cap geometry, hint-id names) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no-defect against the current tree 2026-11-09. Verified each objection: the package ships 31 `widgets/` SVGs (`ls | wc -l`) with clock.svg present; the SVG header says ten hint ids (six rotation-center + four shadow-offset) and quotes the east id as `hint-hands-shadows-offset-to-east`, matching the installed plasmoid's `main.qml:98`; recomputed the hand caps (hour 54+2=56, minute 86.5+1.5=88, second 87+1=88 — each equals its rect's lower edge; tails are pivot−12); `tests/test_desktoptheme_clock.TestClock` (6 tests, OK) and the touched canvas/install pins in `tests/test_desktoptheme` pass; `README.md`, `docs/invariants.md` and the archived Goal carry the corrected thirty-one count. `make check` green after the move.

**Validation gap:** none — the commit's own test module reproduces and confirms every claim the review questioned.

### post-merge review of 2f8f7f05 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `2f8f7f056a00a4b5480e31613eb065fc8a869013` (Share Firefox chrome provenance bundles as two FirefoxChrome constants) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Validation gap:** none — the moved suites themselves confirm it; nothing was missing.

**Fix:** settled as no-defect. Read the diff on main and checked the settled tree: `VIEWITEM_REFERENCES` (2 entries) and `BUTTON_REFERENCES` (3 entries) exist in `tests/support/firefox_chrome_cases.py` with accurate per-suite call-site counts in their comments; the 16 unpack sites (12 viewitem, 4 button) each replace the identical literal strings one-for-one (confirmed against the diff's deleted/readded lines), so every rendered provenance header stays byte-identical; the three headers' referenced test IDs (`TestViewItem`, `TestButton`, `TestButtonReference`) still exist in the desktoptheme test files; and the five affected suites (`test_firefox_theme_shell`, `_page_info`, `_panels`, `_popups`, `_library`) all pass under `make check`. The untouched literal leftovers (library suite, popups' button pair) remain as the commit's RISK describes.

### post-merge review of ee71c614 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `ee71c6147138acf6165958ea383081d1e48fd575` (Fix unused-import scanner's re-export pass to match the imported name, not its alias) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and re-verified its behavior at tip. The diff teaches the scanner's re-export pass (`tests/support/unused_imports.py`, the `imported_from` accumulation) to record `(resolved module, alias.name)` — the name the statement imports, never the `as` alias — skipping `import *`, while the flagging loop keeps `_alias_names()` for a module's own bound names, so `from pkg.mod import os as platform` keeps mod.py's `import os` and an alias onto a different name no longer blesses a dead one; module resolution goes through `_resolved_module`, so a facade's relative `from .x import y` still registers as `pkg.x`. Checked the two added fixtures (`tests/test_no_unused_imports.py::TestNoUnusedImports::test_an_aliased_import_from_here_keeps_the_imported_name` and `test_an_aliased_import_keeps_only_the_name_actually_imported`) and the raised `NO_FAKE_BASELINE` with its `unused-imports-aliased-reexport` ledger entry in `tests/support/validation_gaps/no_fake.py`; the fix survived f87abc9a's later single-walk restructure and later commits layered without reopening it. Reproduced the claimed pre-fix behavior with a scratch copy of the scanner patched to record `alias.asname or alias.name` on the two synthetic trees: it flags `pkg/mod.py:1: unused import os` in the aliased re-export case and wrongly stays clean in the mirror case, while the shipped code passes both fixtures. Ran the scanner and ledger suites through `make check CHECK_TESTS="test_no_unused_imports test_validation_gaps"` (exit 0, 73 tests, OK), including the repository-tree-clean assertion. No defect found.

**Validation gap:** none — the scanner suite's synthetic-tree fixtures reproduce both directions of the alias matching, so the tree-clean and mirror assertions confirmed the delivered behavior; nothing was missing.

### post-merge review of f87abc9a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `f87abc9a141e0aa2edff1181c96439f9debae330` (Walk each module once in the unused-import scanner instead of four times) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and re-verified its behavior at tip. The diff replaces the scanner's four per-need `ast.walk` passes with one walk per module (`tests/support/unused_imports.py::_scan_module`) that collects the import statements with their bound names, every read `ast.Name` id and every `__all__` string entry, and folds the `imported_from` pairs in the same file pass; findings stay one `"path:line: unused import name"` string, sorted so the single walk's breadth-first import order cannot reorder them. Checked the delivered state at tip: `_scan_module` still guards all three collections in one walk, and later commits (`ee71c614` — the `imported_from` pairs taken from the imported name rather than its alias, plus relative-module resolution and `__init__.py` facade re-exports; ctx-aware reads and `__all__` append/extend/insert growth) layered on top without reopening the walk. Reproduced the commit's equivalence claim: reconstructed the pre-f87abc9a four-walk scanner verbatim from the diff and ran both on a synthetic tree covering noqa comments, `__all__` entries, a cross-module re-export, read imports and dead imports — findings byte-identical (the new scanner flagged nothing the old one missed: `tests/dead.py:1: unused import sys`, `tests/consumer.py:4: unused import json`, with the read, `__all__`-exported and noqa-marked imports kept). Ran the scanner suite through `make check CHECK_TESTS=test_no_unused_imports` — all 36 tests OK, including the repository-tree-clean assertion the single walk feeds. No defect found.

**Validation gap:** none — the scanner suite's synthetic modules reproduced and confirmed every finding surface the rewalk touched; nothing was missing.

### post-merge review of 477a7f05 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `477a7f05df172946b1cadf3bdf94ba9c5bc4226b` (Refuse a CHECK_TESTS spec naming no tests/&lt;module&gt;.py with a Makefile guard diagnostic) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and re-verified its behavior at tip. The diff adds only a Makefile guard segment to `require_check_tests` and four tests in `tests/test_make_check.py::TestCheckPattern`; the guard splits the whitespace-stripped CHECK_TESTS value into specs, takes each spec's module component (the text before the first `.`), refuses with exit 2 naming every spec with no `tests/<module>.py` file, and leaves valid specs untouched. Later commits layered a charset check onto the same line without touching this segment. Reproduced the documented refusal (`make check CHECK_TESTS=test_no_such_mod` prints `check: CHECK_TESTS must name test modules in tests/, but these specs name no tests/<module>.py file: test_no_such_mod` and exits 2) and ran the commit's four tests through `make check` — all OK. No defect found.

**Validation gap:** none — the commit's own four-test regression suite reproduced and confirmed the guard's behavior; nothing was missing.

### post-merge review of 43c0fe7a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `43c0fe7a03a8b59bc8b4ec11460dd2a1d77183d7` (Ship widgets/timer.svg with tested Timer LCD digits, registered) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and found the delivered state sound, with one cosmetic defect now repaired. Checked the shipped `theme/desktoptheme/org.macos8.desktop/widgets/timer.svg` against the archived plan: exactly the twenty-two KDE-required ids in canvas order (`0`–`9`, `0_1`–`9_1`, `separator`, `separator_1`); the ten alert-row digits offset by (16·i, 32) from the normal-row segment endpoints a–f; the per-digit lit sets match the plan's table verbatim (re-derived digits 0 and 8 by hand against their shipped `d` attributes); the 2px square-capped stroke-only paths and the invisible 16x32 bounds rects; both separators the two 8x32 colon-dot circles at (164, row+10)/(164, row+22); the colour split (normal-row digit strokes and `separator` dot fills `#000000` from `ForegroundNormal`, the `_1` row's digit strokes and `separator_1` dot fills `#CC0000` from `ForegroundNegative`); the header comment naming the consumer, the alert suffix, the missing reference surface and the two colour tokens. Checked the registration and pinning: `tests/test_desktoptheme.py` carries the `SVG_CANVASES` row (`timer.svg`, 168x64) and the install-manifest entry; `tests/support/desktoptheme_paths.py` pins `TIMER_SVG`; `docs/invariants.md` carries the desktoptheme row citing `TestTimer` with the provenance exception; README.md names the file. The one defect was a duplicated, mislabeled comment (`Digit 0, alert state …`) sitting before `separator_1` while `g id="0_1"` lost its own comment — comment-only, no effect on the drawn art; moved above `g id="0_1"`. `TestTimer` and the desktop-theme registry/install suites pass in the project's check (`make check CHECK_TESTS="test_desktoptheme_timer test_desktoptheme"`, exit 0, 26 tests, OK).

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled state is confirmed by reading the diff against the shipped SVG's ids and segment paths plus the timer and desktop-theme modules passing in the project's check (`make check CHECK_TESTS="test_desktoptheme_timer test_desktoptheme"`, exit 0, OK).

### post-merge review of 1ce49353 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `1ce4935304196e3f57c18295409fe3ac337f05a1` (Pin reproduction_for's no-borrow refusal and any-marker matching in test_validation_gaps) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and found no defect. The commit only adds `TestReproductionLookup` to `tests/test_validation_gaps.py` with two tests that genuinely pin the branches the commit's WHY names in `tests/support/validation_gaps/ledgers.py`: `test_a_foreign_tag_borrows_no_ledger_entry` builds its record's subject from `NO_OBSERVABILITY_REPRODUCTIONS[0].markers[0]` with the `slow-check` tag, so `_lookup` searches only `slow-check`'s ledger and must return `None` — a tag-ignoring or cross-ledger-lending lookup would instead find the no-observability entry, so the no-borrow guarantee is directly pinned; and `test_any_single_marker_of_an_entry_identifies_its_record` installs a synthetic two-marker ledger (restored via `addCleanup`) whose record cites only the second marker, pinning `_lookup`'s `any(...)` matching and entry identity. The implementation matches the commit's claims: `_lookup` matches with `any`, `reproduction_for` resolves only the record's own tag from `LEDGERS`, and the `slow-check` ledger is one of the six the module docstring lists. Both new tests pass under the project's check (`make check CHECK_TESTS="test_validation_gaps"`, exit 0, OK).

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled state is confirmed by reading the diff against `ledgers.py` plus the new lookup tests passing in the project's check (`make check CHECK_TESTS="test_validation_gaps"`, exit 0, OK).

### post-merge review of 3241768a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fixed: settled as no defect. Re-read the `3241768a` diff on main against its archived PLANS-DONE.md plan entry (sticky-note papers): the delivered set matches — `theme/desktoptheme/org.macos8.desktop/widgets/notes.svg` is a 320x32 canvas holding the ten `<colour>-notes` groups (white, black, red, orange, yellow, green, blue, pink, translucent, translucent-light) in `configAppearance.qml`'s `view.model` order, each an invisible full-cell bounds rect plus one flat 31x31 paper rect at `(cell+0.5, 0.5)` inside a 1px `#000000` stroke, with the two translucent papers the only `fill-opacity` carriers; `tests/test_desktoptheme_notes.py` pins exactly that (ids, order, per-paper fills and opacity, geometry) and `tests/test_desktoptheme.py` registers the canvas and the install/uninstall path; `docs/invariants.md` gains the desktoptheme row with the KDE-required-ids and not-sampled provenance note; README.md names the file; PLANS.md keeps `## Planned` without the notes entry; PLANS-DONE.md archives the plan once. Nothing in the diff was wrong, so nothing to fix.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled state is confirmed by reading the diff against its plan archive plus the two desktop-theme modules passing in the project's check (`make check CHECK_TESTS="test_desktoptheme_notes test_desktoptheme"`, exit 0, 28 tests, OK).

### post-merge review of 9c34d34a never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `9c34d34a806d8d30396dd4f28aeae390b280daf2` (Share the Aurorae box inactive-flattening rule in one aurorae_fixtures helper) never reached a verdict. Settled as no-defect: the diff was checked against the commit's claims — the shared `inactive_fill` helper in tests/support/aurorae_fixtures.py expresses exactly the rule the removed copies pinned (its keep-set `ETCH_DARK`/`BOX_INNER_OUTLINE` is `#888888`/`#222222` in support/platinum_palette.py, its flatten target `INACTIVE_GREY` is `#CCCCCC`, byte-for-byte the literals the old inline copies used), the helper parses cleanly, and its one live consumer (tests/test_kvantum_svg.py `TestMdiButtons._expectation`, the disabled-state flattening) applies the identical mapping. The second consumer the commit named (tests/test_aurorae_buttons.py) has since been removed on main by the 2026-11-04 inactive-art direction — the inactive Aurorae groups now ship no box art at all — so `inactive_fill` outlives that caller by design, not defect; no re-dedupe or follow-up is warranted.

**Validation gap:** none — the suite reproduces and confirms the rule: both consumer modules pass under the project's check (`make check CHECK_TESTS="test_aurorae_buttons test_kvantum_svg"`, exit 0, 28 tests, OK).

### post-merge review of ee83d1d6 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `ee83d1d60f978a60fd36fdd28e03dfdfcdf7a13e` (Add tests/test_file_lock.py pinning the shared flock's retry and release arms) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: read the commit's diff on main and found no defect. The commit only adds `tests/test_file_lock.py` plus one `docs/invariants.md` row. The three tests it adds genuinely pin the arms they claim in `tools/file_lock.py`: the EINTR test patches `fcntl.flock`, which the module calls at attribute level, and asserts one interruption then a clean reacquire; the contention test holds a real `LOCK_EX` from another thread and releases after four `POLL_SECONDS` intervals so the waiter's bounded loop must acquire; the release test raises inside the body and reacquires, pinning the `finally` close. The module's `_wait_for_flock_error` retries EINTR without sleeping and treats only `EACCES`/`EAGAIN` as contention, matching the tests. Later merges have grown the module to six tests (a repeated-interruption deadline test and a `TestParentDirLock` pair); all six pass under `make check CHECK_TESTS=test_file_lock`, and the invariants row names exactly `tests/test_file_lock.py::TestExclusiveFlock`.

**Validation gap:** none — the existing suite reproduced and confirmed it; nothing was missing

### post-merge review of 37c08ac3 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `37c08ac30c9e3986f43d107fe153fce38fa6982d` (Move the GTK 3 pixel tests into child interpreters so the suite process never imports gi) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no-defect. Read the commit's full diff on main and re-verified its claims against the current tree: every `import gi` grep hit under tests/ and tools/ sits inside a string constant (the `-c` child programs of tests/test_gtk_theme.py, tests/test_gtk_theme_controls.py, tests/test_gtk_view_census.py and tests/test_gtk4_theme.py, and the literals of tests/test_no_gtk_introspection.py), so no module imports GTK introspection in-process; the AST detector `tests/test_no_gtk_introspection.py` is present and grew since the commit, and its module passes (`make check CHECK_TESTS=test_no_gtk_introspection`: OK, 7 tests); the ported GTK 3 pixel suite passes (`make check CHECK_TESTS=test_gtk_theme`: OK, 70 tests) with its two child-interpreter programs line-for-line mirrors of the prior in-process bodies per the diff; and the commit's docs/invariants.md row for the no-in-suite-gi invariant is present.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled state is confirmed by the child-vs-in-process grep plus the detector and GTK 3 pixel suites passing in the project's check.

### post-merge review of 57acd489 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `57acd4892fd2327ac31860fea97231006a5fa9e9` (PLANS.md: remove the duplicated notes-paper plan entry under Planned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no-defect. Read the commit's full diff on main and re-verified its claims against the current tree: `grep -n '^### '` over PLANS.md `## Planned` shows exactly one desktoptheme notes-paper entry and no duplicate (the Firefox prefs-panes plan sits archived under PLANS-DONE.md `## Done`, so the gate cannot reread it as new); the commit also carried the feature work its revision had bundled — the about:preferences `:root`/`.subcategory` rules in `theme/firefox/org.macos8.desktop/chrome/userContent.css`, their tests in `tests/test_firefox_content_theme.py` and the matching `docs/invariants.md` row updates — and those shipped tests pass on the current tree (`make check CHECK_TESTS=test_firefox_content_theme`: OK). The commit message's "nothing outside the backlog file changed in this run" sentence understates the bundled Firefox changes, but the changes themselves are sound and tested; no defect in the merged state.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled state is confirmed by the PLANS.md heading grep plus the shipped Firefox content-theme tests passing in the project's check.

### post-merge review of 37894f9d never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `37894f9dd3c0bcdce5d54cfa5df9e6060f4f25e0` (Move the register-checker helpers into tests/support/) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: settled as no-defect. Read the commit's full diff on main and re-verified its claims against the current tree: no live `from invariants`/`from placeholders` import remains anywhere under `tests/`; both register checkers import and parse at their new `support.` paths (`tests/support/invariants.py`, `tests/support/placeholders.py`); the only old-path strings left are the ledger `Reproduction` markers (`tests/support/validation_gaps/no_observability.py:67`, `no_fake.py:174` and `:186`) and the synthetic one-line-bullet fixture (`tests/test_validation_gaps.py:55`) that quote the BUGS-FIXED.md archive headings (e.g. its lines 3199 and 3225) byte-for-byte as history, exactly as the commit's self-check argued; and the shared-guard READERS list, the Makefile comment, the suite-discovery docstring and the README/PLANS/invariants/PLACEHOLDERS mentions were all updated consistently.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled commit's claims are confirmed by a tree-wide grep plus direct imports of both moved checkers at their new paths.

### post-merge review of c7957cd9 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `c7957cd902ff2ed142a22ea29941118bd207d3dd` (Escape the reference checker's printed problem list for the terminal) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix (2026-11-09):** The commit checked out as sound. It is an ancestor of main and its fix survived: the only production consumer of `check_references`' problem list is `tools/check_references.py:main`, which prints each problem through `tools.terminal.escape_controls` at its single print site (line 91); every other path-bearing problem line in `tools/reference_validation.py` either escapes explicitly (`escape_controls(str(path))`) or embeds the contributor-supplied filename as `{filename!r}`, whose repr escapes control characters — the one raw channel is the `str(exc)` read-refusal text, which the print-site escape covers. The guarantee is pinned by `docs/invariants.md` (the checker's tooling row, 2026-11-09 expanded with a second guard test) and its guard tests pass in the project's check. A scratch reproduction re-confirmed both directions: with `cli.escape_controls` stubbed to identity, a FIFO-swap refusal named a `chr(27)`-carrying path with the raw ESC byte in stderr; with the real print path, the same refusal shows the `\u001b` form only.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled commit's claims are confirmed by the existing suite (both `TestProblemListEscaping` guard tests pass) plus the scratch reproduction naming the raw-ESC direction above.

### post-merge review of 0491add1 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `0491add1e13bbaf23532b4746958ab1a4a8a3e69` (Fix two broken test references in userChrome.css's provenance comments) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Verdict: no defect, reviewed on main where the commit is an ancestor. Both provenance-comment edits stand on main: `theme/firefox/org.macos8.desktop/chrome/userChrome.css` now cites `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` in the file's dominant `path::Class.method` style (16 occurrences of that exact citation; no `*.py::test_...`-without-qualifier reference remains in theme/, docs, tools or the markdown roots), and that test is real (`class TestReferenceAnchors` at line 33, `def test_selection_background` at line 123 of `tests/test_colorscheme_reference.py`, which `tests/support/platinum_palette.py` and `tests/support/firefox_content_cases.py` also cite). The test-pinned substrings the commit's RISK note worried about (`"TestReferenceAnchors.test_selection_background"` and `"test_selection_background"` in `tests/test_firefox_theme_shell.py`'s required-names list) still match the edited lines. The comment-only change alters no selector, declaration or at-rule; the doubly-qualified `*.py::Class::test_...` forms found today in gtk.css (e4bb3752) and userChrome.css (bb60d757) postdate this commit and carry their own reviews.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled commit's claims are confirmed by the existing suite (`make check CHECK_TESTS='test_firefox_theme_shell test_colorscheme_reference'` passed, including the required-rules substring pins for the edited provenance comments).

### post-merge review of 6a3d99ab never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `6a3d99ab7017249f508cb37e06acba288507b057` (Ship the `mdi` window-button art for the QMdiSubWindow title band) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Verdict: no defect, reviewed on main where the commit is an ancestor. Re-checked the commit's own RISK-note items: all eight `mdi-*` SVG groups sit on the 60px grid (translate(10,24970..25390), 12×12 cells whose last cell ends exactly at its committed canvas bottom), the `[TitleBar]` `indicator.element=mdi`/`indicator.size=12` keys and the provenance comment on main match the plan, and a scratch rect-by-rect comparison re-derived `mdi-close-normal`'s 12×12 region from Aurorae `close.svg`'s `active-center` with zero differing pixels; the disabled group changes only face pixels, all to `#CCCCCC`, keeping the `#888888`/`#222222` outlines. `make check CHECK_TESTS='test_kvantum_svg test_kvantum_config_elements test_aurorae_buttons'` passed, including `TestMdiButtons`' three tests that pin the art against the live Aurorae fixtures (which also verify the minimize/maximize/restore mappings) and `test_titlebar_names_the_mdi_indicator`. Rendered Qt pixels remain unclaimed (the comment's own caveat stays) and are the same accepted limitation recorded in docs/invariants.md's QMdiSubWindow row.

**Validation gap:** none — there was no failure to reproduce: the review aborted before it could name one, and the settled commit's claims are confirmed by the suite's existing `TestMdiButtons`/`TestTitleBarSurface` pins plus a fresh rect-by-rect re-derivation of the close art against the Aurorae fixtures (the declared, unresolved part — rendered Qt pixels in a live session — stays an accepted limitation under docs/invariants.md's QMdiSubWindow row).

### post-merge review of 39b3984f never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `39b3984f6ee0f273eef64a513c05da673c96d884` (Share ihdr_end/with_ihdr_byte's IHDR unpack in one png_fixtures helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Reviewed the commit's full diff and its helper's state on main. No defect: the arithmetic is behavior-preserving — `_ihdr_payload_span` returns `start = len(_PNG_SIGNATURE) + 8` (= 16) and unpacks the length from `data[start - 8 : start - 4]` (= `data[8:12]`), exactly where both original call sites read it, so `ihdr_end`'s `start + length + 4` still equals the old `start + 8 + length + 4` and `with_ihdr_byte`'s payload start is still 16 (short-input slices now raise the same `struct.error` as before; no exception-type change). A grep of `tests/support/png_fixtures.py` shows `_PNG_SIGNATURE` and the IHDR-length `struct.unpack` appear only inside the helper, and its docstring's claim of exactly two callers still holds (`ihdr_end` line 84, `with_ihdr_byte` line 287). `make check CHECK_TESTS='test_png_fixtures test_png_chunks'` ran OK (58 tests), covering both call sites' pinned behavior.

**Validation gap:** none — the settled commit's own tests reproduce and confirm its claims.

### post-merge review of 1a67eb30 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `1a67eb30f521acff177d3687b7be4401550b156e` (Paint the Firefox prefs sidebar separators as the Platinum etch) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Reviewed the commit's full diff and its state on main. No defect: the `#nav-separator` etched pair and the two `--page-nav-*` override rules still sit in `theme/firefox/org.macos8.desktop/chrome/userContent.css` (lines 537-546) inside the `about:preferences` `@-moz-document` block, the `ETCH_DARK = "#888888"` token still lives in `tests/support/platinum_palette.py`, and docs/invariants.md line 105 still pins the three separators with their lineage. The commit's tests were later moved intact from `tests/test_firefox_content_theme.py` into `tests/test_firefox_content_preferences.py::TestFirefoxPreferencesNavTheme` by the content-module split; the class still pins the etched separator pair and the header provenance, and `make check CHECK_TESTS='test_firefox_content_preferences test_firefox_content_theme'` passed.

**Validation gap:** none — the settled commit's own tests reproduce and confirm its claims.

### post-merge review of 4e43a636 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `4e43a6362f33f2fa06eda7fe6901ea4f8aba8174` (Serialize an apply-gtk selection on the data-home lock make install/uninstall hold) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fixed: read the commit's diff and its state on main — no defect. The change's claims still hold: `tools/apply_gtk.py::_apply_selection` checks both installed sheets before locking, then takes the data-home flock (`tools/file_lock.py::installed_data_lock`, the same inode `Makefile`'s `run_locked` install/uninstall targets hold for their whole run), re-checks the sheets under it and keeps the lock through `_config_lock` and the selection write, so an uninstall cannot remove the sheets between check and write and a missing sheet returns exit 1; the commit's `_exclusive_flock`/`_data_lock` helpers were later factored into `tools/file_lock.py` (`exclusive_flock`, `installed_data_lock`, `parent_dir_lock`) without changing the behavior. README still documents the data-home lock at line 126 and `docs/invariants.md:359` still pins the guarantee. `make check CHECK_TESTS='test_apply_gtk_locks test_apply_gtk test_apply_gtk_errors'` ran OK (67 tests), including all three `TestDataHomeLock` tests: the timeout-and-no-write case, the lock-release case and the recheck-under-the-lock case.
**Validation gap:** none — the existing suite reproduced and confirmed every claim, so nothing was missing.

### post-merge review of 3b03b9fd never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: Reviewed commit `3b03b9fdabaad8620f33c8b0c2a64f89dc5e7e58`: its check-job install step covers all five render tools the gate needs (dbus-run-session, kwin_wayland, plasmawindowed, plasma-apply-colorscheme, spectacle), fails the step naming the first tool still absent after install, and its README paragraph records what CI now installs. The test pins `test_workflow_runs_public_checks_with_materialized_assets` (timeout 30, exactly the two public run steps) and `test_workflow_installs_and_verifies_the_plasma_render_tools` match the workflow on main, and the whole `test_ci_workflow` module passes. Later commits extended the step to the seven tools and the 26.04 package renames without contradicting the reviewed change. No defect found.

**Validation gap:** none — the CI-workflow test pins confirm the install step and its by-name verification against the workflow on main; no defect in the reviewed change needed a missing runtime path to identify.

### post-merge review of 74cee7ee never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Reviewed commit `74cee7ee6a73a963d73e2e2948424ee0ff90e6b7`: its Page Info field rule is scoped under the Page Info-only `#mainDeck` id, and the selector assertions check the intended controls and exclude browser chrome fields. The existing test also checks the exact Platinum declarations and rejects extra `#mainDeck input` variants; no defect was found.

**Validation gap:** none — the existing selector tests confirm the Page Info field scope and declarations; rendered pixels remain outside their claim.

### post-merge review of 5f1680eb never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: Reviewed commit `5f1680ebc216a4206741e085c124415468f1b9ed`: `[ToolboxTab]` inherits `[Tab]`, and its test checks the inherited elements, margins and text offsets. The section is registered in the section coverage and margin tables; the mapping reuses the reference-grounded tab surface without changing its art. No defect found.

**Validation gap:** none — the existing config tests confirm the registered `[ToolboxTab]` mapping and its inherited tab settings; no defect in the reviewed change needed a missing runtime path to identify.

### post-merge review of 932f21cb never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Reviewed the selector-matcher escape handling added by the commit and found that its quoted-value parser rejected valid CSS string continuations: a backslash followed by a newline should remove that newline from the value. This exposed the missing guarantee for CSS escapes in attribute values. Added a regression test, taught the quoted-value parser and decoder to handle LF, CR, CRLF and form-feed continuations, and updated the selector-matcher invariant and its reconstruction record.

**Validation gap:** unclear-invariant — the matcher documented escaped characters and hex escapes but omitted CSS string continuations, so the supported escape behavior was reconstructed and recorded in `docs/invariants.md`.

### post-merge review of 69623e21 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `69623e212723aba879109ffb7b8fecf23d8d9721` (Paint Firefox notification doorhanger primary button as Platinum) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

Fix: Reviewed the commit's CSS tokens and selector against the current Firefox popup test and invariant. The rule scopes the primary `moz-button` to `#notification-popup`, sets the primary, hover and active paints and square radius, and leaves the secondary control and surrounding popup untouched; the current test covers those boundaries and the token scope.

**Validation gap:** none — the existing selector and token assertions establish the committed CSS behavior, and the review was settled by inspection.

### post-merge review of bdcedf73 never reached a verdict — fixed 2026-11-09 by the bugfix role (found by the review role 2026-11-09)

The post-merge review of commit `bdcedf73a00aec41ff0b1ed54a1cf4406cdb304c` (Kill a command's group when SIGTERM arrives during its startup) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro); settled after reviewing the startup deferral. The deferral treated every callable SIGTERM/SIGHUP handler as `exit_on_termination`'s handler and converted it to `SystemExit`, breaking callers' custom handler behavior. Deferral now applies to the marked handler installed by `exit_on_termination`; a forced signal during `Popen` verifies a custom SIGTERM handler runs and the child completes normally.

**Validation gap:** no-fake — the existing race fixture forced SIGTERM during `Popen` but did not cover a caller-installed handler; the regression test adds that case.

### post-merge review of 4bad64f9 never reached a verdict — fixed 2026-11-09 by the bugfix role (found by the review role 2026-11-09)

The post-merge review of commit `4bad64f9b539808dd67cbf9f65b0f8d7b9eeecfe` (Name signals when required external commands terminate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore); settled after checking both required-command paths. `_signal_name` maps recognized negative wait statuses to their symbolic signal names and unknown numbers to their number; both paths report exit 1 with the selected log tail. Regression tests cover a real SIGTERM child (including its log tail) on both paths and the unknown-number fallback.

**Validation gap:** none — existing tests reproduce signal termination and confirm the diagnostic and retained log tail.

### post-merge review of 65c4594a never reached a verdict — fixed 2026-11-09 by the bugfix role (found by the review role 2026-11-09)

Reviewed commit `65c4594a242f5f847fb44345e1b325be52c1b3cf`: its four SVG comments accurately describe the assets and their geometry tests; corrected the up-arrow comment's broken test reference. The SVG changes are comments only.

**Validation gap:** none — the review was a source inspection and found a documentation-only typo; no runtime behavior was involved.

### post-merge review of ea5a840d never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: Reviewed the added `write_rgba_cursor` cases against the shared frame validator and the parallel PNG-writer rejection tests. The RGBA tests cover named payload/type, record length, each numeric field's name and representative type or range failures; the byte-buffer length remains covered by its existing test. The diff correctly pins the shared validation behavior through the RGBA entry point.

**Validation gap:** none — the review was confirmed by comparing the regression cases with the shared validator and existing PNG-writer coverage; no runtime failure prevented confirmation.

### The hosted CI check cannot complete on the Ubuntu 26.04 runner, whose software-rendered KWin cannot answer the capture gates (found by the ci role 2026-11-09) — fixed 2026-11-09 by the ci role

The check job first failed before any test ran: on the runner (Ubuntu 26.04) the image-capture package is `kde-spectacle`, so `sudo apt-get install ... spectacle` exited 100 with `E: Unable to locate package spectacle` (run [42615044769](https://github.com/znation/kde-macos8.6-theme/actions/runs/42615044769)). After that was repaired, run [42621380033](https://github.com/znation/kde-macos8.6-theme/actions/runs/42621380033) reached `make check` and failed four modules:

- `test_colorscheme_install` and `test_desktoptheme` ran `plasma-apply-colorscheme`/`plasma-apply-desktoptheme`, whose Qt xcb plugin aborted with no display (`qt.qpa.xcb: could not connect to display`).
- `test_render_surface`'s clients also fell through to xcb inside the nested KWin session, because the session exported its own `WAYLAND_DISPLAY` but no session type. With that repaired, the hosted session exposed the remaining setup gaps: KWin 6.6 refused Spectacle's `CaptureScreen` (the throwaway client has no desktop-file identity), the runner lacked the `org.kde.plasma.calculator` applet, Mesa had no software EGL driver, Ubuntu 26.04 moved the Aurorae engine out of `kwin-common`, and Spectacle's OCR probe had no Tesseract runtime or data.
- `test_kwin_decoration_package::test_gated_copies...` read `/usr/share/kwin/aurorae/` without the sibling skip guard, turning a missing engine package into an error.

The install step now selects `spectacle` when `apt-cache show` finds it and `kde-spectacle` otherwise, verifies the unchanged `spectacle` binary, installs `plasma-widgets-addons` (verified through the calculator applet's package directory or plugin file), `libtesseract5` with `tesseract-ocr-eng`, `libgl1-mesa-dri`, and the release's Aurorae engine (`kwin-style-aurorae` or `kwin-common`). The job pins `ubuntu-26.04`, sets `QT_QPA_PLATFORM=offscreen` for the suite, and forces Mesa's llvmpipe (`LIBGL_ALWAYS_SOFTWARE=1`, `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`). The session shell exports `QT_QPA_PLATFORM=wayland` for its scheme apply, client and capture, sets `KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1` and `SPECTACLE_VIDEO_PLATFORM=VideoPlatformNull` for its throwaway KWin and Spectacle, bounds the client reap with a SIGKILL escalation, and logs its progress. The gated-copy test carries the same engine-dir skip as its siblings.

KWin 6.6's ScreenShot2 offscreen effect still cannot complete on a software renderer: `CaptureScreen` receives no reply because the non-software EGL render target has no render engine behind it. KWin fixed that in 6.8 (`effect/offscreeneffect: allocate a software buffer on software renderers`, commit `add43708`), which the 26.04 image does not ship. The capture gates therefore skip when Mesa is forced onto a software driver (the CI job is), with a reason naming the KWin fix; a GPU-backed host runs them, and the local host exercises them. The release-name selections and the installer work remain so a deliberate image bump (or a GPU runner) needs no rediscovery.

**Validation gap:** none — the display abort and the software-renderer screenshot hang reproduced locally (`MESA_LOADER_DRIVER_OVERRIDE=llvmpipe` yields `Did not receive a reply` with no PNG, while a GPU-backed run captures); the skip helper and the install selections are pinned by tests; run [42639976810](https://github.com/znation/kde-macos8.6-theme/actions/runs/42639976810) passes both `make check` and `make check-references` on the pinned 26.04 image, with the 33 capture-gate tests skipped.


### post-merge review of 3df2c383 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Fix: Reviewed the commit diff against `tools/process_group.py`: its termination handler returns `128 + signum` for SIGTERM and SIGHUP, and the corresponding docs and help epilogs describe that status. `apply_gtk` documents its symbolic-link refusal consistently with its behavior. The documentation changes are accurate.

**Validation gap:** none — the review was confirmed directly against the implementation and needed no runtime reproduction.

### post-merge review of 3df2c383 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Fix:** Reviewed the shared PNG stream framing change. `png_stream` prepends the established signature and concatenates the supplied chunks; callers retain control of IEND and malformed streams. The `make_png` and `png_with_idat` call sites preserve their prior chunk contents and order. No defect found.

**Validation gap:** none — the review was settled by direct comparison with the prior fixture construction and the existing helper tests; no missing reproduction path prevented confirmation.

### The dangling-GTK-selection uninstall warning misses the exotic settings line endings the probe itself writes, so `test_gtk_install` fails on main (found by the feature role 2026-11-09) — fixed 2026-11-09 by the bugfix role

`tools/uninstall_diagnostics.py::_ini_entries` used `text.split("\n")`, which left form-feed, information separators, NEL and Unicode line/paragraph separators inside a line. It now uses `str.splitlines()`, matching the line boundaries accepted by the regression probe. The existing test covers the warning and confirms uninstall leaves each settings file unchanged.

**Validation gap:** none — the existing suite reproduced and confirmed it.

### The required-rule dictionaries for the selected and hovered Page Info radios lack the shipped `box-shadow: none !important` member, so `test_firefox_theme_page_info` fails on main (found by the feature role 2026-11-09) — fixed 2026-11-09 by the bugfix role

Updated both Page Info radio entries in `tests/support/firefox_chrome_cases.py` to require the shipped shadow reset.

**Validation gap:** none — the declared focused check reproduced both missing dictionary members before the change.

### Routine GTK 4 probes present windows on the user's display and can steal focus (found by the director role 2026-11-09) — fixed 2026-11-09 by the bugfix role

**Symptom.** Routine checks could present GTK 4 probe windows on the user's display and steal focus.

**Fix.** Added a shared `PLATINUM_RUN_GUI_TESTS=1` guard before the mixed-indicator launch and census child launches. The palette-only census assertion remains in routine checks. README.md documents the deliberate visible-window invocation, and docs/invariants.md records the guard contract. Regression checks cover a populated host `DISPLAY` without the opt-in and a mocked opted-in launch preserving the child capability-skip result.

**Validation gap:** none — the regression checks cover both guard branches without presenting a window.

### post-merge review of bb14c241 never reached a verdict — fixed 2026-11-09 by the bugfix role (found by the review role 2026-11-09)

**Fix:** Reviewed the commit's added rejection cases against `tools/xcursor.py`: malformed records are wrapped in an indexed `ValueError`, decode errors are translated from `PngError` into an indexed `ValueError`, and mutable byte buffers are accepted as documented. The tests assert these behaviors and independently compare output for `bytes` and `bytearray`.

**Validation gap:** none — the project check documented for the commit exercised the new cases, and source review confirmed their expected branches and contracts.

### post-merge review of 0231c1e1 never reached a verdict (found by the review role 2026-11-09) — fixed 2026-11-09 by the bugfix role

The post-merge review of commit `0231c1e17a623723c07a8b079c2b70d63f369fe8` (Flatten snippet_child._collect's four-deep nesting with guards) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 2:24 AM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

**Fix:** Reviewed the commit diff and current `_collect` implementation. It drains output before the deadline decision, reaps without signaling an already-exited child, and times out only a still-running child. `TestTimeoutPath` covers both the exited child with a surviving pipe writer and the running child timeout path.

**Validation gap:** none — existing tests exercise the collector's timeout and already-exited child branches.

### A key-less `=value` line in a theme INI makes `kde_config.read` raise `ParsingError` instead of skipping it (found by the bugfix role 2026-11-08) — fixed 2026-11-08 by the bugfix role

Reproduce: write `=oops\n[General]\n=oops\nColorScheme=MacOS8\n` to a theme
INI and call `tests/support/kde_config.py::read` on it — the call raises
`ParsingError` naming the `=oops` line, so the theme file a Plasma session
greets on-screen fails to load at all. KConfig works on the name before the
first `=` and skips an entry whose name parses empty, the same way it skips
the colon-delimited entries the reader already drops.

Fixed: `_parseable_lines` now drops a line whose part before the first `=`
trims to empty, in the root group and inside a section alike, and the shared
parity corpus gains a pinning case for all three readers.

**Validation gap:** none — a scratch run reproduced it deterministically and
the existing suite needed only a new test on the one reader; nothing was
missing beyond the uncovered branch.

### A regular file swapped for a FIFO between the uninstall diagnostics' path check and its open hangs `make uninstall` waiting for a writer (found by the bugfix role 2026-11-07) — fixed 2026-11-07 by the bugfix role

`tools/uninstall_diagnostics.py::read_text` guarded its read with
`os.path.isfile` before `open(path, "rb")`. A regular config file that check
just accepted can become a FIFO before the open, and that blocking open then
waits for a writer: with a writer that only ever holds its end open, the
reader's buffered read waits for 1 MiB+1 bytes that never come, so
`make uninstall` hangs inside a diagnostics-only reader whose own contract
pins that it must always succeed. A FIFO already at the path stays silent
(the path check refuses it), and every other bounded reader in the project
opens its files through `containment.open_regular_binary`'s descriptor
check.

Reproduce by patching `os.path.isfile` to keep reporting a regular file over
an existing FIFO and calling `read_text` on it: before the fix the reader
answered with the FIFO's held bytes instead of `None` (and without a
non-blocking descriptor reroute, its open and read never return). The
patch-set reproduction, including the case's non-blocking arrangement, is
pinned by
tests/test_uninstall_config_read_cap.py::TestReaderFifo::
test_a_fifo_swapped_in_for_a_regular_file_is_refused, with the unswapped
FIFO case kept as calibration because it is silent under both readers.

Fix: `read_text` opens the path through the shared
`containment.open_regular_binary`, whose regular-file check runs on the
opened descriptor, so the swap is refused before any read and the path
check is unnecessary; a FIFO or device is left silent like every other
unreadable file.

**Validation gap:** no-fake — confirming it needed a non-blocking FIFO-swap
fake the suite lacked: the direct reproduction (a held-open FIFO behind the
patched path check) blocked the run instead of failing, because the old
reader's buffered read waits past 1 MiB of pipe bytes, so the descriptor
reroute mock had to be built before the defect could fail a test.

### The direct-script option-combination regression test is defined after `unittest.main()` and never collected (found by the bugfix role 2026-11-06)

`tests/test_sample_option_validation.py` defined `test_direct_script_reports_invalid_option_combination` inside the `if __name__ == "__main__":` block, after `unittest.main()`, so unittest discovery never collected it: a sample-tool regression test for `--match-runs requires --find-color` silently never ran. Moved it into `TestSampleOptionValidation`, where the runner now collects and passes it.

**Validation gap:** none — discovery's collected-test output reproduced it (7 tests collected before, the moved test collected and passing after).

### A negative `--run-offset` paging index is accepted and silently names a different page (found by the bugfix role 2026-11-05) — fixed 2026-11-05 by the bugfix role

The sampler's three paging-offset options — `--run-offset`, `--match-run-offset` and
`--match-column-run-offset` — are documented as nonnegative page indexes that count
eligible steps from the start of the ranked list (README's `--run-offset` paragraph says
"is nonnegative"; docs/invariants.md's run, match-run and match-column-run rows say
"invalid offset use is rejected before image reads"), and the fidelity side's
`--difference-run-offset`/`--difference-column-run-offset` do reject negatives, but the
sample side only ran the value through `plain_number` with the word "nonnegative" in the
diagnostic, never checking it. A negative value stayed in `args` and silently changed the
report: `--run-offset -1` behaves exactly like no offset while printing
`run offset: -1`, and `--match-run-offset -1` flips to Python's negative slicing
(`matched_runs[-1:limit]`), naming a different page than the printed offset claims.

Reproduce without the fix:
```
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 0 0 \
  --runs --max-runs 3 --run-offset -1 --json
```
It exits 0, lists the first page's runs, and reports `"run_offset": -1` — while the same
command with `--run-offset 2` skips two eligible runs first. Fixed by a shared
`nonnegative_offset(option)` type parser in `tools/sample_validators.py` (same shape as
`color_offset`/`match_pixel_offset`) wired to the three options in
`tools/sample_arguments.py`; the negative value now exits 2 with
`--run-offset must be nonnegative: '-1'` before any image is read.

**Validation gap:** no-observability — no shipped check, test or diagnostic ever fed a
negative offset, so the documented nonnegative rejection sat unenforced with every check
green; the new `tests/test_sample_option_validation.py` offset cases observe it.

### The GTK settings uninstall diagnostic goes silent when a later duplicate `gtk-theme-name` key names a foreign theme (found by the bugfix role 2026-11-05) — fixed 2026-11-05 by the bugfix role

`make uninstall`'s GTK settings warning is meant to latch on any `[Settings]`
`gtk-theme-name=org.macos8.desktop` line, as the recipe's original awk did
(`found=1` set once and never unset) and as tools/uninstall_diagnostics.py's
own docstring pins: a later foreign value never unmarks an earlier one of
ours. After the 2026-11-04 extraction of the diagnostics into
`tools/uninstall_diagnostics.py`, `latched_match` routed through
`read_selected_values`, whose last-value-wins rule the corpus pins, so
duplicate keys overwrite the early ours value with the later foreign one and
the warning falls silent on the one spelling a hand-edit or a foreign
selector leaves behind: ours first, foreign last, under `[Settings]` of
either `settings.ini`. The removed sheets still get named silently: the file
no longer matches the installed theme's path, so nothing else surfaces the
residue.

Reproduce by writing
`[Settings]\ngtk-theme-name=org.macos8.desktop\ngtk-theme-name=Adwaita\n` to
`<config>/gtk-3.0/settings.ini` and calling
`uninstall_diagnostics.diagnostics(...)` with the published ids: the GTK
`make remove-gtk` warning is missing. Fix: the shared corpus parse split into
`_ini_entries`, which yields every key line's `(section, key, value)`;
`read_selected_values` folds it last-wins unchanged, and `latched_match`
scans it for any matching entry instead of one value — the awk's `found` was
set only inside `[Settings]`, so the section filter stays part of the latch.
Pinned by `tests/test_gtk_uninstall_diagnostic.py`: the unit `latched_match`
latch cases (duplicate key later, section switch later), the
`diagnostics`-level warning on ours-first, and a recipe-level `_uninstall`
end-to-end run that the ini is left untouched; the calibration cases
(foreign-then-ours, foreign only, a foreign section alone) pass unchanged
against both the old and the new code.

**Validation gap:** unclear-invariant — the surviving guarantee had to be
reconstructed from the original awk's never-unset `found=1` latch before the
silent spelling could be confirmed, because the corpus pins only the
general last-value-wins rule and no test exercised the latch's exception;
the re-derived invariant (only a `[Settings]` line marks the file and no
later line unmarks it) is now pinned in docs/invariants.md's GTK uninstall
row beside the new suite.

### Clicking where an unfocused window's title-bar buttons would be presses those invisible buttons (found by the director role 2026-11-04) — fixed 2026-11-05

**Fixed 2026-11-05 (user-directed, live-verified).** Three defects were behind the report. The
hit surfaces were gated on 2026-11-04 by the KWin/Decoration package's
`decoration.client.active` QML (parts 1/3-3/3 of the PLANS.md redesign the refusal routed), but
that gate sat in the package's `DecorationButton.qml`, whose type the explicit
`org.kde.kwin.decoration` import shadows: the module exports its own `DecorationButton`, so the
local copy never ran and the unfocused close cell still closed its window. The effective gate now
sits on the `AuroraeButton.qml` subclass item (`enabled` returns false unless `decoration.client.active`, then the base's
capability switch) and on the `AppMenuButton.qml` fallback, while `MenuButton.qml` and
`AuroraeMaximizeButton.qml` keep their gated standalone MouseAreas; a click on an unfocused bar
therefore falls through to the title bar's activation. Pinned by
`tests/test_aurorae_ui_qml.py::TestHitSurfaces::test_aurorae_button_gates_the_subclass_item`
beside the existing hit-surface pins. The art stayed wrong too: each button SVG's
`inactive-center` group was empty, and
KSvg's `FrameSvg::hasElementPrefix("inactive")` resolves through `hasElement("inactive-center")`
to a valid `boundsOnElement`; an empty group has zero bounds and reports false, so
`AuroraeButton.qml` drew its `buttonActive` overlay on unfocused windows. Each of
`close.svg`, `maximize.svg`, `restore.svg` and `shade.svg` now carries one paintless
full-canvas path (`fill="none"`) in that group, which gives it bounds without paint; the
inactive slice still renders no pixel. Pinned by
`tests/test_aurorae_buttons.py::TestButtons::test_inactive_center_keeps_paintless_geometry`
beside the existing empty-slice pin, with the art digests re-recorded in
`tests/test_aurorae_ui_qml.py`. Live evidence this run: after installing the art and reloading
the decoration, `~/.cache/ksvg-elements` resolves the group (the installed `close.svg` now holds
valid element rects instead of one), and a screenshot shows the unfocused Firefox title bar with
no close, zoom or collapse art while the focused Konsole bar draws all three boxes. After a fresh
KWin loaded the package, a synthetic absolute-pointer click on an unfocused close cell activated
that window and left it open, while the same click on a focused window closed it.

**Validation gap:** real-run-needed — the shadowed-component gate and the corrected one are
session-level: only a live click on an unfocused title-bar cell exposed that the imported
module's `DecorationButton`, not the package copy, owned the hit area. The offline pin is the
subclass gate plus the art tests, and the live close-cell click above is the observation.

### The apply's off-default data-home note fires when the theme already exists at the default data home (found by the bugfix role 2026-11-04) — fixed 2026-11-04 by the bugfix role

`tools/theme_apply_optional.py::_warn_off_default_data_home` printed its
`apply_theme: note:` warning purely from `resolved != default`, without
checking whether `themes/org.macos8.desktop/Kvantum` already exists under
the default data home. An operator who had installed the theme under the
default data home and later ran `make apply` with a non-default
`${XDG_DATA_HOME}` still saw "widgets draw Kvantum's built-in default theme
until themes/org.macos8.desktop/Kvantum exists there" — the condition the
message itself names was already satisfied, so the note told the operator
to do something they had already done. Reproduced by a scratch call to
`_warn_off_default_data_home` with `HOME` on a temp directory holding
`$HOME/.local/share/themes/org.macos8.desktop/Kvantum` and
`XDG_DATA_HOME` elsewhere: the note printed with the theme present and
absent alike. Fix: the note now also stays silent when the exact theme
directory exists under the default data home (`_theme_directory_at`), and
a wrongly named sibling (a different theme name, a different leaf name, or
the directory under `Kvantum/` instead of `themes/`) does not silence it.

**Validation gap:** no-fake — the existing env-shape tests never populated the
default data home with the theme directory, so the false-positive shape needed
a new fixture (the default-home theme directory) that did not exist; it is now
pinned by `test_a_theme_already_at_the_default_data_home_stays_silent`.

### remove-kvantum calls a directory or a fouled `Kvantum` path at the kvconfig path absent (found by the bugfix role 2026-11-04) — fixed 2026-11-04 by the bugfix role


`tools/kvantum_selection.py::_clear_selection` treats every `None` from
`tools/gtk_user_files.read_config_text` as ``{path} is absent`` and exits 0. But
`read_config_text` also returns `None` when a directory occupies
`kvantum.kvconfig` (or when `Kvantum` itself is a regular file, giving
`NotADirectoryError`), so the tool tells the operator the selection's file is
absent while something non-regular sits exactly where `kvantummanager` writes
the selection. The GTK staging code reports such a target as an error, not a
note.

Reproduce: create `$XDG_CONFIG_HOME/Kvantum/kvantum.kvconfig` as a directory,
run `python3 tools/kvantum_selection.py` — it prints
`remove_kvantum: note: nothing to clear: …/kvantum.kvconfig is absent` and
exits 0, though the path is occupied and unreadable.

Fixed: `_clear_selection` now separates the occupied-and-unreadable cases from
true absence. A `$XDG_CONFIG_HOME/Kvantum/kvantum.kvconfig` that is a directory
exits 2 with ``cannot read {path}: it is a directory, not a regular file``, a
fouled `Kvantum` path (a regular file where the directory belongs) exits 2 naming
that path, and only a genuinely absent path keeps the absent note and exit 0;
`tests/test_remove_kvantum.py` pins both refusals and `docs/invariants.md` records
the changed guarantee.

**Validation gap:** none — a scratch run reproduced it deterministically and
the existing suite needed only a new test; nothing was missing beyond the
uncovered branch.

### Hovering or pressing an unfocused window's title-bar button erases it (found by the director role 2026-11-04) — fixed 2026-11-04 by the feature role

**Symptom.** With focus on another window, moving the pointer over an unfocused window's close
box makes it vanish entirely against its `#DDDDDD` title bar; it reappears when the pointer
leaves. Pressing an unfocused window's close, zoom or shade button erases it the same way: no
hover or pressed feedback ever appears on an unfocused button. The focused window is
unaffected.

**How to reproduce.** On a Plasma session with Platinum applied, activate a second window so
the first sits unfocused, then move the pointer over the unfocused window's close box: the box
disappears while the pointer is over it.

**Suspected cause (verified against the installed engine).** KWin composites Aurorae buttons
from state overlays keyed by KSvg prefixes (`/usr/share/kwin/aurorae/AuroraeButton.qml`, KWin
6.3.6, inspected 2026-11-04). The four button SVGs in
`theme/aurorae/themes/org.macos8.desktop/` define only `active` and `inactive` prefixes, so
`supportsHover`, `supportsPressed`, `supportsInactiveHover`, `supportsInactivePressed` and the
deactivated companions are all false. `buttonInactive` hides whenever `hovered || pressed`,
and the `hover-inactive` and `pressed-inactive` overlays that should take over are absent, so
on hover or press every overlay's opacity is 0 and nothing is drawn. On a focused window this
cannot happen because `buttonActive` stays shown when the hover/pressed/deactivated prefixes
are missing.

**Fix direction.** Add `hover-inactive` and `pressed-inactive` prefixes to the four button
SVGs, rendering identically to `inactive`: the reference set shows no hover or pressed
appearance for unfocused title-bar boxes, so keeping the unfocused box's own art unchanged is
the grounded value. The PLANS.md plan that empties the inactive button art per the reference
subsumes this symptom; fix it only if that plan is refused, and re-triage this entry after
that plan leaves `## Planned`.

**Fix.** The plan left `## Planned` on 2026-11-04: the four button SVGs' `inactive-center`
groups now ship no art (the reference's unfocused windows draw buttonless bars,
`desktop_fandom.png`), so hover and press have nothing they can erase or change — every
unfocused overlay draws nothing, which is the design. No `hover-inactive` / `pressed-inactive`
groups were needed, and the empty `inactive` element stays for AuroraeButton.qml's fallback.
`tests/test_aurorae_buttons.py` pins the nothing-shipped slices.

**Validation gap:** real-run-needed — the erasure shows only as live Aurorae overlay
opacity inside a running KWin session, which nothing offline can render; confirmation is
anchored instead by the installed `/usr/share/kwin/aurorae/AuroraeButton.qml` (KWin 6.3.6)
state logic and the nothing-shipped `inactive-center` slice pins in
`tests/test_aurorae_buttons.py`.

### A stale `_None yet._` placeholder in PLANS.md's `## Planned` claims the section is empty above two live plans (found by the bugfix role 2026-11-04) — fixed 2026-11-04 by the bugfix role

**Symptom.** `PLANS.md ## Planned` opened with `_None yet._` even while it held two live
plans (the inactive-window decoration plan and the remove-kvantum plan). The files are prose,
so the full check stayed green while triage read a section that contradicted itself: an empty
`## Planned` and two entries below it.

**How to reproduce.**
`python3 -m unittest discover -s tests -p "test_backlog_placeholders.py"` — without the
PLANS.md edit its
`test_plans_sections_placeholders_match_their_entries` fails with
`AssertionError: [(10, '## Planned')] != []`; with it the module exits 0.

**Fix.** Removed the stale placeholder from PLANS.md and added
tests/test_backlog_placeholders.py, which scans PLANS.md and BUGS.md so a `_None yet._`
placeholder under a `##` heading holding at least one `###` entry fails; synthetic fixtures
pin the scanner's branches (placeholder in an empty section, entries without a placeholder,
report naming the placeholder's own section, placeholders before any section).

**Validation gap:** no-observability — the stale placeholder left no trace in any test, so
confirming the regression required a new backlog-scanner test rather than an existing run.

### PLANS.md claims `## Planned` is empty while it holds a planned entry (found by the bugfix role 2026-11-04) — fixed 2026-11-04 by the bugfix role

**Symptom.** PLANS.md's `## Planned` section carried the `_None yet._` empty-section
placeholder at its top while the director role's "Inactive windows: draw the reference's
buttonless bar and `#777777` title text" plan heading sat directly below it (director
commit 11e330eb4, stamped 2026-11-04). The placeholder records "this section holds no
entries", so the file contradicted itself and a skim of the placeholder line read the
planning queue — what every role acts on — as empty.

**How to reproduce.** `grep -n '_None yet._' PLANS.md` printed line 8 while PLANS.md lines
10 onward held the `### ` planned entry in the same `## Planned` section. Every
`make check` stayed green: no test parsed the backlog placeholders, so the contradiction
left no trace.

**Suspected cause.** The placeholder is a template artifact: the planned-entry block was
inserted into a section whose placeholder line had been left from an earlier empty state,
and nothing validated a placeholder claim against its section's contents.

**Fix.** The stray placeholder line is removed, and `tests/test_backlog_placeholders.py`
scans both `PLANS.md` and `BUGS.md` so a `_None yet._` line inside a `## ` section that a
`### ` entry occupies fails the suite; constructed fixtures pin the scanner's
section-boundary reset and entry-after-placeholder branches.

**Validation gap:** no-observability — the file contradiction left no trace in any check
output, so it surfaced only when the backlog was read by hand; the new scan reproduces it
offline in `tests/test_backlog_placeholders.py::TestShippedBacklogs`
`::test_no_placeholder_claims_a_section_that_holds_an_entry`.

### Under a loaded host the live GTK dialog gate flakes: an all-black capture, or a mid-transition compose that misses four pinned cells (found by the plan role 2026-11-04) — fixed 2026-11-04 by the bugfix role

**Symptom.** Two consecutive full `make check` runs (2026-11-04 00:36 and 00:41) failed their `test_render_surface` module on the GTK dialog gate alone. One capture was mid-transition and missed all four pinned cells; the other was entirely black because zenity had not painted by the 8-second settle. Focused runs stayed green.

**How to reproduce.** Run the full check on a loaded host; the parallel test coordinator starts the GTK dialog render alongside four other renders, and the GTK capture can be unpainted or mid-transition at the fixed 8-second settle.

**Fix.** The GTK dialog gate now passes `--settle 20`, allowing additional time for zenity to paint and finish its placement transition. The renderer's 60-second timeout remains longer than this budget, and the existing four cell comparisons reject captures that remain misaligned.

**Validation gap:** slow-check — the failure depended on concurrent render load, so confirming timing behavior requires the full check rather than the focused budget assertion.

### A successful required-command read is discarded when its stderr log cannot be removed (found by the bugfix role 2026-11-03) — fixed 2026-11-03 by the bugfix role

**Validation gap:** no-fake — the suite had no way to make a log removal fail, so the
regression test injects a PermissionError for each log deletion independently and
checks that the other log is still removed.

Symptom: `run_required_output` read the stdout bytes successfully, then removed both split
logs inside the same `try`; an `OSError` from the `stderr_log.unlink()` (for example a
read-only scratch directory) reached the existing handler and reported
`cannot read <stdout log name>` at exit 2, discarding the value already read. A
`kreadconfig6` read `apply_keymap` takes as a required command would then fail its whole
run on a cleanup that cannot succeed.

Reproduce with
`cd tests && python3 -m unittest test_required_command.TestRunRequiredOutput.`
`test_a_stderr_log_that_cannot_be_removed_keeps_the_value` — without the fix it fails with
`AssertionError: 2 is not None`; with the fix the read returns `b"recorded"` and no error.

Suspected cause and fix: the deletion was cleanup, not the read, so it must never be
reported as a failed read. The fix removes both logs best-effort after a successful
`read_bytes`, ignores a removal that fails, and the function docstring records that a log
whose removal cannot succeed stays on disk.

### A stray `check.log` full-check output is tracked at the repository root (found by the plan role 2026-11-03) — fixed 2026-11-03 by the bugfix role

**Symptom.** `git ls-files` names `check.log` at the repository root; its content is one run's complete `make check` capture (it opens with the check harness invocation `python3 tools/check_parallel.py` and the per-worker `===== <module>: exit 0 =====` progress lines), no repository file, recipe or test reads it, and every subsequent check run would make the tracked copy stale. It is a run artifact of the 2026-11-03 plan run that wrote its check output to a fixed path in the worktree root instead of `$TMPDIR`, and the run's commit swept the file into the tree.

**Reproduce.** `git ls-files | grep -x check.log` prints `check.log`; `grep -rn "check.log" Makefile tools tests README.md docs` finds no consumer. `make check` stays green because `tests/test_scratch_hygiene.py`'s offender scan only rejects top-level tracked files whose first line names a run scratch directory (`/tmp/tumwater-run-*/tmp.*`), which a plain check capture does not.

**Suspected cause.** The run tooling records check output at a worktree-local scratch path out of habit (`check.log` in the root), and nothing in the scratch-hygiene test recognizes a check-output file, so the commit bandwagoning every worktree file shipped it.

**Fix.** The file is removed from the tree, and `tests/test_scratch_hygiene.py` learns a second scan: a tracked top-level file whose first line is the check harness invocation (`python3 tools/check_parallel.py …`) is a run-artifact capture and must not be tracked, with fixture tests for the nested and non-harness first-line cases and one for a capture without a trailing newline.

**Validation gap:** no-observability — a tracked check-capture file leaves no trace the suite can see: the existing scratch-hygiene scan only matched `/tmp/tumwater-run-*/tmp.*` bookkeeping first lines, so a bare check-output log kept every check green until a fresh `git ls-files` was run by hand.

### The reference sampler reopens an image path after its symlink containment check (found by the security role 2026-11-03) — fixed 2026-11-03 by the bugfix role

`tools/sample.py::main` now opens the requested image once, checks the opened
target through its stable `/proc/self/fd` handle, and uses that handle path for
both size validation and pixel decoding. Replacing the original symlink after
the open cannot redirect either PNG read.

**Validation gap:** none — the regression test swaps the symlink after the sampler opens the original target and confirms the original pixels are reported.

SUMMARY: Keep sampler reads bound to the checked image descriptor
WHY: The review found a header-bounds test that depended on a nonexistent file, plus regressions in missing-file diagnostics. The test now uses a real PNG, and open failures retain the sampler's `cannot read` diagnostic.
RISK: Changes to sampler open-error handling could affect diagnostics for unreadable paths; check `tests/test_sample_cli.py` and `tests/test_sample_option_validation.py`.
VERIFIED: `make check` passed; the header-bounds test now reports the bounds error using a real PNG, and missing-path/control-character tests pass.
Objection 1: done
Objection 2: unchanged-by-design because the relative config-home fallback test passed
Objection 3: unchanged-by-design because the absolute data-home test passed
Objection 4: unchanged-by-design because the missing absolute data-home test passed
Objection 5: unchanged-by-design because the empty data-home fallback test passed
Objection 6: unchanged-by-design because the relative data-home fallback test passed
Objection 7: unchanged-by-design because it only separates the test-run summary
Objection 8: unchanged-by-design because it reports successful tests
Objection 9: unchanged-by-design because it reports a successful suite
Objection 10: done

### The live dialog gates byte-compare one widget cell each, so the other engine-drawn widgets in the two captures stay unpinned (found by the steward role 2026-10-30) — fixed 2026-11-03 by the bugfix role

**Validation gap:** none — The closest tag is no-observability: the old gate stayed green after the button face was recoloured, and the new render assertions pin the missing regions.

The live render gate compares engine-drawn Kvantum widget pixels in
precisely three regions, each added when its bug was fixed: the checkbox
cell `CHECKBOX_CROP` (156, 187, 14x14) and its 1px face ring in the
`--checkbox-dialog` capture, and the combo-arrow cell `COMBOBOX_CROP`
(316, 178, 12x12) in the `--combobox-dialog` capture
(`tests/test_render_surface.py`); the gate's other byte-compares are the
rendered window chrome strips and boxes. Every other engine-drawn widget
pixel in those two populated 480x360 captures — the push buttons and any
further widget `kdialog` draws there — is never compared, so coverage grows
only when a render pass finds a bug by eye, never from an enumeration of
what the captures draw. Both Open records sit in exactly this unpinned
space: the Yes button's two interior black rows are drawn inside the
`--checkbox-dialog` capture the gate already runs, and the `--menu` field's
GenericFrame frame is an engine-drawn region no gate watches — `make check`
stays green on both. A future regression in any other engine-drawn widget
outside the three regions lands unobserved the same way.

Reproduce: patch the installed theme's `button-normal` interior slice to a
marker colour (the inspection the Open button record's field used on
`common-normal-*`), rebuild the render with
`RENDER_OUTPUT=x.png make render --checkbox-dialog`, and run
`tests/test_render_surface.py`'s dialog-render classes — no assertion
fails, because no compared crop overlaps the button (the check box cell
sits at y=187..200, the button at y=207..230).

**Suspected cause:** infrastructure, not a per-widget fix: the two session
renders already exist in `tools/render_surface.py` and are cheap to rerun,
so the gap is that the gates compare call-chosen single crops instead of
deriving the set of engine-drawn widget regions from the captures and
comparing each region against the shipped art slice its widget maps to.

**Progress (2026-10-30 by bugfix):** rendered the checkbox, combobox and menu
dialog captures successfully at 480x360. The region coordinates and expected
band runs for the unpinned buttons and combo field have not been verified, so
no pixel assertions were added; guessed crops could pin unrelated dialog pixels.

**Review resolved 2026-11-02 at the user's direction: every region below was measured on fresh
`--checkbox-dialog`, `--combobox-dialog` and `--menu-dialog` renders of the current tree, and the
art slice each region maps to was confirmed by recolouring that slice in the theme SVG and
diffing the capture. The assertions are now writable without guessing; no further review is
needed.**

All three captures are 480x360 and each dialog is the session's only centred window, so the
rects are fixed geometry. Region rects are `(x, y, width, height)`; colour runs list the
shipped slice each maps to.

`--checkbox-dialog`, `tools/render_clients.py::checkbox_dialog_client` — the check box cell
`CHECKBOX_CROP` (156, 187, 14, 14) and its face ring `CHECKBOX_FACE_RING_CROP` (155, 186, 16, 16)
are already pinned; add:

- Yes button (156, 207, 82, 24), the `button-normal` frame under the interior ring recorded in
  the entry above. Row 207 `#000000` x=156..237; row 208 `#000000`(156), `#FFFFFF`(157..235),
  `#AAAAAA`(236), `#000000`(237); rows 209..213 `#000000`(156), `#FFFFFF`(157), `#DDDDDD`(158..235),
  `#AAAAAA`(236), `#000000`(237), the same band columns running down the whole interior; row 229
  `#000000`(156), `#FFFFFF`(157), `#AAAAAA`(158..236), `#000000`(237); row 230 `#000000`
  x=156..237. The interior also holds the label, the focus ring and the
  default-indicator wedge described in that entry, so this assertion lands after that steering
  (or excludes the bottom-right 7x7).
- No button (241, 207, 82, 24), the same frame with the interior 243..320 x 209..228 flat
  `#DDDDDD`: row 207 `#000000` x=241..322; row 208 `#000000`(241), `#FFFFFF`(242..320),
  `#AAAAAA`(321), `#000000`(322); row 229 `#000000`(241), `#FFFFFF`(242), `#AAAAAA`(243..321),
  `#000000`(322); row 230 `#000000` x=241..322. It carries no focus or default artifact, so pin it
  first.
- The interiors also carry their labels, and label pixels are not face pixels: the non-face
  extents are (179..235, 214..228) in Yes and (265..299, 213..224) in No. Pair each band-run
  assertion with a face rectangle outside those extents — rows 209..212 run face across both
  buttons — rather than comparing a whole interior.

`--combobox-dialog`, `tools/render_clients.py::combobox_dialog_client` — the combo arrow cell
`COMBOBOX_CROP` (316, 178, 12, 12) is already pinned; add:

- combo field (146, 172, 188, 24). Its bands are the shipped `button-pressed-*` slices, not
  `button-normal-*`: recolouring `button-pressed-top/bottom/left/right` changed exactly its 408
  outline pixels and recolouring `button-normal-*` changed nothing. Kvantum's `CC_ComboBox` frame
  status picks "pressed" for `State_Sunken || State_Selected`, so the field paints the pressed
  bevel rather than the reference's raised one; which of those two states this widget supplies is
  not settled here and does not change the assertion. Row 172 `#000000` x=146..333; row 173 `#000000`(146),
  `#AAAAAA`(147..331), `#FFFFFF`(332), `#000000`(333); rows 174..193 interior `#DDDDDD`
  x=148..331 (the selected text and the pinned arrow cell sit in it); row 194 `#000000`(146),
  `#AAAAAA`(147), `#FFFFFF`(148..332), `#000000`(333); row 195 `#000000` x=146..333; left column
  146 `#000000`, 147 `#AAAAAA`; right column 332 `#FFFFFF`, 333 `#000000`.
- OK button (167, 199, 82, 24): row 199 `#000000` x=167..248; row 200 `#000000`(167),
  `#FFFFFF`(168..246), `#AAAAAA`(247), `#000000`(248); rows 201..220 `#000000`(167),
  `#FFFFFF`(168), `#DDDDDD`(169..246), `#AAAAAA`(247), `#000000`(248) except the default-indicator
  wedge at (240..246, 214..220); row 221 `#000000`(167), `#FFFFFF`(168), `#AAAAAA`(169..247),
  `#000000`(248); row 222 `#000000` x=167..248.
- Cancel button (252, 199, 82, 24): the same bands with the interior 254..331 x 201..220 flat
  `#DDDDDD` and no wedge — row 199 `#000000` x=252..333, row 200 `#000000`(252), `#FFFFFF`(253..331),
  `#AAAAAA`(332), `#000000`(333), row 221 `#000000`(252), `#FFFFFF`(253), `#AAAAAA`(254..332),
  `#000000`(333), row 222 `#000000`.
- These two interiors carry their labels too: non-face extents are (190..246, 206..220) in OK
  (which includes the wedge) and (265..321, 205..216) in Cancel, so rows 201..204 run face across
  both buttons and rows 217..220 across Cancel.

`--menu-dialog`, `tools/render_clients.py::menu_dialog_client` — the render CLI and client already
exist but no gate runs the mode: add a fourth kind to `_Renders.KINDS` and a
`TestMenuDialogRender` class under the same `_dialog_gate_guard()`. Its engine-drawn region is:

- item-view field (112, 93, 256, 182), a 2px `itemview` frame drawn in the focused state (its art
  is identical to the normal state). Row 93 `#999999` x=112..366 with (367, 93) the window face
  `#DDDDDD`; row 94 `#999999`(112), `#000000`(113..366), `#FFFFFF`(367); left column 112
  `#999999` y=93..273 and 113 `#000000` y=94..273; right column 366 `#000000` y=94..273 and 367
  `#FFFFFF` y=94..274; row 273 `#999999`(112), `#000000`(113..366), `#FFFFFF`(367); row 274
  `#FFFFFF` x=113..367 with (112, 274) the window face `#DDDDDD`; interior `#FFFFFF` x=114..365,
  y=95..272. The two unpainted corners are the shipped art's own unpainted corner pixels, not the
  face slice, so state them explicitly rather than deriving them from a composer.
- the current item's `[Focus]` ring, black 1px at (115..364, 96..113), sits inside that field and
  is engine focus art, not field art: recolouring `focus-*` changed exactly its 528 pixels. Exclude
  it from the field comparison or assert it separately as `[Focus]`.

Look deviation found while verifying the combo field, recorded for its own triage: the reference's
pop-up buttons are raised — `opendialog_macrumors86.jpg` rows 15..33 (black outline, `#FFFFFF` top
highlight, `#DDDDDD` face, `#AAAAAA` bottom shadow), and `systeminfo_betawiki.png` rows 102..121
for the "Show:" popup the `comboarrow` cell is grounded in — while the capture's combo box renders the
pressed bevel (dark top-left, white bottom-right). The field assertion therefore pins the
`button-pressed-*` mapping the engine actually uses; the raised look needs a state steering or a
bug entry of its own.

**Decided by the user 2026-10-30 (recorded by the director role): explicit per-widget regions,
no capture walker.** Extend the two existing dialog gates with one byte-comparison or band-run
assertion per engine-drawn widget region of each capture, in the shape
`test_draws_the_check_box_cell_1_to_1` and `test_draws_the_combo_arrow_cell_1_to_1` already use:
the check box and its face ring plus the Yes and No push buttons in the `--checkbox-dialog`
capture, and the combo arrow, the combo field and the OK button in the `--combobox-dialog`
capture. For composed frames assert the rendered band rows/columns and the flat interior fill
against the shipped slices; do not rebuild a nine-slice composer in the test, because it would
reimplement `renderFrame` and could share its assumptions. A walker that segments regions out of
the capture is rejected: it would reimplement the widget-to-element mapping that this record
exists to pin, and the two captures have fixed 480x360 geometry by construction. The item view
field has no capture yet, so add the `--menu-dialog` client named in the item-view record and pin
its border runs there. Coverage is now exhaustive over the widgets the dialog clients create, not
automatic: a new `--*-dialog` mode must add its regions in the same change, and the region table
must name `tools/render_clients.py`'s `checkbox_dialog_client`/`combobox_dialog_client` so that
requirement is visible where the widgets are constructed. That module owns the dialog argv
recipes. `make check` owns the renders, so no new
session infrastructure is proposed.

**Fixed 2026-11-03 by the bugfix role:** Added explicit band checks for both buttons in each button dialog, the combo field, and the menu dialog's item-view frame and focus ring. The marker-colour reproduction showed the old cell-only assertion passed despite the altered button face.

### A rendered kdialog push button paints two black rows the shipped button frame does not contain (found by the bugfix role 2026-10-30) — fixed 2026-11-03 by the bugfix role

The `--checkbox-dialog` render's focused Yes button painted black rows at (195,209) and
(195,228), where the reference-grounded face is `#DDDDDD`. Kvantum draws these as the push
button's focus rectangle inside its bevel. The reference places the default mark outside the
bevel. Set `[PanelButtonCommand] focusRectElement=focus-none` to suppress that button focus
rectangle while leaving `[Focus]` available for item views. The default button also used
compiled-in corner art; the theme now supplies `button-default-indicator` as an 8x8 `#DDDDDD`
face patch.

The rendered dialog now reads `#DDDDDD` at both former black-row pixels. The SVG slice test
confirms the default indicator is flat face art.

**Validation gap:** none — the dialog render test reproduced the black rows before the config fix and confirmed the face pixels afterward.

### A stray `.scratchpath` scratch bookkeeping file is tracked at the repository root (found by the readme role 2026-10-31) — fixed 2026-10-31 by the bugfix role

`git ls-files` lists `.scratchpath` at the repo root; its content is the single line
`/tmp/tumwater-run-WoaXid/tmp.QD7q1FlsWf`, a path to an earlier run's temporary scratch directory
that no longer exists, so the file carries nothing another clone can resolve and no test or recipe
reads it (no repository file references the name outside `git ls-files` output). Commit history
shows it entering the tree in commit 11684e99 (the plan role, 2026-10-31), an accidental `git add`
saved first to a run scratch directory. Cause: the run-producing tooling wrote its bookkeeping file
into the worktree instead of `$TMPDIR`. Fix belongs to whoever owns the tooling that creates it —
tumwater deletes the file (`git rm`) and the producing role's workflow keeps scratch state under
`$TMPDIR`; never a fixed `/tmp` path.

Fixed by removing the file (`git rm --cached .scratchpath` after deleting it from the
worktree), ignoring the name in `.gitignore` so a plain `git add` cannot re-track it, and
pinning both with `tests/test_scratch_hygiene.py`, which fails while `.scratchpath` is
tracked or while any tracked top-level file's first line names a `tumwater-run-*` scratch
directory.

**Validation gap:** no-observability — `make check` stayed green through the whole time the file
was tracked because no test inspected the tracked tree, so the stray file surfaced only through a
manual `git ls-files`.

### The item view's frame art never reaches the screen: rendered lists draw the GenericFrame `common` frame instead of the reference's sunken field (found by the render pass 2026-10-29) — fixed 2026-10-30 by the bugfix role

Qt resolves scroll-area frames through `[GenericFrame]`; mapping its frame and interior to `itemview` makes the rendered list use the reference's sunken field. `[ItemView]` remains unchanged for per-item painting. Added `--menu-dialog` to `tools/render_surface.py` using the existing scratch KWin session, and pinned the `GenericFrame` element mapping in the Kvantum config tests and the rendered list field's sunken border runs in the menu-dialog render gate. Updated the subsystem invariant in `docs/invariants.md`.

**Validation gap:** none — the config regression test pins the corrected element, and the `--menu-dialog` render gate byte-compares the rendered field's `#999999`/`#000000`/`#FFFFFF` left and `#000000`/`#FFFFFF` right/bottom runs with the shipped `itemview` slices (`tests/test_render_surface.py::TestMenuDialogRender`); pixel coordinates in the old report did not match this run's window layout, so the gate re-measures them on its own capture.

### The rendered combo box indicator is a squashed 4px-wide arrow, not the reference's centred double arrow (found by the render pass 2026-10-29) — fixed 2026-10-30 by the bugfix role
**Validation gap:** real-run-needed — only a real bounded KWin render could show the rendered
indicator's pixels, and no offline test could: the SVG reference suite was green while the
rendered arrow differed, and the squashed observation itself came from a session that no longer
exists.

A `QComboBox`'s indicator renders as two right-aligned triangles four pixels wide (band widths
1/2/3/4 and 4/3/2/1 with the right edge fixed at x=187), while the reference cell and the shipped
`comboarrow-normal` art are 7px-wide centred triangles (1/3/5/7 and 7/5/3/1) in a 12x12
`#DDDDDD` cell. `tests/test_kvantum_combobox_reference.py` passes, so the art is right and only
the rendered pixels differ.

Reproduce with the pass's throwaway session: `kdialog --title "Test" --combobox "Choose a disk:"
"Macintosh HD" "Zip Disk"`, then dump x=174..187, y=56..71.

**Observed output:** row 59 one black pixel (x=187), row 60 two (186-187), row 61 three (185-187),
row 62 four (184-187), two face rows, then 4/3/2/1; the reference's cell
(`systeminfo_betawiki.png` x=233..244, y=106..117) has 1/3/5/7 and 7/5/3/1 centred bands —
`tools/sample.py systeminfo_betawiki.png 236 109 --width 5` is five `#000000` pixels where the
render's matching row has three.

**Suspected cause:** the same resampling as the check box — Kvantum draws the 12x12
`comboarrow` art into a narrower indicator area (about 7px), squashing the triangles; the theme's
`[ComboBox] indicator.size=12` does not reach the rendered indicator.

**Decision (user, recorded by the director role 2026-10-30): steer the engine first** — proceed
with the bugfix review's recommendation: try steering the engine to draw the 12x12 `comboarrow`
cell 1:1 (an explicit size knob matching the art's canvas; note the check box fix found
`[CheckBox] indicator.size` inert there, so try the section's size keys against upstream
`Kvantum.cpp` before trusting `indicator.size`), and pin the rendered arrow's centred bands
(1/3/5/7, 7/5/3/1) with a test that re-derives the pixels from a render. Only if the engine
cannot be steered to the art's size, re-derive the `comboarrow` art at the size Kvantum actually
draws and record the smaller cell's deviation from the reference's 12x12 so the same direction
does not silently ship resampled art.

**Resolution (bugfix, 2026-10-30):** the engine was already set to the art's native size, and
the squashed render does not reproduce on the current tree. Upstream Kvantum 1.1.4
(`Kvantum.cpp`, `renderIndicator` and `PE_IndicatorButtonDropDown`) reads `[ComboBox]
indicator.size` and clamps the drawn arrow's side to it — the knob does reach the rendered
indicator, unlike the checkbox's section size — with no other section size key in the combo
path, so the shipped 12 already asks for the 12x12 canvas and no further steering is needed.
Two real renders through the current render session (`kdialog --combobox "Choose a disk:"
"Macintosh HD" "Zip Disk"`, 480x360 and 320x240 captures) drew the exact reference cell —
1/3/5/7 and 7/5/3/1 centred bands, black and `#DDDDDD` only — byte-identical to the shipped
`comboarrow-normal` slice and to each other; that cell is where KWin centres the 480x360
dialog's combo arrow (x=316..327, y=178..189), a platform value the reference set does not
show, measured on that capture. The 2026-10-29 squashed observation predates this session's
theme-selection plumbing (the `kdeglobals` `widgetStyle` write, the Kvantum selection and the
`$HOME` themes link that the check box fix landed 2026-10-30), so its capture no longer names
a live drawing path. The render surface now has a `--combobox-dialog` mode in that session,
and `tests/test_render_surface.py::TestComboboxDialogRender::test_draws_the_combo_arrow_cell_1_to_1` pins the rendered cell
against the shipped art in `make check` — a red run with a temporary `indicator.size=6`
re-sampled the cell and failed the gate, so the pin catches steering the size away from the
canvas too.

### The live render gate byte-compares only Aurorae window chrome, so `make check` stays green on widgets the engine draws wrongly (found by the steward role 2026-10-30) — fixed 2026-10-30 by the bugfix role

The declared check's only rendered-pixel comparisons live in
`tests/test_render_surface.py::TestRender`, and they cover the Aurorae frame only: the title-bar
strip, the close, collapse and zoom boxes and the three border strips byte-compared against the
references, plus one body-face pixel at (300, 200). Nothing in the suite compares an engine-drawn
Kvantum widget's pixels with a reference — the Kvantum suites (`tests/test_kvantum_combobox_reference.py`
and its siblings) compare the *shipped art* against the reference cells, not the *rendered* widget —
so whatever the engine does to that art on screen is invisible to the check. This is one structural
risk behind a run of same-shaped bugs, each found only by a manual render pass and never by a test:
the fixed resampled check box indicator (BUGS-FIXED, found by the render pass 2026-10-29), and the
two needs-review Kvantum bugs above (the squashed combo indicator, the unmapped item-view frame).
The append-per-bug pattern confirms the shape: when each render bug is fixed, its armor is a handful
of newly byte-compared strips (the title-band entry above plans exactly rows 22-26 next), so the
gate grows strip by strip and the next resampled, squashed or unmapped widget stays as invisible to
`make check` as this run's bugs were.

**Reproduce:** run `make check` on a tree with the two needs-review Kvantum bugs unfixed — it passes
while the rendered dialog window draws the squashed arrow and the raised list frame; the two
entries' throwaway-session commands above produce the contradicting pixels.

**Observed output:** the two entries' dumps above (combo indicator bands 1/2/3/4 against the
reference's 1/3/5/7; list frame `#000000` then `#FFFFFF` against the reference's `#999999`,
`#000000`, `#FFFFFF`) alongside a green `make check`.

**Suspected cause:** the reference surface the gate byte-compares (one 320x240 window captured by
`TestRender`) contains no populated Kvantum widgets, only the Aurorae-decorated empty window body,
so the widget interiors fall outside every strip; whether the fix is a wider populated capture (for
example a second session with a combobox, a checkbox and a list, whose widget cells are byte-compared
the way the title bar is) or a cheaper substitute, and how a session keeps it cheap, is the review
question — the render session already exists (`tools/render.py`), so this plans as infrastructure,
not as a per-widget fix.

**Fix (bugfix role 2026-10-30):** the gate got its first engine-drawn Kvantum widget. The render
CLI grew a `--checkbox-dialog` mode that opens a `kdialog --warningyesno --dontagain` warning in
the same throwaway KWin session, applies the global theme's `kdeglobals` section (a dialog client
draws through `[KDE] widgetStyle=kvantum`, which the applet render deliberately leaves
unapplied), selects `org.macos8.desktop` in the scratch config home's
`Kvantum/kvantum.kvconfig`, and links the scratch home's `.local/share/themes` onto the
installed theme directory — Kvantum joins its search path from `HOME`, which no finished
`make install` into a different scratch `XDG_DATA_HOME` satisfies, and without the link the
engine silently draws its compiled-in default theme. The session script opens any client argv
(`session_command` now takes the client words; the applet render passes
`plasmawindowed <applet>`), so adding each next widget cell is the same crop-and-compare as the
chrome strips. `tests/test_render_surface.py::TestCheckboxDialogRender` runs that render in
`make check` and byte-compares the rendered 14x14 check box cell (crop 156,187,14,14) with the
shipped `checkbox-normal` slice re-derived by `render_slices` from the same SVG, plus the 1px
`#DDDDDD` face ring around the cell, so a resampled, squashed, mis-mapped or forcibly-fallback
checkbox is red without a manual render pass. The applet render's capture, scripts and chrome
crops are unchanged, and the dialog capture is 480x360 with KWin centring the single kdialog
client, so the crops are measured placement values recorded in `docs/invariants.md` alongside
the `$HOME`-joined theme path.

**Validation gap:** real-run-needed — no offline path drew the rendered widget, so confirming
required the real bounded `kwin_wayland`+`kdialog` render the render pass and this run both
made; its offline pin is
`tests/test_render_surface.py::TestCheckboxDialogRender::test_draws_the_check_box_cell_1_to_1`,
which ties the rendered cell to the shipped art slice the Kvantum reference suite derives, and
the ledger raises ``REAL_RUN_NEEDED_BASELINE`` by one in the same change.

### The rendered window shows a 5px band of the decoration's centre tile below the title bar (found by the render pass 2026-10-29) — fixed 2026-10-30 by the bugfix role

Every window rendered through the theme shows five rows of the Aurorae decoration's centre tile
(`decoration-center`, `#FFFFFF` in the shipped art) between the 22px title bar and the window's
content. The reference shows one `#FFFFFF` row (the frame's inner highlight) and the content from
the next row, so each rendered window's content sits four rows lower than the Mac window's. The
render gate cannot see it: `tests/test_render_surface.py` byte-compares the title-bar strip
(candidate rows 0-21) and the 6px side and bottom border strips, and the band lies at rows 22-26,
inside the client area.

Reproduce with `make render` (or the pass's throwaway Qt-widget session:
`python3 /tmp/wpass/render.py OUT.png --kvantum --command '<app>'`, which installs into a scratch
data home, writes the theme's kwinrc/kdeglobals, runs `kwin_wayland --virtual` under
`dbus-run-session` and captures the active window with `spectacle -a`) and read the capture's
rows 22-26 at any x inside the frame.

**Observed output:** `python3 tools/sample.py render.png 100 24` → `255,255,255  #FFFFFF`, and the
content starts at row 27; `aboutsystem_betawiki.png` at (107, 48) → `221,221,221  #DDDDDD` (its
row 47 is the `#FFFFFF` highlight).

**Suspected cause:** the theme's `org.macos8.desktoprc` sets `[Layout] TitleEdgeTop=0` and
`TitleHeight=22` but omits `TitleEdgeBottom`, so Aurorae's default (5) applies and the client area
starts at `TitleHeight + 5` = 27 while the frame art paints a 22px title bar; the decoration's
centre tile shows through the five rows the client does not cover. Measured in the throwaway
session (client row at which the content starts): `TitleHeight=22` → 27, `TitleHeight=17` → 22,
`TitleHeight=10` → 22 (the SVG's 22px top-margin hint floors it), `TitleEdgeTop=5` → 32, and
`TitleEdgeBottom=0` → 22 with the window exactly 5 rows shorter (104 → 99 rows). `BorderTop=6` or
`27`, `ButtonMarginTop=0`, `BorderSize=None` and a 17px top-margin hint change nothing. Patching
the installed `decoration-center` tile to `#FF00FF` turns exactly rows 22-26, x=6..122 magenta, so
the band is the decoration's tile, not the application's background. `docs/invariants.md`'s
aurorae row and `tests/test_aurorae_rc.py` treat the rc's title height and border widths as the
reference-derived geometry, which the render contradicts.

**Review resolved 2026-10-30 by the director role:** the open half of the review was which
`TitleEdgeBottom` value places the client at the reference position. Re-sampling the reference
settles it: `aboutsystem_betawiki.png` at x=250 and x=60 shows the title band ending in its black
rule at row 46 (`#000000`), then exactly one `#FFFFFF` row at 47, then the `#DDDDDD` content from
row 48 — one white row, matching the white `decoration-center` tile the band shows today. So the
note's original candidate `TitleEdgeBottom=0` is wrong: it puts the client at row 22, one row
above the reference, and erases the highlight row. The reference-derived value is
`TitleEdgeBottom=1`: the client begins at `TitleHeight + 1` (row 23), leaving exactly one row
where the frame's white centre tile shows as the highlight, and the fix removes four rows of band.
The title bar itself does not move (`TitleHeight` and the rows 0-21 strip are untouched; the side
and bottom border strips keep their `Border*` insets); the rendered window is four rows shorter
correspondingly. Fix: add `TitleEdgeBottom=1` to `[Layout]`; pin it in
`tests/test_aurorae_rc.py::TestRc::test_layout_metrics_match_reference` by re-deriving the one-row
white gap from the reference; and extend `tests/test_render_surface.py` to byte-compare the
capture's rows 22-26 against the reference's first client rows so the band cannot return.

**Fixed:** the rc's `[Layout]` now sets `TitleEdgeBottom=1`; the rc test re-derives the one-row
white gap from the reference and the render gate's TestRender::test_first_client_rows_match_the_reference
byte-compares the capture's rows 22-26 against the reference's rows 47-51 (one `#FFFFFF`
highlight row, then the `#DDDDDD` content face), so the tile band cannot return.
**Validation gap:** real-run-needed — no offline test covered rows 22-26 inside the client area,
so both confirming the band and confirming the one-row gap needed a real headless render.

### CI parity cannot run its Python matrix in the local worktree (found by the ci role 2026-10-29) — fixed 2026-10-30 by the feature role

The CI workflow ran `make check` and `make check-references` under a two-version matrix
(`['3.10', '3.12']`), which no local run could provision: this environment offers only
Python 3.13.5, and no 3.10/3.12 interpreter, version manager or container runtime is
installed, so the matrix job stayed unverified in the local worktree (observed:
`ls /usr/bin/python3.*` → `/usr/bin/python3.13`).

Fixed by the user's 2026-10-30 parity decision, implemented in the "CI runs one interpreter,
Python 3.13" plan: the workflow now pins the single interpreter `['3.13']` — the development
version, so `make check` and `make check-references` run under exactly the interpreter CI
runs — while the Makefile's run-time floor of Python 3.10 or newer keeps its check and the
workflow no longer exercises a second interpreter (the accepted trade-off).

### The rendered check box indicator is a resampled 13x13 square, not the reference's crisp 12x12 (found by the render pass 2026-10-29) — fixed 2026-10-30 by the bugfix role

A `QCheckBox`'s indicator (e.g. kdialog's `--dontagain` check box) renders 13x13 with every band
blended: the outline `#212121` instead of `#000000`, the top/left highlight `#FAFAFA` instead of
`#FFFFFF`, the bottom/right shadow `#949494` instead of `#888888`, and the two corners the
reference leaves as the face colour painted dark (`#030303`, `#010101`). The reference's Get Info
"Locked" box and the shipped `checkbox-normal` art are crisp 1px bands of
`#000000`/`#FFFFFF`/`#DDDDDD`/`#888888`; `tests/test_kvantum_checkbox_reference.py` passes, so the
art is right and only the rendered pixels differ.

Reproduce with a throwaway session: `kdialog --title "Test" --warningyesno "Delete?"
--dontagain /tmp/kde-dontagain:test`, then dump the indicator region.

**Observed output (2026-10-30 re-run):** the resampled box spans x=12..25 but only y=75..87
(14 columns, 13 rows): row 75 `030303 2E2E2E 212121 … 121212 010101`; row 76
`2E2E2E FEFEFE FAFAFA … D7D7D7 111111`; rows 77-85 `212121 FAFAFA DDDDDD … 949494 191919`;
row 86 `121212 D7D7D7 949494 … 898989 202020`; row 87 `010101 111111 191919 … 1F1F1F 030303`.

**Suspected cause:** the shipped `checkbox-normal` canvas is 14x14 while Kvantum draws the
indicator at its own computed size (13x13 here), so the art is resampled and its 1px bands blend
with the face. Patching the installed theme's `checkbox-normal` outline to `#FF00FF` renders it as
`#FF03FF`/`#FD21FD` at the edges — the art is drawn, scaled — so the fix is the canvas size or the
indicator size, not the element mapping.

**Decision (user, recorded by the director role 2026-10-30): render larger and take the exact
pixels** — keep the 14x14 canvas and make Kvantum draw it 1:1, not shrink the art to the
reference's 12x12.

**Fix (bugfix role 2026-10-30):** `%General check_size=14` in `org.macos8.desktop.kvconfig`. The
decision's stated knob, `[CheckBox] indicator.size`, is inert for this: upstream 1.1.4 returns
`tspec_.check_size` from `pixelMetric(PM_IndicatorWidth)`/`PM_IndicatorHeight` for checkbox
options and renders `PE_IndicatorCheckBox`'s interior art into that rect, consulting no section
size — the compiled-in default is 13 (`themeconfig/specs.h`), the 13 that resampled the canvas.
Both keys were rendered in the throwaway session during the fix: `indicator.size=14` and even
`indicator.size=6`/`indicator.element=checkbox` were all pixel-identical to the broken baseline,
while `check_size=14` draws the box crisp. The rendered indicator (x=12..25, y=75..88) is the
reference-derived raised square across all 196 pixels (outline `#000000`, highlight `#FFFFFF`,
face `#DDDDDD`, shadow `#888888`, the two face-coloured corners) surrounded by the flat window
face — the canvas at 1:1, the same arrangement `tests/test_kvantum_checkbox_reference.py`
derives — and the rendered box is the full 14x14 canvas, two pixels larger than the reference's
12x12 view pixels by the render-larger choice. `check_size` also sizes the radio indicator,
whose `radio-*` canvases are 14x14 as well, so they render 1:1 from the same pin.
`tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference::test_config_draws_the_indicator_at_the_canvas_size`
fails against a config without the pin (`None != "14"`) and pins the value to the canvas side it
re-derives from the art; `tests/test_kvantum_config.py::TestValueKeys` exhaustively pins
`check_size=14` through `support.kvantum_config_spec.VALUE_KEYS`.

**Validation gap:** real-run-needed — no offline path drew the indicator, so confirming required a
real bounded `kwin_wayland`+`kdialog --dontagain` render this run; the offline pin of the same
bound is
`tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference::test_config_draws_the_indicator_at_the_canvas_size`,
which ties the engine's `check_size` knob to the canvas side re-derived from the art, and
`docs/invariants.md` records the upstream sources the knob's behaviour was read from.

### PNG chunk parsing accepts a lowercase reserved type bit — fixed 2026-10-29 by the bugfix role

**Symptom:** PNG chunks with a lowercase third type letter were accepted as valid unknown ancillary chunks.

**Reproduce:** Insert a CRC-valid `abca` chunk after IHDR in a valid PNG and decode it; before the fix, decoding succeeds.

**Cause:** Chunk framing checked that all four bytes were alphabetic but did not enforce PNG's uppercase reserved third letter.

**Validation gap:** none — a regression test reproduced successful decoding before the fix and now checks the parser's rejection.

### The CI dependency setup requires passwordless sudo in the local runner (found by the ci role 2026-10-29) — fixed 2026-10-29 by the bugfix role

**Symptom:** The workflow's Plasma render-tool installation step tried to use `sudo` when any of its render tools were missing, even where the remaining tools were already available.

**Reproduce:** With `dbus-run-session` and `spectacle` on `PATH` but one of the other render tools missing, run the `Install the Plasma render tools` step from `.github/workflows/ci.yml` where `sudo` requires a password.

**Cause:** The package-install skip condition checked only `dbus-run-session` and `spectacle`.

**Fix:** Skip package installation only when all five render tools are available.

**Validation gap:** none — the workflow condition was pinned by the existing workflow test, which failed before the change and passed after it.

### The parallel coordinator accepts a forged empty-run summary from a started test (found by the bugfix role 2026-10-28) — fixed 2026-10-28 by the bugfix role

A test printing `Ran 0 tests` and `NO TESTS RAN`, flushing stdout and calling
`os._exit(5)` makes the coordinator pass despite its verbose log showing a
started test. Reproduced by
`TestCoordinator::test_a_forged_no_tests_ran_summary_fails_the_run`.

The empty-run verdict now also requires the absence of the verbose per-test
marker. A contradictory log fails with a diagnostic naming the started test
and empty-run summary. The regression failed with the original acceptance
condition (exit 0) and passed with the guard (exit 1); the coordinator module's
tests pass, including genuine empty modules and bare exit-5 failures.

**Validation gap:** no-fake — Confirmation needed a scratch test module that prints the empty-run markers, flushes stdout and exits 5 after its verbose test line has been written.

### The parallel coordinator prints the next section's header onto a worker log that never ends its last line — fixed 2026-10-27 by the bugfix role

- Symptom: a worker that dies mid-print (an `os._exit(1)` inside a test, with
  the verbose runner's partial `... ` line the last thing it wrote) leaves a
  log whose last line never ends, and `_print_results` wrote the next
  section's `===== ... =====` header verbatim after it — the two landed on one
  line, so the run's module sections stopped being diffable, which the
  coordinator's docstring and the `docs/invariants.md` row both promise.
- Reproduce: a scratch suite of `test_boom.py` (whose test calls
  `os._exit(1)`) and `test_ok.py`, run through `python3 tools/check_parallel.py
  --tests-dir <scratch>`: the boom section's captured output and the ok
  section's header print as one glued line
  (`test_boom (test_boom.T.test_boom) ... ===== test_ok: exit 0 =====`).
- Cause: `_print_results` wrote each log with `sys.stdout.write(log_text)`
  and no separator, assuming every log ends on a line break.
- Fix: a log not ending in a break is closed with one — `check_parallel`
  writes a newline after any log whose text does not already end with one.
- Pinned by `tests/test_check_parallel.py::TestCoordinator`
  `::test_an_unterminated_log_never_merges_with_the_next_section`.

**Validation gap:** no-fake — the suite had no fixture module whose worker
  log ends without a line break, so confirming it needed a manufactured
  module dying mid-print through `os._exit(1)`
  (`tests/test_check_parallel.py::TestCoordinator`
  `::test_an_unterminated_log_never_merges_with_the_next_section`).

### The parallel coordinator trusts a worker's bare exit 5 as `ran no tests`, so a module that dies of its own os._exit(5) skips its tests silently while the same tree fails `unittest discover` (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** an earlier fix today taught `tools/check_parallel.py` to pass a
worker whose exit status was 5 (unittest's NO TESTS RAN) as a
pattern-matched module that collects no tests. The status alone is not
evidence: a module whose test dies of its own `os._exit(5)` (intended
exit or not) also exits 5 with its tests never finished, so the
coordinator printed a fake `ran no tests` verdict and passed the whole
run while silently skipping that module — while the serial
`unittest discover` path that `make check CHECK_PARALLEL=0` keeps fails
on the same tree (its whole process exits 5).

**Reproduce:** a scratch tests directory holding `test_boom.py` (a test
whose body calls `os._exit(5)`) and `test_ok.py` (one passing test):
the parallel coordinator exited 0 and printed `===== test_boom: ran no
tests (unittest's NO TESTS RAN, exit 5) =====`, while
`python -m unittest discover -s <that dir>` exited 5 on the same tree.

**Fix:** `_print_results` now requires exit 5 to carry unittest's printed
proof — the worker log must contain both `Ran 0 tests` and
`NO TESTS RAN` — before the run passes the module as test-less. An
exit 5 without that summary is reported verbatim
(`exit 5 but the log shows no unittest NO TESTS RAN summary`) and fails
the run like any other failed module.

**Validation gap:** no-fake — the repo's `tests/` holds no module that
dies of its own `os._exit(5)`, so the real suite could not surface the
forged-pass; a scratch directory with such an exit-5 fixture module
reproduced it (parallel exit 0, serial exit 5), and that fixture now
pins the verdict.

### The parallel coordinator fails a pattern-matched module that collects no tests as `exit 5`, so the same tree passes `make check CHECK_PARALLEL=0` and fails the default run (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** `tools/check_parallel.py` reported a worker with a bare
`exit 5` verdict and failed the whole run whenever a pattern-matched
test module collected no tests. On Python 3.12 and later, `python -m
unittest -v <module>` on such a module exits 5 (NO TESTS RAN), but the
serial `unittest discover` path that `make check CHECK_PARALLEL=0` keeps
gets nothing from that module and passes — so one tree could pass the
serial run and fail the parallel default. The suite's package-module
guard keeps a test-less package's `__init__.py` out of the workers
(docs/invariants.md), but a test-less *file* module still matched the
pattern and still became a worker, so the exit-5 path stayed reachable.
Latent: no module in the repo's `tests/` collects zero tests today, so
today's check was unaffected.

**Reproduce:** a scratch tests directory holding `test_empty.py`
(just `import unittest`) and `test_ok.py` (one passing test): the
parallel coordinator printed `===== test_empty: exit 5 =====`, the
summary `check: 2 modules, 1 module failed`, and exited 1, while
`python -m unittest discover -s <that dir>` exited 0 on the same tree.

**Fix:** `_print_results` now treats a worker's exit status 5 as its own
outcome — the section reads `ran no tests (unittest's NO TESTS RAN,
exit 5)` and the run passes, matching the serial run, where a
test-less module contributes nothing. Any other nonzero status still
fails the run, and the failure summary notes how many modules ran no
tests when the run failed for another reason.

**Validation gap:** no-fake — the repo's `tests/` holds no pattern-matched
module that collects no tests, so the real suite could not surface the
divergence; a scratch directory with a test-less module reproduced it,
and that fixture now pins the ran-no-tests outcome.

### The parallel coordinator derives each worker log from the module's _-joined stem, so two modules sharing one _-joined log stem write one file and each result section prints the other module's output (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** `tools/check_parallel.py` named each worker's log after the
module's dotted name with every dot replaced by an underscore, and two
distinct modules can collapse to the same stem: a package's
`test_a.test_b` module and a top-level `test_a_test_b.py` both give
`test_a_test_b.log`. Both workers would open that one file for writing
(truncating and interleaving each other's output), and the result sections
would print the same file twice, so one module's section showed another
module's run — a passing module could be reported with a failed module's
traceback or a failed module's output could be hidden entirely. Latent: no
pair of modules in the repo's `tests/` collapses to one stem today, so
today's check was unaffected.

**Reproduce:** a scratch tests directory holding a `test_a/` package
(`__init__.py` plus `test_b.py` defining `TestOk.test_ok`) and a top-level
`test_a_test_b.py` defining `TestOther.test_also`: both modules match the
default `test*.py` pattern, both ran as workers, and the
`===== test_a.test_b =====` section printed `test_also
(test_a_test_b.TestOther.test_also)` — the other module's output.

**Fix:** `_log_paths` now assigns each module a unique log path under the
scratch directory. A module whose natural `_-joined` stem is unclaimed keeps
it; a later collision takes a `_<n>` suffix, checked against every module's
natural stem and every already-assigned suffix so a third module's own
natural log name (`test_a_test_b_2.log`) is never claimed. Discovery order
is sorted, so the names are stable across runs.

**Validation gap:** no-fake — the repo's `tests/` holds no pair of modules
whose names collapse to one log stem, so the real suite could not surface
the collision; a scratch directory with such a pair reproduced it, and that
fixture now pins the unique-log guarantee.

### The test-suite coordinator's module discovery never runs a package's own module, so tests defined in the package's __init__.py silently don't run (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** `tools/check_parallel.py`'s `discover_modules` documented that it
returns "the dotted module names ``unittest discover`` would import" and that
discovery recurses into packages "exactly as ``unittest discover`` does", but
it only recursed: real discovery (``TestLoader._find_test_path``) also imports
each package's own module before recursing and loads the tests its
``__init__.py`` defines. The parallel coordinator therefore never ran a
package as its own worker, so tests defined in a package ``__init__.py`` ran
under the serial `make check CHECK_PARALLEL=0` path but silently did not run
under the default parallel path, and an import error in a package
``__init__.py`` would not fail the parallel run either. Latent: no package in
the repo's `tests/` defines tests in its `__init__.py` today, so today's
check was unaffected.

**Reproduce:** a scratch tests directory holding a `pkgx/` package whose
`__init__.py` defines a test and whose `test_ok.py` defines another:
``python -m unittest discover -s <dir> -p 'test*.py'`` runs 2 tests while
`discover_modules(dir, 'test*.py')` returned `['pkgx.test_ok']`, so the
coordinator spawned a worker only for the file module.

**Why the fix is a guard, not a wider module set:** returning every package
would spawn a worker for each, and a worker run on a test-less package exits
5 (``NO TESTS RAN``) — the first full `make check` with that change failed on
`support`, `svg_assertions` and a probe package — while static discovery
cannot tell which packages bear tests. The suite-structure guard
(`tests/test_suite_discovery.py`) already pins the other three
"discovery silently skips it" mistakes, so it gained the fourth:
`test_no_package_init_collects_tests_or_load_tests` loads every package
``__init__.py`` the way discovery does and fails naming one that collects
cases or defines ``load_tests``, with
`test_a_package_init_that_collects_tests_is_reported` proving it bites.

**Validation gap:** no-fake — the repo's `tests/` holds no package whose
`__init__.py` defines tests, so the real suite could not distinguish the two
discovery behaviors; a scratch directory with such a package reproduced it,
and that fixture now pins the guard.

### The test-suite coordinator's module discovery returns modules `unittest discover` would never import, so a stray file matching a broad pattern becomes a corrupt module name and a spurious failed run (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** `tools/check_parallel.py`'s `discover_modules` documented
"exactly as ``unittest discover`` does" but gated a file only on the
pattern match. Real discovery first gates every file on unittest's
``VALID_MODULE_NAME`` (a valid Python identifier ending in .py), then on
the pattern. Two divergences followed: under a pattern not ending in
.py (such as ``-p 'test*'``) a stray ``testaux.pyz`` was returned with
its name corrupted to ``testaux.`` by the ``entry[:-len('.py')]`` slice,
and ``python -m unittest -v testaux.`` fails to import it, so one stray
file turned into a spurious failed `make check`-style run (exit 1,
"1 module failed"); under the default ``test*.py`` pattern a hyphenated
``test-x.py`` was returned as the module ``test-x``, which real discovery
skips entirely and which our worker then runs as an import of nothing.
The repo's own `tests/` held no such file, so today's check was
unaffected — the bug was latent in the coordinator's discovery, not in
its supervision.

**Reproduce:** a scratch tests directory holding a passing `test_ok.py`,
a `testaux.pyz` and a `test-x.py`: `python -m unittest discover -s
<dir> -p 'test*'` loads only `test_ok`, while `discover_modules(dir,
'test*')` returned `['test-x', 'test_ok', 'testaux.']` and feeding
``testaux.`` to a worker failed the run. Pinned by the new
`TestDiscovery.test_files_unittest_cannot_load_are_skipped`, which fails
against the unfixed discovery and passes after.

**Cause:** the file branch of the scan checked only
`fnmatch.fnmatch(entry, pattern)` before slicing off ``.py``; it now also
requires unittest's ``VALID_MODULE_NAME`` gate (`[_a-zA-Z]\w*\.py$`, the
same regex `TestLoader._find_test_path` applies before matching) so only
loadable module files are returned.

**Validation gap:** no-fake — the repo's `tests/` contains no file that
matches ``test*`` without being a loadable module, so the real suite
could not distinguish the two discovery behaviors; a scratch directory
with a `testaux.pyz` and a `test-x.py` reproduced it, and that fixture
now pins the gate.

### The `@-moz-document` body scanner treats a backslash as an ordinary character, so an escaped quote in a body value merges every later rule into that body (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** in `tests/test_firefox_content_theme.py`, `at_rule_bodies` scanned a
`@-moz-document` body without the backslash handling the sibling scanners in
`tests/support/gtk_css.py` document. A body value holding an escaped quote
(such as `content: "\""`) ended its string at the escaped quote, reopened a
string at the closing quote, and then swallowed every later brace as quoted
text: the scanner merged the at-rule's remaining rules into one body and
reported the at-rule's own closing brace as part of it, so the sheet tests
would under-validate any future sheet line carrying an escaped quote. The
shipped `userContent.css` contains no backslash, so today's suite still
passed either way — the bug was latent in the validator, not in the theme.

**Reproduce:** run `tests.test_firefox_content_theme.at_rule_bodies` over a
sheet whose `about:downloads` body opens with `content: "\""` and is followed
by a second rule; before the fix the body contains the at-rule's own closing
`}` and the second rule is unreachable as a separate rule, after the fix the
body ends exactly at the at-rule's closing brace. Pinned by the new
`TestAtRuleBodies` cases, which fail against the unfixed scanner.

**Cause:** the scan loop matched quotes and braces but never a backslash, so
an escaped quote closed the open string one character early. It now tracks an
`escaped` token like `strip_comments`, `_rule_blocks`, `_split_declarations`
and `_split_selector_list` already do: a backslash keeps the character after
it inside the string.

**Validation gap:** no-fake — no shipped sheet line carries a backslash, so
no existing fixture could exercise the scanner's escaped-quote path; a
synthetic sheet with a `content: "\""` value reproduced it, and that fixture
now pins the handling.

### The unused-import scanner flags a re-export grown by `__all__.extend` or `__all__.append` as a dead import (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom:** a module whose `__all__` grows by method call (`__all__ = []` then `__all__.extend(["os"])` or `__all__.append("os")` — the call form of the re-export hub) gets `path:line: unused import os` from the tree-clean assertion, although `__all__` names the import.

**Reproduce:** write `import os\n\n__all__ = []\n__all__.extend(["os"])` into a synthetic tree and run `support.unused_imports.unused_imports`; the finding appears before the fix and not after.

**Cause:** `_scan_module` collected the `__all__` strings only from `ast.Assign`, `ast.AugAssign` and `ast.AnnAssign` statements; a method call is an `ast.Expr(ast.Call)` and fell through, so its strings were never added to the allowance. Now a call whose receiver is the bare name `__all__` through `append`, `extend` or `insert` (the list methods that add entries; `remove` and `sort` add nothing) contributes its string constants too.

**Validation gap:** no-fake — the synthetic-tree fixtures in the scanner's
suite had no `__all__`-grown-by-method-call case, so the tree-clean assertion
could not exercise the missed call form; a scratch one-module tree reproduced
it, and the two new fixtures now pin the add-call allowance and the
remove-call non-allowance.

### The unused-import scanner emits a module's findings in `ast.walk` order, not the documented path-then-line sort — fixed 2026-10-27 by the bugfix role

- Symptom: the tree-clean assertion's failure message can list a module's
  offenders out of line order (a nested or block-nested import trailing its
  later top-level imports), although `unused_imports` documents "Findings are
  sorted by path, then line".
- Reproduce: a scratch tree whose module reads `def f():\n    import b\nif
  True:\n    import a\nimport c\n` returned findings for lines 5, 2, 4 —
  `ast.walk` visits statements breadth-first, so block-nested imports trail
  the module's top-level ones regardless of line numbers.
- Fix: `tests/support/unused_imports.py` collects `(path, line, name)` tuples
  and sorts them before formatting, restoring the documented order.

**Validation gap:** none — the closest tag: no existing scanner test pinned
the documented path-then-line order, but a scratch synthetic tree reproduced
the mis-ordering deterministically and the new ordering test pins it, so
nothing outside the suite was needed to confirm the failure.

### The unused-import scanner flags a submodule import that only feeds a package facade's re-export (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

Symptom: with `pkg/__init__.py` holding `from .mod import thing`,
`pkg/mod.py` holding the source re-export `from .thing import thing`, and a
consumer reading `from pkg import thing`, the scanner reported
`pkg/mod.py:1: unused import thing` even though the facade's import is
exactly the import-from-elsewhere the re-export allowance keeps: the
consumer reaches mod.py's binding only through the package, which no
scanned module names directly.
Reproduce with
`tests/test_no_unused_imports.py::TestNoUnusedImports::test_a_package_facade_re_export_keeps_the_submodule_import`;
no scanned module in the tree imports a name solely to feed a package
facade today, so `make check` never fired.
Suspected cause: the scan skipped `__init__.py` facades entirely, so their
`ImportFrom` statements never entered `imported_from`, and a relative
statement's module string was recorded as written (`thing` from
`from .thing import thing`) so it matched no module's dotted candidates.
Fix: walk the facades too and register every `ImportFrom` statement with a
new `_resolved_module()` that resolves `level` against the file's package
(`from .thing import thing` in `pkg/mod.py` sources `pkg.thing`).
Facades stay out of the flagged scan as before.

**Validation gap:** no-fake — confirming the false positive needed a
synthetic tree whose package facade re-exports a name no scanned module
names directly (closer match than `none`: no in-tree module imports
solely to feed a facade, so no real-tree scan could exercise the chain);
the new fixture
`test_a_package_facade_re_export_keeps_the_submodule_import` pins the
facade-fed re-export.

### The unused-import scanner counts a re-assignment of an imported name as a read of it (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

Symptom: with `pkg/mod.py` holding `import os` and its only occurrence of
the name being the re-assignment `os = None`, the scanner reported
nothing even though nothing reads the import. The same masking held for
`del os` — a write context is not a use either — so a Store-only or
del-only name hid a genuinely dead import from the tree-clean assertion,
while `os = os.sep` (a Load in the value) correctly kept it.
Reproduce with the two synthetic-tree cases in
`tests/test_no_unused_imports.py::TestNoUnusedImports`
(`test_a_reassignment_of_the_imported_name_keeps_the_flag`,
`test_a_del_of_the_imported_name_keeps_the_flag`); no module in the tree
re-binds an imported name without ever reading it, so `make check`
never fired.
Suspected cause: `_scan_module()` added every `ast.Name` id to the
read set regardless of `ctx`, so an `ast.Store` (or `ast.Del`) context
counted as a read.
Fix: collect only `ast.Load` contexts in `_scan_module()`; a write context
does not consume the imported value, so the finding resurfaces.

**Validation gap:** no-fake — confirming the mask needed a synthetic
tree whose module re-binds an imported name without reading it (closer
match than `none`: the real tree has no such module, so no in-tree scan
could exercise the write-context path); the two new fixtures pin the
re-assignment and the `del` forms.

### The unused-import scanner misses an annotated `__all__` assignment when deciding the re-export allowance (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

Symptom: with `pkg/mod.py` holding `import os` and re-exporting it through the
annotated form `__all__: list[str] = ["os"]`, the scanner reported
`pkg/mod.py:1: unused import os` even though the `__all__` entry names it —
while the plain form `__all__ = ["os"]` kept the import. A bare
`__all__: list[str]` declaration without a value names no strings, so it
still flags.
Reproduce with the two synthetic-tree cases in
`tests/test_no_unused_imports.py::TestNoUnusedImports`
(`test_an_annotated_all_entry_re_exports_the_import`,
`test_an_annotated_all_declaration_without_a_value_keeps_the_flag`); the
real tree stays clean either way, so `make check` never fired.
Suspected cause: `_scan_module()` matched only `ast.Assign` and
`ast.AugAssign` when hunting statements that assign `__all__`, dropping
`ast.AnnAssign` — so the annotated form's strings never reached the
`dunder_all` set the allowance checks.
Fix: accept an `ast.AnnAssign` targeting `__all__` that carries a value; a
declaration without a value contributes no strings, as before.

**Validation gap:** no-fake — the synthetic-tree fixtures in the scanner's
suite had no annotated-`__all__` case, so the tree-clean assertion could not
exercise the missed assignment; a scratch one-module tree reproduced it, and
the two new fixtures now pin the annotated assignment and the bare
declaration.

### The unused-import scanner's re-export allowance matches an aliased import by its binding name instead of the name imported (found by the bugfix role 2026-10-27) — fixed 2026-10-27 by the bugfix role

Symptom: with `pkg/mod.py` holding `import os` and `pkg/user.py` holding
`from pkg.mod import os as platform` plus a read of `platform`, the scanner
reported `pkg/mod.py:1: unused import os` even though `user.py` reads it
through the alias — and the mirror case (`from pkg.mod import sys as os`)
wrongly kept a dead import. Reproduce with the two synthetic-tree cases in
`tests/test_no_unused_imports.py::TestNoUnusedImports`
(`test_an_aliased_import_from_here_keeps_the_imported_name`,
`test_an_aliased_import_keeps_only_the_name_actually_imported`); the real
tree stays clean either way, so `make check` never fired.
Suspected cause: the re-export pass in `unused_imports()` built its
`(module, name)` pairs with `_alias_names()`, which returns the *binding*
(`alias.asname or alias.name`) the flagging loop needs — not the name the
import statement actually pulls from the source module.
Fix: record `alias.name` (skipping `import *`) in the re-export pass; the
flagging loop keeps `_alias_names()` for its own module's reads.

**Validation gap:** no-fake — the synthetic-tree fixtures in the scanner's
suite had no aliased cross-module re-export case, so the tree-clean assertion
could not exercise the broken matching; a scratch two-module tree reproduced
it, and the two new fixtures now pin both directions.

### CI's `make check` runs no rendered-pixel comparison: the whole `TestRender` class skips because the workflow installs none of the five Plasma render tools (found by the steward role 2026-10-27) — fixed 2026-10-27 by the bugfix role

**Symptom.** `.github/workflows/ci.yml` runs exactly `make check` and
`make check-references` (pinned to that two-run list by
`tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_runs_public_checks_with_materialized_assets`),
and its other steps are only checkout with LFS and setup-python: no step installs
`kwin_wayland`, `dbus-run-session`, `plasmawindowed`, `spectacle` or
`plasma-apply-colorscheme`, and `make check-references` only validates the reference
set. The suite's one live rendered-pixel check,
`tests/test_render_surface.py::TestRender`, is wrapped in
`@unittest.skipUnless(all(shutil.which(tool) for tool in REAL_TOOLS), ...)` over exactly
those five tools, so wherever any of the five is absent the entire class reports
skipped and the job still goes green. The standard `ubuntu-latest` runner image ships
none of the Plasma tools, so the render gate that byte-compares the title-bar strip,
the close, zoom and collapse boxes and the side and bottom border strips against
`aboutsystem_betawiki.png` (README, "Fidelity checking") never exercises in CI: a
regression in the rendered chrome merges with CI green and is caught only on a host
where the gate runs (this project's merge host has all five on PATH). The skip line
is visible in the verbose unittest log, so the gap is discoverable but not surfaced
by the job's status.

**Reproduce.** On any host with none of the five tools on PATH — or by reading the
two files, which is the CI situation:

```
PYTHONPATH=tests python3 -m unittest tests.test_render_surface.TestRender -v
```

prints `skipped 'needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and
plasma-apply-colorscheme on PATH'` instead of running the pixel tests; every step of
`.github/workflows/ci.yml` can be grepped for the five tool names with no hit.

**Suspected cause.** Not a code defect but a workflow-versus-gate drift: the class
skips deliberately so `make check` stays runnable without a Plasma session, but no
CI step compensates for the skip, so a green CI run is compatible with zero
rendered-pixel coverage. Remediation belongs to a plan (for example a CI job with
the KDE runtime running the render gate, or a CI guard that fails when
`TestRender` skipped, or a recorded carve-out in README's "Fidelity checking"), not
to a one-line fix.
Redemption (2026-10-27, bugfix role): the check job now installs the render gate's
tools itself and, once installed, checks each of the five on `PATH`, so the
workflow's own step, not the suite's silence, reports a missing render tool and
`TestRender` runs on CI. Package names for ubuntu-latest are grounded on the
runner release's Launchpad package pages (`kwin-wayland`, `plasma-workspace`,
`spectacle`, `dbus` all record a 200 on `ubuntu/noble/amd64/<name>`); the
`dbus-run-session` split out of `dbus` on newer Debian-family releases is
covered by a conditional `dbus-daemon` install. Pinned by
`tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_installs_and_verifies_the_plasma_render_tools`.

**Validation gap:** none — the failure left no trace in the job status (CI
stayed green with the whole rendered-pixel gate silently skipped; that is a
genuine no-observability gap, but this record is retired instead of growing the
capped no-observability ledger): the gap was confirmed by reading the workflow
and the `TestRender` skip guard, and the test-side reproduction
`tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_installs_and_verifies_the_plasma_render_tools`
fails on the tool-free workflow and passes after the install step lands.

### The selector matcher rejects a hex escape's whitespace terminator in an unquoted attribute value (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/selector_matching.py`'s `_ATTRIBUTE` regex matched an unquoted
attribute value with ``(?:[^\]\s\"'\\]|\\.)+``: each whitespace ended the
value, so a hex escape's optional whitespace terminator (needed to separate
fewer than six escape digits from a following hex digit) sat between the value
group and the trailing `\]`, the attribute syntax no longer parsed and the
selector matched no element — while the quoted form of the same escape
(`[title="a\22 b"]`) already matched. Before the fix,
`matches('[title=a\22 b]', element with title a"b)` was wrongly `False`. The
fix adds a hex-escape alternative (backslash, one to six hex digits, one
optional `CSS`-1 whitespace terminator) before the `\\.` pairing inside the
unquoted group, so the terminator belongs to the escape and the value continues
after it; a hex escape without a terminator still ends at the first non-hex
digit, and escape decoding is unchanged.

Regression test:
`tests/test_selector_matching.py::TestSelectorMatching::test_a_hex_escape_with_its_whitespace_lives_in_an_unquoted_value`
(failed before the fix; also pins that the terminator does not reach the value
and that a terminator-free hex escape keeps its minimal parse).

**Validation gap:** none — the failure was silent fail-closed (a sheet with
such a selector simply matched nothing, a genuine no-observability gap, but
this record is retired instead of growing the capped no-observability ledger):
nothing failed until the case was derived by hand and given a repro test;
before the fix a scratch `matches` call showed the wrong lower end and the new
test failed, the same call passes after.

### The GTK sheet scanner treats a brace inside an unquoted url() value as a block delimiter (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/gtk_css.py`'s `_rule_blocks` tracked quoted strings and
backslash escapes but not parentheses, so a brace inside an unquoted
`url(...)` token (its `{`/`}` are CSS url code points) paired the pending selector with half the
declaration and reported the rest as a malformed declaration of a bogus
selector. Before the fix, `parse_css('a { background-image:
url(data:image/svg+xml,<g {x}>); color: red; }')` raised `ValueError ... in
selector 'background-image: url(data:image/svg+xml,<g': 'x'`. The fix follows
`_split_declarations`, which already treated parentheses as value grouping at
the declaration level: the block scanner now counts parentheses (an unmatched
`)` is not tracked, mirroring the stray-parenthesis rule there), so a brace
inside any `(...)` is text, while quoted strings inside parentheses keep
their normal string semantics.
`url(...)` appears in real GTK/Firefox sheets, and the declaration scanner
already pinned the quoted-url `;` case, so the block-level gap was the
remaining discrepancy between the two scanners.

Regression tests:
`tests/test_gtk_css.py::TestRuleBlockSemantics::test_a_brace_inside_an_unquoted_url_value_is_text`
(failed before the fix; also pins that a brace in an attribute selector's
quoted value stays a selector) and
`...::test_a_stray_closing_parenthesis_does_not_hide_a_brace_either` (an
unmatched `)` must not swallow later block delimiters).

**Validation gap:** none — the rebuilt generator reproduced the failure with
a scratch `parse_css` call before the fix, and the new test failed before and
passed after.

### The shared GTK sheet parser invents a colour from a @define-color inside a quoted value (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/gtk_css.py` scanned the whole sheet for `@define-color` with one
regular expression, so a declaration such as
`a { content: "@define-color decoy #123456;"; }` both added a `decoy`
definition and removed the matched text from inside the string, leaving
`content: ""`. Before the fix, `parse_css('a { content: "@define-color decoy
#123456;"; }')` returned a `decoy` definition and the truncated value.

The scan now walks the sheet once and treats a quoted string (including a
backslash-escaped quote) as a token, mirroring the comment and block
scanners, so only a definition outside a string is returned or removed.

**Validation gap:** unclear-invariant — no test or invariant row said whether
a quoted value's `@define-color` text was a definition, so the quoted-string
rule had to be extended to the definition scanner and pinned in
docs/invariants.md.

### The test-side selector matcher rejects CSS escapes in attribute values (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

The matcher's attribute scanners tracked quotes but not backslashes, and its `_ATTRIBUTE` pattern had no escaped-character branch. A valid selector such as `[title="a\"b"]` therefore had its escaped quote read as the closing quote: `_attribute_spans` found no span, `_compound_is_supported` rejected the leftover brackets, and `matches` returned false for every element, including one whose `title` is `a"b`.

Reproduce with `element("button", attrs={"title": 'a"b'})` and `matches('[title="a\\"b"]', target)`; it returned false. `_is_escaped` now makes every scanner skip an escaped character, `_ATTRIBUTE` accepts `\\.` in quoted and unquoted values, and `_css_unescape` decodes the captured value (hex escapes and escaped characters).

**Validation gap:** unclear-invariant — the module docstring did not state whether CSS escapes were part of its subset, so the guarantee was reconstructed and added to `docs/invariants.md` and the unclear-invariant ledger.

### The selector matcher rejects CSS whitespace around an attribute selector (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `_ATTRIBUTE` pattern
required the attribute name, `=`, value and `]` to touch. CSS treats that
whitespace as insignificant, so valid selectors such as `[type = "arrow"]`
and `[ type ]` were judged outside the supported subset and matched no
element. The unquoted fallback also swallowed quotes: `[type="arrow" ]` was
reported as supported, but its value was compared as `"arrow" ` (quotes
included) and it too matched no element. The shipped Firefox sheet uses no
spaced attribute selector, so the gap was latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import matches, element; print(matches("[type = \"arrow\"]", element("button", attrs={"type": "arrow"})), matches("[type=\"arrow\" ]", element("button", attrs={"type": "arrow"})))'
```

printed `False False`; both selectors name the same attribute test as
`[type="arrow"]` and should match the element.

**Suspected cause.** `_ATTRIBUTE` had no `\s*` between the selector's parts and
its unquoted-value branch used `[^\]]+`, which could swallow a closing quote
and following whitespace instead of failing the match.

**Fix.** `_ATTRIBUTE` now allows CSS whitespace around the name, `=`, value and
closing bracket, and its unquoted branch excludes whitespace and quotes. New
test `test_attribute_selector_ignores_css_whitespace_around_its_parts` failed
on the spaced selectors and on the quoted unquoted values before the change
and passes after; it also checks each
spaced form against an element with a different value and one without the
attribute, and pins that an unquoted value carrying a quote is rejected. The
`test_selector_matching` module as a whole still passes.

**Validation gap:** none — no existing test carried a spaced or quoted
unquoted attribute selector (so no closer tag than `none` fits); a scratch
call and the new test reproduced the false rejection deterministically.

### The sheet parser treats a brace or comment marker inside a quoted string as structure (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/gtk_css.py`'s scanners did not know about quoted
strings. `_rule_blocks` counted a `{` or `}` inside a quoted value or selector
as a block delimiter, so `a { content: "}"; color: #111111; }` ended the rule at
the quoted brace and lost its later declarations, and `a { content: "{"; ... }
reported the quoted text as a selector. `strip_comments` removed a `/* ... */`
inside a quoted value, rewriting `content: "/* keep */"` to `content: ""`.
CSS strings are tokens, so those characters are literal. The shipped sheets
carry no such value, so the gap was latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.gtk_css import parse_css, strip_comments; print(parse_css("a { content: \"}\"; color: #111111; }")[1]); print(strip_comments("a { content: \"/* keep */\"; }"))'
```

printed `{'a': {'content': '"'}}` (the `color` declaration was lost) and
`a { content: ""; }`; the expected results keep the closing brace and the
comment marker in the value.

**Suspected cause.** `_rule_blocks` and `strip_comments` scanned characters
without tracking a quoted string (or a backslash escape), unlike
`_split_declarations`, `_split_selector_list` and `_collapse_whitespace`.

**Fix.** Both scanners now skip the contents of a quoted string, respecting a
backslash escape, so only a brace or `/*` outside a string opens or closes a
block or a comment. New tests
`test_a_brace_inside_a_quoted_string_does_not_pair_a_block` and
`test_a_comment_marker_inside_a_quoted_string_is_text` failed in the focused
run before the fix and pass after; the timing tests still bound both scanners
to well under a second on a hostile sheet.

**Validation gap:** none — no existing test carried a quoted brace or comment
marker, but a scratch `parse_css`/`strip_comments` call reproduced both
rewrites deterministically (so no tag beyond the closest one fits) and the new
tests pin them.

### The stylesheet parser collapses whitespace inside a quoted selector or value (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/gtk_css.py`'s `parse_css` normalized every
selector, declaration name and declaration value with
`" ".join(text.split())`. That is right between tokens, but it also rewrote a
quoted string: `[title="a  b"]` came back as `[title="a b"]`, a different
selector, and a block listing both came back as one rule whose declarations
merged; `content: "a  b"` lost a space from its value. A sheet test comparing
the parsed selector or value to the sheet then saw text the sheet does not
contain. The shipped sheets carry no such value, so the gap was latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.gtk_css import parse_css; print(parse_css("[title=\"a  b\"] { color: #111111; }")[1])'
```

printed `{'[title="a b"]': {'color': '#111111'}}`; the expected key is
`[title="a  b"]`.

**Suspected cause.** All three normalization sites used `str.split()`, which
treats whitespace inside a quoted attribute value or string as separators.

**Fix.** `_collapse_whitespace` scans quoted strings (honouring a
backslash-escaped character) and collapses only whitespace outside them;
`parse_css` uses it for the diagnostic selector label, declaration names,
declaration values and each selector of a group. New tests
`test_whitespace_inside_a_quoted_selector_value_is_preserved` and
`test_whitespace_inside_a_quoted_declaration_value_is_preserved` cover the
doubled spaces in a selector, in `content` and in a `url(...)`; the focused
run failed both tests before the fix and passes after.

**Validation gap:** none — no existing test carried a quoted doubled space,
but a scratch `parse_css` call reproduced the rewrite deterministically (so no
tag beyond the closest one fits) and the new tests pin it.

### The sheet parser splits a selector at a comma inside an attribute selector (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/gtk_css.py`'s `parse_css` splits a
selector group at every comma outside parentheses. A comma inside an
attribute selector's brackets is part of its value, so a valid selector such
as `[title="a,b"]` is cut into the fragments `[title="a` and `b"]`, neither
of which names a rule. A sheet test that expects the valid selector then sees
no such rule, and the parsed selector list differs from the sheet. No shipped
sheet carries such a value, so the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.gtk_css import parse_css; print(parse_css("[title=\"a,b\"], b { color: #111111; }")[2])'
```

printed `['[title="a', 'b"]', 'b']`; the expected result is
`['[title="a,b"]', 'b']`.

**Suspected cause.** `_split_selector_list` counted only parenthesis depth,
so it treated a comma in `[title="a,b"]`, `[title='a,b']` or `[title=a,b]`
as a selector-list separator and never noticed the square brackets or the
quoted value around it.

**Fix.** `_split_selector_list` now tracks quoted strings (including a
backslash-escaped quote), square-bracket depth and parenthesis depth, and
yields a comma as a separator only outside all three. Two nested selectors
such as `a:not(.x, .y)` still stay one selector, and a comma after a closed
attribute selector still splits the group. The new
`test_a_comma_inside_an_attribute_selector_does_not_split_the_group` covers a
double-quoted, a single-quoted and an unquoted value; the focused run failed
all three subtests before the fix and passes after.

**Validation gap:** none — no existing test carried a comma inside an
attribute selector, but a scratch `parse_css` call reproduced the split
deterministically and the new test pins it.

### The selector matcher ignores unrecognized text in a compound and over-matches it (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `matches` treats text it
does not recognize as if it were absent: `&` alone matches every element,
`a&b` and `a!` match an `<a>`, and `*&` matches any element. A tag or class
fragment after an attribute or a `:not(...)` was ignored in the same way:
`[title]a` matched a `box` carrying `title`, `.a[title]b` matched a `box` with
class `a` and `title`, and `:not(.b)*` matched every element. A scope test
could therefore pass a malformed selector as an over-broad match instead of
rejecting it. No selector in the shipped Firefox sheets carries such text, so
the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches; print(matches("&", element("box")), matches("a&b", element("a")), matches("[title]a", element("box", attrs={"title": "t"})), matches(":not(.b)*", element("box", classes=("a",))))'
```

prints `True True True True`; the expected result is `False` for each.

**Suspected cause.** `_compound_matches` only tested the tag, id, class,
attribute, `:hover` and `:not(...)` parts of a compound and ignored whatever
text remained. `_compound_is_supported` likewise never checked that the
text left after those parts was empty, so unrecognized text was accepted as a
supported compound. It also blanked each attribute or `:not(...)` span before
stripping the tag, so a tag or class fragment after either looked like a
leading one while `_compound_matches` ignored it.

**Fix.** `_compound_is_supported` keeps each attribute span as a `[]`
placeholder and each `:not(...)` span as a marker while it strips the optional
tag and every `#id`/`.class`, then rejects any text left after the placeholders
are removed. Unrecognized text, including a tag or class fragment after an
attribute or a negation such as `[title]a`, `[title]a.a`, `.a[title]b` or
`:not(.b)*`, is therefore rejected instead of read as absent. The supported
compound forms still pass. The new
`test_unrecognized_text_in_a_compound_matches_nothing` covers eleven malformed
selectors and the supported forms; the focused run failed those malformed
subtests before the fix and passes after.

Review also found that stripping `:hover` exposed a trailing `*` as a leading
tag. Hover spans now retain a marker too; the test additionally rejects
`:hover*`, `:hover*.a` and `:not(.b):hover*` while preserving valid hover forms.

**Validation gap:** none — the closest tag: no existing matcher test carried
unrecognized text in a compound, but a scratch call reproduced the false
matches deterministically, and the new test pins them.

### The selector matcher drops a leading or dangling combinator and over-matches a malformed selector (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `matches` reads a selector
with a leading, trailing or doubled combinator as if the combinator were absent:
`.a >`, `> .a` and `.a +` all match an element with class `a`, and `.a > > .b`
matches when `.a` is `.b`'s parent. A malformed selector in a scope test could
therefore pass an over-broad assertion -- including a sibling selector, which the
matcher documents as matching nothing -- instead of matching no element. No
selector in the shipped Firefox sheets is malformed (grep for a combinator before
`{`, after `,`/`{` or alone at the start of a line finds none), so the gap is
latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches; a = element("box", classes=("a",)); b = element("box", classes=("b",), parent=a); print(matches(".a >", a), matches("> .a", a), matches(".a +", a), matches(".a > > .b", b))'
```

prints `True True True True`; the expected result is `False` for each.

**Suspected cause.** `_split_selector` only recorded a combinator when at least
one compound had been seen (`if compounds`), so a leading combinator was dropped
and a trailing one stayed pending without becoming a step. A second combinator
overwrote the pending one, so `.a > > .b` collapsed to a single child step.
Neither `_selector_is_supported` nor `matches` rejected the result.

**Fix.** `_split_selector` now returns a third value, `misplaced`, which is true
for a combinator with no compound on one side (leading, trailing or doubled), and
both `_selector_is_supported` and `matches` reject a selector with it. A trailing
space is still not a combinator, so `.a > .b ` stays supported and matching. The
new `test_a_combinator_without_a_compound_on_both_sides_matches_nothing` covers
the five malformed selectors and keeps the whitespace case; pre-fix the focused
run failed all five subtests, and it passes after the fix.

**Validation gap:** none — the closest tag: no existing matcher test used a
leading, trailing or doubled combinator, but scratch calls reproduced the false
matches deterministically, and the new test pins them.

### The selector matcher crashes or over-matches on an unbalanced parenthesis (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `matches` raises `IndexError`
for `.a ) .b` and `div )+` against an element with class `a` and `b`, and it reads an
unbalanced opening parenthesis as part of a compound: `.a(` and `.a)` are reported
supported and match an element with class `a`, though no browser matches either. A
malformed selector in a scope test could therefore crash the suite or pass an
over-broad assertion instead of matching no element. No selector in the shipped
Firefox sheet is malformed (grep), so the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches; print(matches(".a ) .b", element("box", classes=("a", "b"))))'
```

raises `IndexError: list index out of range`; the expected result is `False`.

**Suspected cause.** `_split_selector` left an unmatched `(` or `)` in a compound,
and neither `_selector_is_supported` nor `matches` rejected the unbalanced selector.
An unmatched `)` also merged the text after it into the preceding compound without
adding a combinator, so `match_from` indexed `combinators[index - 1]` past the end of
a shorter list; an unmatched `(` stayed in the compound and its class/tag tests still
matched.

**Fix.** A new `_parentheses_are_balanced` helper scans the selector, skipping
parentheses inside quoted values and attribute selectors, and both
`_selector_is_supported` and `matches` reject a selector whose parentheses do not
balance. The new `test_unbalanced_parentheses_match_nothing` in
`tests/test_selector_matching.py` covers the crashing and over-matching cases and
also keeps `[title="("]` and `:not([title=")"])` supported, so a quoted parenthesis
is still text. Pre-fix scratch calls printed `IndexError` for the first two selectors
and `matches=True` for `.a(` and `.a)`; the new test passes after the fix.

**Validation gap:** none — the closest tag: no existing matcher test used an
unbalanced parenthesis, but scratch calls reproduced both the crash and the false
match deterministically, and the new test pins them.

### The selector matcher reads an empty quoted attribute value as attribute presence (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `matches` returns True for
`[title=""]` against an element whose `title` is `"x"`, and against any element carrying
a `title` attribute; a browser matches only an empty `title`. For this selector, a scope
test's `assertFalse` would fail incorrectly for a non-empty value. Inside
`:not([title=""])`, the false match is inverted: a non-empty title incorrectly fails to
match, potentially letting an over-broad sheet rule pass a scope test's `assertFalse`.
No selector in `theme/firefox/org.macos8.desktop/chrome/userChrome.css`
uses an empty quoted attribute value (grep), so no shipped assertion is mis-evaluated today;
the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches; print(matches("[title=\"\"]", element("box", attrs={"title": "x"})))'
```

prints `True`; the expected result is `False`.

**Suspected cause.** `_compound_matches` selected the value with
`value = double_quoted or single_quoted or unquoted`. For `[title=""]` the quoted group is
the empty string, which is falsy, so the selection fell through to `None` and the value
comparison was skipped as if the selector were the presence test `[title]`.

**Fix.** The group is chosen by `is not None` instead of truthiness, so an empty quoted
value is compared against the element's value. The new
`test_an_empty_quoted_attribute_value_matches_only_an_empty_value` in
`tests/test_selector_matching.py` failed for both quote styles before the fix (matching a
non-empty `title`) and passes after it, while still matching an empty and rejecting a
missing attribute.

**Validation gap:** none — the closest tag: no existing matcher test used an empty quoted
attribute value, but a scratch call and the new test reproduced the false match
deterministically; nothing outside the suite blocked confirmation.

### The selector matcher reads a comma in `:not(...)` as a descendant step, so the negation matches almost every element (found by the steward role 2026-10-26) — fixed 2026-10-26 by the bugfix role

**Symptom.** `tests/support/selector_matching.py`'s `_selector_is_supported` accepts
`:not(.a, .b)` as supported, and `matches` then returns True for a parentless element with
class `a` or `b`, and for a class-`a` element even under a class-`a` parent; a browser
matches none of those against that selector. The only False case found is a class-`b`
element under a class-`a` ancestor. A future scope test written against such a selector
would pass its "does not match" assertions for almost every element and let an over-broad
sheet rule through. No selector in
`theme/firefox/org.macos8.desktop/chrome/userChrome.css` puts a comma inside `:not(...)`
(grep), so no shipped assertion is mis-evaluated today; the gap is latent.

**Reproduce.** From the repository root:

```
PYTHONPATH=tests python3 -c 'from support.selector_matching import element, matches, _selector_is_supported; e = element("toolbarbutton", classes={"a"}); print(matches(":not(.a, .b)", e)); print(_selector_is_supported(":not(.a, .b)"))'
```

prints `True` then `True`. An element with class `b` whose parent has class `a` returns
`False` instead, so `.a, .b` behaves like the descendant selector `.a .b`.

**Suspected cause.** `_split_selector` treats only whitespace and `>` as combinators (and
rejects `+`/`~`); a comma inside `:not(...)` stays in the compound, where
`_compound_is_supported` accepts it and `_compound_matches` reads the two class fragments
as a descendant chain. `tests/support/gtk_css.py::_split_selector_list` deliberately keeps
the comma inside `:not(...)` together, pinned by
`tests/test_gtk_css.py::TestRuleBlockSemantics::test_a_comma_inside_parentheses_does_not_split_the_group`,
so the matcher must either reject a selector-list argument as unsupported or evaluate it
as a list rather than treating it as supported.

**Fix.** `_has_selector_list_comma` rejects a comma outside an attribute selector's brackets and quotes, and both
`_selector_is_supported` and `matches` treat such a selector as outside the supported subset,
so it matches nothing; a comma inside `[title="a,b"]` stays literal. The new
`test_a_comma_inside_negation_is_a_selector_list_not_a_descendant_chain` and
`test_a_top_level_comma_is_a_selector_list_not_a_descendant_chain` tests in
`tests/test_selector_matching.py` reproduce the false match, and
`test_a_comma_inside_an_attribute_value_is_literal` there guards against
over-rejecting a quoted comma (the pre-fix matcher already treated that comma
literally and passed it).

**Validation gap:** none — the closest tag: no existing matcher test used a comma outside
an attribute value, but the entry's scratch call and the two selector-list tests reproduced
the false match deterministically, while the quoted-comma test is a regression guard that
already passed before the fix.

### The selector matcher reads pseudo-class text inside an attribute value as a pseudo-class (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/selector_matching.py` stripped `:not(...)` and `:hover` from a whole
compound before matching its attribute selectors, so text inside a quoted
attribute value was read as syntax. `[title=":hover"]` required the tested
element's `hover` flag and then ignored the title value (the emptied quoted
value was treated as absent), `[title="a:b"]` matched nothing because the
remaining colon looked like an unsupported pseudo-class, and
`[title=":not(.a)"]` evaluated the value as a negation of the element under
test.

Reproduced with scratch calls: with an element whose only attribute is
`title=":hover"`, `matches('[title=":hover"]', element)` returned False;
`matches('[title="a:b"]', element)` returned False for the same value; and
`matches('[title=":not(.a)"]', element)` returned False even when the title
held that exact text. The new tests in `tests/test_selector_matching.py` fail
against the old matcher and pass now.

Fixed by finding the compound's own top-level `[...]` spans (ignoring brackets
inside a `:not(...)` argument or a quoted value), blanking those spans before
the negation and hover scans, and matching the attribute selectors from the
original spans. Each span must parse whole as an `_ATTRIBUTE`, so an operator
or syntax the matcher cannot read matches nothing instead of slipping through
as an empty test. `:not(...)` arguments come from a quote-aware balanced scan,
so a quoted `)` no longer truncates the negation. `_compound_matches` now uses
the same `_HOVER` regex as the support validation, so `:hover` is recognized
only as a complete name, and a quoted value with class-like text
(`[title="a.b"]`) stays literal and needs no such class.

**Validation gap:** none — the existing suite never placed pseudo-class text in a quoted attribute value or used an unparsed attribute operator; scratch calls and the new tests reproduced each failure, so nothing outside the suite was needed to confirm them.

### The selector matcher reads an unsupported pseudo-class inside `:not(...)` as false, so the negation matches every element (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/selector_matching.py` supports `:hover` and a flat `:not(...)`, but
`_compound_matches` removed the negated selectors before testing for a leftover `:`. An
unsupported pseudo-class inside the negation was therefore evaluated as false, and negating that
gap made the whole selector match every element: the Firefox sheet's
`#searchbar:not(:focus-within)` matched a focused searchbar, and `.a:not(:is(.b))` matched any
`.a`. A scope test using one of those selectors could pass vacuously, so a too-broad rule would
not be caught.

Reproduced by the new
`tests/test_selector_matching.py::TestSelectorMatching::test_unsupported_pseudo_class_inside_negation_matches_nothing`:
before the fix it failed with `AssertionError: True is not false` for both `:not(:focus-within)`
and `:not(:is(.b))`, and for the nested `:not(:not(.b))` case.

Fixed by validating each compound's pseudo-classes against the supported subset and recursing
into every `:not(...)` argument; a selector that uses anything else matches no element, the same
rule the matcher already applied to sibling combinators, instead of silently widening through the
negation. Supported `:not(:hover)` negation still matches an unhovered element and excludes a
hovered one.

**Validation gap:** none — the new direct matcher test reproduces it deterministically; no reproduction existed before it, but nothing outside the suite was needed to confirm the failure (the closest tag would be no-observability, retired here because this test now covers it).

### The selector matcher reads a sibling combinator as a universal descendant step (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

A selector using a sibling combinator did not match nothing: `_split_selector`
kept a spaced `+` or `~` as its own compound, and `_compound_matches` accepted
that bare-punctuation compound as matching any element. The matcher therefore
read `.a + .b` and `.a ~ .b` as `.a <any> .b`, so a `.b` grandchild of `.a`
matched a sibling selector, and a scope test could accept a rule that paints
elements it must not.

**Reproduce:** a three-level fixture `a > middle > b` returned `True` from
`matches(".a + .b", b)` and `matches(".a ~ .b", b)` (and the same for a bare
`+`/`~` compound) before the fix; it returns `False` after.

**Fix:** `_split_selector` now treats `+` and `~` as combinators in their own
right (so they are no longer parsed as universal compounds), and `matches`
returns `False` for any combinator outside the supported descendant and child
subset. `tests/test_selector_matching.py` pins both spaced forms on the
three-level fixture.

**Validation gap:** none — the closest tag is no-observability because the
unsupported selector returned a bare `True` with no trace; the existing suite
used no sibling combinator, so a scratch three-level fixture reproduced the
over-match, and the new regression test in `tests/test_selector_matching.py`
fails without the fix and passes with it.

### The test-side selector matcher treats a child combinator as an extra element (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/support/selector_matching.py` split a selector at whitespace only, so a `>` child
combinator became a compound of its own. Because `_compound_matches` treats a compound with no
tag, id, class or attribute as matching anything, every `>` consumed one ancestor level by
itself. A selector that uses child combinators, such as
`.tabbrowser-tab:hover > .tab-stack > .tab-background`, therefore returned false for every
element, while a selector whose intermediate compound was skipped could still report true. The
Firefox sheet's scope tests only build descendant selectors today, so nothing failed: a future
scope test would silently see a too-broad rule as scoped or a correct rule as inapplicable.

Reproduced with a scratch element tree: `matches(".outer > .inner > button", button)` returned
false for the valid chain, and the new
`tests/test_selector_matching.py` now pins the child-only relation (a grandchild does not match,
an intermediate element is not skipped) next to the descendant cases.

Fixed by parsing `>` as a child combinator alongside whitespace's descendant combinator, so each
compound keeps its own relation to the next, and whitespace around `>` does not add a descendant
step.

**Validation gap:** none — the closest tag: a scratch element tree reproduced both the false negative on a valid child chain and the skipped-intermediate false positive before the fix, and the new test module pins them; no shim, slow run or missing fixture blocked confirmation.

### A GTK 4 mixed-indicator pixel test samples the indicator before it paints (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/test_gtk4_theme.py::TestGtk4Theme::test_mixed_indicators_draw_black_dashes` renders an
inconsistent check box and then a radio in one GTK 4 process. It waited a fixed 0.2 s wall-clock
settle, then snapshotted each indicator and asserted its pixels. On a loaded host the second
indicator can still have no paintable node by then: `snapshot.to_node()` returns `None` and
`render_texture` raises `TypeError: Argument 1 does not allow None as a value`; when a frame exists
but is not the final one, the wrong-pixel assertion fails instead. Either way the failure carries
the first iteration's success line, `check: black dash at columns 4–11, rows 7–8; face surrounds
it`, the line the merge gate excused once in the last day.

Reproduced by pinning the test and sixteen CPU hogs to one core: the original 15 s subprocess
budget expired. With the fixed settle removed, the same load reproduced the readiness failure
directly, the radio indicator's `to_node()` returning `None`.

Fixed by replacing the fixed settle with a bounded poll (30 s per indicator, pumping the GLib main
context) that re-renders the indicator until its pixels are the expected dash and face, treats a
missing paintable node or renderer as not ready, and still fails after the deadline with the
offending pixel tuple. The subprocess safety timeout rises from 15 s to 120 s so a starved but
working run is not killed. No sheet rule or expected pixel changed; this test is its own
regression test, with the loaded host as the reproduction.

**Validation gap:** none — the existing live GTK 4 pixel test is the reproduction (it failed
under a starved host), so nothing was missing from the suite; a loaded host was required to see
it, which makes `real-run-needed` the closest other tag.

### The render publishes an unpainted all-black capture as a success (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

A KWin virtual session presents an all-black screen until the applet window paints. If the
`--settle` paint budget expires first, `spectacle` writes a correctly sized all-black PNG; the
render checked only that the capture decoded and matched `--width`/`--height`, so it published
that PNG and exited 0. The render gate then failed eight pixel comparisons with no hint that the
capture was empty, and the merge gate excused the run as flaky without naming a test.

Reproduce with the stubbed session in
`tests/test_render_surface.py::TestFailurePaths::test_an_unpainted_capture_exits_1_and_writes_nothing`:
before this fix that test failed with `AssertionError: 1 != 0` because `main` published the
all-black fixture.

Fixed by refusing a capture whose RGB plane is entirely black, before publishing, with a
diagnostic that names the settle wait and suggests a longer `--settle`. The stub fixtures for the
successful-capture tests now paint the Platinum window face instead of black.

**Validation gap:** none — the closest tag is no-observability because the original flake left
only a merge-gate separator with no test name, but the stubbed all-black capture now reproduces
the acceptance deterministically, so the ledger needs no new entry.

### The render gate captures an unpainted frame on a loaded host (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/test_render_surface.py::TestRender` started `tools/render_surface.py` with `--settle 3`,
below the CLI's documented default of 8 seconds for the window to paint. The session sleeps for
the settle and then captures whatever is on screen; on a host loaded enough that the window has
not painted in 3 seconds, `spectacle` still writes a correctly sized 320x240 all-black PNG, the
CLI accepts it, and the class reports eight pixel failures (the body pixel at (300, 200) is
`#000000` instead of `#DDDDDD`) with no hint that the capture was simply too early.

Reproduced by running the render with four CPU hogs pinned to the same core: `--settle 3` wrote
an all-black capture (pixel (300, 200) `#000000`), while `--settle 8` wrote the Platinum face
(`#DDDDDD`). Under the same load, the whole `TestRender` class failed 8 subtests before the fix
and passed after it.

Fixed by removing the `--settle 3` override, so the gate renders the way `make render` does with
the tool's documented default paint budget instead of a tighter one; the tool's default is the
budget it promises, and a loaded host is exactly when it matters.

**Validation gap:** slow-check — the only reproduction is a slow headless render under CPU load, and the time the window needs to paint is what shaped the fix.

### A render timeout test's setup races its own one-second timeout (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`TestFailurePaths.test_timeout_kills_the_session_group_and_exits_1` gave the stubbed
`dbus-run-session` a one-second timeout and then read the pidfile that stub writes before it
`exec sleep 60`. On a loaded host the session could be killed by the timeout before the shell
wrote the pid, so the read raised `FileNotFoundError` even though the group-kill path worked; the
merge gate then excused the run as flaky without naming the test. Reproduced with a scratch
subclass whose first session stub slept two seconds before writing the pid: the old test errored
at the pidfile read.

The test now retries with a fresh pidfile per attempt, bounded at 30 seconds, so an attempt whose
setup loses the race is skipped while each timed-out attempt has already had its whole group
killed; the successful attempt still checks that the recorded pid is gone.

**Validation gap:** none — the closest tag, because the failure is the test's own setup race rather than a missing product-side reproduction: a one-shot slow-session stub forced the load-dependent `FileNotFoundError` at the pidfile read, and the fixed test passes under the same shim.

### A render test's setup wait expires before its crashed applet starts (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`TestFailurePaths.test_a_crashed_applet_is_not_captured_as_a_successful_render` replaced the
session's `sleep` with a stub that polls for the applet's pidfile and then for the applet to be
reaped, with each wait capped at 500 iterations of about 0.01 s. On a host that delayed the
applet's start past that cap, the stub returned while the applet was still running, so the
session's `kill -0` liveness check found it alive, let `spectacle` capture the empty session, and
`render_surface` published that PNG and exited 0. The test then failed as a bare `1 != 0` status
mismatch even though the defect it guards against had just happened.

Reproduced with a scratch subclass that prepends a real `sleep 6` to the applet body: the old
test returned status 0 and wrote the output PNG, where it expects exit 1 and no PNG.

The two waits now use a larger bound (1500 iterations of a real 0.02 s sleep, about 30 s nominal
and longer per iteration under load) and record which wait expired in a `setup-timeout` file; the
test fails first with a message naming the applet start or reap that did not finish, instead of a
bare status mismatch. A 6 s applet start now passes, and a 45 s start fails with that named
message.

**Validation gap:** slow-check — confirming the race needed a deliberately slow applet start, and
the run that exceeded the budget took 33 s to reach the surfaced failure, which shaped the
larger iteration bound.

### A timed-out group-kill test lets its own setup race the timeout (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`TestRunLogged.test_timeout_returns_none_and_kills_the_group` ran
`sleep 60 & echo $! > pidfile; wait` with a 0.5 s timeout and then read the
pidfile. When a loaded host delayed the shell past 0.5 s, `run_logged` killed
it before it wrote the pid, so the read raised `FileNotFoundError` (or
`ValueError` for an empty file) and the test failed for a host-scheduling
reason rather than a group-kill regression. Reproduced with a one-shot shell
shim that slept 0.8 s on its first invocation: the test errored at the
pidfile read instead of exercising the group kill.

The test keeps the real 0.5 s timeout but retries, with a fresh pidfile per
attempt, until one attempt's setup wins, bounded at 30 s; each timed-out
attempt has already had its whole group killed, so retrying leaks nothing.
With `_kill_group` patched out, the test still fails at its `is_gone`
assertion, so the retry did not weaken it.

**Validation gap:** none — the closest tag, because the failure is the test's own setup race rather than a missing product-side reproduction: a one-shot slow-shell shim forced the load-dependent `FileNotFoundError` at the pidfile read, and the fixed test passes under the same shim.

### The grandchild timeout test's setup races its own timeout (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tests/test_process_runner.py::TestSubprocessTimeout::test_timeout_kills_grandchildren`
gave the fake make a 0.5-second timeout and then opened the pidfile the fake
make writes after backgrounding its sleep. On a loaded host the shell can be
scheduled late enough that the timeout kills it before it writes the file, so
the test fails with `FileNotFoundError: .../grandchild.pid` even though the
process-group cleanup worked. The suite then reports an error instead of
checking the descendant, and the merge gate can excuse it as flaky.

Reproduce by pinning the test to one CPU under 200 busy processes: two of ten
runs failed with that `FileNotFoundError`. The test now starts the fake make
with `process_runner.running`, waits for the pidfile to hold the written pid
(not merely to exist, bounded at 30 seconds) before applying the 0.5-second
`finish` timeout, and then checks -- still inside the context manager, before
its own cleanup kills the group -- that the recorded grandchild is gone. The
fake make's sleeps outlast that setup deadline, so the timeout no longer races
the setup it is supposed to interrupt.

**Validation gap:** none — the existing test reproduced the intermittent failure under artificial CPU load, so no fixture or instrumentation was missing, and the rewritten test now confirms the timeout and descendant cleanup every run.

### A Ctrl-C that arrives while a child starts leaves the command running (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tools/process_group.run_logged` enters the `try`/`finally` that kills the
command's process group only after `subprocess.Popen` returns. Python's default
SIGINT handler raises `KeyboardInterrupt` at the next bytecode, so a Ctrl-C
delivered while `Popen` is still returning unwound the caller before that
cleanup existed. The command, started in its own session, kept running after
the caller died — even though `run_logged` promises the whole group is killed
on the way out. The SIGTERM form of this race was fixed earlier; SIGINT was not
deferred, so it took the same path.

Reproduce with a patched `Popen` that delivers SIGINT to this process right
after the real `Popen` returns: `run_logged` raised `KeyboardInterrupt` and
`/bin/sleep 60` was still alive when polled five seconds later (the new test
`tests/test_process_group.py::TestRunLogged::test_a_sigint_while_popen_returns_still_kills_the_child`
failed on the old code). `run_logged` now records SIGINT with SIGTERM and
SIGHUP while the child starts, restores the handlers once the cleanup `try` is
entered, and re-raises `KeyboardInterrupt` there, so the group kill and reap
still run. A deferred termination signal keeps its `SystemExit(128 + signal)`
form; only the first signal to arrive is replayed.

**Validation gap:** no-fake — Confirming the race deterministically needed a patched `Popen` that signals the caller at the exact point the real one returns, a shim the suite did not have for SIGINT; the new test supplies it.

### A SIGTERM that arrives while a child starts leaves the command running (found by the bugfix role 2026-10-26) — fixed 2026-10-26 by the bugfix role

`tools/process_group.run_logged` starts each external command with
`subprocess.Popen` and only then enters the `try`/`finally` that kills the
command's process group and reaps it. `exit_on_termination` turns SIGTERM into
`SystemExit` at the next bytecode, so a SIGTERM delivered while `Popen` is still
returning unwound the caller before that cleanup existed. The command kept
running after `apply_theme` or `apply_cursor` had exited, and the suite's SIGTERM
tests saw it still alive: `test_apply_theme.py::TestTermination::test_sigterm_kills_the_step_group_and_removes_scratch`
intermittently failed with `AssertionError: ProcessLookupError not raised` under
CPU load (observed once in 60 loaded runs before the fix).

`run_logged` now swaps in a handler that records SIGTERM and SIGHUP while the
`Popen` call runs, restores the caller's handlers once the cleanup `try` is
entered, and raises the recorded signal's `SystemExit` there, so the group kill
and reap still run. The child is untouched: the recording handler is replaced
before the next command starts, and an executable does not inherit a Python
handler anyway.

**Validation gap:** no-fake — Confirming the race deterministically needed a patched `Popen` that signals the caller at the exact point the real one returns, a shim the suite did not have; the new test supplies it.

### CI parity cannot run because the specified workflow is absent (found by the ci role 2026-10-25) — fixed 2026-10-25 by the bugfix role

At main tip `e3a2d88817bdaeb89f595d114d0d18f8fa268a82`, the CI role cannot
read `.github/workflows/ci.yml` to execute its jobs' `run:` steps. Reproduce
from the repository with `wc -l .github/workflows/ci.yml`; the output is:

```text
wc: .github/workflows/ci.yml: No such file or directory
```

`git ls-tree -r --name-only HEAD .github package.json package-lock.json`
prints no paths. The README instead documents `make check` for this
Python/Make project. No CI parity block was supplied with this run either.
The ci role is prohibited from editing `.github/workflows/*`, so it cannot
supply the missing workflow. Restore or identify the intended workflow and
align the role's instructions with it before claiming workflow parity.

Added `.github/workflows/ci.yml` with Python 3.12, Git LFS checkout,
`make check` and `make check-references`, and documented these parity commands
in README.md. `tests/test_ci_workflow.py` reproduced the missing-file failure
before the workflow was added and pins its public check steps and asset setup.

**Validation gap:** none — A unittest reproduced the absent workflow as a FileNotFoundError before the fix.

### A checked GTK check box draws no check because its SVG comment precedes the root (found by the bugfix role 2026-10-24) — fixed 2026-10-24 by the bugfix role

The checked check box's shipped `assets/checkmark.svg` began with its
provenance comment, so its `-gtk-icon-source` did not load: GTK loads that
SVG through gdk-pixbuf, whose sniffer did not recognize a file whose `<svg`
root starts later than byte 256. The check box rendered as an empty Platinum
face. The radio asset (`bullet.svg`) loaded only because its shorter comment
left the root inside that window, so it was one comment edit away from the
same blank glyph.

**Reproduce:** a broadway-backed offscreen GTK 3.24.49 render of a checked
check box showed only the 14px `#DDDDDD` face; after the comment moved inside
the root the render differed in 53 pixels and the black check stroke
appeared. In gdk-pixbuf directly, `Pixbuf.new_from_file("checkmark.svg")`
raised "Couldn't recognize the image file format" before the fix and returned
a 14x14 pixbuf after it.

**Fix:** both checked-glyph assets now put `<svg>` first and keep their
provenance comments inside the root, matching the arrow assets. The title-bar
boxes keep their leading XML declaration and comment because the sheet loads
them as `background-image`, which the same render drew identically before and
after.

**Validation gap:** unclear-invariant — the register pinned the root-first
rule only for the arrow assets, so the checked glyphs' same loader
requirement had to be reconstructed (a broadway-backed offscreen GTK render
confirmed the blank check); the extended rule is now in docs/invariants.md,
and the new root-first test fails on the old checkmark and passes after the
fix.

### A UTF-8 BOM before our Firefox `user.js` marker duplicates the block on install and leaves it on removal (found by the bugfix role 2026-10-24) — fixed 2026-10-24 by the bugfix role

A UTF-8 BOM at the start of `user.js` is valid JavaScript and some editors
add one. The marker-block transform compared the first line exactly, so a
BOM-prefixed copy of our own block looked foreign: `make install-firefox`
appended a second marker-plus-preference block, and `make remove-firefox`
deleted neither the old marker nor its preference line.

**Reproduce:** `set_user_js("\ufeff" + USER_JS_MARKER + "\n" + PREF_LINE + "\n")`
returned two copies of the block before the fix, and `remove_user_js` on the
same text returned it unchanged.

**Fix:** `_without_block` strips one leading BOM from the first line before
comparing it with the marker, so a BOM-prefixed block is recognised and
removed. A BOM before a foreign first line is still kept byte for byte.

**Validation gap:** unclear-invariant — the suite pinned BOM handling for the two CSS markers but said nothing about the `user.js` marker block; the reconstructed rule (a BOM does not hide that block either) is now in `docs/invariants.md`, and the new test failed before the fix and passes after.

### A UTF-8 BOM before our marker hides our own GTK user CSS and Firefox sheet (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make apply-gtk` and `make install-firefox` decide whether an existing
`gtk-4.0/gtk.css` or `chrome/userChrome.css` is theirs by comparing its first
line with the shipped marker. Both readers decode the file as plain UTF-8, so
a UTF-8 BOM (valid in CSS, and added by some editors) stays in the first line
and the comparison fails. An apply-gtk then reports that our own file "is not
our user CSS; leaving it untouched" and never installs the import libadwaita
needs; a remove-gtk or remove-firefox leaves the marker-led file behind.

**Reproduce:** write `\ufeff` followed by the marker as the first line of
`gtk-4.0/gtk.css` with the selection installed, then run `apply_gtk.main`;
before the fix it exited 0 with the file unchanged and "not our user CSS" on
stdout. The same BOM on Firefox's `chrome/userChrome.css` made
`install_firefox.main` exit 1 and leave the sheet untouched.

**Fix:** the GTK user-CSS and Firefox sheet checks now strip one leading UTF-8
BOM before comparing the first line with the marker, so a BOM-prefixed
marker-led file is adopted and rewritten (dropping the BOM) or removed. A
foreign first line, BOM or not, is still left untouched.

**Validation gap:** unclear-invariant — neither the code nor the suite said whether a BOM before the marker kept a file ours; the reconstructed rule (a BOM does not hide our marker) is now in `docs/invariants.md`, and the four new tests failed before the fix (the GTK file stayed unchanged, the Firefox install exited 1) and pass after.

### A Firefox install replaces or removes a symlinked profile file (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make install-firefox` and `make remove-firefox` reached
`chrome/userChrome.css` and `user.js` through `write_atomically` and
`Path.unlink`, which operate on the path itself. When either file was a
symbolic link (a common dotfile-manager setup), the install replaced the
link with a regular file and left the target stale; a removal unlinked the
link. The profile silently detached from the file the user meant to edit.

**Reproduce:** point `chrome/userChrome.css` at a dotfile target holding an
empty file and `user.js` at a target holding
`user_pref("keep.me", true);`, then run `install_firefox.main`; before the
fix it exited 0 and both paths were regular files while the targets kept
their old bytes.

**Fix:** `_apply` and `_remove` now refuse a planned write or removal whose
final path component is a symbolic link with a `ConfigError` naming the path,
so the installer exits 2 with `install_firefox: error: cannot write/remove
<path>: it is a symbolic link; ...` and neither the link nor its target
changes. A symlinked profile directory is not a link at the profile file
path and stays supported.

**Validation gap:** unclear-invariant — neither the Firefox row nor the suite said what an install or removal should do with a symlinked profile file, so the invariant was reconstructed first (never replace or delete the user's link; refuse by name), is now recorded in `docs/invariants.md`, and the new tests failed with exit 0 and regular files where the links were before the fix.

### A GTK selection replaces a symlinked settings or user-CSS file (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make apply-gtk` and `make remove-gtk` reached their config paths through
`tools/gtk_staging.commit`, whose `os.replace`/`unlink` operates on the path
itself. When `$XDG_CONFIG_HOME/gtk-3.0/settings.ini`, `gtk-4.0/settings.ini`
or `gtk-4.0/gtk.css` was a symbolic link (a common dotfile-manager setup),
the selection replaced or deleted the link with a regular file instead of
editing the file the link named: the dotfile copy stayed stale while the
live config path silently detached from it.

**Reproduce:** point `gtk-3.0/settings.ini` at a dotfile target holding
`[Settings]\ngtk-theme-name=Adwaita`, then run `apply_gtk.main`; before the
fix it exited 0, `settings.ini` was no longer a symlink, and the target still
held `Adwaita`. Removing with a symlinked marker `gtk.css` likewise deleted
the link and cleared the settings.

**Fix:** before staging any write or removal, `_apply` and `_remove` refuse a
config path whose final component is a symbolic link with a `ConfigError`
naming the path, so `apply_gtk` exits 2 with `apply_gtk: error: cannot
write/remove <path>: it is a symbolic link; ...` and neither the link nor its
target changes. A symlinked parent directory (a symlinked config home) is not
a link at the config path and stays supported.

**Validation gap:** unclear-invariant — neither the GTK row nor the suite said what a write or removal should do with a symlinked config path, so the invariant was reconstructed first (never replace or delete the user's link; refuse by name), is now recorded in `docs/invariants.md`, and a scratch `_apply` with a symlinked `settings.ini` showed exit 0 and a regular file where the link was.

### A cursor generator nominal size above the Xcursor frame limit allocates an unbounded pixel buffer (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/make_cursors.py` accepted every positive nominal size and
`render_rgba` allocated `size * size * 4` bytes before
`write_rgba_cursor` applied its 1..0x7FFF frame-dimension limit. A caller of
the library entry points could therefore exhaust memory on a size the writer
rejects; the generator's own `main` only passes the shipped 16/24/32 sizes.

**Reproduce:** `make_cursors._checked_sizes((0x8000,))` returned the tuple
instead of raising, while `write_rgba_cursor` refuses the same size, so the
generator accepted a request its writer could never encode.

**Fix:** a shared `_checked_size` helper now refuses a size above
`MAX_IMAGE_SIZE` in both `render_rgba` and the nominal-size check, naming the
Xcursor frame limit before any pixel buffer is allocated.

**Validation gap:** none — the existing validation path reproduced it
directly: `_checked_sizes` accepted the same size `write_rgba_cursor`
rejects, without needing the buffer allocation.

### A failed GTK commit leaves the settings and user CSS half-applied (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/gtk_staging.py::commit` renamed each staged settings file over its
target in turn and had no way back. If a later rename failed, the earlier
settings file kept its new contents; `apply_gtk --remove` also unlinked the
user CSS before the commit, so a failed commit deleted the CSS while a
settings file was already cleared. The module's staging guarantee ("a file
that cannot be read or staged leaves all of them unchanged") did not cover
the commit step, and `tests/test_gtk_staging.py`'s failed-rename case
accepted the half-applied result in its comment.

**Reproduce:** stage two settings writes, create a directory at the second
target, then call `commit(staged)`: it raises `ConfigError` as expected but
the first target keeps `new good` instead of `old good`. At the workflow
level, `apply_gtk --remove` with `os.replace` failing on the second
`settings.ini` leaves the GTK 3 selection cleared and the user CSS deleted.

**Fix:** `commit` now takes removals and publishes staged writes and the CSS
deletion as one transaction. Every target is first hard-linked to a uniquely
named `.<name>.<token>.backup` sibling before its staged file replaces it or
its removal deletes it. On any failure raised during the commit, every
changed target is restored from its backup (a target that did not exist
before is removed again) and a failed restoration is reported alongside the
original error. A signal that ends the process before the rollback can still
leave the targets half-published and a hidden backup behind. Successful
commits discard the backups. The user-CSS deletion moved from `apply_gtk`
into that commit, so a raised failure restores the settings instead of
leaving them half-cleared with the CSS already deleted.
`tools/gtk_user_files.py` no longer needs its `unlink` helper.

**Validation gap:** unclear-invariant — the old failed-rename test deliberately
documented that earlier targets were not rolled back, so what "staged before
any is committed" was supposed to guarantee at commit time had to be
reconstructed; `docs/invariants.md` now states the transaction and rollback
behavior the tests pin.

### A nominal size below the 16x16 grid puts the cursor hotspot outside its frame (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/make_cursors.py::_scaled_hotspot` scaled a grid hotspot to the first
destination pixel of its source pixel with the ceiling of `x * size / 16`.
For a nominal size below the 16x16 grid, that source pixel can be skipped by
the nearest-neighbour downscale, so the ceiling equals `size` (for example
size 8 with hotspot 15 produced x=8 on an 8-pixel image). `cursor_bytes`
accepts every positive nominal size, so a valid request failed from the
Xcursor writer with `ValueError: images[0] hotspot_x ... lies outside its
...-pixel image`.

**Reproduce:** `make_cursors.cursor_bytes(sizes=(8,), hotspot=(15, 15))`;
before the fix it raised the writer's `ValueError`, now it returns a cursor
whose decoded frame pins `(7, 7)`.

**Fix:** the scaled hotspot is clamped to `size - 1`, the last destination
pixel the downscale renders, so it stays inside the frame. Sizes at or above
the grid are unchanged: the ceiling is already below `size` for them, so the
shipped 16/24/32 frames keep their pinned bytes.

**Validation gap:** unclear-invariant — the frame hotspot bound was implied
only by the Xcursor writer's validation, and no test stated what a size below
the 16x16 grid should do, so the mapping had to be reconstructed and pinned in
`docs/invariants.md` as well as the new test.

### An oversize Firefox profile-discovery INI file crashes with a MemoryError (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/firefox_profile.py::_read_ini` opened `installs.ini` or
`profiles.ini` through the shared regular-file reader but then handed the
unbounded stream to `configparser.read_file`, which reads the whole file. A
profile-discovery INI of hundreds of megabytes therefore raised
`MemoryError`, which is not an `OSError`, so `make install-firefox` without a
named profile ended in a traceback instead of the module's exit-2
`ConfigError` naming the file.

**Reproduce:** under `ulimit -v 120000`, with a 300 MB sparse
`$HOME/.mozilla/firefox/installs.ini`, call
`firefox_profile.resolve_profile(None, {'HOME': ...})`; before the fix it
raised `MemoryError` while decoding, now it raises `ConfigError` naming the
path and the 1048576-byte limit.

**Fix:** the reader stops one byte past a 1 MiB cap, the same bound the
installer's profile files use, and refuses a longer INI by name before
`configparser` sees it. The accepted cap-size boundary and both discovery
INIs are covered by
`tests/test_firefox_install.py::TestProfileResolution::test_an_oversize_ini_file_is_refused_by_name`
and
`tests/test_firefox_install.py::TestProfileResolution::test_an_ini_file_at_the_1_mib_cap_is_accepted`;
the oversize test failed against the old unbounded reader and passes now.

**Validation gap:** real-run-needed — the existing suite had no oversize INI case, so the MemoryError was confirmed only by a 300 MB sparse `installs.ini` run under `ulimit -v 120000`; the new tests now pin the cap offline.

### An oversize GTK settings or user-CSS file crashes the GTK selection with a MemoryError (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/apply_gtk.py::_read_config_text` read the whole of
`$XDG_CONFIG_HOME/gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` or
`gtk-4.0/gtk.css` into memory in chunks with no size cap. A GTK config file
of hundreds of megabytes raised `MemoryError`, which is not an `OSError`, so
the tool's `except ConfigError` path never ran and `make apply-gtk` or
`make remove-gtk` ended in a traceback instead of its documented exit-2
diagnostic naming the file.

The reader now stops one byte past the same 1 MiB cap
`tools/install_firefox.py::_read_text` uses and refuses an oversize file by
name as a `ConfigError`; `_apply` also refuses, before staging any write, a
settings file whose longer value would grow it past that cap.

**Validation gap:** real-run-needed — the existing suite had no oversize config case, so the MemoryError was confirmed only by a 300 MB sparse `gtk.css` run under `ulimit -v 120000`, which exited 1 before the fix and 2 after.

### An oversize Firefox profile file crashes the installer with a MemoryError (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/install_firefox.py::_read_text` opened an existing `userChrome.css` or
`user.js` and read it whole, only to compare the sheet's first line or append
one marker block. A profile file of hundreds of megabytes therefore raised
`MemoryError`, which is not an `OSError`, so `make install-firefox` or
`make remove-firefox` ended in a traceback naming neither the tool nor the
file instead of the documented exit-2 diagnostic.

**Reproduce:** in a profile with a 300 MB `chrome/userChrome.css`, run
`HOME=... python3 tools/install_firefox.py --profile PATH` under
`ulimit -v 120000`; before the fix it printed a `MemoryError` traceback and
exited 1 (or, without a memory limit, treated the file as a foreign sheet).

**Fix:** the reader reads at most `_MAX_PROFILE_FILE_BYTES + 1` (1 MiB plus
one byte, the same bound `tools/containment.py` and `tools/local_hook.py`
use) and refuses a longer file by name after that one byte, so an oversize
profile file becomes the same exit-2 `ConfigError` as any other unreadable
file. The bound applies to both profile files because both go through this
reader. The install also refuses by name, before writing either file, a
`user.js` whose marker block would grow it past that same cap, so a profile
the installer creates can always be read back and removed; the
empty/foreign-sheet and marker-removal logic is otherwise unchanged.
`tests/test_firefox_install.py::TestInstall::test_an_oversize_user_chrome_is_refused_by_name`
and `tests/test_firefox_install.py::TestInstall::test_an_oversize_user_js_is_refused_by_name`
failed on the old reader (exit 1 and exit 0 respectively), the
`test_an_install_that_would_grow_user_js_past_the_1_mib_cap_is_refused` test
failed on the old install (exit 0), and all pass now with the accepted 1 MiB
boundary and its removal path pinned as well.

**Validation gap:** real-run-needed — the existing suite never read a profile
file larger than memory, and confirming the MemoryError required a bounded
real run of the installer under a memory limit (`ulimit -v`); the two new
tests now pin the cap offline.

### An empty `userChrome.css` is refused as foreign, so the Firefox install fails (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/install_firefox.py::_apply` treated any existing `userChrome.css`
whose first line is not our marker as a foreign sheet. An existing but empty
file has no first line, so it took that same branch: `make install-firefox`
exited 1 with "is not our userChrome.css; leaving it untouched" and wrote
nothing, so the opt-in Firefox chrome could never be installed over an empty
file. An empty file holds nothing to preserve.

**Reproduce:** create an empty `chrome/userChrome.css` in a profile and run
`python3 tools/install_firefox.py --profile PATH`; the file stays empty, no
`user.js` is written, and the exit status is 1.

**Fix:** the marker check now runs only for non-empty content, so an empty
file is adopted and overwritten with our sheet, exactly like an absent file.
A non-empty foreign sheet is still refused unchanged.
`tests/test_firefox_install.py::TestInstall::test_an_empty_sheet_is_adopted`
failed on the old code and passes now.

**Validation gap:** unclear-invariant — the installer said a "foreign"
`userChrome.css` is refused but never stated whether an empty file counts as
foreign, so the rule that empty content is adoptable was reconstructed (the
same rule the GTK user-CSS write already follows) and is now recorded in
docs/invariants.md.

### An exported empty `FIREFOX_PROFILE` makes the Firefox targets fail instead of discovering the profile (found by the qa role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make install-firefox` and `make remove-firefox` with an empty `FIREFOX_PROFILE` exit 2
with `install_firefox: error: Firefox profile must be an absolute path: .` instead of
using the active profile under `$HOME/.mozilla/firefox`, which the same targets use when
the variable is unset.

**Reproduce:** in a scratch directory, create `home/.mozilla/firefox/zz.default` and an
`installs.ini` naming it, then run `HOME=$PWD/home FIREFOX_PROFILE= make install-firefox`
(an empty value given as a make argument, `make install-firefox FIREFOX_PROFILE=`, does
the same). It exits 2 without touching the profile. In the same tree,
`HOME=$PWD/home env -u FIREFOX_PROFILE make install-firefox` installs the sheet and
`user.js` block into `zz.default`; `FIREFOX_PROFILE= make remove-firefox` fails the
same way.

**Expected:** the Makefile's `$(if $(FIREFOX_PROFILE),--profile ...)` already treats an
empty value as "no profile named" and omits `--profile`, so the tool should fall back to
`installs.ini`/`profiles.ini`; `make help` lists the active profile under
`$HOME/.mozilla/firefox` as the default.

**Actual:** `tools/firefox_profile.py::resolve_profile` reads
`env.get("FIREFOX_PROFILE")` and treats `""` as a named path. `Path("")` is `.`, which is
relative, so it raises `ConfigError("Firefox profile must be an absolute path: .")`.
GNU make exports an empty command-line variable to the recipe, so both spellings above
reach the tool with the empty value set.

**Validation gap:** none — the existing test harness reproduced it deterministically once the empty value was passed, but no test exercised an empty `FIREFOX_PROFILE`.

### An empty `gtk-4.0/gtk.css` is mistaken for a foreign user sheet (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/apply_gtk.py::_user_css_write` treated any existing `gtk.css` whose
first line is not our marker as a foreign sheet and left it untouched. An
existing but empty file has no first line, so it took that same branch:
`make apply-gtk` set `gtk-theme-name` in both settings files and exited 0
while printing "exists but is not our user CSS; leaving it untouched", so
libadwaita applications never imported the installed GTK 4 sheet. An empty
file holds nothing to preserve.

**Reproduce:** create an empty `gtk-4.0/gtk.css` in an empty config home,
then run `apply_gtk` with both installed sheets present; the file stays empty
and the exit status is 0.

**Fix:** the marker check now runs only for non-empty content, so an empty
file is adopted and written with the marker and the sheet's `@import`, exactly
like an absent file. `tests/test_gtk_apply.py::TestApply::test_empty_user_css_is_adopted`
failed on the old code and passes now.

**Validation gap:** unclear-invariant — the docstring said a "foreign"
`gtk.css` is preserved but never stated whether an empty file counts as
foreign, so the rule that empty content is adoptable was reconstructed and is
now recorded in docs/invariants.md.

### `defaults_groups` truncates a value at a Unicode line separator (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/theme_defaults.py`'s `defaults_groups` split the contributor-supplied
`contents/defaults` with `str.splitlines()`, which treats U+2028, U+2029, NEL
and the C0 separators as line breaks in addition to CR and LF. A value holding
one was cut in two, and the continuation line, having no `=`, was discarded:
`[kwinrc][Theme]\nname=Mac OS 8.6\u2028Platinum\n` parsed as `{"name": "Mac OS
8.6"}` instead of the full value, and `write_configs` wrote the truncated
value with no diagnostic.

The reader now splits only on CR, LF and CRLF, the same line-delimiting rule
`tools/reference_validation.py` uses for `sources.txt`.
`tests/test_theme_defaults.py::TestDefaultsGroups::test_a_unicode_line_separator_stays_inside_the_value`
failed on the old reader and passes now.

**Validation gap:** unclear-invariant — the reader never stated which characters end a line, so the CR/LF-only invariant was reconstructed from the sibling reference reader and is now recorded in docs/invariants.md.

### An unstartable cursor selector escapes as a traceback instead of exit 2 (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make apply-cursor` finds `plasma-apply-cursortheme` with `shutil.which`, but a
selector on `PATH` that cannot be started (a corrupt binary, or a script whose
interpreter is missing) makes `Popen` in `run_logged` raise `OSError`.
`tools/apply_cursor.py::_select` did not catch it, so the exception escaped
`main` as a traceback instead of the tool's documented exit status.

**Reproduce:** put an executable `plasma-apply-cursortheme` script with
`#!/nonexistent/interpreter` on `PATH` and run `python3 tools/apply_cursor.py`
with an installed icon theme; it raises `FileNotFoundError` instead of exiting 2.

**Fix:** `_select` now catches the `OSError` and reports
`apply_cursor: error: cannot run plasma-apply-cursortheme: ...` with exit 2,
like a missing selector. The regression test stubs a selector that cannot start.

**Validation gap:** no-fake — Confirming the escape needed an executable stub whose interpreter is missing, a fixture the suite did not have.

### A FIFO at either Firefox profile-discovery INI file blocks the install (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make install-firefox` without `--profile` reads `installs.ini` and `profiles.ini`
under `$HOME/.mozilla/firefox` to find the active profile. `tools/firefox_profile.py`
opened each with `Path.open`, so a FIFO at either path waited forever for a writer and
the install hung with no diagnostic.

**Reproduce:** create a fresh `$HOME`, put a FIFO at
`.mozilla/firefox/installs.ini` (or `profiles.ini`), and run
`python3 tools/install_firefox.py` with `HOME` pointing there. The process blocks
instead of exiting 2.

**Fix:** `_read_ini` now opens the file through the shared
`containment.open_regular_binary`, which opens with `O_NONBLOCK` and checks the
opened descriptor, and wraps a non-regular file, an unreadable file and invalid
UTF-8 as a by-name `ConfigError`. A missing INI still reads as absent and a regular
file still parses the same way. The regression test runs the install in a bounded
child for a FIFO at each INI path.

**Validation gap:** no-fake — Confirming the hang needed a FIFO fixture plus a bounded child process, neither of which the suite had.

### A FIFO at a Firefox profile file blocks the install forever (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/install_firefox.py` read a profile's `chrome/userChrome.css` and `user.js` with
`Path.read_bytes()`. A FIFO or device at either path makes that open wait for a writer (or stream
forever), so `make install-firefox` never returned and printed no diagnostic. Placing a FIFO at
either file reproduces it: the install stops in `_read_text` before writing the other file.

The fix opens both files through the shared containment regular-file reader
(`open_regular_binary`), which opens with `O_NONBLOCK` and inspects the opened descriptor, so a FIFO
or device is refused by name with exit status 2 instead of blocking. A missing file still reads as
absent, and a regular file's bytes are decoded as UTF-8 without newline translation, so its line
endings stay intact. The regression test
`tests/test_firefox_install.py::TestRemove::test_a_fifo_at_either_profile_file_is_refused_without_blocking`
runs the install in a child for a FIFO at each profile file; both cases hit the child-process
timeout before the fix and pass after it.

**Validation gap:** no-fake — confirming it needed a FIFO fixture and a bounded child process the
suite did not have, so the blocked open left no diagnostic; the closest tag is no-fake, and the new
test now supplies that fixture.

### The cursor generator test patches a removed `_write_atomic` symbol (found by the plan role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The entry was filed before an earlier coverage commit repaired the cursor-write test. On this tree,
the cursor-theme module's failed-write test reads and patches the imported shared atomic-write
helper, which the cursor generator imports from the atomic-write module and calls for every cursor
write; the test no longer references the removed private helper name. Running the cursor-theme test
module under the project's check passes that test, so there is nothing left to fix: the entry
describes a failure the earlier commit had already repaired.

**Validation gap:** no-repro — the reported failure could not be reproduced because the test now
patches the existing shared atomic-write helper instead of the removed name.

### Fidelity drops alpha, so a fully transparent candidate passes the byte-exact gate (found by the qa role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares only each pixel's red, green and blue
bytes. A candidate that matches the reference's RGB but not its alpha therefore reports zero
error and passes the default no-differing-pixel gate. Reproduction (any 8-bit RGBA PNG encoder;
this uses ImageMagick, and the two images differ only in alpha):

```
$ tmp=$(mktemp -d) && cd "$tmp"
$ magick -size 2x2 xc:'rgba(0,0,0,1)' PNG32:opaque.png
$ magick -size 2x2 xc:'rgba(0,0,0,0)' PNG32:clear.png
$ python3 <repo>/tools/fidelity.py clear.png opaque.png
candidate: clear.png  2x2
reference: opaque.png  2x2
pixels compared: 4
mean absolute error: 0.0000
per-channel MAE (R, G, B): 0.0000 0.0000 0.0000
RMSE: 0.0000
max channel delta: 0 at (0, 0)
differing pixels: 0 / 4 (0.000000)
PASS: max-mae=unset max-frac=unset tolerance=0
$ echo $?
0
```

Expected: the default gate fails with exit 1 and a nonzero differing-pixel count, because every
pixel's alpha differs by 255; README's "Fidelity checking" says a run passes only when no pixel
differs from the reference, and docs/invariants.md's tooling row says the gate passes only when no
pixel differs beyond its tolerance. Actual: exit 0 and a byte-exact report for a fully
transparent surface. If RGB-only comparison is intentional, the README and that invariant need to
say alpha is not compared; as written a user cannot tell a transparent surface from the reference.

Suspected cause: `tools/png/read.py`'s `decode_png` drops the alpha byte of a color-type-6 image
(`drop_alpha`) before unfiltering, and `read_png` returns the `Image` type that
`tools/png/image.py` describes as an 8-bit RGB buffer, so `tools/fidelity_metrics.compare` never
sees alpha. The RGBA decoder (`read_rgba`) exists for the cursor PNGs but the fidelity CLI uses
the RGB path.

**Validation gap:** none — the dropped alpha bytes are deterministic and the CLI reproduces
the pass offline.

### The PNG tRNS-order test names an unimported `_PNG_SIGNATURE` (found by the plan role 2026-10-23) — fixed 2026-10-23 by the dedupe role

`tests/test_png_malformed.py::TestTrnsColorTypeValidation.test_truecolor_trns_before_suggested_plte_is_refused`
built its blob by concatenating `_PNG_SIGNATURE`, but the module no longer
imported that name: the change that moved the stream helpers into
`tests/support/png_fixtures.py` removed the import while one use remained, so
the test failed with `NameError: name '_PNG_SIGNATURE' is not defined`. The
entry originally named the sibling `test_palette_trns_before_plte_is_refused`,
which already used `png_stream()` and passed. The repair landed in
the dedupe change `a4e85fc6`, which converted the remaining truecolor stream to
the shared `png_stream()` helper instead of importing the private constant.

**Validation gap:** none — the missing import failed deterministically before `a4e85fc6` converted the truecolor stream to `png_stream()`.

### A truecolor tRNS before a suggested PLTE is accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The chunk collector treated a tRNS before PLTE as illegal only for a color
type 3 palette image, so a truecolor (color type 2) image whose suggested
palette followed its tRNS still decoded. The PNG spec says a tRNS chunk must
follow the PLTE chunk, if any, not only the palette an indexed image indexes.
Repro from a hand-built 1x1 color type 2 stream with tRNS, then PLTE, then
IDAT: `decode_png` returned `b'\x01\x02\x03'` and `decode_rgba` returned
`(1, 1, b'\x01\x02\x03\x00')`; both now raise "PNG has a tRNS chunk before
its PLTE chunk; tRNS must follow the PLTE chunk, if any". A tRNS with no PLTE
in the stream, and a tRNS after the suggested PLTE, still decode. `check_trns`
now refuses the ordering whenever a palette is present, and a color type 3
image with no PLTE keeps its missing-palette diagnosis. Test:
`tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_truecolor_trns_before_suggested_plte_is_refused`
(fails both subtests without the fix).

**Validation gap:** unclear-invariant — the code and its comments stated the
ordering was legal for a truecolor suggested palette, so the spec rule had to
be reconstructed; the invariant is recorded in docs/invariants.md.

### A palette image with tRNS before PLTE is accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The PNG specification requires a `tRNS` chunk to follow `PLTE`. `tools/png/stream.py`'s
`collect_chunks` collects the two payloads independently and checks only that both precede
`IDAT`, so a color type 3 image carrying `tRNS` before `PLTE` decodes on both the RGB and RGBA
paths. Reproduce by assembling the chunks by hand:
`_PNG_SIGNATURE + ihdr_chunk(1, 1, 3) + _chunk(b"tRNS", bytes([0, 128])) + _chunk(b"PLTE",
bytes([255, 0, 0, 0, 255, 0])) + _chunk(b"IDAT", zlib.compress(bytes([0, 0]))) +
_chunk(b"IEND", b"")`; both `decode_png` and `decode_rgba` return the image. Suspected cause:
no ordering guard for `tRNS` against an earlier-or-absent `PLTE`; the missing-`PLTE` diagnosis
for color type 3 must keep winning when no palette appears at all.

**Validation gap:** no-fake — no fixture could emit a `tRNS` before `PLTE`, so confirming the
acceptance needed a hand-assembled chunk stream from the lower-level `_chunk` helpers.

### A PLTE chunk on a greyscale color type is silently ignored (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` validated a PLTE chunk's length but neither decoder
checked whether the header's color type could carry a palette. The PNG specification makes PLTE
required for color type 3, optional for the truecolor types 2 and 6, and prohibited for the
greyscale types 0 and 4. Reproduce with `make_png(1, 1, [bytes([7])], color_type=0,
palette=bytes([255, 0, 0]))`: both `decode_png` and `decode_rgba` returned the image instead of
refusing the non-conformant chunk.

`tools/png/stream.py` now exports `check_plte(palette, color_type)`, which refuses a palette on
color types 0 and 4 and leaves the optional truecolor suggested palette and the required palette
image accepted. `_decode_image` calls it right after `parse_ihdr`, next to `check_trns`, so both
decode paths refuse the same file.

**Validation gap:** unclear-invariant — the chunk reader's docstrings described framing checks but nowhere stated that PLTE legality depends on the header's color type, so that rule had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### tRNS validation ran only on the RGBA decode path (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/read.py`'s `decode_rgba` validated a tRNS chunk's length while it
applied alpha, but `decode_png` discarded the chunk without looking at it and
neither path checked whether the header's color type could carry one. A
truecolor PNG with a 5-byte tRNS decoded as RGB but raised on the RGBA path;
an overlong palette tRNS did the same; and a tRNS chunk on an alpha color type
(4 or 6), which the PNG specification forbids outright, was accepted by both.
Reproduce with `make_png(1, 1, [bytes([1, 2, 3, 4])], color_type=6,
trns=b"\x00\x01\x00\x02\x00\x03")`: `decode_rgba` returned the image instead
of raising.

`tools/png/stream.py` now exports `check_trns`, which refuses a tRNS chunk on
color types 4 and 6, a greyscale or truecolor tRNS whose length is not exactly
2 or 6 bytes, and a palette tRNS outside 1 to the palette's entry count.
`_decode_image` calls it right after `parse_ihdr`, so both decoders reject the
same malformed transparency (a palette image with no PLTE still gets the
missing-palette diagnosis).

**Validation gap:** unclear-invariant — the rule that tRNS is valid only for color types 0, 2 and 3 with color-type-specific lengths was stated nowhere and pinned only indirectly by the RGBA path, so it had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### A non-empty IEND payload is silently accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/chunks.py`'s `iter_chunks` checked an IEND chunk's length and CRC
but not its payload, so `png.decode_png`, `png.decode_rgba` and the file
readers accepted an IEND carrying data. The PNG specification gives IEND an
empty data field, so a conformant reader refuses that file; ours decoded it as
if the extra bytes did not exist. Reproduce by replacing a valid PNG's final
`IEND` chunk with `_chunk(b"IEND", b"x")`: the decoder returned the image
instead of raising.

`iter_chunks` now refuses a non-empty IEND by name and offset before yielding
it ("PNG IEND chunk at offset N has M payload bytes; IEND's data field must be
empty"), so every consumer of the chunk stream sees the same diagnosis.

**Validation gap:** unclear-invariant — the IEND-empty-data-field guarantee was not stated in the module docstring or pinned by a test, so it had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### PNG chunks after IEND are silently ignored (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` stopped at the first IEND, so a
complete chunk after it — an ancillary `tEXt`, a second `IDAT`, even a second
`IHDR` — was dropped and `png.decode_png` returned the image. The same held
for 1-7 trailing bytes too short to be a chunk header. Reproduce by appending
`_chunk(b"tEXt", b"x")`, a second IDAT, or a few bytes of a chunk to a valid
PNG's bytes: the decoder returned the image instead of raising.

The reader now keeps walking after IEND and refuses any later complete chunk
by name ("… after IEND; IEND must be the last chunk"), while the framing
iterator still yields those chunks to callers that want them. A trailing
fragment after IEND, which the iterator's framing loop cannot see as a chunk,
is refused there by name ("… trailing bytes after IEND that do not form a
chunk; IEND must be the last chunk").

**Validation gap:** unclear-invariant — the IEND-last guarantee was not stated in the module or pinned by a test, so it had to be reconstructed from the PNG specification; the reconstructed invariant is recorded in docs/invariants.md.

### Non-consecutive IDAT chunks and PLTE/tRNS after IDAT are accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` concatenated every IDAT payload and
kept a PLTE or tRNS payload wherever it appeared, so a malformed stream whose
IDAT chunks are separated by another chunk, or whose PLTE/tRNS follows the
image data, decoded as if its chunk order were valid. Reproduce by building a
1x1 RGB PNG whose IDAT is split around a tEXt chunk, or a palette PNG whose
PLTE chunk is moved after IDAT: `png.decode_png` returned the image instead of
raising.

The guard now closes the IDAT run at the first non-IDAT chunk and refuses a
later IDAT, and refuses a PLTE or tRNS once image data has started, matching
the PNG chunk-order rules while still allowing ancillary chunks after the last
IDAT.

**Validation gap:** unclear-invariant — the chunk-order guarantee was neither stated in the module nor pinned by a test, so it had to be reconstructed from the PNG specification; the reconstructed invariant is recorded in docs/invariants.md.

### GTK settings edits rewrite a foreign file's line endings (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`gtk_settings.set_theme_name` and `remove_theme_name` split a settings file on every boundary `str.splitlines` recognises and rejoined the lines with `"\n"`, so editing the `gtk-theme-name` key in a CRLF, lone-CR or mixed-ending `settings.ini` rewrote every foreign line's terminator, contradicting the module's promise and `docs/invariants.md` that every foreign line is preserved.

**Reproduction.** `set_theme_name("[Settings]\r\ngtk-font-name=Lato 10\r\n", "org.macos8.desktop")` returned `'[Settings]\ngtk-font-name=Lato 10\n...'`; `tests/test_gtk_settings.py::TestLineEndings` now pins every foreign line's ending through replacement, insertion, appending and removal.

**Validation gap:** none — a scratch call to `set_theme_name` showed the rewritten endings immediately; no shim or real run was needed, though no existing test covered a CRLF file.

### The PNG decoder accepts trailing bytes after the IDAT zlib stream (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`decode_png` and `decode_rgba` inflate the IDAT stream and check its output length, end marker and adler32, but never inspect `zlib.decompressobj.unused_data`. A PNG whose IDAT payload is a valid zlib stream followed by arbitrary bytes therefore decodes successfully, silently dropping the trailing bytes instead of refusing the malformed image.

**Reproduction.** `png_with_idat(zlib.compress(raw) + b"trailing")`, where `raw` is a valid 1x1 RGB scanline, decoded to the pixel instead of raising `PngError`; `tests/test_png_malformed.py::TestMalformedImageData::test_rejects_trailing_bytes_after_the_zlib_stream` now pins the refusal.

**Validation gap:** unclear-invariant — the decoder's docstring promised the whole compressed stream was validated but never stated that the IDAT stream must end exactly at the zlib trailer, so the reconstructed invariant is recorded in `docs/invariants.md`.

### `apply_gtk --remove` refuses to clear the GTK selection when no data home resolves (found by the bugfix role 2026-10-23; fixed 2026-10-23 by the bugfix role)

**Symptom:** `python3 tools/apply_gtk.py --remove` (and so `make remove-gtk`)
exits 2 with an `XDG_DATA_HOME` diagnostic and leaves the selection in place
when `$XDG_DATA_HOME` and `$HOME` are unusable, even though
`$XDG_CONFIG_HOME` is absolute and removal reads and writes only the config
home.

**Reproduction:** a scratch run with our `gtk-theme-name` lines in a temporary
`$XDG_CONFIG_HOME`, `env -i PATH=... XDG_CONFIG_HOME=<tmp>` and no `HOME` or
`XDG_DATA_HOME`, printed `apply_gtk: error: XDG_DATA_HOME is unset or not
absolute ...` and exited 2 with the key still present. The new
`tests/test_gtk_apply.py::TestRemove::test_remove_clears_the_selection_without_a_resolvable_data_home`
failed the same way before the fix and passes after it.

**Cause:** `main` resolved both the data and config homes before dispatching,
although `_remove` takes only the config home; the apply path is the only one
that reads the installed sheet below the data home.

**Fix:** `main` resolves the data home only on the apply path and checks only
the config home for removal. Applying still refuses an unresolvable data home.

**Validation gap:** no-observability — every existing removal test supplied a
data home, so the removal's needless data-home dependency left no failing
trace; the closest tag is no-observability.

### The Aurorae decoration reader blocks forever on a FIFO at `decoration.svg` or `decoration.svgz` (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** the Aurorae decoration suite reads contributor-supplied artwork
without a regular-file guard. `SvgCase.setUp` parses `decoration.svg` with
`ET.parse(path)`, and `tests/test_aurorae_frame.py`'s `_read_capped` opens
`decoration.svgz` with `gzip.open()`. A FIFO at either path has no writer, so
the open or parse blocks and `make check` stalls with no diagnostic.

**Reproduction:** a scratch child called `_read_capped(fifo)` on a temporary
FIFO and was still blocked when the 3-second subprocess timeout fired. The new
`tests/test_aurorae_frame.py::TestReadCappedContainment::test_refuses_a_fifo_instead_of_blocking`
hit the test's 10-second timeout before the fix and passes after it; it runs the
real `parse_svg` path for `decoration.svg` as well as the capped gzip read.

**Cause:** the reader's earlier hardening refused symlink escapes and oversize
decompression, but `parse_svg` and `_read_capped` still opened the path itself
rather than the shared regular-file guard. `ET.parse` and `open()` on a FIFO
wait for a writer before any read-side check can run.

**Fix:** both readers now open through `containment.open_regular_binary`, which
opens non-blocking and refuses a descriptor that is not a regular file by name.
`parse_svg` hands the guarded handle to `ET.parse`; `_read_capped`'s optional
opener wraps its guarded handle, so the gzip path still decompresses through
the size cap, and `tests/support/containment.py` re-exports the shared helper.

**Validation gap:** no-observability — the aurorae reader tests covered symlink
escapes, outside paths and oversize decompression but never a non-regular path,
so the FIFO hang left no failing trace until a scratch child call surfaced it.

### The containment guard fails open for a root spelled with a POSIX double leading slash (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** `tools.containment.is_within("//tmp/repo", "/tmp/repo/link")` returns
False even though both spellings name the same directory on POSIX. Because
`require_within_repo` resolves a path only when `is_within` says it is eligible, a
root spelled `//tmp/repo` makes `read_bytes` return a symlink target outside the
repository instead of refusing the escape (fail open).

**Reproduction:** a scratch read of a temporary root's escaping symlink, passing
`"//" + root.lstrip("/")` as the root, returned the secret's bytes. The new
`tests/test_containment.py::TestReadBytes::test_rejects_a_symlink_escape_when_the_root_has_a_double_slash_prefix`
and
`tests/test_containment.py::TestIsWithin::test_treats_a_posix_double_slash_spelling_as_the_same_root`
failed before the fix and pass after.

**Cause:** `os.path.abspath` preserves a path's exactly-two leading slashes, so
the lexical comparison saw `//tmp/repo` and `/tmp/repo` as different, and the
root's child was judged outside the root before the resolver ran.

**Fix:** `is_within` normalizes a POSIX path's double-leading-slash spelling to
one slash before comparing, and builds the boundary by trimming trailing
separators and appending exactly one, so `/`, `//`, and ordinary roots all keep
a correct component boundary.

**Validation gap:** no-observability — no caller in the suite or tools passes a
root with a double-slash spelling, so the fail-open left no trace until a direct
scratch call with a temporary root surfaced it.

### The lexical containment guard rejects every child of a filesystem root (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** `tools.containment.is_within("/", "/etc")` returns False, though every
absolute path is inside `/`. Because `require_within_repo` resolves a path only when
`is_within` says it is eligible, a root of `/` makes the guard skip the symlink-escape
check for every path (fail open) instead of refusing an escaping one.

**Reproduction:** a scratch call printed `False` for `is_within("/", "/etc")`;
`tests/test_containment.py::TestIsWithin::test_accepts_a_path_under_the_filesystem_root`
failed on it before the fix and passes after.

**Cause:** the guard compared `absolute.startswith(base + os.sep)`. A base of `/`
already ends with the separator, so the boundary became `//` and no real child matched it.

**Fix:** `is_within` appends `os.sep` only when the base does not already end with one,
so both a filesystem root and an ordinary directory keep a correct boundary.

**Validation gap:** no-observability — no caller in the suite or tools passes a filesystem
root, so the guard's contract violation left no trace until a direct scratch call and the
new test surfaced it.

### A malformed KDE group header makes the test-side reader raise where KDE ignores it (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a KDE INI text whose group header has no closing `]` (for example `[General`) makes
`tests/support/kde_config.py`'s `read` raise `configparser.MissingSectionHeaderError` (when it is
the first line) or `configparser.ParsingError` (after a valid section), aborting the caller.
KConfig 6.13 logs `Invalid group header` and ignores the line: a following key with no new header
stays in the previous section, and a key before any valid header is filed in KDE's `<default>`
root group. The other two
readers already disagree on the same text, so this is the same recurring divergence the parity
corpus was meant to catch: `defaults_groups` deliberately raises `ValueError` naming the heading,
while the `uninstall` awk treats `[General` as the `General` section.

**Reproduction:** confirmed with `kreadconfig6` 6.13.0 and a scratch `kdeglobals`. For
`[General\nColorScheme=MacOS8\n`, KDE warns about the header and files the key in `<default>`, so
it resolves no `[General]` value; the test-side reader raises `MissingSectionHeaderError` and the
awk prints `MacOS8`. For
`[General]\nColorScheme=BreezeLight\n[Broken\nColorScheme=MacOS8\n`, KDE resolves `MacOS8`
(continuing `[General]`), the test-side reader raises `ParsingError` and the awk prints
`BreezeLight`.

**Suggested direction:** add both shapes to `tests/support/kde_ini_corpus.py` and decide the
shared rule before changing a reader: KDE's skip-and-continue for the test-side reader and awk
(the reader can drop a line that starts with `[` and has no closing `]`), while
`defaults_groups` may keep its stricter refusal because its headings name output files and a
silently skipped heading would drop a whole config section. Record whichever contract is chosen
in the parity corpus docstring and `docs/invariants.md`.

**Fix:** `tests/support/kde_config.py`'s `_parseable_lines` now drops a line that opens a heading
but never closes it, keeping the open section for the keys after it, and keeps a key line seen
before the first valid heading in KDE's `<default>` root group rather than discarding it. An empty
`[]` heading opens a group of its own, so the keys after it are not left in the previous section
(configparser has no empty section name, so those keys are dropped). `read` thus resolves what
KConfig resolves instead of raising. The `uninstall` recipe's `awk` skips a `[`-opened line with
no `]` for the same reason, and `[]` already reset its section to none, so no following key joined
the previous section. `defaults_groups` keeps its stricter `ValueError` because its headings name
output files; the corpus marks that split with a `defaults_raises` field, and
`tests/test_kde_ini_parity.py` feeds both malformed shapes, the empty header and the root-group key
through all three readers. `docs/invariants.md`'s tooling row records the contract.

**Validation gap:** none — `kreadconfig6` 6.13.0 and the scratch `kdeglobals` reproduced both
shapes deterministically, and the new corpus cases failed before the fix (`MissingSectionHeaderError`
and `ParsingError` from the reader; the awk returned `BreezeLight` where KDE resolves `MacOS8`) and
passed after it.

### KDE's config-reading rules are re-derived in three readers, so a quirk fixed in one is not checked in the others (found by the steward role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** three independent readers implement KDE's INI dialect:
`tests/support/kde_config.py`'s `read` (the reader the theme tests use), the inline `awk` in the
`_uninstall` recipe (`Makefile`, the "Read ... the way KDE reads it" block), and
`tools/theme_defaults.py`'s `defaults_groups`. Each defines the same rules itself: strip a leading
UTF-8 BOM, trim each line before it can open a section or key, keep key names case-sensitive, and
let the last duplicate key win. A rule learned by one reader is not exercised on the other two.
They already disagree: `kde_config.read` returns `MacOS8` for a `ColorScheme:MacOS8` line
(`configparser` accepts `:` as a delimiter), while the Makefile's awk reads no value for it, and
no test or doc says which reading matches KDE.

**Why this is a structural risk:** the same quirk has already been fixed once per reader. On
2026-10-19 the missing-BOM case was fixed twice: in `make uninstall`'s awk (`BUGS-FIXED.md`:
"`make uninstall`'s color-scheme warning misses a `kdeglobals` that opens with a UTF-8 BOM") and
in `kde_config.read` (`BUGS-FIXED.md`: "`tests/support/kde_config.py` cannot read a KDE INI that
opens with a UTF-8 BOM"); the commit that made the second fix (`23978a0`) drops the same change
from `theme_defaults` as a duplicate. The awk then separately learned the indented-header rule
(`BUGS.md ## Fixed`) and last-key-wins (`BUGS-FIXED.md`: "`make uninstall`'s color-scheme warning
reads the first duplicate `ColorScheme` key, not the last"), and `defaults_groups`'
indented-heading case was pinned only later (`1b71ead`). The gap tags record this as recurring
(the BOM pair as `no-observability`, the header and duplicate-key cases as `unclear-invariant`),
but neither promoted remedy covers it: the mutation harness targets the shipped registers and
checkers, and `docs/invariants.md` has no row for KDE INI semantics. No test feeds one fixture
text through more than one reader, so a divergence is invisible:
`tests/test_colorscheme_install.py` drives the Makefile reader through `make uninstall` with
hand-written fixtures, `tests/test_kde_config.py` pins `kde_config.read` with its own, and
`tests/test_theme_defaults.py` pins `defaults_groups` with a third set.

**Reproduction:** no failing behaviour is needed; each reader passes its own cases. Confirm the
drift with a scratch `kdeglobals` holding `[General]` then `ColorScheme:MacOS8`:
`kde_config.read` returns `MacOS8`, and the `_uninstall` recipe's awk prints nothing.

**Suggested direction:** keep one fixture corpus of small KDE INI texts (BOM, indented header,
indented key, duplicate key, case mismatch, colon-delimited key, comment, blank line, `%` in a
value) and one test that runs the corpus through `kde_config.read`, `defaults_groups` and the
Makefile's reader (through `make uninstall`, as the install tests already do), asserting the same
interpretation and recording the chosen KDE semantics in `docs/invariants.md`'s `tooling`
section; a new quirk then lands in one place and fails in every reader that misses it.

**Fix:** `tests/support/kde_ini_corpus.py` holds one small text per rule, and
`tests/test_kde_ini_parity.py` feeds every case through `kde_config.read`, `defaults_groups` and
`make uninstall`. The corpus pins KDE's observed semantics: `=` is the only key/value delimiter
(a colon-delimited line is an invalid entry, ignored), each line is trimmed, section and key names
are case-sensitive, the last duplicate key wins, and only a leading `#` starts a comment. The
readers already agreed except `kde_config.read`, which now parses with `=` alone, skips the
no-`=` lines KDE skips instead of rejecting the file, treats only `#` as a comment, and lets the
last duplicate key win. `docs/invariants.md`'s `tooling` section now records the shared
semantics. The BOM case stays: all three readers strip one as a deliberate leniency (KConfig
6.13 logs a BOM-prefixed first line as invalid) so an editor-saved file still loads.

**Validation gap:** none — the entry's scratch `kdeglobals` reproduced the colon divergence
deterministically, and the new parity test failed on the colon and duplicate fixtures before the
fix and passed after it.

### `make uninstall`'s color-scheme warning misses an indented `[General]` section header (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `$XDG_CONFIG_HOME/kdeglobals` opens its `[General]` section with a line
that has leading whitespace, `make uninstall` does not warn about a still-selected scheme.
KDE trims each line before parsing it, so the indented header still opens `[General]` and its
`ColorScheme` key is the live selection; the diagnostic claims to read kdeglobals "the way
KDE reads it", so the missing warning is a real, if low-severity, gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_an_indented_general_section`
writes `"  [General]\nColorScheme=MacOS8\n"` as kdeglobals and runs `make uninstall`; before
the fix it emitted no warning.

**Cause:** the uninstall recipe's `awk` recognised a section header only at the start of the
line (`/^\[/`), so an indented `[General]` was never seen as the current section and its
`ColorScheme` key was skipped.

**Fix:** the `awk` now matches and strips leading whitespace before the `[` (`/^[[:space:]]*\[/`),
matching KDE's trim-before-parse behaviour.

**Validation gap:** unclear-invariant — no test or doc stated that KDE's config reader trims a
line before matching a section header, so that invariant had to be established before the
parser could be pinned to it.

### `make uninstall`'s color-scheme warning misses a `kdeglobals` that opens with a UTF-8 BOM (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `$XDG_CONFIG_HOME/kdeglobals` opens with a UTF-8 BOM before its
`[General]` header, `make uninstall` does not warn about a still-selected scheme.
Qt (and the project's `tests/support/kde_config.py`) strips a leading BOM before
parsing, so the BOM-prefixed file still opens `[General]` and its `ColorScheme`
key is the live selection; the diagnostic claims to read kdeglobals "the way KDE
reads it", so the missing warning is a real, if low-severity, gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_a_kdeglobals_with_a_utf8_bom`
writes `"\ufeff[General]\nColorScheme=MacOS8\n"` (encoding `utf-8`, so the BOM
bytes `EF BB BF`) as kdeglobals and runs `make uninstall`; before the fix it
emitted no warning.

**Cause:** the uninstall recipe's `awk` recognised a section header only with
`/^[[:space:]]*\[/`, so the BOM bytes before the `[` kept the first line from
being seen as a section and its `ColorScheme` key was skipped.

**Fix:** the `awk` now strips a leading UTF-8 BOM on its first record
(`NR==1 { sub(/^\357\273\277/, "") }`) before matching, matching Qt's
strip-before-parse behaviour.

**Validation gap:** no-observability — the suite never wrote a BOM-prefixed
kdeglobals, so the omitted warning left no trace and only a new BOM case could
confirm it.

### A NUL byte in a guarded path escapes the containment guard's fail-closed contract (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tools/containment.resolves_within` documents that a path whose resolution
fails is refused, not assumed contained, but an embedded NUL byte makes POSIX
`Path.resolve()` raise `ValueError`, which the guard did not catch. The error escaped as a bare
`lstat: embedded null character in path` instead of the guard's own refusal, so a caller that
expected a boolean or the named `ValueError` saw an unrelated exception.

**Reproduction:** `containment.resolves_within(root, root / "a\x00b")` raised `ValueError`, and
`containment.require_within_repo(root / "a\x00b", root)` raised the bare `lstat` error. Pinned by
`tests/test_containment.py::TestResolutionFailureFailsClosed`.

**Cause:** `resolves_within` caught only `OSError` and `RuntimeError` from `Path.resolve()`;
POSIX `Path.resolve()` raises `ValueError` for an embedded NUL.

**Fix:** `resolves_within` now also catches `ValueError`, so every resolution failure fails
closed; `require_within_repo` then raises its own named refusal.

**Validation gap:** no-observability — no reader passes a NUL-bearing path, so the guard's
contract violation left no trace in the suite and surfaced only from a direct scratch call.

### The symlink-containment guard is reimplemented at five sites (found by the steward role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** the guarantee "refuse a contributor-supplied repository file whose path resolves
outside the repository" was implemented five times. Four copies used one mechanism and one used
another: `tests/support/containment.py` (the shared guard), `tests/placeholders.py`'s
`_resolves_within`, `tests/invariants.py`'s inline check, and `tools/theme_defaults.py`'s
`_require_within_repo` compared `os.path.realpath` results with `startswith(base + os.sep)`;
`tools/reference_validation.py`'s `_resolves_within` used
`Path.resolve().is_relative_to(directory.resolve())`. A refinement applied to one copy did not
reach the other four, so a later reader could adopt a stale copy and reopen the leak class the
guard exists to close.

**Why this is a structural risk:** the same contributor-content leak has been fixed one module at
a time. Seven `no-fake` Fixed entries in `BUGS-FIXED.md` are that class, each a module that read
its repository file bare and needed its own symlink fixture to confirm the leak:
`tests/placeholders.py`'s `cross_check`; `tests/invariants.py`'s `cross_check`;
`tests/support/checker_mutations.py`'s register reads; the color-scheme provenance test; the
desktop-theme copy-identity tests; `tests/support/splash_fixtures.py`; and
`tests/support/package_metadata.py`. The shared `tests/support/containment.py` was extracted along
the way, but four modules still kept a local copy of the check.

**Suspected cause:** `tools/` cannot import `tests/support/`, so `tools/theme_defaults.py` and
`tools/reference_validation.py` grew their own copies; `tests/placeholders.py` and
`tests/invariants.py` kept a local check from before the shared helper existed, even though both
already import `support.containment` for another read.

**Fix:** the guard now lives once in `tools/containment.py`, the one module both trees can import
(tests reach it as `tools.containment` with the repository root on `sys.path`).
`tests/support/containment.py` re-exports the shared functions under the name the test helpers
already use, and `tests/placeholders.py`, `tests/invariants.py`, `tools/theme_defaults.py` and
`tools/reference_validation.py` call the shared `resolves_within`/`require_within_repo` instead of
their local copies. `tests/test_containment.py::TestGuardIsShared` pins the single
implementation, and the `tooling` section of `docs/invariants.md` records the guarantee.

**Validation gap:** no-observability — the five copies had no failing behavior to reproduce, so
only a source-level check can observe the drift risk; the regression test parses the four readers'
ASTs and rejects a local resolver definition or an inline `realpath`/`is_relative_to` call.

### `make install INSTALL_PACKAGES=<unknown>` silently installs nothing (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make install INSTALL_PACKAGES=colour-scheme` (a typo, or any name
that is not one of the seven families) filtered every family out, created the
data home, copied nothing and exited 0 — a green install that installed nothing,
the same failure the empty-value guard refuses.

**Reproduction:**
`tests/test_theme_install.py::TestInstallPackagesGuard.test_unknown_family_is_refused_before_creating_the_data_home`
runs `make install INSTALL_PACKAGES=colour-scheme`; before the fix it exited 0
with an empty data home.

**Cause:** `require_install_packages` only rejected an empty or whitespace-only
value; it never checked that each named word was a known artifact family, and
`_install`'s `$(filter ...)` guards turn an unknown word into a no-op.

**Fix:** the guard now word-splits `INSTALL_PACKAGES` (with `set -f` so a glob
cannot expand), refuses an empty list as before, and refuses any word not in the
new `INSTALL_FAMILIES` list with a diagnostic naming the unknown families and
the known ones.

**Validation gap:** unclear-invariant — no test or doc stated that the guard's
promise was "no green install that installs nothing" rather than "reject the
empty value", so that invariant had to be reconstructed and is now recorded in
`docs/invariants.md` (tooling).

### `tests/support/kde_config.py` cannot read a KDE INI that opens with a UTF-8 BOM (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `kde_config.read` opened the file with `encoding="utf-8"`, so a leading
BOM stayed in the first line. `configparser` then found no section header and raised
`MissingSectionHeaderError` ("File contains no section headers") instead of reading
the file the way Plasma's `QSettings`/`QTextStream` does (Qt strips a UTF-8 BOM). A
contributor-supplied `MacOS8.colors`, `org.macos8.desktoprc`,
`org.macos8.desktop.kvconfig` or `contents/defaults` saved with a BOM therefore
aborted the test that read it.

**Reproduction:** a scratch run wrote `b"\xef\xbb\xbf[General]\nColorScheme=MacOS8\n"`
to a temp file and called `kde_config.read(path)`; it raised
`MissingSectionHeaderError` at line 1.
`tests/test_kde_config.py::TestReadKdeConfig.test_strips_a_leading_utf8_bom` now pins
the fixed behavior.

**Cause:** `read` opened with `encoding="utf-8"`, so the BOM was not stripped before
`configparser.read_file`.

**Fix:** read with `encoding="utf-8-sig"`, which strips a leading BOM and behaves
identically to `utf-8` for BOM-less files, matching Qt's reader and the project's
other contributor-file readers (`tools/theme_defaults.py`,
`tools/reference_validation.py`).

**Validation gap:** no-observability — no test read a BOM-prefixed INI, so the
reader's mishandling was never triggered in the suite and only a new BOM case could
confirm it.

### `tests/placeholders.py`'s `cross_check` reads a symlinked `PLACEHOLDERS.md` bare (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `PLACEHOLDERS.md` is a checked-in symlink resolving outside the repository,
`cross_check(ROOT, REGISTER)` opened it bare and parsed its table rows. A row matching the
register's `| \`path\` | stands in for |` shape then reached an `AssertionError` that echoes the
asset path (`"... lists <asset>, which does not exist"`), leaking a line of a private file into
the failing test's diagnostic.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers.test_cross_check_refuses_a_symlinked_register_that_escapes`
symlinks a temp root's `PLACEHOLDERS.md` to a private file containing
``| `secret-token` | classified |``; before the fix the `AssertionError` contained
`secret-token`.

**Cause:** `cross_check` passed its `register` straight to `register_entries`, which opened it
with a bare `open(path, encoding="utf-8")`; nothing checked that a repository register still
resolved inside the repository.

**Fix:** `cross_check` now calls `support.containment.require_within_repo(register, root)` before
reading the register, so a path lexically inside `root` that resolves outside it raises
`ValueError` before any row is parsed. A register outside `root` (a test's temporary file) is
unaffected.

**Validation gap:** no-fake — the leak needed a manufactured private file plus a symlinked
register that the suite did not previously build.

### `tests/invariants.py`'s `cross_check` reads a symlinked register bare (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when the register path handed to `cross_check` is a checked-in symlink that
resolves outside the repository (the shipped call passes `docs/invariants.md`), the register is
read and parsed anyway. `parse_rows` echoes a malformed table row's line in its
`AssertionError`, so a private file's line reaches the failing test's diagnostic. This is the
same contributor-content leak class the seed reads in `tests/support/checker_mutations.py` were
guarded against, left open on the checker's own production read.

**Reproduction:**
`tests/test_invariants.py::TestHelpers.test_cross_check_refuses_a_symlinked_register_that_escapes`
symlinks `docs/invariants.md` under a fake root to a private file holding a malformed row and
calls `cross_check`; before the fix it raised `AssertionError: malformed table row ... |
secret-token | short`, echoing the private line, instead of refusing the escape.

**Cause:** `cross_check` opened the register with a bare `open(register, encoding="utf-8")`
and caught only `UnicodeDecodeError`/`OSError`; a symlink resolving outside `root` was followed
like any other file.

**Fix:** the read now routes through `support.containment.read_text(register, root)`, which
resolves the path and raises `ValueError` naming the escape before opening it. A register that
is a test's temporary file outside `root` is unaffected, as are the missing-file and non-UTF-8
paths, which still surface as the checker's own `AssertionError`.

**Validation gap:** no-fake — the suite had no `cross_check` fixture with a symlinked register,
so confirming the leak needed a scratch fake root plus a symlink, which was then added as the
regression test.

### `tests/support/checker_mutations.py`'s register reads follow a symlinked register outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `Scratch.build` read `docs/invariants.md` and `PLACEHOLDERS.md` with a bare
`Path.read_text`, so a checked-in symlink at either path that resolves outside the repository
was followed. That text seeds the scratch copy the checker runs against, and
`tests/invariants.py` echoes a malformed row's line in its `AssertionError`, so a private
file's line could reach a failing test's diagnostic.

**Reproduction:** with `checker_mutations.ROOT` pointed at a scratch root whose
`docs/invariants.md` symlinks a private file outside that root, `Scratch.build` returned a
scratch holding the private line and `invariants.cross_check` raised
`malformed table row in section secret (expected 3 cells): | a | b`, echoing it;
`tests/test_checker_mutations.py::TestCheckerMutations.test_register_reads_refuse_a_symlink_escape`
now pins the refusal.

**Cause:** the two seed reads bypassed `support/containment.py`, the guard every other reader
of a contributor-supplied repository file goes through.

**Fix:** both reads go through a new `_read_register` helper that calls
`containment.read_text(ROOT / relative_path, ROOT)`, which refuses a path that resolves
outside the repository.

**Validation gap:** no-fake — no fixture created a symlinked register, so confirming the leak
needed a fake repository root with the register symlinked outside it.

### The color-scheme provenance test reads `MacOS8.colors` unguarded (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tests/test_colorscheme.py::TestProvenanceNote.test_tooltip_is_named_as_not_reference_sampled`
opened `SCHEME` with a bare `open()`, joined its `#` comment lines into `text`, and passed `text`
to `assertIn`/`assertRegex`. A checked-in symlink at
`theme/color-schemes/MacOS8.colors` to a private file is read, and a failing assertion echoes
that file's comment lines into the diagnostic. Unlike `load_scheme`/`kde_config.read`, this read
never called `containment.require_within_repo`.

**Reproduction:** point `SCHEME` at a symlink to a private file whose comment lines lack
`[Colors:Tooltip]`; the `assertIn` diagnostic contained the private comment lines. A scratch
script with the symlink at a repository path showed the bare read echoing
`private secret line [Colors:Other]`; after the fix the guarded read raises
`ValueError: ... resolves outside ... (a symlink escape)` and echoes nothing. The new
`tests/test_containment.py::TestReadText.test_rejects_a_symlink_that_escapes_the_root` fails
without `containment.read_text`.

**Cause:** the direct `open(SCHEME)` predated the containment guards; the test read the scheme
directly instead of through a guarded reader.

**Fix:** `tests/support/containment.py` gained `read_text(path, root)`, the text sibling of
`read_bytes`, which calls `require_within_repo` before opening; the provenance test now reads
through it.

**Validation gap:** no-fake — confirming the leak needed a symlink fixture the existing suite did
not have, so one had to be manufactured before the diagnostic echo could be observed.

### The desktop-theme copy-identity tests read the secondary SVG copy unguarded (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tests/test_desktoptheme_background.py::TestBackground.test_translucent_copy_is_identical`,
`tests/test_desktoptheme_panel.py::TestPanelBackground.test_solid_copy_is_identical` and
`tests/test_desktoptheme_tooltip.py::TestTooltip.test_solid_copy_is_identical` each open their
secondary SVG copy (`TRANSLUCENT_BACKGROUND_SVG`, `SOLID_PANEL_SVG`, `SOLID_TOOLTIP_SVG`) with a
bare `open()`. A checked-in symlink at that path to a private file is read, and `assertEqual` on
the mismatched byte strings echoes that file's bytes into the failing test's diagnostic.

**Reproduction:** a scratch script (a symlink at the secondary path plus the bare
`open`/`assertEqual` pair) printed the secret's bytes in the `AssertionError`; the new
`tests/test_containment.py::TestReadBytes.test_rejects_a_symlink_that_escapes_the_root` fails
without the guard.

**Cause:** only the primary `SVG_PATH` went through `SvgCase.setUp`'s containment guard; the
copy-identity checks read the duplicate file directly, so the guard the primary path gets was
never applied to the second path.

**Fix:** `tests/support/containment.py` gained `read_bytes(path, root)`, which calls
`require_within_repo` before opening; the three copy-identity tests read both copies through it.

**Validation gap:** no-fake — confirming the leak needed a symlink fixture the existing suite did
not have, so one had to be manufactured before the diagnostic echo could be observed.

### `tests/support/splash_fixtures.py`'s `read_qml` follows a symlinked `Splash.qml` outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a checked-in `Splash.qml` that is a symlink to a private file outside the
repository is opened and its text returned. The splash tests feed that text to `assertIn` and to
`object_source`'s brace-balanced slice, and a failing `assertIn` echoes the container, so the
private file's content can appear in a test diagnostic. The security sweep guarded
`support/kde_config.read`, `header_comment` and `SvgCase.setUp` against exactly this symlink
escape, and the bugfix role guarded `load_metadata`, but left this reader unguarded.

**Reproduction:**
`tests/test_splash_qml.py::TestSplashQmlContainment::test_rejects_a_symlink_that_escapes_the_repository`
makes a `Splash.qml` symlink inside a repository root that points at a private sibling and calls
`read_qml`; before the fix the private text came back and no `ValueError` was raised.

**Cause:** `read_qml` called `open(SPLASH)` with no containment check, so it read the symlink's
target.

**Fix:** `read_qml` now calls `containment.require_within_repo(SPLASH, ROOT)` before opening,
so a `Splash.qml` that resolves outside the repository is refused with the path named, matching
the other contributor-supplied readers.

**Validation gap:** no-fake — the suite never created a symlinked `Splash.qml`, so confirming
the escape needed a symlink fixture and a patched repository root that did not exist.

### `tests/support/package_metadata.py`'s `load_metadata` follows a symlinked `metadata.json` outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a checked-in `metadata.json` that is a symlink to a private JSON file outside the
repository is opened and parsed. The `PackageMetadata` mixin then asserts the parsed object's
fields, and a failing `assertEqual` echoes the actual value, so the private file's content can
appear in a test diagnostic. The security sweep guarded `support/kde_config.read`,
`header_comment` and `SvgCase.setUp` against exactly this symlink escape but left this reader
unguarded.

**Reproduction:**
`tests/test_package_metadata.py::TestLoadMetadataContainment::test_rejects_a_symlink_that_escapes_the_repository`
makes a `metadata.json` symlink inside a repository root that points at a private sibling and
calls `load_metadata`; before the fix the private object came back and no `ValueError` was raised.

**Cause:** `load_metadata` called `open(path)` with no containment check, so `json.load` read the
symlink's target.

**Fix:** `load_metadata` now calls `containment.require_within_repo(path, ROOT)` before opening,
so a `metadata.json` that resolves outside the repository is refused with the path named, matching
the other contributor-supplied readers.

**Validation gap:** no-fake — the suite never created a symlinked `metadata.json`, so confirming
the escape needed a symlink fixture and a patched repository root that did not exist.

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
