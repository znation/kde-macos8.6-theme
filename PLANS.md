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
(startup splash, desktop layout, defaults); the desktop theme (twenty-five widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight,
plus `dialogs/background.svg`; the panel resize and slider handles in
`widgets/containment-controls.svg` still come from the default theme); the Aurorae window decoration (frame, close, zoom and
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
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, and the drag-and-drop/forbidden aliases, not traced from Apple's
artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; help, progress, pencil, `zoom-in` and `zoom-out` still come from the fallback
cursor theme; **system sounds** are out
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
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Platinum panel edit-mode chrome, part 2/2: ship the panel resize and slider handles (planned 2026-10-23 by the plan role; follows the landed part 1/2 margin highlight)

**Goal.** The desktop theme ships no `widgets/containment-controls.svg`, so while a panel is in
edit mode its offset, minimum and maximum drag handles and its centre indicators come from the
default theme's blue-grey artwork. Ship our own `widgets/containment-controls.svg` for the
fourteen element ids the installed panel configuration resolves, drawn as raised Platinum
thumbs with lavender centre lines. No reference screenshot shows panel edit mode, so the art is
our own: the ids and natural indicator sizes are KDE-required (taken from the installed default
theme and the two consumers), while the colours reuse the grounded Platinum face/bevel palette
and the `#CCCCFF` selection anchor.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg`: a `<svg
width="42" height="42" viewBox="0 0 42 42">` whose fourteen consumers are id-bearing `<g>`
elements at the origin, each holding rects with 0-based coordinates so KSvg reads that group's
bounding box as its natural size. Open with a comment naming the consumers
(`PanelConfiguration.qml` sets the north/south/east/west prefix, `Ruler.qml` asks for the two
centre indicators, and `SliderHandle.qml` builds `prefix + '-' + graphicElementName`), the ids,
and the provenance exception.
  - The twelve slider groups are `north-offsetslider`, `north-minslider`, `north-maxslider`,
`north` repeated for `south`, `east` and `west`. Each is a 9x9 raised Platinum thumb painted in
this document order (later rects override earlier ones, the slider.svg rule):
`<rect width="9" height="9" fill="#DDDDDD"/>`; `<rect y="1" width="9" height="1"
fill="#FFFFFF"/>`; `<rect y="7" width="9" height="1" fill="#999999"/>`; `<rect x="1"
width="1" height="9" fill="#FFFFFF"/>`; `<rect x="7" width="1" height="9"
fill="#999999"/>`; then the four outline rects `<rect width="9" height="1"
fill="#000000"/>`, `<rect y="8" width="9" height="1" fill="#000000"/>`, `<rect width="1"
height="9" fill="#000000"/>` and `<rect x="8" width="1" height="9" fill="#000000"/>`.
  - The grip is the last rect of each slider group: the three offset sliders carry a 3x3 black
centre dot `<rect x="3" y="3" width="3" height="3" fill="#000000"/>`; the north/south
min/max sliders carry a vertical 1x5 black bar `<rect x="4" y="2" width="1" height="5"
fill="#000000"/>`; the east/west min/max sliders carry the horizontal 5x1 bar `<rect x="2"
y="4" width="5" height="1" fill="#000000"/>`.
  - The two centre indicators are `vertical-centerindicator` (a vertical panel stretches it
across the panel width) with one `<rect width="42" height="1" fill="#CCCCFF"
fill-opacity="0.4"/>`, and `horizontal-centerindicator` (a horizontal panel stretches it down
the panel height) with one `<rect width="1" height="42" fill="#CCCCFF"
fill-opacity="0.4"/>`. The 42x1/1x42 natural geometry and the 0.4 opacity are the installed
default theme's; the colour is the grounded selection lavender.
- `tests/support/desktoptheme_paths.py`: add `CONTAINMENT_CONTROLS_SVG` pointing at
`widgets/containment-controls.svg`.
- `tests/test_desktoptheme.py`: add `("containment-controls.svg", CONTAINMENT_CONTROLS_SVG,
42, 42)` to `SVG_CANVASES` and `os.path.join("widgets", "containment-controls.svg")` to
`TestInstall.INSTALLED_FILES`, so the canvas, unique-id, self-containment, registry-completeness
and install-lifecycle checks cover the new file.
- New `tests/test_desktoptheme_containmentcontrols.py` (`SvgCase`, `SVG_PATH =
CONTAINMENT_CONTROLS_SVG`):
  - `test_containment_controls_contract`: all fourteen ids are present, ids are unique, and the
file has no script, style or external reference.
  - `test_sliders_are_raised_platinum_thumbs_with_grips`: render each of the twelve slider
groups with `render_slices` and compare its full pixel map to `raised_thumb_pixels(9, 9)` from
`support.thumb_fixtures` with the pinned grip pixels overwritten to `BLACK` -- the 3x3 dot for
the offset sliders, the vertical 1x5 bar for north/south min/max, the horizontal 5x1 bar for
east/west min/max. This pins every pixel, the 9x9 natural size and the grip orientation, so a
shifted bevel, a resized group or a swapped grip fails.
  - `test_center_indicators_are_lavender_lines`: each indicator group renders exactly 42
`SELECTION` pixels in the pinned 42x1 or 1x42 shape, and each of its rects carries
`fill-opacity="0.4"`.
  - `test_containment_controls_colours`: `assert_fill_palette(self, self.tree,
extra={SELECTION})`, so the parsed fill set is exactly the Platinum face/bevel palette plus the
selection lavender.
- `README.md`: replace the sentence that says the panel resize and slider handles still come from
the fallback theme with one naming `widgets/containment-controls.svg`, its twelve offset/min/max
sliders and its two centre indicators.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the panel edit-mode sliders are
raised Platinum thumbs and the centre indicators lavender lines, pinned by
`tests/test_desktoptheme_containmentcontrols.py::TestContainmentControls`; the provenance
exception records that no reference screenshot shows panel edit mode, the fourteen ids and the
42x1/1x42 indicator geometry plus 0.4 opacity are KDE-required, and the colours reuse the
grounded Platinum and selection anchors.
- `PLANS.md`: in the scope-drift paragraph, change the widget-SVG count from twenty-five to
twenty-six, name the new containment-controls file, and drop the claim that its handles still
come from the default theme.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg` (new),
`tests/test_desktoptheme_containmentcontrols.py` (new),
`tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`,
`docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 42x42 canvas with the fourteen pinned ids present and unique, every
slider group rendering as the pinned 9x9 raised thumb plus its orientation's grip, and the two
indicator groups rendering as the pinned 42x1 or 1x42 lavender line at 0.4 opacity.
- The parsed fill set is exactly `#000000`, `#FFFFFF`, `#999999`, `#DDDDDD` and `#CCCCFF`;
dropping an id, resizing a group, swapping a bevel colour or turning a grip the wrong way fails
a test.
- `TestSvgRootCanvas`'s registry and `TestInstall.INSTALLED_FILES` cover the new file,
`tests/invariants.py` accepts the new `## desktoptheme` row, and README and the scope-drift
paragraph name it with the scope-drift count at twenty-six.
- `make check` is green.

### Retire the `no-fake` validation gap with a fixture ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-fake` tag, 14 Fixed entries)

**Goal.** Fourteen Fixed entries in BUGS-FIXED.md carry `gap: no-fake` — confirming the failure
needed a fake, shim or manufactured fixture the shipped suite did not have. The shared fixture kit
those records needed now exists (`symlinked_repo` in `tests/support/symlink_fixtures.py`, the
scratch/mutation helpers in `tests/support/checker_scratch.py`, `tests/support/invariants_mutations.py`
and `tests/support/placeholders_mutations.py`, and the chunk builders in
`tests/support/png_fixtures.py`), and the fixes have reproducing tests, but no ledger maps the
records to those fixtures and nothing stops a new `no-fake` record landing uncovered. Add the third
validation-gap ledger, mirroring the `no-observability` and `unclear-invariant` ones, and give the
one hand-assembled PNG stream a named builder, so a future no-fake failure lands with a fixture and
a test instead of growing the tag.

**Cited entries.** The fourteen `gap: no-fake` records in BUGS-FIXED.md:
- Symlink-escape fixtures (7): `tests/placeholders.py`'s `cross_check` reads a symlinked
  `PLACEHOLDERS.md` bare; `tests/invariants.py`'s `cross_check` reads a symlinked register bare;
  `tests/support/checker_mutations.py`'s register reads follow a symlinked register outside the
  repository; The color-scheme provenance test reads `MacOS8.colors` unguarded; The desktop-theme
  copy-identity tests read the secondary SVG copy unguarded; `tests/support/splash_fixtures.py`'s
  `read_qml` follows a symlinked `Splash.qml` outside the repository;
  `tests/support/package_metadata.py`'s `load_metadata` follows a symlinked `metadata.json`
  outside the repository.
- Unreadable / non-UTF-8 / dangling-path fixtures (4): `tests/invariants.py`'s `cross_check` lets
  an unreadable register escape as a bare `OSError`; `tests/support/package_metadata.py` lets an
  unreadable `metadata.json` escape as a bare `OSError`; `tests/placeholders.py` lets an unreadable
  register escape as a bare `OSError`; `tests/placeholders.py` lets a dangling symlink inside
  `theme/` escape as a bare `FileNotFoundError`.
- Manufactured inputs (3): A palette image with `tRNS` before `PLTE` is accepted;
  `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception; `tests/invariants.py` lets a reference to an unreadable test file escape as an
  unrelated exception.

**Approach.**
- `tests/support/png_fixtures.py`: add `palette_trns_before_plte()`, returning the record's stream
  (`png_stream(ihdr_chunk(1, 1, 3), _chunk(b"tRNS", bytes([0, 128])), _chunk(b"PLTE", bytes([255,
  0, 0, 0, 255, 0])), _chunk(b"IDAT", zlib.compress(bytes([0, 0]))), _chunk(b"IEND", b""))`), so
  the malformed-order case has a named fixture rather than a hand-assembled chunk list.
  `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`
  calls the builder and keeps its two-decoder assertion and its `tRNS chunk before` / `PLTE chunk` /
  `follow` needles.
- `tests/support/validation_gaps.py`: name the third tag in the module docstring; add
  `NO_FAKE_BASELINE = 14`; add `NO_FAKE_REPRODUCTIONS`, reusing the `Reproduction` namedtuple
  (name, markers, reference), with one entry per record — markers name the module and the failure,
  and the reference is the reproducing test:
  - `png-trns-before-plte` → `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`.
  - `placeholders-symlinked-register` → `tests/test_placeholders.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `invariants-symlinked-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `checker-mutations-symlinked-register` → `tests/test_checker_mutations.py::TestCheckerMutations::test_register_reads_refuse_a_symlink_escape`.
  - `colorscheme-provenance-symlink` → `tests/test_containment.py::TestReadText::test_rejects_a_symlink_that_escapes_the_root`.
  - `desktoptheme-copy-symlink` → `tests/test_containment.py::TestReadBytes::test_rejects_a_symlink_that_escapes_the_root`.
  - `splash-symlink` → `tests/test_splash_qml.py::TestSplashQmlContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `metadata-symlink` → `tests/test_package_metadata.py::TestLoadMetadataContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `invariants-unreadable-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_unreadable_register`.
  - `metadata-unreadable` → `tests/test_package_metadata.py::TestLoadMetadata::test_unreadable_file_names_the_path`.
  - `placeholders-unreadable-register` → `tests/test_placeholders.py::TestHelpers::test_register_entries_rejects_an_unreadable_register`.
  - `placeholders-dangling-symlink` → `tests/test_placeholders.py::TestHelpers::test_markers_rejects_a_dangling_symlink_within_the_theme_root`.
  - `invariants-nul-row` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_a_reference_with_a_nul_byte`.
  - `invariants-unreadable-test-file` → `tests/test_checker_mutations.py` (the `unreadable-test-file` mutation).
  Add `no_fake(records)` filtering the tag, `no_fake_reproduction(record)` using the existing
  `_lookup`, and extend `reproduction_for` to dispatch `no-fake` and say so in its docstring.
- `tests/test_validation_gaps.py`: update the module docstring to three ledgers; add
  `TestNoFakeLedger` mirroring `TestNoObservabilityLedger`: every `no-fake` record names a
  reproduction, every reproduction reference is a real test via `check_reference`, every entry
  covers a shipped record, the record count is at most `NO_FAKE_BASELINE` (message tells the next
  author to add an entry and raise the baseline by one), and an unmatched mechanism returns `None`.
- `docs/invariants.md`: extend the tooling row that names the two existing ledgers to name the
  `no-fake` ledger and `tests/test_validation_gaps.py::TestNoFakeLedger`.

**Files touched.** `tests/support/png_fixtures.py`, `tests/support/validation_gaps.py`,
`tests/test_png_malformed.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 14 `no-fake` records; each
  resolves to exactly one `NO_FAKE_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every reproduction reference names a real test, so a deleted or misspelled reference fails
  `check_reference`; a new `no-fake` record without an entry, or a count above 14, fails the suite.
- The palette `tRNS`-before-`PLTE` test still refuses on both decode paths through the named
  builder; reversing the builder's chunk order or changing its payload fails the test.
- `tests/invariants.py` accepts the updated tooling row, and `make check` is green.

## Done
