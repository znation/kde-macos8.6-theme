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
(startup splash, desktop layout, defaults); the desktop theme (twenty-six widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
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
