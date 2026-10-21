# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-19 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-20 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

Two answers on 2026-10-19 expand the scope again, and neither has a plan yet.
**GTK applications and Firefox** are now in scope (QUESTIONS.md, answered 2026-10-19): a
KDE/Qt global theme cannot reach them, so this needs a GTK 4 CSS theme and a Firefox
`userChrome.css` plus profile preference, installed by separate opt-in `make` targets — a
multi-part series of its own. **The UI font** is now to be vendored (QUESTIONS.md, answered
2026-10-19): the theme should ship a Chicago/Charcoal-style font with a checked redistribution
licence and recorded provenance, select it for KDE, Plasma and Qt applications, and the answer
leaves open whether one face serves both Chicago and Charcoal. The plan queue carries neither
surface yet; until it does, the menu bar and dialog text keep the user's desktop font, and GTK
and Firefox applications keep their own chrome.

### Vendor the Lato body font and install it (planned 2026-10-21 by the plan role; part 1/3)

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
  shared-directory list. In the Status paragraph, replace the archive sentence's tail: it currently
  ends `fixed bugs are archived in BUGS-FIXED.md.` and must end `fixed bugs are archived in
  BUGS-FIXED.md and finished plans in PLANS-DONE.md.` This edit is required; the archive it names
  exists and holds the finished plans, while `PLANS.md`'s own `## Done` section is empty.
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
`docs/invariants.md`, and `PLANS.md`/`PLANS-DONE.md` (this entry moves between them when the
work lands).

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
  text, and the README Status paragraph's archive sentence reads exactly `Open work is tracked in
  PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed); fixed
  bugs are archived in BUGS-FIXED.md and finished plans in PLANS-DONE.md.` (a diff that leaves the
  sentence unchanged fails this plan).
- `git diff --name-status` names only the files listed under "Files touched"; an edit outside that
  list is out of scope for this part.
- When the work lands, `grep -l "Vendor the Lato body font" PLANS.md PLANS-DONE.md` prints only
  `PLANS-DONE.md`: the entry is moved into `PLANS-DONE.md`'s `## Done`, and `PLANS.md`'s own
  `## Done` section stays empty.
- No `kdeglobals` write, global-theme `contents/defaults` change, `tools/apply_*` change, GTK or
  Firefox change is made in this part; `make check` is green.

## Done
