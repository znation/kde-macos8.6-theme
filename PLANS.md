# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (eighteen widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
placeholder 32x32 art for the desktop's hard-disk, folder, document and Trash icons, tracked in
`PLACEHOLDERS.md`; the Apple-logo kicker icon is not drawn); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-18 by the plan
role): a **Qt widget style** for KDE applications (the desktop theme styles only Plasma shell
widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of Qt's built-in `Windows` style, and the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — planned as the three-part "Mac OS 8.6 Kvantum widget style" series below (parts 2
and 3 wait on part 1); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

### Mac OS 8.6 Kvantum widget style, part 1/3: ship the `org.macos8.desktop` Kvantum theme with the Platinum palette and the core-control art (planned 2026-10-18 by the plan role)

**Goal.** The user answered 2026-10-18 that a pixel-matched Platinum Qt style should ship as a
Kvantum theme and be selected (Option 1). This part creates that theme package and installs it,
leaving the global theme's `widgetStyle=Windows` selection untouched until the whole widget set is
themed (part 3). It ships the Platinum palette, the grounded geometry and our own SVG art for the
controls the reference screenshots show most directly: push and tool buttons, line edits, combo
boxes, check boxes, radio buttons, the focus ring, the generic frame and the indicator arrows.

**Background (Kvantum's theme layout, read from its master source).** A Kvantum theme is a
directory `<name>/` holding `<name>.kvconfig` and `<name>.svg`. Kvantum merges the theme config over
its compiled-in `default.kvconfig` and draws an element the theme SVG lacks from its compiled-in
`default.svg` (`Style::setTheme`, `Style::setupThemeDeps`, `rendering.cpp`). Its per-user theme
search paths are `$XDG_CONFIG_HOME/Kvantum/<name>/`, `~/.themes/<name>/Kvantum/`,
`~/.local/share/themes/<name>/Kvantum/` and `/usr/share/Kvantum/<name>/`; the third is under the
default `$(XDG_DATA_HOME)`, so this repo installs a Kvantum theme with no new config-home plumbing.
The SVG's nine-slice convention is `<element>-<state>` for the centre plus
`<element>-<state>-top|-bottom|-left|-right|-topleft|-topright|-bottomleft|-bottomright`; the
`.kvconfig`'s `frame.top/bottom/left/right` tell Kvantum how to slice. The theme is opt-in until
part 3, so a machine without Kvantum is unaffected.

**Approach.**
1. New `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`:
   - `[%General]`: `author`, `comment`, `scroll_width=16` (the desktop theme's `widgets/scrollbar.svg`
     `hint-scrollbar-size` is 16), `scroll_arrows=true` (the reference scroll bars carry an arrow
     button at each end), `composite=true`.
   - `[GeneralColors]`, each value grounded as named: `window.color`/`button.color`/`mid.color`/
     `mid.light.color` `#DDDDDD` (`[Colors:Window]`/`[Colors:Button] BackgroundNormal`),
     `base.color` `#FFFFFF` (`[Colors:View] BackgroundNormal`), `alt.base.color` `#EEEEEE`
     (`[Colors:View] BackgroundAlternate`), `highlight.color`/`inactive.highlight.color` `#CCCCFF`
     (`[Colors:Selection] BackgroundNormal`), `text.color`/`window.text.color`/
     `button.text.color`/`tooltip.text.color`/`highlight.text.color` `#000000`,
     `disabled.text.color` `#888888` (`[Colors:Button] ForegroundInactive`),
     `tooltip.base.color` `#FFFFCC` (`[Colors:Tooltip] BackgroundNormal`), `link.color` `#0000EE`,
     `link.visited.color` `#551A8B`; the bevel roles `light.color=#FFFFFF`
     (`tests/platinum_palette.WHITE`) and `dark.color=#999999` (`platinum_palette.GREY`).
   - Core-control sections, `inherits=PanelButtonCommand` where `default.kvconfig` does:
     `[PanelButtonCommand]` (`frame.element=button`, `interior.element=button`,
     `frame.top/bottom/left/right=2`, `indicator.element=arrow`, `indicator.size=9`, black text in
     every state), `[PanelButtonTool]`, `[LineEdit]` (`frame.element=lineedit`,
     `interior.element=lineedit`), `[ComboBox]`, `[CheckBox]` (`interior.element=checkbox`),
     `[RadioButton]` (`interior.element=radio`), `[Focus]` (`frame.element=focus`, 1px),
     `[GenericFrame]` (`frame.element=common`), `[IndicatorArrow]`.
2. New `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: our own art for `button`,
   `lineedit`, `checkbox`, `radio`, `focus`, `common` and the `arrow-up`/`arrow-down`/`arrow-left`/
   `arrow-right` indicators, in the states above and the nine-slice convention. A raised face is a
   `#DDDDDD` interior with a 1px `#000000` outline and a 1px `#FFFFFF` top/left, `#999999`
   bottom/right bevel (the 2px raised face `widgets/button.svg` draws); the line edit is the white
   sunken field of `widgets/lineedit.svg`; the check and radio marks follow `widgets/checkmarks.svg`.
   The artwork is our own drawing, not a copy of a reference icon or of Kvantum's default SVG.
3. `Makefile`: `KVANTUM_ID := org.macos8.desktop`, `KVANTUM_PACKAGE := theme/kvantum/$(KVANTUM_ID)`,
   `KVANTUM_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(KVANTUM_ID)/Kvantum`; in `_install`
   stage the two files into it and rename them in (the files sit directly in a `Kvantum/`
   directory, so the package-directory swap of `install_package` does not fit), and in `_uninstall`
   remove them and their staging names. `install -d` the `themes/$(KVANTUM_ID)/Kvantum` path; leave
   the shared `themes/` parent alone.
4. `tests/test_kvantum.py` (new): parse the `.kvconfig` with `tests/kde_config.read`; assert every
   `[GeneralColors]` key equals the `MacOS8.colors` value or `platinum_palette` constant named in
   the mapping above; assert `[%General] scroll_width == "16"` and `scroll_arrows == "true"`; assert
   each core section's `frame.top/bottom/left/right` is `"2"` (`[Focus]` is `"1"`); parse the SVG
   with `xml.etree.ElementTree` and assert `attribute_values(tree, "fill")` is exactly
   `platinum_palette.PLATINUM_FILLS`, that every element id the `.kvconfig` names has its centre and
   eight slice ids present, and that `assert_unique_ids`, `assert_no_external_references`,
   `assert_no_script_elements` and `assert_no_style_elements` pass; install/uninstall round trip
   through `theme_install.install`/`uninstall`, asserting
   `<tmp>/themes/org.macos8.desktop/Kvantum/org.macos8.desktop.{kvconfig,svg}`.
5. `README.md`: name the Kvantum theme as an installed artifact, state it is not selected yet, give
   the opt-in (`kvantummanager --set org.macos8.desktop` once Kvantum is installed), the caveat that
   Kvantum finds it only when `$(XDG_DATA_HOME)` is the default `$HOME/.local/share`, and update the
   status line's artifact count.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` (new),
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` (new), `Makefile`,
`tests/test_kvantum.py` (new), `README.md`.

**Acceptance criteria.**
- The `.kvconfig` parses; each `[GeneralColors]` value equals the mapped `.colors` role or
  `platinum_palette` constant; `[%General] scroll_width` is `16` and `scroll_arrows` is `true`.
- Every core section's `frame` margins are 2px and `[Focus]`'s are 1px, pinned by name.
- The SVG's parsed `fill` set is exactly `PLATINUM_FILLS`; every referenced element id and its eight
  slices are present; the four safety assertions pass.
- `make install XDG_DATA_HOME=<tmp>` places `<tmp>/themes/org.macos8.desktop/Kvantum/` with both
  files and `make uninstall` removes them; the existing five artifacts' install/uninstall tests
  still pass.
- `contents/defaults` is byte-unchanged (the selection change is part 3), shown by `git diff`.
- README names the artifact and the opt-in, and `make check` is green.

### Mac OS 8.6 Kvantum widget style, part 2/3: the remaining Platinum widget art (planned 2026-10-18 by the plan role; requires part 1/3 landed)

**Goal.** Part 1 shipped the palette and the core-control art. This part adds our own Platinum art
and `.kvconfig` sections for the remaining Qt widget classes, so every control the theme draws is
ours rather than falling back to Kvantum's compiled-in default shapes: scroll bars, sliders,
progress bars, spin boxes, tabs, menus and the menu bar, group boxes, tooltips, item views,
splitters, headers and toolbars.

**Approach.**
- Extend `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` with sections modelled on
  `default.kvconfig`: `[Scrollbar]` (`indicator.size=16`), `[ScrollbarSlider]`
  (`frame.element=scrollbarslider`, 2px raised), `[ScrollbarGroove]` (the flat `#EEEEEE` trough of
  `widgets/scrollbar.svg`), `[Slider]`/`[SliderCursor]`, `[Progressbar]`/`[ProgressbarContents]`,
  `[IndicatorSpinBox]`, `[Tab]`/`[TabFrame]`/`[TabBarFrame]`, `[MenuItem]`/`[MenuBarItem]`/
  `[MenuBar]`/`[Menu]`, `[GroupBox]`, `[ToolTip]`, `[ItemView]`, `[Splitter]`, `[HeaderSection]`,
  `[Toolbar]`. Raised faces keep 2px margins, sunken fields 1px; the selection fill is `#CCCCFF`;
  the tooltip face is `#FFFFCC`.
- Extend `org.macos8.desktop.svg` with the matching elements in the same nine-slice convention and
  fill attributes.
- Extend `tests/test_kvantum.py`: the same fill-set, id, frame-margin and safety assertions over the
  new elements, with `platinum_palette.TROUGH` (`#EEEEEE`) and `TOOLTIP_FACE` (`#FFFFCC`) added to
  the expected fill set for the elements that draw them.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/test_kvantum.py`.

**Acceptance criteria.**
- The `.kvconfig` holds the new sections, each raised frame 2px and each sunken field 1px, with
  `[Scrollbar] indicator.size` 16, pinned by name.
- The SVG's parsed `fill` set is exactly `PLATINUM_FILLS | {TROUGH, TOOLTIP_FACE}`; every newly
  referenced element id and its eight slices are present; the safety assertions pass.
- The part 1 palette and core-control assertions are unchanged and still pass.
- `make check` is green.

### Mac OS 8.6 Kvantum widget style, part 3/3: select the Kvantum style from the global theme (planned 2026-10-18 by the plan role; requires part 2/3 landed)

**Goal.** With the theme complete, switch the global theme from Qt's built-in `Windows` style to
`kvantum`, select our theme name in the running session, and document the fallback when Kvantum is
not installed.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: change the `[kdeglobals][KDE]`
  `widgetStyle` value from `Windows` to `kvantum`.
- `tests/test_lookandfeel.py`: replace `test_widget_style_is_the_built_in_windows_style` with
  `test_widget_style_is_kvantum`, pinning `"kvantum"` and recording that the theme is our own
  Kvantum theme (a separately installed engine); the section/key list is unchanged.
- `tools/apply_theme.py`: add a best-effort `_select_kvantum_theme` step mirroring
  `_reconfigure_kwin` — run `kvantummanager --set org.macos8.desktop` when `shutil.which` finds
  `kvantummanager`, otherwise print a note and continue. `kvantummanager` is not added to
  `REQUIRED_TOOLS`, so `make apply` still succeeds without Kvantum. Derive the theme name from the
  same `org.macos8.desktop` id the Makefile installs so the two cannot drift.
- `tests/test_apply_theme.py`: `TestCommandOrder` expects the `kvantummanager --set
  org.macos8.desktop` call in the recorded order, and a new test asserts the step is skipped with a
  note when the stub is removed.
- `README.md`: the widget-style sentence now says the global theme selects our Kvantum theme; when
  Kvantum is not installed the widgets fall back to another style (choose one in System Settings →
  Application Style), and `make apply` runs `kvantummanager --set` when it is available.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/test_lookandfeel.py`, `tools/apply_theme.py`, `tests/test_apply_theme.py`, `README.md`.

**Acceptance criteria.**
- `contents/defaults` has `[kdeglobals][KDE] widgetStyle=kvantum`; the section order and key lists in
  `TestDefaults.test_the_expected_sections_and_keys_are_set` are unchanged, and the renamed test
  pins the value.
- With a `kvantummanager` stub on `PATH`, `make apply` records `kvantummanager --set
  org.macos8.desktop`; with the stub removed it prints a note and still exits 0.
- README documents the selection and the no-Kvantum fallback.
- `make check` is green.

### Own icon art: `PLACEHOLDER:` markers and a test that keeps `PLACEHOLDERS.md` complete (planned 2026-10-18 by the plan role)

**Goal.** The user answered 2026-10-18 that the theme's own artwork ships as placeholders for
now and that the placeholders must be tracked "so we don't forget to replace them all
eventually". Establish that tracking: every placeholder asset in the shipped theme carries a
`PLACEHOLDER:` comment naming what it stands in for, and one register, `PLACEHOLDERS.md`, lists
each one. The `org.macos8.desktop` icon theme already shipped the register and its five
icons, so this entry adds the marker convention and the test that keeps the register complete.

**Approach.**
- `PLACEHOLDERS.md` at the repository root (shipped with the icon theme): a short intro and a
  table with one row per placeholder asset. Add the `PLACEHOLDER:` marker to each registered
  asset.
- Marker convention: a placeholder asset carries the literal token `PLACEHOLDER:` in a comment
  in its own file format — `<!-- PLACEHOLDER: <what it stands in for> -->` for SVG, a `#`
  comment for text config.
- `tests/test_placeholders.py` (new): a `markers(root)` helper that walks `theme/` for text
  files (`.svg`, `.qml`, `.colors`, `.theme`, `.desktop`, `.json`, `index.theme`, `defaults`),
  skips `PLACEHOLDERS.md`, and returns `{relative path: marker text}`; a `register_entries(path)`
  helper that parses the table's backticked paths. Tests: every marker file is in the register;
  every register path exists on disk and carries a marker; the register's row set equals the
  marker set. Synthetic fixtures under `tmp_dir.make_tmp_dir` pin both helpers (a marker found, a
  register missing its path, a register path with no marker), so the mechanism is tested on a
  populated register.
- `README.md`: the shipped-artifact description already points at `PLACEHOLDERS.md`; state
  there that a placeholder asset carries the `PLACEHOLDER:` marker.

**Files touched.** `PLACEHOLDERS.md`, `tests/test_placeholders.py` (new), the placeholder SVGs,
`README.md`.

**Acceptance criteria.**
- Every register path exists on disk and carries a `PLACEHOLDER:` marker; the register's row
  set equals the marker set.
- With a fixture file carrying `PLACEHOLDER:` under a temp theme root, `markers` finds it; a
  register missing its path fails the cross-check, and a register path with no marker fails it.
- The repository's own `theme/` tree is cross-checked against `PLACEHOLDERS.md`, so the first
  placeholder added without a register row fails `make check`.
- README states the marker convention and points at `PLACEHOLDERS.md`.
- `make check` is green.

### Mac OS 8.6 Platinum icon theme: replace the placeholder art with final non-infringing art (planned 2026-10-18 by the feature role)

**Goal.** The `org.macos8.desktop` icon theme shipped our own placeholder art for
the desktop's hard-disk, folder, document and Trash icons, tracked in PLACEHOLDERS.md. Replace
each placeholder with final, non-infringing Mac OS 8.6-style art so the desktop icons read as
Platinum without reproducing Apple's artwork, keeping the package layout, its 32x32 grid and the
global theme's selection unchanged. The Apple-logo kicker icon stays out of scope.

**Approach.**
- Draw each of the five icons PLACEHOLDERS.md lists (`drive-harddisk`, `text-x-generic`,
  `folder`, `inode-directory`, `user-trash`) as our own 32x32 art on the pixel grid, in the
  Platinum grey/black palette; keep the file names, contexts and `index.theme` the icon theme
  shipped, so only the SVG contents change.
- Record how the art was derived in this entry when it lands (drawn here, not traced from a
  reference icon).
- Remove each replaced icon's row from PLACEHOLDERS.md, and delete the file when the last row
  goes; update `tests/test_icon_theme.py` so the placeholder registry is checked to match the
  shipped set exactly (empty once the last placeholder is replaced).

**Files touched.** `theme/icons/org.macos8.desktop/32x32/` (the five SVGs), `PLACEHOLDERS.md`,
`tests/test_icon_theme.py`.

**Acceptance criteria.**
- Each shipped icon is final art, and PLACEHOLDERS.md lists exactly the icons that are still
  placeholders (none when the plan is done).
- `tests/test_icon_theme.py` passes with an empty or removed placeholder registry.
- The global theme still selects `org.macos8.desktop`, and `make check` is green.

## Done

### Mac OS 8.6 Platinum desktop icon theme: a minimal `org.macos8.desktop` icon package for the icons the desktop shows (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** The desktop's icons wore the default Breeze icons. Ship the first
`org.macos8.desktop` icon-theme package with our own placeholder art for the hard-disk, folder,
document and Trash icons the desktop shows, select it from the global theme's `contents/defaults`,
and track each placeholder in PLACEHOLDERS.md so the final non-infringing art can replace them
(the 2026-10-18 answer in QUESTIONS.md asks for our own art, not a reproduction of Apple's
Platinum icons). Scope: the icons a default desktop shows, at 32x32 only; everything else
inherits Breeze. The Apple-logo kicker icon is out of scope.

**Approach.**
- New package `theme/icons/org.macos8.desktop/`: `index.theme` (name `org.macos8.desktop`,
  `Inherits=breeze`, a `Directories` entry for each shipped context) and one 32x32 SVG per icon
  under `32x32/<context>/`: `drive-harddisk` (devices), `text-x-generic` (mimetypes), and
  `folder`, `inode-directory` and `user-trash` (places). SVGs rather than PNGs so the placeholder
  art needs no alpha channel and no Git LFS object; each draws on the 32x32 grid so the final art
  can keep the same shape. PLACEHOLDERS.md lists every one.
- Global theme `contents/defaults`: add `[kdeglobals][Icons] Theme=org.macos8.desktop`; the LNF
  defaults mechanism applies this key. `tests/test_lookandfeel.py::TestDefaults` gains the new
  section and a test that the selection names the shipped package.
- Makefile: `ICON_THEME_ID`/`ICON_THEME_PACKAGE`/`ICON_THEME_INSTALL_DIR` (install dir
  `$(DESTDIR)$(XDG_DATA_HOME)/icons`) installed and uninstalled in `_install`/`_uninstall`
  beside the other five artifacts.
- `tests/test_icon_theme.py` (new): `index.theme` names the theme and inherits Breeze; every
  shipped icon is a 32x32 SVG in a declared `Size=32` directory; PLACEHOLDERS.md names each one;
  `make install` copies the package under `<tmp>/icons/org.macos8.desktop/` and `make uninstall`
  removes it, checked through `InstallLifecycleCases`.
- `README.md`: list the icon theme as the sixth artifact and say the global theme selects it.

**Files touched.** `theme/icons/org.macos8.desktop/` (new), `PLACEHOLDERS.md` (new),
`contents/defaults`, `tests/test_lookandfeel.py`, `tests/test_icon_theme.py` (new),
`tests/theme_install.py`, `tests/install_lifecycle_cases.py`, `tests/test_theme_install.py`,
`Makefile`, `README.md`.

**Out of scope.** The Apple-logo kicker icon; final icon art (the replacement entry under
`## Planned`); sizes other than 32x32 (the menu bar and app menus want 16px); the full Platinum
icon set (Breeze fills the rest).

**Acceptance criteria.**
- `index.theme` declares `Name=org.macos8.desktop` and `Inherits=breeze` (pinned), and every
  shipped icon sits in a declared `Size=32` directory.
- `contents/defaults` holds `[kdeglobals][Icons] Theme=org.macos8.desktop`, pinned by
  `TestDefaults`.
- `make install XDG_DATA_HOME=<tmp>` installs `<tmp>/icons/org.macos8.desktop/` and `make
  uninstall` removes it; the other artifacts' install/uninstall tests still pass.
- Every shipped icon is a 32x32 SVG and every one is named in PLACEHOLDERS.md.
- README documents the artifact and the selection.
- `make check` is green.

### Local theme apply, part 2/2: `make install-local-hook` writes an uncommitted `post-commit` hook that runs `make apply` (planned 2026-10-18 by the director role; done 2026-10-18)

**Goal.** After every commit in this clone, the newest theme is automatically installed and
applied, through a `post-commit` hook that lives only in this clone's git directory and is never
committed or pushed, so other clones and contributors are unaffected.

**Approach.**
- Add `tools/local_hook.py`, stdlib-only, with `install` and `uninstall` subcommands (argparse via
  `tools/cli.py`'s `EscapingArgumentParser`):
  - Resolve the hooks directory with `git rev-parse --git-path hooks` (in this clone the common
    `.git/hooks`, shared by the `.tumwater/worktrees/*` linked worktrees) and the repository top
    level with `git rev-parse --show-toplevel`.
  - Write an executable `post-commit` shell script carrying the marker line
    `# installed by kde-macos8.6-theme: make install-local-hook`. Its body runs
    `cd "$(git rev-parse --show-toplevel)" && make apply`, sends output to stderr, and swallows a
    non-zero status so a failed apply never blocks the commit.
  - `install` refuses, with a diagnostic naming the path, to overwrite an existing `post-commit`
    that lacks the marker; a re-run over its own hook is idempotent (same bytes).
  - `uninstall` removes the file only when the marker is present and refuses on a foreign hook.
- Add `install-local-hook` and `uninstall-local-hook` targets to `Makefile` (`.PHONY` and `help`),
  each running `$(PYTHON) tools/local_hook.py <subcommand>` under the Python guards.
- Document the local-only workflow in README.md: the hook is uncommitted so other clones are
  unaffected; every commit in this clone, including the feature worktrees under
  `.tumwater/worktrees/`, re-applies the theme from the committing worktree; `make apply` is the
  manual equivalent; a fast-forward merge creates no commit and so does not trigger the hook.

**Files touched.** `Makefile`, `tools/local_hook.py` (new), `tests/test_local_hook.py` (new),
`README.md`.

**Acceptance criteria.**
- In a throwaway `git init` repo (under `tests/tmp_dir.py`), `tools/local_hook.py install` creates
  an executable `<hooks>/post-commit` whose bytes carry the marker and whose body names `make
  apply`; a second install succeeds and leaves the bytes unchanged.
- An existing non-marker `post-commit` makes both `install` and `uninstall` exit non-zero naming
  the path, and leaves its bytes untouched.
- `uninstall` removes a hook this tool installed and leaves a foreign one.
- `make -n install-local-hook` shows the Python invocation, and `help` lists both targets.
- `make check` passes.

### Local theme apply, part 1/2: `make apply` installs and re-applies the theme to the running Plasma session (planned 2026-10-18 by the director role; done 2026-10-18)

**Goal.** A single command, `make apply`, makes the just-built theme the running Plasma session's
current theme without a logout: it installs the five artifacts exactly as `make install` does,
then re-selects the color scheme, desktop theme and global theme so the shell, KWin and KDE
applications reread the new files.

**Approach.**
- Add `tools/apply_theme.py`, a Python 3.10+ stdlib-only script with the same `if __package__:`
  import guard as `tools/render_surface.py`. It runs these commands in order and exits 0 only when
  every required one succeeds:
  1. `lookandfeeltool -a org.macos8.desktop` — re-applies the global theme. Do **not** pass
     `--resetLayout` (README's Installing section: the desktop layout is replaced only when that
     flag is given, so the user's panels survive).
  2. `plasma-apply-colorscheme MacOS8`
  3. `plasma-apply-desktoptheme org.macos8.desktop`
  4. `qdbus6 org.kde.KWin /KWin reconfigure`, falling back to `qdbus`; when neither exists, print a
     note and continue (the decoration then reloads on the next KWin restart).
  Steps 2-3 run after step 1 because `lookandfeeltool` applies the theme's defaults wholesale; the
  explicit component selections then hold whatever the user had chosen. Steps 1-3 are required: a
  missing tool exits 2 naming it (`shutil.which`), a non-zero command exits 1 with the output
  tail, mirroring `tools/render_surface.py`'s `_failure` shape and the `REQUIRED_TOOLS` guard.
- When `DBUS_SESSION_BUS_ADDRESS` is unset, `$XDG_RUNTIME_DIR` is an absolute path, and
  `$XDG_RUNTIME_DIR/bus` exists, default the variable to `unix:path=$XDG_RUNTIME_DIR/bus`, so the
  command works from a non-login shell (the hook in part 2). Otherwise leave it alone.
- Add an `apply` target to `Makefile` whose recipe first refuses a non-empty `DESTDIR` with a
  diagnostic naming it (applying a staged tree to the running session is wrong), then runs
  `$(MAKE) --no-print-directory install`, then `$(PYTHON) tools/apply_theme.py` under
  `require_python`/`require_python_version`. Add `apply` to the `.PHONY` line and a `help` line.
- Document `make apply` in README.md's Installing section, including that the startup splash
  changes only appear on the next login.

**Files touched.** `Makefile`, `tools/apply_theme.py` (new), `tests/test_apply_theme.py` (new),
`README.md`.

**Acceptance criteria.**
- `tools/apply_theme.py` invokes the four commands in the order above, never passes `--resetLayout`,
  and defaults `DBUS_SESSION_BUS_ADDRESS` only under the three conditions above. Test with fake
  executables on `PATH` built like `tests/process_runner.py`'s fakes, recording each argv.
- A missing required tool exits 2 naming it; a failing command exits 1 and prints its output tail;
  a missing `qdbus6`/`qdbus` only prints a note and still exits 0.
- `make apply DESTDIR=<dir>` exits non-zero with a diagnostic naming `DESTDIR`, and does not run
  the apply script.
- `make -n apply` shows `install` running before the script, and `help` lists `apply`.
- `make check` passes.

### Mac OS 8.6 menu-bar top highlight: a `north-` panel-background state whose centre carries the white row 0 (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** The reference menu bar's row 0 is a 1px `#FFFFFF` highlight across the whole bar
(`desktop_betawiki.png`: (10,0), (300,0), (301,0) are `#FFFFFF`; rows 1..17 `#DDDDDD`, row 18
`#999999`, row 19 `#000000`, as the comment at the top of
`contents/layouts/org.kde.plasma.desktop-layout.js` records). `widgets/panel-background.svg` paints
that highlight only in its `top`, `topleft` and `topright` slices. Plasma never draws those slices
on our menu bar. `PanelView` passes `enabledBorders` to the panel's FrameSvg
(`/usr/share/plasma/shells/org.kde.plasma.desktop/contents/views/Panel.qml`, `enabledBorders:
panel.enabledBorders`), and that drops each border lying on a screen edge. A top panel always
loses its top border, and the layout's full-width, non-floating 20px bar also loses its left and
right borders. So the installed bar starts with the `#DDDDDD` centre at row 0 and has no
highlight at all. Draw the highlight from the centre instead, in a state only top panels use.

**Approach.** `Panel.qml`'s `adjustPrefix()` sets the panel FrameSvg prefix to `["north", ""]`
for a `TopEdge` containment, and KSvg uses `north` whenever `north-center` exists. Add a complete
`north-` nine-slice state to `theme/desktop-themes/org.macos8.desktop/widgets/panel-background.svg`
and leave the unprefixed state (bottom, left and right panels) unchanged:
- Grow the root canvas from 12x12 to 12x22 (`width`, `height` and `viewBox`). The `north-`
  groups overlap the unprefixed ones at the origin, the same way `button.svg`'s
  `normal`/`pressed`/`focus` states share one canvas. KSvg renders each element by id, so the
  overlap is harmless.
- `north-` margin hints: a 2px border around an 8x18 centre. `north-hint-top-margin` (2,0,2,2),
  `north-hint-bottom-margin` (2,20,2,2), `north-hint-left-margin` (0,2,2,2),
  `north-hint-right-margin` (10,2,2,2), plus zero-thickness insets mirroring the unprefixed ones:
  `north-hint-top-inset` (2,0,8,0), `north-hint-bottom-inset` (2,22,8,0),
  `north-hint-left-inset` (0,2,0,18), `north-hint-right-inset` (12,2,0,18). Do not add a
  `north-hint-tile-center`. KSvg reads `hint-tile-center` without a prefix (see the docstring of
  `assert_slice_ids_present` in `tests/svg_assertions/tree.py`), so the existing hint makes the
  north centre tile at its 8x18 size. With the top border disabled, the 20px bar's centre area
  is exactly 18 rows: one tile high, 1:1.
- `north-center` at `translate(2,2)`, 8x18: row 0 `#FFFFFF`, rows 1..17 `#DDDDDD`. This is the
  one slice that draws on the shipped bar, together with `north-bottom`.
- `north-bottom` at `translate(2,20)` and `north-bottomleft`/`north-bottomright` at (0,20) and
  (10,20): the same pixels as the unprefixed `bottom`/`bottomleft`/`bottomright`.
- `north-left` at (0,2), 2x18: row 0 `#FFFFFF #FFFFFF`, rows 1..17 `#FFFFFF #DDDDDD`.
  `north-right` at (10,2), 2x18: row 0 `#FFFFFF #999999`, rows 1..17 `#DDDDDD #999999`. Row 0
  continues the centre's highlight. These show only on a top panel the user shortens so that it
  no longer touches a side edge.
- `north-top`/`north-topleft`/`north-topright` at (2,0), (0,0) and (10,0): copies of the
  unprefixed slices. Plasma never draws them on a top-edge panel, but every state needs all nine
  `SLICE_IDS`.
- Rewrite the header comment so it says which state a top panel uses and why the highlight
  lives in `north-center`.

**Out of scope (unreachable through panel-background).** The reference's rounded black screen
corners: (0,0)..(4,0) and (1019,0)..(1023,0) are `#000000`, antialiased through `#555555`,
`#AAAAAA` and `#888888`/`#BBBBBB`. The 1px `#FFFFFF` left column at x=0 and the `#999999` right
column at x=1023 are also out of scope. Plasma draws no left or right border on a full-width
panel, and a tiled centre cannot place a single column. Record both in the header comment as
known limits.

**Files touched.**
- `theme/desktop-themes/org.macos8.desktop/widgets/panel-background.svg`: the `north-` state
  and the 12x22 canvas.
- `tests/test_desktoptheme_panel.py`:
  - set `PREFIXES = ("", "north")` on `TestPanelBackground`, so the inherited `NineSliceCase`
    checks (ids present, tiles placed by margins, tiles within their margins) cover the new state;
  - extend the `rect_geometry` expectation in `test_panel_background_hint_geometry` with the
    twelve `north-hint-*` rects;
  - add a `NORTH_EDGE_PIXELS` table and a test that pins every pixel of the nine `north-`
    slices with `render_slices`/`assert_slice_pixels`/`pixel_map`;
  - add a `ReferenceScreenshotMixin` test (`tests/reference_image.py`; it skips when the LFS
    image is missing) on `desktop_betawiki.png`. Using the mixin's `pixel(x, y)`, it checks that each
    pixel of column 10 rows 0..17 equals the matching `north-center` row, and that rows 18..19
    equal `north-bottom`'s two rows.
- `README.md`: in the `widgets/panel-background.svg` (the menu bar) parenthetical, say that the
  top menu bar draws its white top highlight from a top-panel (`north-`) state.

**Acceptance criteria.**
- `north-center` renders 8x18 with row 0 `#FFFFFF` and rows 1..17 `#DDDDDD`, and a test pins
  each of those pixels.
- The unprefixed slices' pixels and hint geometry are unchanged: `PANEL_EDGE_PIXELS` and the
  existing hint-geometry entries pass with no edits.
- The `NineSliceCase` structural checks pass for both `""` and `"north"`.
- The reference test re-derives the north centre and bottom rows from `desktop_betawiki.png`
  column 10.
- `make check` is green.

**Implementation note (2026-10-18, feature).** Growing the canvas to 12x22 made the unprefixed
`hint-bottom-margin` (ends at y=12) fail `assert_root_canvas`'s far-edge tie, so that helper gained
an `origin_states` argument (`tests/svg_assertions/checks.py`, covered in
`tests/test_svg_assertions_checks.py`); `tests/test_desktoptheme.py` passes `("",)` for the panel
SVG and pins its canvas as 12x22. `north-topright` copies the unprefixed `topright` pixels, whose
shadow overwrites the highlight at (1,0).

### Mac OS 8.6 Qt widget style: select Qt's built-in square-bevel `Windows` style from the global theme (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** Applying the global theme today changes only the Plasma shell, the window decoration and
the colours. Every KDE application keeps drawing its own buttons, scroll bars, tabs and menus with
Breeze: rounded corners, flat fills and a blue focus glow. The Mac OS 8.6 references show none of
these. This plan answers the "Qt widget style" item in the steward's scope-drift note at the top
of `## Planned`, without adding a dependency. It sets the global theme's
`[kdeglobals][KDE] widgetStyle` to Qt's built-in `Windows` style (`QWindowsStyle`, compiled into
`libQt6Widgets`, so nothing new is installed). It is independent of the menu-title-spacing plan.

**Why `Windows`, and its provenance.** The reference set cannot pick a QStyle by pixel, so this
records the qualitative match, per the principle on KDE-required values the references do not
show. `systemprofiler_betawiki.png` (and the Platinum frame this repo already ships in
`widgets/frame.svg`) show square, unrounded controls. Their 3D bevel is light at the top-left and
dark at the bottom-right, and the scroll bar has an arrow button at each end of its trough.
`QWindowsStyle` draws exactly that geometry (square bevelled buttons, an arrow at each end of the
scroll bar), with colours from the `QPalette` that KDE builds from `MacOS8.colors`. `Fusion` (the
other built-in style) rounds its corners and adds gradients, and Breeze rounds its corners and
draws a focus glow. A pixel-matched Platinum Qt style would need a style engine such as Kvantum,
which is a new dependency. It stays out of scope here, and asking the user whether to take on that
dependency is a separate QUESTIONS.md entry for a later run. The key and value form follows
Breeze's own `/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/contents/defaults`
(`[kdeglobals][KDE]` / `widgetStyle=Breeze`). Plasma's platform theme hands the value to
`QStyleFactory::create`, whose keys on this machine include `Windows` and `Fusion`.

**Approach.**
1. `theme/look-and-feel/org.macos8.desktop/contents/defaults`: add a first group
   `[kdeglobals][KDE]` with the single key `widgetStyle=Windows`, placed before
   `[kdeglobals][General]` as in Breeze's file.
2. `tests/test_lookandfeel.py`: add the constant `STYLE_SECTION = "kdeglobals][KDE"` beside
   `DEFAULTS_SECTION`. In `TestDefaults.test_the_expected_sections_and_keys_are_set`, expect
   `[STYLE_SECTION, DEFAULTS_SECTION, PLASMA_SECTION, KWIN_SECTION, WALLPAPER_SECTION]` and
   `options(STYLE_SECTION) == ["widgetStyle"]`. Add
   `TestDefaults.test_widget_style_is_the_built_in_windows_style`, asserting the value is exactly
   `"Windows"`. Its docstring records the provenance above (square bevels and an arrow at each end
   of the scroll bar in `systemprofiler_betawiki.png`; built into QtWidgets, so no new dependency;
   Kvantum deferred).
3. `README.md` (outside the tumwater markers): in the "Installing" paragraph that lists what
   applying the global theme selects, add one sentence: the global theme also selects Qt's
   built-in `Windows` widget style (`[kdeglobals][KDE] widgetStyle`), so KDE applications draw
   square bevelled Platinum-like controls instead of Breeze's rounded ones. Choose another style in
   System Settings → Application Style.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/test_lookandfeel.py`, `README.md`.

**Acceptance criteria.**
- `contents/defaults` has a `[kdeglobals][KDE]` group holding only `widgetStyle=Windows`. The
  existing groups and keys are unchanged (shown by `git diff` on the file).
- `test_the_expected_sections_and_keys_are_set` pins the new section order and key list, and
  `test_widget_style_is_the_built_in_windows_style` pins the value. Each fails when the line is
  removed or the value changed.
- The existing `TestPackageValid` (kpackagetool validation) and install tests still pass. `make
  check` is green.
- README.md describes the selected style and how to change it.

**Out of scope.** A pixel-matched Platinum Qt style (Kvantum or a custom QStyle: a new dependency,
so the user's call). Fonts (Charcoal does not ship, and the LNF `defaults` file does not set
fonts). The icon theme, cursor theme and sounds from the scope-drift note.

### Mac OS 8.6 menu-title spacing: 7px horizontal padding in `widgets/menubaritem.svg` (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** Space the application-menu titles in the menu bar as Mac OS 8.6 does. The
`org.kde.plasma.appmenu` title padding comes from `widgets/menubaritem.svg`'s margin hints. In
`/usr/share/plasma/plasmoids/org.kde.plasma.appmenu/contents/ui/MenuDelegate.qml`,
`leftPadding`/`rightPadding`/`topPadding`/`bottomPadding` are the `rest` `FrameSvgItem`'s
`margins`, and `main.qml` sets `columnSpacing: 0`. Today every margin is 3px, so two titles'
text sits 6px apart plus the font's side bearings. The reference has about twice that. The done
menu-bar layout plan listed "the Mac OS 8.6 menu-title metrics for `appmenu`" as a later plan.
This is that plan. It is independent of the desktop-icon-labels plan.

**Grounding (`macos8.6-screenshots/desktop_betawiki.png`, 1024x768, lossless).** Scan columns
x=32..259 over menu-bar rows y=1..17 (row 0 is the white highlight, row 18 the bevel). A column
is ink when any of its pixels is exactly `#000000`. Group ink columns into titles, starting a
new title at a gap of 8 or more blank columns. Inside a title the largest gap is 2. That gives
File x=44..63, Edit 79..101, View 115..145, Special 160..203, Help 219..244. The blank gaps
between neighbours are 15, 13, 14 and 15 columns (sum 57). Mac OS 8.6 highlights an open title
in a rectangle that meets its neighbour's, so each side gets half the gap:
`57 // (2 * 4) = 7`. The padding is therefore 7px left and 7px right. Top and bottom stay 3px.
`main.qml` sets `Layout.minimumHeight: implicitHeight`, so a larger vertical margin would push
the applet past the 20px panel, and the panel's height is already pinned against the reference
by `TestPanelHeightMatchesReference`.

**Approach.**
1. `theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg`: make the canvas 20x12
   (`width="20" height="12" viewBox="0 0 20 12"`) with a 7px left and right border, a 3px top
   and bottom border, and the same 6x6 centre tile:
   - `hint-tile-center` at (7,3,6,6).
   - For each of `normal`, `hover` and `pressed`: `-hint-top-margin` (7,0,6,3),
     `-hint-bottom-margin` (7,9,6,3), `-hint-left-margin` (0,3,7,6) and
     `-hint-right-margin` (13,3,7,6).
   - Each state's nine slice groups move to the new tile origins: topleft (0,0) 7x3, top (7,0)
     6x3, topright (13,0) 7x3, left (0,3) 7x6, center (7,3) 6x6, right (13,3) 7x6, bottomleft
     (0,9) 7x3, bottom (7,9) 6x3, bottomright (13,9) 7x3. Each rect fills its tile. `pressed` rects
     stay `fill="#CCCCFF"`. `normal`/`hover` rects stay `style="fill:#FFFFFF"
     fill-opacity="0.01"` with no `fill` attribute.
   - Rewrite the header comment's contract sentence ("3px border around a 6px centre tile on a
     tight 12x12 canvas") to give the new border, and add the grounding above: the reference,
     the four title gaps, and the `// 8` rule.
2. `tests/test_desktoptheme_menubaritem.py`:
   - Add module constants `LEFT = RIGHT = 7`, `TOP = BOTTOM = 3`, `TILE = 6`, and
     `SIZES = nine_slice_tile_sizes(20, 12, LEFT, RIGHT, TOP, BOTTOM)`. `nine_slice_tile_sizes`
     is in `svg_assertions` and is already used by `tests/test_desktoptheme_plasmoidheading.py`.
   - `test_menubaritem_hint_geometry`: `assert_hint_geometry` and `nine_slice_margins` assume
     one square border, so compare `rect_geometry(self.tree)` (from `svg_assertions`) with an
     explicit dict: `hint-tile-center` plus the twelve margin hints listed in step 1, as string
     tuples like the helpers produce. Update its comment.
   - `test_menubaritem_slices_fill_their_tiles`: `assert_slices_fill_their_tiles` is square-only,
     so loop over `SIZES` for each `(prefix, colour)` pair and call `assert_slice_pixels(case,
     slices, f"{prefix}-{name}", pixel_map((colour,) * (w * h), w, h))`, as the shared helper's
     body does. Do not change the shared helper.
   - Add `TestMenuTitleSpacingMatchesReference(ReferenceScreenshotMixin, unittest.TestCase)`
     (from `tests/reference_image.py`) with `REFERENCE` = the `desktop_betawiki.png` path (built
     from `theme_install.ROOT` as `tests/test_lookandfeel_layout.py` does). Add a module helper
     `title_gaps(image)` that applies the scan rule from Grounding with `png.pixel_at` and
     returns the blank-gap list. Tests:
     - `test_reference_title_gaps`: `title_gaps(self.image) == [15, 13, 14, 15]`.
     - `test_horizontal_margin_is_half_the_mean_gap`: the `width` of `normal-hint-left-margin`
       and `normal-hint-right-margin` (read through `rect_geometry`) both equal
       `str(sum(gaps) // (2 * len(gaps)))`.
3. `tests/test_desktoptheme.py`: change the `SVG_CANVASES` entry to
   `("menubaritem.svg", MENUBARITEM_SVG, 20, 12)`.
4. README.md: in the `widgets/menubaritem.svg` inventory sentence, add that its 7px side
   padding spaces the application-menu titles as the reference menu bar does.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg`,
`tests/test_desktoptheme_menubaritem.py`, `tests/test_desktoptheme.py`, `README.md`.

**Acceptance criteria.**
- `make check` passes. `TestMenuTitleSpacingMatchesReference` runs (does not skip) when the LFS
  image is materialized. The inherited `NineSliceCase` tests (`test_tiles_placed_by_margins`,
  `test_tiles_stay_within_their_margins`, `test_slice_ids_present`) pass against the new
  geometry. If one assumes a square border, extend that helper with a test in
  `tests/test_svg_assertions_*.py` rather than skipping it.
- Each of these makes a named test fail: a left or right margin hint other than 7 wide, a top
  or bottom hint other than 3 high, a slice rect one pixel short of its tile, or a canvas other
  than 20x12.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` still installs a byte-identical
  `widgets/menubaritem.svg` (the existing `TestInstall`).
- Manual smoke test (needs a Plasma session): with a KDE app focused, the appmenu titles sit
  about 14px apart plus side bearings. A title's open-menu `#CCCCFF` fill extends 7px past its
  text on each side.

**Known deviations (recorded, not fixed here).** `org.kde.plasma.windowlist`'s `MenuButton.qml`
also reads `leftPadding`/`rightPadding` from this file, so the right-hand application menu gains
the same 7px padding. The reference's right-hand menu is not measured here, because its grip and
icon need a custom plasmoid (see the desktop-layout plan's out-of-scope list). The glyph gaps
also depend on the KDE font's side bearings, since Charcoal does not ship, so the rendered gap
will be within a pixel or two of the reference, not exactly equal.

### Mac OS 8.6 desktop icon labels: one line of text under each icon (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** Mac OS 8.6 shows each desktop icon's name on one line under the icon. A long name is
cut off, not wrapped. Plasma's desktop Folder View wraps names onto up to 2 lines
(`textLines` default 2), and every grid cell is sized for 2 lines. The global theme's desktop
layout should set the desktop containment to one label line.

**Reference (sampled 2026-10-18, lossless `macos8.6-screenshots/desktop_betawiki.png`,
1024x768).** Use the same tile comparison as `TestDesktopIconsMatchReference.differs_from_wallpaper`
(a pixel differs from `tools/make_wallpaper.py` `TILE_ORIGIN`/`TILE_SIZE` tile pixel). Over
x >= 880, the fully drawn icon blocks span these rows:
- 157..200 ("Browse the Internet", alias).
- 220..264 ("Get QuickTime Pro").
- 284..328 ("Mail", alias).
- 348..392 ("Register with Apple", alias).
- 668..712 ("Trash").

Each block is 45 rows: the 32-row icon body plus one 13-row label line. Where the label is wider
than the body (x outside 960..991), it fills rows 188..200, 252..264 and 380..392, 13 rows each. So
no label has a second line. "Register with Apple", the longest, runs to x=1023, the screen's
last column, still on one line. The first block (rows 47..72, "Macintosh HD") is not fully
drawn in this capture, so it is not a sample.

**Plasma facts (checked 2026-10-18).**
`/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/config/main.xml` group
`General`, entry `textLines` (Int, default 2) is "the (maximum) number of lines of text to use
below Folder View icons". `ui/FolderItemDelegate.qml` uses it as the icon-view label's
`maximumLineCount`, with `wrapMode: Text.NoWrap` when it is 1, so a long name elides on one line.
`ui/FolderView.qml` sizes each cell `iconSize + gridUnit * textLines + smallSpacing * 3` high.
With the 32px icons the layout already sets, one line also brings the row pitch nearer the
reference's 63..64 rows (157 → 220 → 284 → 348) than two lines would.

**Approach.** In `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
add `desktopsArray[j].writeConfig("textLines", 1);` after the existing `iconSize` call, inside
the same `["General"]` group. Add a comment line above it citing the 45-row blocks (32-row body plus
one 13-row label line). Do not touch `labelWidth`, `textColor` or any other key.

**Files touched.**
- `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`.
- `tests/test_lookandfeel_layout.py`:
  - Add `"textLines": 1` to the `DESKTOP_ICONS` constant. The existing
    `test_desktop_icon_arrangement` then pins it through `desktop_config` with no new test
    method.
  - In `TestDesktopIconsMatchReference`, add a class constant
    `LABELLED_ICON_ROWS = [(157, 200), (220, 264), (284, 328), (348, 392), (668, 712)]` and
    `ICON_BODY = 32`.
  - Add `test_each_label_is_one_line`. For each `(top, bottom)`, collect the rows in
    `range(top - 5, bottom + 6)` holding a differing pixel at x >= `RIGHT_COLUMN_LEFT`. Assert
    they run exactly from `top` to `bottom`, so the block is bounded. Then assert
    `bottom - top + 1 - ICON_BODY == 13`: one label line, with no room for a second.
    The ±5-row margins stay clear of the neighbouring blocks: every gap between blocks is at least 19 rows.
- `README.md`: in the sentence ending "lines its icons up in one 32px column at the right edge,
  as Mac OS 8.6 does", add that each icon's name sits on one line under it.

**Acceptance criteria.**
- `make check` passes with the new test.
- Removing the `textLines` call, or changing it to 2, makes `test_desktop_icon_arrangement`
  fail.
- `test_desktop_writes_the_general_group`, `test_widgets_in_menu_bar_order` and the clock
  tests still pass unchanged.
- Manual smoke test (needs a Plasma session): after `lookandfeeltool -a org.macos8.desktop
  --resetLayout`, a file in `~/Desktop` with a long name shows it on one elided line.

**Out of scope.** The Mac label box (black text on a white rectangle). `FolderItemDelegate.qml`
hard-codes white text with a shadow when Folder View is the containment, and its `textColor`
setting is not used there, so the stock plasmoid cannot draw that box. Also out of scope: Mac OS
cutting a name off at the screen edge where Plasma elides it with "…", which no Folder View
setting changes.

**Implementation note (2026-10-18, feature).** The first block measures 44 rows (157..200), not 45,
so "block height minus 32 is 13" does not hold for every block. `test_each_label_is_one_line`
instead asserts each block is bounded as listed and that, where the label is wider than the body
(x outside `ICON_BODY` 960..991), the label rows are exactly the last `LABEL_LINE` = 13 rows of the
block. The `ICON_BODY` constant is the column range, not a row count.

### Mac OS 8.6 desktop icon arrangement: one right-aligned column of 32px icons (planned 2026-10-18 by the plan role; done 2026-10-18)

**Goal.** Mac OS 8.6 puts its desktop icons in one column at the right edge of the screen, from
the top down, at 32x32. Plasma's desktop Folder View defaults to rows from the top-left at 64px.
The global theme's desktop layout should set the desktop containment to match.

**Reference (sampled 2026-10-18, lossless `macos8.6-screenshots/desktop_betawiki.png`,
1024x768).** Compare each pixel below the menu bar with the wallpaper tile
(`tools/make_wallpaper.py` `TILE_ORIGIN` = (0, 128), period 128). That gives these non-pattern
blocks at x >= 880: rows 47..72 (x 941..1010), 157..200 (x 925..1023), 220..264 (x 929..1022),
284..328 (x 960..991), 348..392 (x 926..1023), and the Trash at rows 668..712 (x 960..991). The
icon bodies span exactly x = 960..991, which is 32 columns. Across x = 0..879, rows 20..699 (every
second pixel), nothing differs from the tile, so the icons sit only in the right-hand column.
The Control Strip below row 740 is not an icon.

**Plasma facts (checked 2026-10-18).**
`/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/config/main.xml` group
`General`:
- `arrangement`: 0 = Rows, 1 = Columns.
- `alignment`: 0 = Left, 1 = Right.
- `iconSize`: 0 = 22px, 1 = 32px (`Kirigami.Units.iconSizes.medium`, see `ui/code/FolderTools.js`
  `iconSizes`), default 3 = 64px.

`ui/FolderViewLayer.qml` maps them to `flow: arrangement === 0 ? FlowLeftToRight :
FlowTopToBottom` and `layoutDirection: alignment === 0 ? LeftToRight : RightToLeft`. So
`arrangement=1`, `alignment=1` fills a column top-down, starting at the right edge. A containment
in the layout script takes the same `currentConfigGroup` / `writeConfig` calls the clock widget
uses.

**Approach.** In `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
add these calls inside the existing `desktopsArray` loop, after the `wallpaperPlugin` line:
`desktopsArray[j].currentConfigGroup = ["General"];` then
`desktopsArray[j].writeConfig("arrangement", 1);`, `writeConfig("alignment", 1);` and
`writeConfig("iconSize", 1);`. Put one comment above them citing the reference
rows and columns above. Do not write `positions` or any other key. A containment that is not
Folder View (`org.kde.plasma.desktop`) ignores keys it does not declare, so no plugin check is
needed.

**Files touched.**
- `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`.
- `tests/test_lookandfeel_layout.py`:
  - A module constant `DESKTOP_ICONS = {"arrangement": 1, "alignment": 1, "iconSize": 1}`.
  - A helper `desktop_config(text)` that returns the `desktopsArray[j].writeConfig("k", v);`
    calls as `{key: int}`, modelled on `clock_config`.
  - In `TestLayout`: `test_desktop_writes_the_general_group`. The
    `desktopsArray[j].currentConfigGroup = ["General"];` line comes before the first
    `desktopsArray[j].writeConfig(`, and both lie after the `for (var j` loop header.
  - In `TestLayout`: `test_desktop_icon_arrangement` checks `desktop_config(text) == DESKTOP_ICONS`.
  - A new `TestDesktopIconsMatchReference(ReferenceScreenshotMixin, unittest.TestCase)`.
    `test_icons_sit_in_one_right_column` re-derives the reference with the tile comparison
    above. It asserts no differing pixel at x < 880 for rows 20..699, and at least one differing
    pixel at x >= 880 in rows 40..80. `test_icon_body_is_32_columns_wide` asserts the differing
    columns in rows 284..328 run from 960 to 991, i.e. 32 == the `iconSize` 1 pixel size. Use
    the `REFERENCE` constant. Read the tile origin from `tools.make_wallpaper.TILE_ORIGIN` /
    `TILE_SIZE`; do not copy the numbers.
- `README.md`: extend the sentence "The layout also switches each desktop in the current activity
  to the image wallpaper plugin." to say it also lines desktop icons up in one 32px column at the
  right edge, as Mac OS 8.6 does.

**Acceptance criteria.**
- `make check` passes with the new tests.
- Reverting any one of the three `writeConfig` values makes `test_desktop_icon_arrangement` fail.
- `test_widgets_in_menu_bar_order` and the clock tests still pass. The new calls use
  `desktopsArray[j]`, not a `panel.addWidget` handle, so `clock_config` does not pick them up.
- Manual smoke test (needs a Plasma session): after `lookandfeeltool -a org.macos8.desktop
  --resetLayout`, a file in `~/Desktop` appears at the top-right as a 32px icon. A second file
  appears below it.

**Out of scope.** Pinning the Trash to the bottom-right corner (Folder View has no such
setting), the icon label style (Mac OS 8.6 draws a white label box), and the icons themselves
(the icon-theme question in the scope-drift note above).

### Mac OS 8.6 Platinum tooltip (`widgets/tooltip.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Plasma tooltips should stop falling back to Breeze's rounded, translucent tooltip and
draw a flat Platinum one: a square `#FFFFCC` face with a 1px `#000000` outline. Two consumers read
the tooltip artwork, and the theme ships neither file today, so KSvg resolves both from the
fallback theme:
- `PlasmaComponents.ToolTip` (`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/ToolTip.qml`)
  draws its background from `imagePath: "solid/widgets/tooltip"`. It also draws a second
  `FrameSvgItem` with `prefix: "shadow"`; with no `shadow-*` elements nothing is drawn there,
  which is the same choice `widgets/button.svg` makes for its `ButtonShadow`.
- `libPlasmaQuick.so.6` (panel `ToolTipArea` tooltips, e.g. hovering the clock or a tray icon)
  holds the UTF-16 strings `widgets/tooltip` and `solid/` (`strings -el`).

Provenance (per PRINCIPLES.md: record it for a KDE-required value the reference set does not
show): no reference screenshot shows a Balloon Help balloon. QUESTIONS.md "How should the tooltip
palette anchor be grounded?" (decided 2026-10-08, option 2) records `[Colors:Tooltip]
BackgroundNormal=255,255,204` as a KDE-required role from the classic Platinum palette. This
widget paints its face from that value, and its outline is the same 1px black square outline
`widgets/background.svg` (the menu body) uses. The SVG header comment must say both things, and
that no pixel is screenshot-anchored.

**Approach.**
- New `theme/desktop-themes/org.macos8.desktop/widgets/tooltip.svg`. Copy the structure of
  `widgets/background.svg` exactly: 16x16 canvas, a 3px border around a 10px centre tile, the
  same `hint-*-margin` and zero-size `hint-*-inset` rects (styled with `style=`, so the parsed
  `fill` set stays the artwork palette), and the nine slices `top`/`bottom`/`left`/`right`/
  `center`/`topleft`/`topright`/`bottomleft`/`bottomright`. Swap the `#FFFFFF` face for
  `#FFFFCC`. Keep the black outline on the outer edge of each slice, with no bevel, no
  `shadow-*` and no `blurred*` elements. The 3px margins become the tooltip's text padding
  (`ToolTip.qml` sets `topPadding: backgroundItem.margins.top`, and so on), the same padding as
  the menu body.
- New `theme/desktop-themes/org.macos8.desktop/solid/widgets/tooltip.svg`, byte-identical to the
  file above. KSvg does not map `solid/widgets/tooltip` onto `widgets/tooltip`: Breeze ships
  `/usr/share/plasma/desktoptheme/default/solid/widgets/tooltip.svgz` for that reason, so without
  this copy `PlasmaComponents.ToolTip` would keep Breeze's artwork.
- Install needs no Makefile change: `install_package` copies the package with `cp -r`.

**Files touched.**
- The two SVGs above.
- `tests/desktoptheme_paths.py`: add `TOOLTIP_SVG` (`widgets/tooltip.svg`) and
  `SOLID_TOOLTIP_SVG` (`solid/widgets/tooltip.svg`).
- `tests/test_desktoptheme.py`:
  - Add both paths to `SVG_CANVASES` at 16x16, and update the comment above it, which counts
    the canvases by size. `test_registry_covers_every_shipped_svg` walks the package with
    `os.walk`, so it fails until both files are registered.
  - Add both paths to `TestInstall.INSTALLED_FILES`.
- New `tests/test_desktoptheme_tooltip.py`, modelled on `tests/test_desktoptheme_background.py`.
  `TestTooltip(NineSliceCase, unittest.TestCase)` with `SVG_PATH = TOOLTIP_SVG` holds:
  - `test_tooltip_hint_geometry`: the same `assert_hint_geometry(self, self.tree, [""], 3, 10, {…insets…})`
    call as `test_background_hint_geometry`.
  - `test_tooltip_pixels`: `assert_face_bevel(self, slices, "", TOOLTIP_FACE, "flat", size=10)`.
  - `test_tooltip_colours`: `attribute_values(self.tree, "fill") == {BLACK, TOOLTIP_FACE}`.
  - `test_face_is_the_scheme_tooltip_background`: `TOOLTIP_FACE` equals
    `hex_colour(...)` of `load_scheme().get("Colors:Tooltip", "BackgroundNormal")` split into
    ints. This ties the artwork to the colour scheme, so changing one without the other fails.
  - `test_solid_copy_is_identical`: the bytes of `SOLID_TOOLTIP_SVG` equal those of
    `TOOLTIP_SVG`.
  Define `TOOLTIP_FACE = "#FFFFCC"` in `tests/platinum_palette.py`, with a comment saying it is
  the `[Colors:Tooltip]` KDE-required role and is not screenshot-sampled.
- `README.md`: in the desktop-theme paragraph, after the `widgets/background.svg` sentence, name
  `` `widgets/tooltip.svg` `` (the flat `#FFFFCC` Platinum tooltip with a black outline, for
  panel and `PlasmaComponents.ToolTip` tooltips) and say that a byte-identical copy ships at
  `solid/widgets/tooltip.svg`, where `PlasmaComponents.ToolTip` looks for it.
  `tests/test_readme_theme_files.py` requires the backticked `widgets/tooltip.svg` token. Its
  `*/*.svg` glob does not see the nested `solid/` copy, so do not invent a token rule for it.

**Out of scope.** A balloon-shaped tail (Plasma tooltips are rectangular frames), a drop shadow,
and the tooltip text font.

**Acceptance criteria.**
- `make check` passes, and `make check CHECK_PATTERN='test_desktoptheme_tooltip.py'` runs the
  new tests.
- Each of these makes a named test fail: changing the face in either SVG; changing the scheme's
  `[Colors:Tooltip] BackgroundNormal` without the SVG; deleting the `solid/` copy or letting it
  diverge; moving or resizing a margin hint; leaving either file out of `SVG_CANVASES`.
- `make install XDG_DATA_HOME=<tmp>` installs both `widgets/tooltip.svg` and
  `solid/widgets/tooltip.svg` under `plasma/desktoptheme/org.macos8.desktop/`.

### Mac OS 8.6 menu-bar clock format: 12-hour time with AM/PM, no date, no seconds (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Make the menu-bar clock read like the Mac OS 8.6 one. The reference menu bar
(`macos8.6-screenshots/desktop_betawiki.png`) shows only `5:01 PM`: one line of text from x=882
to x=925, with dark pixels only in rows 5..13. It is followed by the Application-menu separator.
Two-colour pixels (`#000000` on `#DDDDDD`) make the glyphs exact. `desktop_archiveorg8.6hd.png`
shows the same form (`h:mm PM`). Today
`theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js` adds
`org.kde.plasma.digitalclock` with no configuration. So Plasma's defaults apply
(`/usr/share/plasma/plasmoids/org.kde.plasma.digitalclock/contents/config/main.xml`, group
`Appearance`): `showDate=true` puts the date beside or below the time in the 20px bar, and
`use24hFormat=1` follows the locale, so many users get a 24-hour clock. The layout plan listed
"the clock format" as a later plan.

**Approach.**
- In the layout script, keep the clock's widget handle and write three `Appearance` keys with
  the Plasma scripting API. Upstream's `updates/digitalclock_rename_timezonedisplay_key.js` uses
  the same `currentConfigGroup`/`writeConfig` calls:
  ```js
  var clock = panel.addWidget("org.kde.plasma.digitalclock");
  // Reference desktop_betawiki.png x=882..925: "5:01 PM" — 12-hour with
  // AM/PM, no seconds, no date.
  clock.currentConfigGroup = ["Appearance"];
  clock.writeConfig("showDate", false);
  clock.writeConfig("showSeconds", 0);   // Never
  clock.writeConfig("use24hFormat", 0);  // 12-Hour (Qt.Unchecked: always appends AM/PM)
  ```
  `use24hFormat` index 0 is "12-Hour" in `configAppearance.qml`. `DigitalClock.qml` appends
  `amPm` when the value is `Qt.Unchecked` (0). `showSeconds` choices are `Never`/`ToolTip`/
  `Always`, and the default is 1, so 0 is needed here: the reference has no seconds. Every other
  `addWidget` line stays as it is.
- Known limit (put it in the script comment, not in a test): whether the hour has a leading zero
  comes from the locale's time format. The clock has no setting for it.

**Files touched.**
- `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`:
  the change above.
- `tests/test_lookandfeel_layout.py`:
  - `test_widgets_in_menu_bar_order` uses the regex `^panel\.addWidget\("([^"]+)"\)\s*;`, which
    would no longer match the clock line. Widen it to allow an optional `var <name> = ` prefix,
    so the order and the `addWidget(` count checks still cover all six widgets.
  - Add a helper `clock_config(text)`. It finds the variable bound to
    `panel.addWidget("org.kde.plasma.digitalclock")` and returns a dict of its
    `<var>.writeConfig("<key>", <literal>)` calls, read as JS literals (`false`, ints). Then
    add `test_clock_writes_the_appearance_group` (the script contains
    `<var>.currentConfigGroup = ["Appearance"]` before the first `writeConfig`).
  - Add `test_clock_format_matches_reference`, which asserts exactly
    `{"showDate": False, "showSeconds": 0, "use24hFormat": 0}`.
  - New `TestClockMatchesReference(ReferenceScreenshotMixin, unittest.TestCase)` on
    `REFERENCE`, with constants `CLOCK_LEFT = 882`, `CLOCK_RIGHT = 925`, `CLOCK_TOP = 5`,
    `CLOCK_BOTTOM = 13`. A pixel is dark when its red channel is below 100.
    - `test_reference_clock_is_one_line`: in rows 1..17 of the bar, the dark columns of
      x=800..932 span exactly `CLOCK_LEFT..CLOCK_RIGHT`. Every dark pixel in that span lies in
      rows `CLOCK_TOP..CLOCK_BOTTOM`. That is one text line, so no date row (`showDate`
      false).
    - `test_reference_clock_has_am_pm_suffix`: the letter map of x=909..925, rows 5..13 equals
      this pinned "PM" glyph (`#` dark, `.` otherwise), which shows the 12-hour suffix:
      ```
      #####..##......##
      ##..##.##......##
      ##..##.###....###
      ##..##.###....###
      #####..#.##..#.##
      ##.....#.##..#.##
      ##.....#..###..##
      ##.....#..###..##
      ##.....#...#...##
      ```
- `README.md`: after "the clock and the window list" in the layout paragraph (the phrase wraps
  across two lines), add a clause
  saying the clock shows 12-hour time with AM/PM and no date or seconds, as the Mac OS 8.6 menu
  bar does.

**Out of scope.** Clock font and size (`autoFontAndSize` stays true), the Application-menu separator and icon at the right, and the
Apple-menu icon.

**Acceptance criteria.**
- `make check` passes. The two `TestClockMatchesReference` tests run (they do not skip) when the
  LFS image is materialized.
- Each of these makes a named test fail: removing any of the three `writeConfig` calls, changing
  any of their values, or dropping the `currentConfigGroup` line.
  `test_widgets_in_menu_bar_order` still fails when an `addWidget` id is reordered or added.
- `make install XDG_DATA_HOME=<tmp>` installs the updated layout script, and
  `tests/test_lookandfeel.py::TestPackageValid` still passes.

### Clear the title-bar pinstripes around the zoom box, as Mac OS 8.6 does (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** In the reference the pinstripes stop short of the right-hand box group, and the 3px
space between the zoom and collapse boxes is flat `#CCCCCC`. The theme draws the
`decoration-top` stripes right up to the zoom box and through the `ButtonSpacing` gap, because
Aurorae paints the uniform top tile under the button row and leaves the spacing undrawn.
`systemprofiler_betawiki.png` rows y=26..38:
- x=770..775: the stripes. `#FFFFFF` on even rows (26..36), `#777777` on odd rows (27..37).
- x=776: `#777777` on the odd rows, `#CCCCCC` on the even rows and on row 38. The grey stripe is
  offset 1px to the right of the white one, so it ends one column later.
- x=777..780: `#CCCCCC`.
- x=781..792: the zoom face, and x=793 its highlight column.
- x=794..796: `#CCCCCC`. This is the spacing.
- x=797: the collapse face begins.

`aboutsystem_betawiki.png` shows the same 5-column gap to the left of its collapse box
(x=338..342), so the gap belongs to whichever box is leftmost in the right-hand group.
`ButtonsOnRight=AL` in `theme/look-and-feel/org.macos8.desktop/contents/defaults` makes that
box the zoom box. Aurorae keeps a disabled button visible (`AuroraeButton.qml` hides a button
only when its SVG path is empty), so a non-maximizable window still shows a zoom box.

**Approach.** Bake the gap and the spacing into the zoom widget. The installed Aurorae plugin
reads a per-button `ButtonWidthMaximizeRestore` key: `strings` over
`/usr/lib/x86_64-linux-gnu/qt6/plugins/org.kde.kdecoration3/org.kde.kwin.aurorae.so` lists it
next to `ButtonWidthClose` and `ButtonWidthShade`. The `AuroraeMaximizeButton.qml` width
reads it, and the `KSvg.FrameSvgItem` fills the button (`anchors.fill: parent`), so a 21x13
center-only SVG renders 1:1.
- `org.macos8.desktoprc` `[Layout]`:
  - add `ButtonWidthMaximizeRestore=21`. That is the 5 gap columns, the 12 face columns, the
    highlight column and the 3 spacing columns.
  - set `ButtonSpacing=0`.
  - keep `ButtonWidth=13`, which the close and collapse buttons still use.

  The collapse box keeps `TitleEdgeRight=4`. The zoom face lands 3px left of the collapse
  face's left edge plus the highlight, as before, and the close box is unchanged: the left group
  has a single button, so the spacing never applied to it.
- `maximize.svg` and `restore.svg`:
  - Make the canvas `width="21" viewBox="0 0 21 13"`.
  - Shift every existing rect in both groups by +5 in x. Do it with a mechanical rewrite of the
    `x` attributes. A group-level translate is not an option, and the renderer refuses
    rect-level transforms.
  - In `active-center`, add the gap and spacing rects. Local column 0 is `#777777` on odd local
    rows 1..11 and `#CCCCCC` on the even rows 0..12. Columns 1..4 and 18..20 are `#CCCCCC` on
    all 13 rows.
  - In `inactive-center`, the same columns are all `#CCCCCC`, the flat inactive title bar.
  - Update each file's header comment with the new canvas and the provenance above.
- `shade.svg`, `close.svg` and `decoration.svg` are untouched.

**Tests** (`tests/aurorae_fixtures.py`, `tests/test_aurorae_{buttons,rc}.py`):
- Add `ReferenceImageCase.profiler_region(x0, y0, width, height)`, returning region-local
  `{(x, y): '#RRGGBB'}`, and make `profiler_box` call it.
- Add a constant `ZOOM_BOX_X = 5` to `tests/aurorae_fixtures.py`, the face's local x in the zoom canvas.
- `TestRc.test_button_spacing_matches_reference` (`test_aurorae_rc.py`): keep the derivation of the 3-column gap
  between the zoom highlight and the collapse face. Assert `ButtonSpacing` is `0`, and that the
  derived gap equals `ButtonWidthMaximizeRestore - ZOOM_BOX_X - 13`.
- New `TestRc.test_zoom_button_width_matches_reference` (`test_aurorae_rc.py`). Find the last `#777777` column on
  profiler rows 26..37 in x=760..780; it must be 776. Assert `ButtonWidthMaximizeRestore`
  equals the collapse face's first column (797, found as in the spacing test) minus that column.
  Also assert that `ZOOM_BOX_X` equals the zoom face's first column (781) minus that column.
- `TestButtons.test_zoom_box_matches_reference`: compare each zoom SVG's `active-center`
  against `self.profiler_region(776, 26, 21, 13)`. That covers every gap, face, highlight and
  spacing pixel.
- `TestButtons._glyph(path, group, offset=0)`: compare `art[(x + offset, y)]` with
  `base[(x, y)]` over the close box's points, and return the differing points in box-local
  coordinates. Pass `offset=ZOOM_BOX_X` for both zoom SVGs in `test_zoom_glyph_is_the_reference_glyph`
  and `test_inactive_glyphs_survive`, so `ZOOM_GLYPH` and the x0=781 reference lookup stay as
  they are.
- `test_inactive_center_is_flat` needs no change: `_inactive_fill` already maps `#777777` to
  `#CCCCCC`. Check that it passes against the wider canvas.
- Update the module docstring's list of what the file pins.

**Docs.** In README.md, change "13x13 close/zoom/collapse widgets" so it says the close and
collapse widgets are 13x13 and the zoom widget is 21x13: its box plus the stripe-free gap to
its left and the flat spacing to its right.

**Files touched.** `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`, `maximize.svg`,
`restore.svg`, `tests/aurorae_fixtures.py`, `tests/test_aurorae_{buttons,rc}.py`, `README.md`.

**Acceptance criteria.**
- The rc has `ButtonSpacing=0`, `ButtonWidthMaximizeRestore=21` and `ButtonWidth=13`, each
  re-derived from the profiler image by the tests above.
- Both zoom SVGs' `active-center` renders exactly the profiler pixels x=776..796, y=26..38. Their
  `inactive-center` is that region with every fill except `#888888`/`#222222` flattened to
  `#CCCCCC`, and the zoom glyph survives.
- `close.svg`, `shade.svg` and `decoration.svg` are byte-identical to before (`git diff --stat`).
- `make check` passes.

**Trade-off, decided here.** The zoom button's click area grows by 5px on its left and 3px on its
right, over pixels Mac OS paints as title bar. Zoom is non-destructive and reversible, and the
brief asks for pixel fidelity, so the gap ships.

**Out of scope.**
- The matching 4px gap and 1px offset to the right of the close box (aboutsystem x=24..28,
  profiler x=226..230). It would widen the close button's click area to the right
  (`ButtonWidthClose=18`), so a click 5px right of the box would close the window. QUESTIONS.md
  "Should the close button's click area widen to clear the pinstripes beside it?" asks for that
  decision.
- The cleared band around the title text. Aurorae has no title-background element.

**Implementation note (2026-10-17, feature).** Landed as planned. The zoom SVGs' x attributes were shifted by +5 mechanically and the gap and spacing rects added; `ZOOM_BOX_X` and the profiler-derived `ButtonWidthMaximizeRestore` test are in `tests/aurorae_fixtures.py` and `tests/test_aurorae_rc.py`.

### Grow the Aurorae title-bar boxes to 13x13 with their white highlight (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** In the reference, each Platinum title-bar box is its 12x12 face (the `#888888`
top/left shadow, the `#222222` outline, the gradient) *plus* a 1px `#FFFFFF` highlight: a column
just right of the face and a row just below it. The top-right pixel of the column and the
bottom-left pixel of the row are `#CCCCCC`. Sampled with `tools/png`:

- `aboutsystem_betawiki.png` close box: face x=11..22, y=29..40; white column x=23 at y=30..41;
  white row y=41 at x=12..23; `#CCCCCC` at (23,29) and (11,41). The collapse box at (343,29)
  matches, with its column at x=355.
- `systemprofiler_betawiki.png`: the close face at (213,26) has its column at x=225. The zoom face
  at x=781..792 has its column at x=793 (y=27..38) and its row at y=38 (x=782..793). Then come
  `#CCCCCC` x=794..796, the collapse face x=797..808, its column at x=809, `#CCCCCC` x=810..811,
  `#999999` x=812, and the black outline at x=813.

The shipped buttons are 12x12 (`ButtonWidth=12`, `ButtonHeight=12` in
`theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`), so the highlight is never drawn
on purpose. The collapse box only gets it because the `decoration-topright` corner tile happens
to paint `#FFFFFF` at its local x=1. The close and zoom boxes sit directly against the
`decoration-top` stripes, which have a `#FFFFFF`/`#777777` stripe where the column should be and a
`#CCCCCC` row where the row should be white. The fix makes each box a 13x13 widget that draws
its own highlight.

**Approach.**
1. `close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`: change the canvas to `width="13"
   height="13" viewBox="0 0 13 13"`. In `active-center`, add `#FFFFFF` at x=12, y=1..12 and at
   y=12, x=1..11, and `#CCCCCC` at (12,0) and (0,12). Leave every existing pixel and glyph alone.
   In `inactive-center`, set those same added pixels to `#CCCCCC`. That is what
   `_inactive_fill` already returns for any colour other than `#888888`/`#222222`, and it matches
   `decoration-inactive-top`, a flat `#CCCCCC` field with no highlight. Update each file's header
   comment: 13x13, the highlight's sample coordinates, and the inactive flattening.
2. `org.macos8.desktoprc` `[Layout]`: `ButtonWidth=13`, `ButtonHeight=13`, `ButtonSpacing=3`
   (zoom column x=793 to collapse face x=797), `TitleEdgeRight=4` (collapse column x=809 to
   outline x=813). `TitleEdgeLeft=4` and `ButtonMarginTop=4` do not change, because the face
   still starts at the same offset. Aurorae's `AuroraeButton.qml` stretches each button's
   `active-center` to `buttonWidth x buttonHeight` (`FrameSvgItem anchors.fill`), so the canvas
   has to equal the rc size to render 1:1.
3. `decoration.svg`: update the header comment that describes the 12x12 button footprint. The
   footprint becomes frame-local x=4..5 of the top-left corner and x=0..1 of the top-right
   corner, y=4..16. Change no artwork.
4. README.md: replace "12x12 close/zoom/collapse widgets" with 13x13, and mention the highlight.

**Tests (`tests/aurorae_fixtures.py`, `tests/test_aurorae_{buttons,rc,frame}.py`).** Measure every size from the reference, not from
constants:
- Change the `profiler_box` / `reference_box` default `size` to 13 (in `ReferenceImageCase`,
  `tests/aurorae_fixtures.py`). `TestButtons` (`test_aurorae_buttons.py`) then compares
  every pixel of the 13x13 boxes, highlight included: close (11,29) and (213,26), zoom (781,26),
  collapse (343,29) and (797,26). Update the docstring.
- `TestRc._close_box_size` (`test_aurorae_rc.py`) → return the button size: the `#888888` bounding box plus the
  `#FFFFFF` column and row next to it. Assert that the column x=max+1 and the row y=max+1 are
  white along the face's span, then return width+1 and height+1.
  `test_layout_metrics_match_reference` keeps comparing it with `ButtonWidth`/`ButtonHeight`.
- `test_button_offsets_match_reference`: compute `TitleEdgeRight` from the collapse box's
  highlight column, `right - (collapse_x + collapse_w)`, and in the profiler as
  `outline[-1] - 809`. The comments should name x=809 as the highlight column.
- `test_button_spacing_matches_reference`: the gap runs from the zoom box's highlight column to
  the collapse face. Assert that `zoom_right + 1` is `#FFFFFF` on the face rows, then that
  `ButtonSpacing == collapse_left - zoom_right - 2`.
- `TestCorners.BUTTON_MASK` (`test_aurorae_frame.py`): make it the 13x13 footprint, `decoration-topleft` x in (4, 5) and
  `decoration-topright` x in (0, 1), y in range(4, 17), and update its docstring.
- Add `test_highlight_is_reference_white`, which checks that in both references the face's
  right column and bottom row are `#FFFFFF` and the two corner pixels are `#CCCCCC`. This pins
  the new pixels to the image, separately from the whole-box comparison.

**Files touched.** The four button SVGs, `org.macos8.desktoprc`, the `decoration.svg` comment,
`tests/aurorae_fixtures.py`, `tests/test_aurorae_{buttons,rc,frame}.py`, and README.md.

**Acceptance criteria.**
- Each button SVG's root canvas is 13x13. Its `active-center` render equals the reference
  13x13 box pixel for pixel: close against both references, zoom (`maximize.svg` and
  `restore.svg`) against the profiler, collapse against both.
- `inactive-center` equals `active-center` with every pixel except `#888888`/`#222222` flattened
  to `#CCCCCC`. The existing `test_inactive_center_is_flat` and `test_inactive_glyphs_survive`
  pass unchanged.
- The rc reads `ButtonWidth=13`, `ButtonHeight=13`, `ButtonSpacing=3`, `TitleEdgeRight=4`,
  `TitleEdgeLeft=4`, `ButtonMarginTop=4`, and the reference-derived tests above re-derive each
  value.
- `make check` passes, including the README theme-file tests.

**Out of scope (possible follow-up).** Mac OS also clears the stripes for a few pixels beyond
each highlight: about 4–5 `#CCCCCC` columns before the stripes resume (aboutsystem x=24..28;
profiler x=226..229, and x=776..780 before the zoom box), plus a gap around the title text.
Aurorae tiles `decoration-top` uniformly, so reproducing those gaps needs wider per-button
widths (`ButtonWidthClose` etc., which Aurorae supports) or explicit spacers. That is a separate
design decision, so it is not planned here.

### Mac OS 8.6 zoom box glyph and collapse (windowshade) box for the Aurorae decoration (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it touches only the
`org.macos8.desktop` Aurorae package, one line of the global theme's `contents/defaults`, their
tests and README. It needs no other plan to land first.

**Goal.** Make the title bar's right-hand boxes match retail Mac OS 8.6: a **zoom box** and then,
at the far right, a **collapse box** that shades the window (KWin "shade" is the Mac windowshade).
Today's decoration gets this wrong. `maximize.svg` and `restore.svg` draw the glyph of the
right-hand box in `aboutsystem_betawiki.png` at x=343..354, y=29..40: two horizontal `#222222`
bars at local y=5 and y=7 spanning x=2..10. That is the **collapse** box glyph, not the zoom glyph.
"About This Computer" is not zoomable, so it shows only close + collapse. The retail Japanese 8.6
screenshot `systemprofiler_betawiki.png` (1024x768, lossless) shows all three boxes in one title
bar:
- close box at x=213..224;
- zoom box at x=781..792;
- collapse box at x=797..808.

All three span y=26..37. Verified while planning with `tools/png.read_png` + `pixel_at`:
- The profiler's close box and collapse box are pixel-identical to aboutsystem's close box at
  (11,29) and its right-hand box at (343,29).
- The zoom box equals the close box except at exactly 11 pixels, all `#222222`: local (7,2)..(7,6)
  and (2,7)..(7,7). This is the classic inner square drawn in the upper-left.
- The gap between the zoom and collapse faces is 4 columns (x=793..796).
- The collapse box's right edge sits the same distance from the frame edge as aboutsystem's box,
  so `TitleEdgeRight=5` stays valid.

The current `tests/test_lookandfeel.py::test_titlebar_buttons_match_the_reference` docstring
says "there is no collapse box on either side". That is wrong for windows that can be zoomed.

**Approach.**
1. `theme/aurorae/themes/org.macos8.desktop/shade.svg` (new): move the current `maximize.svg`
   artwork here unchanged. Keep its 12x12 canvas, the `active-center` and `inactive-center`
   groups, and the same rects. Rewrite its header comment to name it the collapse box, citing
   aboutsystem (343,29) and systemprofiler (797,26). Aurorae loads `shade.svg` for the `L` button
   (`auroraeTheme.shadeButtonPath` in `/usr/share/kwin/aurorae/AuroraeButton.qml`). The button
   is visible whenever that file exists (`visible = buttonSvg.imagePath != ""`). Its width comes
   from `ButtonWidthShade`, which defaults to `ButtonWidth`, so the rc needs no new width key.
   A shaded window sets `toggled`. The SVG ships no `pressed` prefix, so Aurorae keeps drawing
   the `active` art for it, the same as for the other boxes.
2. `maximize.svg` and `restore.svg`: replace the two-bar glyph with the zoom glyph. Each becomes
   the close box's rects (`close.svg` `active-center` / `inactive-center`) plus `#222222` at the
   11 pixels listed above, in both groups. The inactive group keeps the glyph, because
   `_inactive_fill` keeps `#222222`. Mac OS does not change the zoom box when a window is zoomed,
   so `restore.svg` stays identical to `maximize.svg` apart from its header comment, as it is
   today. Update both header comments to cite systemprofiler (781,26).
3. `org.macos8.desktoprc` `[Layout]`: set `ButtonSpacing=4` (today it is 8, which nothing reads,
   because each side has one button). Aurorae uses it as the row spacing in
   `AuroraeButtonGroup.qml`.
4. `theme/look-and-feel/org.macos8.desktop/contents/defaults` `[kwinrc][org.kde.kdecoration2]`:
   set `ButtonsOnRight=AL` (A = maximize/zoom, then L = shade/collapse at the far right).
   `ButtonsOnLeft=X` is unchanged.
5. README.md: in the window-decoration paragraph, name `shade.svg` in backticks. This is required
   by `tests/test_readme_theme_files.py::test_every_aurorae_svg_is_named_in_readme`. Describe the
   rc as having "12x12 close/zoom/collapse widgets". In the Installing paragraph, say a new window
   has the zoom box and the collapse box on the right.

**Tests** (`tests/test_aurorae_*.py`, `tests/test_lookandfeel.py`):
- Add a `SHADE_SVG` constant and put it in `BUTTON_SVGS`. Add `"shade.svg"` to
  `TestInstall.INSTALLED_FILES`.
- Add a second reference: `PROFILER_REFERENCE` = `macos8.6-screenshots/systemprofiler_betawiki.png`,
  read with `read_reference(..., max_rows=38)` in `TestButtons.setUpClass`, after
  `ReferenceImageCase.setUpClass`. Add a `profiler_box(x0, y0)` helper that mirrors `reference_box`
  and calls `skip_unless_materialized` on its own path and error.
- `TestButtons`:
  - `test_zoom_box_matches_reference`: compare `maximize.svg` and `restore.svg` `active-center`
    against `profiler_box(781, 26)`.
  - New `test_collapse_box_matches_reference`: compare `shade.svg` against
    `reference_box(343, 29)` and also against `profiler_box(797, 26)`.
  - Rename `ZOOM_GLYPH` to `COLLAPSE_GLYPH` (same set). Pin it on `shade.svg` in the existing glyph
    test and in `test_inactive_zoom_glyph_survives` (rename that test to cover both glyphs).
  - Add `ZOOM_GLYPH = {(7, y) for y in 2..6} | {(x, 7) for x in 2..7}`, pinned the same way against
    the close box, in both the active and the inactive groups.
- `TestRc`:
  - New `test_button_spacing_matches_reference`. It derives the gap from the profiler image:
    first `#888888` column of the collapse face minus last `#888888` column of the zoom face
    minus 1, searching x=775..815, y=26..37. It asserts `ButtonSpacing` equals that gap (4).
  - Extend `test_button_offsets_match_reference` with one check: `TitleEdgeRight` re-derived from
    the profiler window also equals the rc value. The profiler window's right outline is the last
    black pixel of row y=22 within x<816. The collapse face's right edge is x=808.
- `tests/test_lookandfeel.py::test_titlebar_buttons_match_the_reference`: assert
  `ButtonsOnRight == "AL"`. Rewrite the docstring to cite systemprofiler's zoom + collapse boxes.

**Files touched.**
- `theme/aurorae/themes/org.macos8.desktop/{shade.svg (new), maximize.svg, restore.svg, org.macos8.desktoprc}`
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`
- `tests/test_aurorae_*.py`, `tests/test_lookandfeel.py`
- `README.md`

`decoration.svg`/`.svgz`, `close.svg` and the Makefile stay unchanged: `install_package` copies
the whole package directory.

**Acceptance criteria.**
- `shade.svg` exists with `active-center` and `inactive-center`. Its active box equals both
  reference collapse boxes pixel for pixel. Its inactive box is the `_inactive_fill` derivation
  of the active box.
- `maximize.svg` and `restore.svg` active boxes equal the systemprofiler zoom box at (781,26)
  pixel for pixel. Each differs from `close.svg` at exactly `ZOOM_GLYPH`, in both states.
- `ButtonSpacing=4` and `ButtonsOnRight=AL`, each pinned by a test that re-derives it from the
  reference or names the box order.
- `make install` installs `shade.svg` (pinned by `TestInstall`). `kpackagetool6` still accepts
  the package wherever `TestPackageValid` runs.
- README names `shade.svg`, and `make check` passes.

### Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no shipped
SVG, and needs no other plan to land first.

**Goal.** Ship `widgets/plasmoidheading.svg` so the header and footer bands of applet popups draw
the Platinum etched rule (the `#888888`-over-`#FFFFFF` pair `widgets/line.svg` already ships)
between the band and the popup body. Today those bands are invisible:
`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/extras/PlasmoidHeading.qml` draws its
`KSvg.FrameSvgItem` (`imagePath: "widgets/plasmoidheading"`, `prefix: "header"` or `"footer"`)
only while `fromCurrentImageSet === backgroundSvg.fromCurrentImageSet`, and the backgroundSvg is
`dialogs/background`, which our package ships. So Plasma hides the Breeze fallback, and the
heading of kickoff, the system tray, notifications, the digital-clock calendar, network, volume,
bluetooth, clipboard and device-notifier popups runs into the body with no divider.
`grep -rni plasmoidheading` over the repo (outside `.git`) finds nothing, and no PLANS.md entry
covers it.

**Consumer contract (verified in installed Plasma 6 QML and Breeze).** One FrameSvg with two
prefixes, `header` and `footer`, each a full nine-slice (`<prefix>-topleft` … `<prefix>-center`)
plus `<prefix>-hint-{top,bottom,left,right}-margin`. In a popup, `BackgroundMetrics.getMargin`
returns the window's negative padding, so the band's insets pull it out over the
`dialogs/background.svg` 3px border on its top/left/right (header) or bottom/left/right (footer).
`enabledBorders` always includes top and bottom, and left/right only when the band touches the
window edge. Breeze (`/usr/share/plasma/desktoptheme/default/widgets/plasmoidheading.svgz`)
paints a background fill plus a 1px `ColorScheme-Text` line in the last row of `header-bottom`
(and the first row of `footer-top`), with 6px borders.

**Design decisions (settled; do not revisit).**
- Every border is 3px, the same as `dialogs/background.svg`, so where the band overlays the
  dialog border it lines up with it exactly.
- Every slice paints nothing (a transparent placeholder) except the rule rows. So the band shows
  the dialog's `#DDDDDD` face and the dialog's own outline/bevel shows through the band's
  top/left/right (header) or bottom/left/right (footer) edges. The corners are placeholders too,
  so the rule stops at the inside of the dialog's bevel instead of crossing it.
- `header-bottom` (6x3): row 0 placeholder, row 1 `#888888`, row 2 `#FFFFFF`, which puts the rule
  on the band's bottom edge, dark first. `footer-top` (6x3): row 0 `#888888`, row 1 `#FFFFFF`,
  row 2 placeholder, which puts the rule on the band's top edge. The same dark-then-light order
  as `line.svg`'s `horizontal-line`.
- Colours and provenance: `#888888`/`#FFFFFF` are the etched group-box rule sampled from
  `macos8.6-screenshots/systemprofiler_betawiki.png` at `(260,153)`/`(260,154)`, the
  provenance `line.svg` and `tests/test_desktoptheme_line.py::TestLineReference` already pin.
  This file does not re-sample them: its test ties the rule colours to `line.svg`'s
  `horizontal-line` instead. Using the etched rule as a popup header divider is a KDE-required
  surface that the reference set does not show (no 8.6 screenshot has a Plasma-style popup
  heading). Record that in the SVG comment as the nearest Platinum equivalent: the rule that
  divides a Platinum window's body.

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/plasmoidheading.svg`, modelled on
   `widgets/listitem.svg` (a 12x12 canvas where two prefixes share the same tile positions):
   - root `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">`
     and a comment naming the consumer (`PlasmaExtras.PlasmoidHeading`), the visibility rule
     above, the design decisions and the provenance;
   - `hint-tile-center` at `(3,3,6,6)` and `header-hint-*-margin` / `footer-hint-*-margin` with
     `listitem.svg`'s geometry (the `nine_slice_margins` layout, border 3, size 6), all
     `style="fill:#…"` like `listitem.svg`;
   - for each prefix, nine `<g id>` slices translated to the standard 3/6/3 tile origins. Each
     holds one full-tile placeholder rect, `style="fill:#FFFFFF" fill-opacity="0.01"` with no
     `fill` attribute. `header-bottom` adds `<rect y="1" width="6" height="1" fill="#888888"/>`
     and `<rect y="2" width="6" height="1" fill="#FFFFFF"/>` after it, and `footer-top` adds the
     same rects at `y="0"` and `y="1"`. The placeholder comes first, so `render_slices` reads its
     rows as `None` and its bounding box gives each tile its full 3px extent. No `class=`,
     `<style>`, `<script>`, rect `transform` or other id.
2. `tests/desktoptheme_paths.py`: add
   `PLASMOIDHEADING_SVG = os.path.join(PACKAGE, "widgets", "plasmoidheading.svg")` beside
   `LINE_SVG`.
3. `tests/test_desktoptheme.py`: import it; add `("plasmoidheading.svg", PLASMOIDHEADING_SVG,
   12, 12)` to `SVG_CANVASES` (and add "plasmoid heading" to the 12x12 group in the comment above
   it); add `os.path.join("widgets", "plasmoidheading.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_plasmoidheading.py`: `TestPlasmoidHeading(NineSliceCase,
   unittest.TestCase)` with `SVG_PATH = PLASMOIDHEADING_SVG` and `PREFIXES = ("header",
   "footer")`, plus module constants `DARK = "#888888"`, `LIGHT = "#FFFFFF"` and
   `SIZES = nine_slice_tile_sizes(12, 12, 3, 3, 3, 3)` (exported by `svg_assertions`; its keys
   are the nine slice names). Tests are listed in the
   acceptance criteria.
5. `README.md`: in the Installing section's desktop-theme inventory, name
   `widgets/plasmoidheading.svg` (the transparent header/footer band of applet popups, divided
   from the body by the same etched `#888888`/`#FFFFFF` rule). `tests/test_readme_theme_files.py`
   fails until README names it.

**Files touched.** New: `widgets/plasmoidheading.svg`,
`tests/test_desktoptheme_plasmoidheading.py`. Edited: `tests/desktoptheme_paths.py`,
`tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move this entry to Done). The Makefile does
not change: `make install` already copies the whole widgets directory.

**Acceptance criteria.**
- `make check` exits 0, including the new module, `tests/test_desktoptheme.py` (canvas pin,
  registered-SVG check, `TestInstall`) and `tests/test_readme_theme_files.py`.
- The inherited `NineSliceCase` checks pass for both prefixes: slice ids present, tiles placed by
  margins, tiles within margins, no script.
- `test_hint_geometry`: `assert_hint_geometry(self, self.tree, ("header", "footer"), 3, 6)`.
- `test_rule_rows`: `render_slices(tree)["header-bottom"] == pixel_map((None,)*6 + (DARK,)*6 +
  (LIGHT,)*6, 6, 3)` and `render_slices(tree)["footer-top"] == pixel_map((DARK,)*6 +
  (LIGHT,)*6 + (None,)*6, 6, 3)`.
- `test_other_slices_paint_nothing`: every other one of the 18 slices (the eight `header-*` and
  eight `footer-*` names besides those two) equals `pixel_map((None,) * (w*h), w, h)` for its
  `(w, h)` in `SIZES`.
- `test_colours`: `attribute_values(tree, "fill") == {DARK, LIGHT}` and
  `attribute_values(tree, "fill-opacity") == {"0.01"}`.
- `test_rule_matches_line_svg`: parse `LINE_SVG` and require
  `render_slices(line_tree)["horizontal-line"] == {(0, 0): DARK, (0, 1): LIGHT}`. The heading's
  rule then cannot drift from the separator whose colours `TestLineReference` pins to the
  reference pixels.
- `assert_unique_ids`, `assert_no_style_elements` and `assert_no_external_references` pass.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs `widgets/plasmoidheading.svg`
  byte-identical to the source (checked by the extended `TestInstall.INSTALLED_FILES`).
- Manual smoke test (needs a Plasma session): the system-tray and kickoff popups show a grey
  line over a white line under their header row, the band otherwise matches the grey popup body,
  and the popup's black outline and bevel stay continuous behind the band.

### Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no shipped
SVG, and needs no other plan to land first.

**Goal.** Ship `widgets/line.svg` so Plasma's separators draw the Platinum etched rule (a dark
grey line with a white line beside it) instead of Breeze's 20%-opacity text-colour hairline.
`widgets/line` is the most-read desktop-theme element the package still lacks: grepping the
installed QML for `imagePath: "widgets/line"` finds it in `PlasmaComponents.SpinBox`,
`PlasmaExtras.ListSectionHeader`, `PlasmaExtras.ExpandableListItem`, and in the kicker, system
tray, notifications, digital-clock calendar, volume, network, bluetooth, margins-separator and
konsole-profiles plasmoids. `ls theme/desktop-themes/org.macos8.desktop/widgets/` shows no
`line.svg`, and no PLANS.md entry covers it.

**Consumer contract (verified in installed Plasma 6 QML and Breeze).** Consumers read exactly two
element ids, `horizontal-line` (10 uses) and `vertical-line` (3 uses), through `KSvg.SvgItem`
(whose implicit size is the element's natural size; `ListSectionHeader.qml` stretches it with
`Layout.fillWidth`, the system tray anchors it left/right) or through
`lineSvg.elementSize("horizontal-line").height` (kicker's `horLineHeight`). Breeze's
`/usr/share/plasma/desktoptheme/default/widgets/line.svgz` draws each as one 1x1 rect inside a
`<g id>`. So the thickness of each element is its natural size across the line, and the element
is stretched along the line.

**Reference and provenance.** `macos8.6-screenshots/systemprofiler_betawiki.png` (1024x768
lossless PNG, `sources.txt` "Mac OS 8.6, Japanese (Apple System Profiler …)") shows the Platinum
etched group-box rules on the `#EEEEEE` window body. `python3 tools/sample.py
macos8.6-screenshots/systemprofiler_betawiki.png X Y` gives:
- horizontal rule: `(136,136,136)` = `#888888` at `(260,153)`, `(255,255,255)` = `#FFFFFF` at
  `(260,154)`, body `#EEEEEE` at `(260,152)` and `(260,155)`;
- vertical rule: `#888888` at `(241,128)`, `#FFFFFF` at `(242,128)`, body `#EEEEEE` at
  `(240,128)` and `(243,128)`.
The rule is therefore 2px thick: dark first (top / left), white second (bottom / right). The same
`#888888`/`#FFFFFF` pair recurs at `(678,128)`/`(679,128)` (another vertical rule).

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/line.svg`: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="4" height="2" viewBox="0 0 4 2">` with a
   comment naming the widget, its two element ids, the consumers named above and the
   provenance above (file, coordinates, colours).
   - `<g id="vertical-line">` (no transform) holding `<rect width="1" height="1" fill="#888888"/>`
     and `<rect x="1" width="1" height="1" fill="#FFFFFF"/>`: a 2-wide x 1-tall element at (0,0).
   - `<g id="horizontal-line" transform="translate(3,0)">` holding
     `<rect width="1" height="1" fill="#888888"/>` and
     `<rect y="1" width="1" height="1" fill="#FFFFFF"/>`: a 1-wide x 2-tall element at (3,0).
   - Column 2 stays empty so the two elements' bounds do not touch. Rects carry no `id`, no
     `transform`, and literal `fill` attributes. No `class=`, `<style>`, `<script>`, `style=`
     attribute, hint rect or any other id.
2. `tests/desktoptheme_paths.py`: add `LINE_SVG = os.path.join(PACKAGE, "widgets", "line.svg")`
   beside `ARROWS_SVG`.
3. `tests/test_desktoptheme.py`: import `LINE_SVG`; add `("line.svg", LINE_SVG, 4, 2)` to
   `SVG_CANVASES` (and mention the 4x2 canvas in the comment above it); add
   `os.path.join("widgets", "line.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_line.py`, modelled on `tests/test_desktoptheme_arrows.py`
   (`SvgCase` with `SVG_PATH = LINE_SVG`), with module constants `DARK = "#888888"` and
   `LIGHT = "#FFFFFF"` used by both classes:
   - `TestLine` (see acceptance criteria).
   - `TestLineReference(unittest.TestCase)`: `setUpClass` calls
     `reference_image.read_reference(REFERENCE)`, `setUp` calls `skip_unless_materialized`, and a
     `pixel` helper wraps `png.pixel_at` (follow `SplashReferenceCase` in
     `tests/splash_fixtures.py`).
5. `README.md`: in the Installing section's desktop-theme inventory, name `widgets/line.svg`
   (the 2px Platinum etched separator, `#888888` then `#FFFFFF`, that list section headers,
   spin boxes and the kicker, system-tray and notification separators draw).
   `tests/test_readme_theme_files.py` fails until README names it.

**Files touched.** New: `widgets/line.svg`, `tests/test_desktoptheme_line.py`. Edited:
`tests/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move this
entry to Done). The Makefile does not change: `make install` already copies the whole widgets
directory.

**Acceptance criteria.**
- `make check` exits 0, including the new module, `tests/test_desktoptheme.py` (canvas pin,
  `TestInstall`) and `tests/test_readme_theme_files.py`.
- `TestLine.test_line_contract`: `assert_ids_present(self, tree, ("horizontal-line",
  "vertical-line"))`; `{g.get("id") for g in groups_with_id(tree)} == {"horizontal-line",
  "vertical-line"}`; `assert_unique_ids`, `assert_no_script_elements`,
  `assert_no_style_elements` and `assert_no_external_references` pass; and
  `attribute_values(tree, "fill") == {DARK, LIGHT}`.
- `TestLine.test_line_pixels`: `render_slices(tree)["horizontal-line"] == pixel_map((DARK,
  LIGHT), 1, 2)` and `render_slices(tree)["vertical-line"] == pixel_map((DARK, LIGHT), 2, 1)`.
- `TestLine.test_line_placement`: the `vertical-line` group has no `transform` and the
  `horizontal-line` group's `transform` is exactly `"translate(3,0)"`, so the elements' canvas
  bounds are 2x1 at (0,0) and 1x2 at (3,0) (the natural sizes consumers read).
- `TestLineReference.test_horizontal_rule_matches_reference` asserts `pixel(260,153) ==
  (0x88,0x88,0x88)`, `pixel(260,154) == (0xFF,0xFF,0xFF)`, and `pixel(260,152) ==
  pixel(260,155) == (0xEE,0xEE,0xEE)`; `test_vertical_rule_matches_reference` asserts the same
  at `(241,128)`, `(242,128)`, `(240,128)` and `(243,128)`. Each also asserts that
  `"#%02X%02X%02X" % pixel(...)` equals `DARK` / `LIGHT`, tying the sample to the SVG literal.
  Both skip (not fail) when the LFS image is not materialized.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs `widgets/line.svg` byte-identical to
  the source (checked by the extended `TestInstall.INSTALLED_FILES`).
- Manual smoke test (needs a Plasma session): the system-tray popup's header separator and a
  kicker submenu separator show a grey line over a white line, with no translucent hairline.


### Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Make applying the global theme with its desktop layout give one Mac OS 8.6 menu bar:
a single 20px panel across the top of the screen, holding the Apple menu at the left, the
application's menus after it, and the clock and Application menu at the right. Today
`theme/look-and-feel/org.macos8.desktop/contents/` ships no `layouts/` directory. So
`lookandfeeltool -a org.macos8.desktop --resetLayout` (or ticking "Desktop and window layout" in
System Settings → Global Theme) keeps Breeze's bottom taskbar, which `widgets/panel-background.svg`
then draws as a menu-bar bevel at the wrong edge and height.

**Grounding (sampled 2026-10-17 with `tools/png.read_png` + `pixel_at`).** In
`macos8.6-screenshots/desktop_betawiki.png` (retail, 1024x768), at both x=300 and x=400:
row 0 is `#FFFFFF`, rows 1–17 are `#DDDDDD`, row 18 is `#999999`, row 19 is `#000000`, and
row 20 is the desktop pattern `#63639C`. So the menu bar is 20px tall, and its bottom rule ends
at row 19. `desktop_betawiki86b9.png` has the same rows, but it is a beta, so it is not
evidence. `desktop_archiveorg8.6hd.png` (800x600) has a shorter, resampled bar, so ignore it.
These rows match the 2px bottom margin (`#999999` over `#000000`) that
`tests/test_desktoptheme_panel.py` `PANEL_EDGE_PIXELS` already pins.

**Approach.**
- New `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
  modelled on `/usr/share/plasma/layout-templates/org.kde.plasma.desktop.appmenubar/contents/layout.js`
  and on Breeze's `org.kde.breeze.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`. It does
  exactly this, with no `loadTemplate` call (Breeze's `defaultPanel` template is the bottom taskbar
  this replaces):
  - `var panel = new Panel;`
  - `panel.location = "top";`
  - `panel.height = 20;` (a literal, not `gridUnit`-derived; comment it with the sampled rows
    above).
  - `panel.floating = false;` (Plasma 6 panels float by default, which would detach the bar
    from the screen edge. `floating` is a Panel scripting property: the string sits next to
    `lengthMode`/`hiding` in `plasmashell`.)
  - `panel.addWidget(...)` in this order:
    1. `org.kde.plasma.kicker` (the Apple menu; this plan does not configure its icon)
    2. `org.kde.plasma.appmenu` (the global menu, as the stock appmenubar template uses)
    3. `org.kde.plasma.panelspacer`
    4. `org.kde.plasma.systemtray` (kept so that notifications and status icons still have a
       home; Mac OS 8.6 has no equivalent)
    5. `org.kde.plasma.digitalclock`
    6. `org.kde.plasma.windowlist` (the 8.6 Application menu at the far right: it shows the
       active window and switches between windows)

    All six plasmoids are installed under `/usr/share/plasma/plasmoids/`.
  - Then Breeze's wallpaper loop over `desktopsForActivity(currentActivity())`, setting
    `wallpaperPlugin = 'org.kde.image'`, so the `[Wallpaper] Image=org.macos8.desktop` default in
    `contents/defaults` has an image wallpaper to select.
- New `tests/test_lookandfeel_layout.py` (stdlib only, regex over the JS text; no JS engine).
  Put a module-level `LAYOUT` path constant next to the test.
  - `test_layout_file_is_shipped`: the file exists under the package's `contents/layouts/`.
  - `test_exactly_one_panel`: `new Panel` occurs once.
  - `test_panel_is_a_flush_top_bar`: matches `panel.location = "top"`, `panel.floating = false`
    and `panel.height = (\d+)`.
  - `test_panel_height_matches_the_reference`: re-derives the height from
    `desktop_betawiki.png` and checks it equals the JS `panel.height`. Wrap the read in
    `reference_image.read_reference` / `skip_unless_materialized`, as the other reference
    tests do. Derive the height as the first row y at column 400 whose pixel is `#000000` and
    whose next row is not panel grey, plus 1; it must be 20. Also assert that row 0 is
    `#FFFFFF` and row y-1 is `#999999`, so that a moved bevel fails the test.
  - `test_widgets_in_menu_bar_order`: the ordered list of `addWidget("…")` ids equals the six
    above, which pins that `org.kde.plasma.taskmanager`/`icontasks`/`kickoff` are absent.
  - `test_desktops_use_the_image_wallpaper`: matches `wallpaperPlugin = 'org.kde.image'`.
- `tests/test_lookandfeel.py` `TestPackageValid` already validates the installed package, and
  `make install` copies the whole package directory through `install_package`. So no Makefile
  change is needed. Confirm that the installed tree contains `contents/layouts/` (extend an
  existing install assertion only if one lists package files).
- README.md: in the paragraph that describes the global theme, add one sentence. It names
  `contents/layouts/org.kde.plasma.desktop-layout.js`, says that applying the theme with
  `lookandfeeltool -a org.macos8.desktop --resetLayout` (or with "Desktop and window layout"
  ticked) replaces the panels with the single 20px top menu bar, and lists the widgets.
  Plasma replaces the user's existing panels only when the layout is applied, so state that
  plainly.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`
(new), `tests/test_lookandfeel_layout.py` (new), `README.md`.

**Out of scope (later plans).** The Apple-logo icon for kicker (needs an icon theme or a
shipped icon), the Mac OS 8.6 menu-title metrics for `appmenu`, and the clock format.

**Acceptance criteria.**
- `make check` passes, including the new `tests/test_lookandfeel_layout.py`. Its reference-height
  test runs (does not skip) when the LFS image is materialized, and reads `20`.
- Changing `panel.height` to any value other than the re-derived height, adding a second
  `new Panel`, dropping `panel.floating = false`, or reordering or adding an `addWidget` id each
  makes a named test fail.
- `make install XDG_DATA_HOME=<tmp>` installs
  `<tmp>/plasma/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
  and `kpackagetool6 --type Plasma/LookAndFeel --show org.macos8.desktop` still validates (via the
  existing `TestPackageValid`).

### Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17 by the director role, from the BUGS.md entry "No automated Plasma render/capture step feeding the fidelity check"; done 2026-10-17)

**Provenance.** This replaces the BUGS.md entry "No automated Plasma render/capture step feeding
the fidelity check" (found 2026-10-07). That entry was refused on 2026-10-07 because no offline
render path existed. At the user's direction it is now a plan, because a headless path does
exist on this machine. On 2026-10-17 the director probed it with no display server and isolated
`XDG_*` directories, and every step below exited 0:
- `make install XDG_DATA_HOME=<tmp>/data`;
- seeding `<tmp>/cfg/kwinrc` and `<tmp>/cfg/plasmarc` (below);
- `dbus-run-session -- kwin_wayland --virtual --no-lockscreen --width 320 --height 240 --socket
  <name> --exit-with-session "sh -c 'plasmawindowed org.kde.plasma.calculator & sleep 8;
  spectacle -b -n -f -o <out.png>'"`.

The result was a 320x240 PNG showing the Platinum Aurorae title bar and Platinum push buttons. The
window body pixels sampled `#DDDDDD` (`tests/platinum_palette.py` `FACE`). Without the seeded
config the same capture rendered Breeze. Two things did not work, and the approach avoids them:
- `plasma-apply-colorscheme` run *outside* the KWin session dumped core.
- `lookandfeeltool -a` run inside the session wrote `kdeglobals` but not the `kwinrc`
  decoration keys.
`xvfb-run`, `Xvfb` and `qml`/`qmlscene` are still absent; the path above needs none of them.

**Goal.** Add one bounded, non-interactive command that renders a themed Plasma surface at a fixed
size and writes it as the candidate PNG `tools/fidelity.py` consumes. Pin it with a test that
`make check` runs.

**Approach.**
- New `tools/render_surface.py`. Use the standard library only, following the argparse /
  `report_error` style of `tools/fidelity.py` and `tools/cli.py`.
  - CLI: `python3 tools/render_surface.py OUTPUT [--applet ID] [--width W] [--height H]
    [--settle SECONDS] [--timeout SECONDS]`.
  - Defaults: `--applet org.kde.plasma.calculator`, 320x240, `--settle 8`, `--timeout 90`.
  - Exit status: 0 when written, 1 when the render or capture fails, 2 for usage errors or
    missing tools.
  - `main()` creates a `tempfile.mkdtemp()` scratch root holding `rt/` (mode 0700, used as
    `XDG_RUNTIME_DIR`), `cfg/` (`XDG_CONFIG_HOME`) and `data/` (`XDG_DATA_HOME`). It removes the
    root in a `finally`. The user's real config and session are never touched.
  - It runs `make install XDG_DATA_HOME=<data>` from the repo root.
  - It writes `cfg/kwinrc` and `cfg/plasmarc` from the `[kwinrc][org.kde.kdecoration2]` and
    `[plasmarc][Theme]` groups of `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
    parsed by a small helper `_defaults_groups()`. That way the render follows the global theme
    rather than a second copy of its keys.
  - It launches `dbus-run-session -- kwin_wayland --virtual --no-lockscreen --width W --height H
    --socket render-surface --exit-with-session <sh -c script>`. The script runs these steps in
    order:
    1. `plasma-apply-colorscheme MacOS8`;
    2. `plasmawindowed <applet> &`;
    3. `sleep <settle>`;
    4. `spectacle -b -n -f -o <OUTPUT>`.
  - The child environment drops `WAYLAND_DISPLAY` and `DISPLAY` and sets the three `XDG_*` paths.
    The child runs in its own session (`start_new_session=True`). On `--timeout` the script
    kills the whole process group, as `tests/process_runner.py` does, and exits 1.
  - Before launching, the script checks every external binary above with `shutil.which` and
    exits 2 naming the first one missing.
  - After the run it checks that `OUTPUT` exists and decodes with `tools/png.py` `read_png` at
    exactly W x H. Otherwise it exits 1.
- `Makefile`: add a public `render` target, `$(PYTHON) tools/render_surface.py
  $(RENDER_OUTPUT)`, with `RENDER_OUTPUT ?= render.png`. List it and `RENDER_OUTPUT` in `make
  help`. Add `render.png` to `.gitignore`.
- New `tests/test_render_surface.py`:
  - `TestDefaultsGroups` always runs and parses the real `contents/defaults`. It asserts that
    `_defaults_groups()` returns the `kwinrc` decoration theme
    `__aurorae__svg__org.macos8.desktop` and the `plasmarc` theme name.
  - `TestMissingTool` always runs. It puts an empty directory on `PATH` and asserts exit 2
    with the missing binary named on stderr.
  - `TestRender` is decorated `unittest.skipUnless` all of `kwin_wayland`, `dbus-run-session`,
    `plasmawindowed`, `spectacle` and `plasma-apply-colorscheme` are on `PATH`. In
    `setUpClass` it renders once to a temp file, using `process_runner.start` and
    `process_runner.finish(..., timeout=150)`. It asserts:
    - exit 0;
    - a 320x240 PNG;
    - the pixel at (300, 200) in the window body equals `platinum_palette.FACE`.
  - The render test is slow (about 10–15 s; this machine can throttle under load). Run it once
    per class, never per method.
- `README.md`: one sentence in the `make check`/`make help` paragraph naming `make render` and
  what it writes. Also update the `tools/fidelity.py` module docstring sentence "The Plasma
  render step that produces the candidate image is outside this tool" to name
  `tools/render_surface.py`.

**Out of scope.** These belong to a later plan once a render exists to compare:
- choosing a reference crop and `tools/fidelity.py` thresholds for a rendered surface;
- rendering a `plasmashell` panel.

**Acceptance criteria.**
- `make render` on this machine writes a 320x240 `render.png` whose window body pixel is
  `#DDDDDD`. It leaves `$HOME/.config` and `$HOME/.local/share` unmodified, and removes its
  scratch root.
- `make check` passes. `TestRender` runs here and skips cleanly where the tools are absent.
- No process from the render outlives the script. After `make render`, `pgrep -f
  'socket render-surface'` finds nothing.

**As built (2026-10-17, feature role).** `REQUIRED_TOOLS` also lists `make`, which the script runs
for the install. The capture is written inside the scratch root and copied to `OUTPUT` only after
it decodes at exactly W x H, so a failed run never leaves a stale or partial `OUTPUT`. Beyond the
plan, `tests/test_render_surface.py` covers argument validation and the failure and timeout paths
against shell stubs of the external tools, so those run where KDE is absent.


### Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Make part 1's `theme/wallpapers/org.macos8.desktop` package (see "Mac OS 8.6 default
desktop pattern as a Plasma wallpaper package") reach the user. `make install` copies it into
`${XDG_DATA_HOME}/wallpapers/`, the user-local directory Plasma's image wallpaper and
`kpackagetool6 -t Wallpaper/Images` search. `make uninstall` removes it. Applying the global
theme selects it.

**Approach.**
- `Makefile`:
  - Add `WALLPAPER_ID := org.macos8.desktop`,
    `WALLPAPER_PACKAGE := theme/wallpapers/$(WALLPAPER_ID)` and
    `WALLPAPER_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/wallpapers` next to the `AURORAE_*`
    variables.
  - In `_install`, add `install -d "$(WALLPAPER_INSTALL_DIR)"` plus
    `$(call install_package,$(WALLPAPER_ID),$(WALLPAPER_PACKAGE),$(WALLPAPER_INSTALL_DIR))`.
  - In `_uninstall`, add the matching `rm -rf` of the package and its `.staging`/`.old`
    siblings, the same way as the Aurorae line.
  - Update the `_uninstall` comment's list of shared parents.
- `tests/theme_install.py`: add `installed_wallpaper_dir(destdir)`
  (`<destdir>/<XDG_DATA_HOME>/wallpapers`) and `installed_wallpaper(destdir, package_id)`,
  modelled on `installed_aurorae_dir` / `installed_aurorae_theme`.
- `tests/test_wallpaper.py`: add
  `TestInstall(FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase)`,
  shaped like `tests/test_aurorae_package.py::TestInstall`:
  - `KIND = "wallpapers"`
  - `PACKAGE_ID`
  - `PACKAGE_DIR`
  - `INSTALLED_FILES`: `metadata.json` and `contents/images/1024x768.png` (add more only if
    the cases accept nested paths; check `tests/install_lifecycle_cases.py`)
  - `COPY_FAILURE_GLOB = "*/wallpapers/*"`
  - overrides of `installed_parent` / `installed_package_dir`
- `tests/test_theme_install.py`: the spaced-root lifecycle test that asserts the scheme, the
  look-and-feel, the desktop theme and the Aurorae theme are installed and then removed also
  asserts the wallpaper package.
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: append `[Wallpaper]` with
  `Image=org.macos8.desktop`, the same form as Breeze's `Image=Next`.
- `tests/test_lookandfeel.py`:
  - Add the `"Wallpaper"` section and its `["Image"]` option to
    `TestDefaults.test_the_expected_sections_and_keys_are_set`.
  - Add `test_wallpaper_names_the_shipped_package`: `Image` equals the `KPlugin.Id` of
    `theme/wallpapers/org.macos8.desktop/metadata.json`.
- `README.md` "Installing" (outside the tumwater markers): the artifact count goes from four to
  five; name `wallpapers/` among the destinations and the shared directories `make uninstall`
  leaves in place. Add one sentence: the wallpaper is the retail 128x128 desktop pattern,
  shipped at fixed resolutions so it renders 1:1 when the screen matches one. Keep
  `tests/test_readme_theme_files.py` and `tests/test_readme_commands.py` green.

**Files touched.** `Makefile`, `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/theme_install.py`, `tests/test_wallpaper.py`, `tests/test_theme_install.py`,
`tests/test_lookandfeel.py`, `README.md`.

**Acceptance criteria.**
- `make install DESTDIR=<tmp>` creates
  `<tmp><XDG_DATA_HOME>/wallpapers/org.macos8.desktop/metadata.json`, and
  `make uninstall` removes that package and its `.staging`/`.old` siblings while leaving
  `wallpapers/` and any other package in it.
- The `TestInstall` lifecycle and failed-copy cases pass for the wallpaper.
- `TestDefaults` pins `[Wallpaper] Image=org.macos8.desktop` and ties it to the package
  metadata `Id`.
- `make check` passes.


### Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** The theme still shows Plasma's default wallpaper, but the desktop is the largest
surface in every reference. In the retail desktop `macos8.6-screenshots/desktop_betawiki.png`
(1024x768, lossless), the desktop picture is a **128x128 tile anchored at screen (0,0)**. The
tile at `x=0..127, y=128..255` is byte-identical to 32 other 128-aligned tiles. Each tile in
row `y=0` differs in 2560 pixels (128 x 20, the menu bar's height); tiles under icons and
windows differ too. The tile has 42 colours; the most common is `#63639C`, followed by
`#65659E`, `#64649D`, `#6767A0`, `#66669F` and `#62629B`. Part 1 ships that tile as a Plasma
wallpaper package (`Wallpaper/Images`) of full-screen PNGs. Part 2 ("Install the Mac OS 8.6
wallpaper package and select it from the global theme", which requires this part) installs the
package and has the global theme select it.

**Why full-screen PNGs and not an SVG or a single tile.** The Plasma look-and-feel `[Wallpaper]`
defaults group takes only `Image=<package id>`. Breeze's
`/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/contents/defaults` uses `Image=Next`.
`lookandfeeltool` and `kcm_lookandfeel.so` contain no `FillMode` string, so a theme cannot ask
for tiling. Plasma therefore scales the package image whose size is nearest the screen
("Scaled and Cropped"). An exact-size PNG renders the tile 1:1; a scaled SVG pattern or tile
would blur the 1-px dither. This follows Breeze's `Next` package, which ships
`contents/images/<W>x<H>.png` per resolution.

**Approach.**
- `tools/png_write.py` (new, standard library only: `zlib`, `struct`): add
  `encode_png(width, height, rgb) -> bytes`. It writes 8-bit RGB (colour type 2),
  non-interlaced, filter type 0 on every row, one IDAT compressed at `zlib` level 9, and
  `IHDR`/`IDAT`/`IEND` with CRCs. It raises `ValueError` when `rgb` is not bytes/bytearray of
  exactly `width*height*3`, or when either dimension is not a positive int. This is a separate
  module because `tools/png.py` is the reader and is already over 500 lines.
- `tools/make_wallpaper.py` (new): define these constants:
  - `REFERENCE = "macos8.6-screenshots/desktop_betawiki.png"`
  - `TILE_ORIGIN = (0, 128)`
  - `TILE_SIZE = 128`
  - `RESOLUTIONS`: `(1024,768)`, `(1280,800)`, `(1280,1024)`, `(1366,768)`, `(1440,900)`,
    `(1600,900)`, `(1680,1050)`, `(1920,1080)`, `(1920,1200)`, `(2560,1440)`, `(2560,1600)`,
    `(3840,2160)`
  - `PACKAGE_DIR = "theme/wallpapers/org.macos8.desktop"`

  Also add these functions:
  - `tile_from_reference(image) -> bytes`: the 128x128 RGB block at `TILE_ORIGIN`, read from a
    `tools.png.Image`.
  - `tiled_rgb(tile, width, height) -> bytes`: pixel `(x, y)` is `tile[y % 128][x % 128]`. Build
    each row by repeating the tile row and slicing; do not loop per pixel.
  - `main()`: reads the reference with `tools.png.read_png` and writes
    `PACKAGE_DIR/contents/images/<W>x<H>.png` for each resolution with `encode_png`. Each image
    starts at the tile origin, matching the reference's screen-anchored pattern. The output is
    deterministic, so re-running produces identical bytes.

  The files total about 670 KB at level 9 (measured: 1024x768 ≈ 28 KB, 3840x2160 ≈ 146 KB).
  They are committed like the other PNGs, so they go through Git LFS per `.gitattributes`.
- `theme/wallpapers/org.macos8.desktop/metadata.json` (new): `KPlugin` with
  `"Id": "org.macos8.desktop"` and `"Name": "Mac OS 8.6"`. Copy
  `"Authors": [{"Name": "kde-macos8.6-theme"}]`, `"License": "GPL-2.0-or-later"` and
  `"Version": "0.1.0"` from `theme/look-and-feel/org.macos8.desktop/metadata.json`. Add a
  `Description` ("Mac OS 8.6 default desktop pattern") and
  `"KPackageStructure": "Wallpaper/Images"`.
- Generate the images by running `python3 tools/make_wallpaper.py` once, and commit them.

**Files touched.** `tools/png_write.py`, `tools/make_wallpaper.py`,
`theme/wallpapers/org.macos8.desktop/metadata.json`,
`theme/wallpapers/org.macos8.desktop/contents/images/*.png` (generated),
`tests/test_png_write.py`, `tests/test_wallpaper.py`.

**Acceptance criteria.**
- `tests/test_png_write.py`:
  - `encode_png` output decodes with `tools.png.decode_png` back to the same width, height and
    `rgb`, for a 1x1 image and for a multi-row image of distinct pixels.
  - A wrong-length `rgb`, a zero dimension and a `bool` dimension each raise `ValueError`.
- `tests/test_wallpaper.py`, `TestMetadata`: reuse `tests/package_metadata.PackageMetadata` the
  way `tests/test_lookandfeel.py::TestMetadata` does. Pin `KPackageStructure == "Wallpaper/Images"`
  and `Id == "org.macos8.desktop"`.
- `tests/test_wallpaper.py`, `TestImages` (each read goes through
  `tests/reference_image.skip_unless_materialized`, since the shipped PNGs are LFS objects):
  - `contents/images/` holds exactly `<W>x<H>.png` for each of `make_wallpaper.RESOLUTIONS`.
  - Each image decodes to its named size.
  - Each image's `rgb` equals `make_wallpaper.tiled_rgb(tile, W, H)`, where `tile` is the
    top-left 128x128 block of the shipped `1024x768.png`. This proves every image is the same
    tile, anchored at (0,0).
- `tests/test_wallpaper.py`, `TestReferenceTile` (skip unless `desktop_betawiki.png` is
  materialized):
  - `tile_from_reference(read_png(REFERENCE))` equals the shipped tile.
  - The block at `TILE_ORIGIN` equals the reference block at `(384, 384)` and at `(768, 512)`,
    two other 128-aligned positions, which re-derives the 128 px period.
  - The reference pixel at `(300, 500)` is `#63639C` and equals tile pixel
    `(300 % 128, 500 % 128)`.
- `tests/test_wallpaper.py`, `TestPackageValid(KPackageInstallCase)` with
  `KPACKAGETOOL_TYPE = "Wallpaper/Images"`: `kpackagetool6 -i` accepts the package.
- `make check` passes.

### Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no existing
SVG, and needs no other plan to land first. It does not depend on the BUGS.md entry "Splash
progress bar pins the panel face and the empty track as its track and fill colours (found by the
plan role 2026-10-17)". That bug and this plan read the same reference pixels, and neither
change needs the other.

**Goal.** Ship `widgets/bar_meter_horizontal.svg` so `PlasmaComponents.ProgressBar` draws the
Platinum progress bar (a sunken grey track with a lavender fill) instead of Breeze's. Today the
package has no `bar_meter_horizontal` file (`grep -rln "bar_meter" theme tests` finds nothing), so
the notification job progress (`org.kde.plasma.notifications/contents/ui/components/JobItem.qml`),
the task-manager progress overlay (`org.kde.plasma.taskmanager/contents/ui/TaskProgressOverlay.qml`)
and the media controller's `ExpandedRepresentation.qml` fall back to Breeze.

**Consumer (verified in installed Plasma 6 QML).**
`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/ProgressBar.qml` declares a
`KSvg.Svg` with `imagePath: "widgets/bar_meter_horizontal"` and two `KSvg.FrameSvgItem`s on the
same `imagePath`: the `background` uses `prefix: "bar-inactive"` across the full width, and the
`contentItem` uses `prefix: "bar-active"`, which is `position * availableWidth` wide (for an
indeterminate bar, a quarter-width chunk that slides back and forth) and is hidden when narrower
than `fixedMargins.left + fixedMargins.right`. Both items are
`barSvg.elementSize("hint-bar-size").height` tall when the SVG has a `hint-bar-size` element,
and otherwise top margin plus bottom margin. `widgets/bar_meter_vertical` is out of scope:
`ProgressBar.qml` never reads it.

**Reference and provenance.** `macos8.6-screenshots/boot2_betawiki.png` (240x180 lossless PNG,
`sources.txt` "Mac OS 8.6 (boot screen)") shows the "Starting Up" bar just after it starts. It is
a 0.375x thumbnail of the 640x480 screen. In the thumbnail, the bar occupies rows y=99..102 and
columns x=101..138: x=101..105 hold the lavender filled portion, and x=106..138 the grey unfilled
track. `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png X Y` gives these exact
values, which this plan pins:
- track shadow (top row) `(154,154,154)` = `#9A9A9A` at `(120,99)`;
- track face `(173,173,173)` = `#ADADAD` at `(120,100)`;
- track light edge (bottom row) `(184,184,184)` = `#B8B8B8` at `(120,102)`;
- fill face `(155,155,234)` = `#9B9BEA` at `(102,100)`;
- fill dark edge (lower row) `(120,120,209)` = `#7878D1` at `(102,101)`.
The thumbnail cannot resolve the bar's pixel geometry, so its shape is provenance, recorded here.
The bar is a classic 1px sunken bevel: shadow on the top and left, light on the bottom and right.
The fill draws the same shadow on its top/left and `#7878D1` on its bottom/right. The bar is 10px
tall (the thumbnail's 4 rows / 0.375 ≈ 10.7), with 3px nine-slice borders.

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/bar_meter_horizontal.svg`: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">` with a
   comment naming the widget, its consumer and both prefixes, and the provenance above.
   - Hints (id-bearing rects; KSvg reads only their geometry): `hint-tile-center` 4x4 at (3,3).
     For each of `bar-inactive` and `bar-active`: `{prefix}-hint-top-margin` 4x3 at (3,0),
     `-hint-bottom-margin` 4x3 at (3,7), `-hint-left-margin` 3x4 at (0,3), `-hint-right-margin`
     3x4 at (7,3). Also `hint-bar-size` 10x10 at (0,0). These are exactly
     `nine_slice_hint_geometry(["bar-inactive", "bar-active"], 3, 4)` plus that one extra rect.
   - Both prefixes have nine `<g id="{prefix}-{slice}">` groups (`topleft`, `top`, `topright`,
     `left`, `center`, `right`, `bottomleft`, `bottom`, `bottomright`). The groups sit at the
     canvas origins the margin hints give them: corners at (0,0)/(7,0)/(0,7)/(7,7), top (3,0),
     bottom (3,7), left (0,3), right (7,3), centre (3,3). Draw both prefixes over the same region,
     as frame.svg does for its states. Inside the groups, plain rects with no id and literal
     `fill` attributes paint each prefix's 10x10 bar as follows. The outer top row and outer left
     column are the shadow (`#9A9A9A` for both prefixes). The outer bottom row and outer right
     column are the light edge (`#B8B8B8` inactive, `#7878D1` active). Every other pixel is the
     face (`#ADADAD` inactive, `#9B9BEA` active). At the two mixed corners the shadow takes the
     top-right pixel (0-based (9,0)) and the bottom-left pixel ((0,9)), and the light edge takes
     the bottom-right pixel ((9,9)).
   - Leave out `class=`, `<style>`, `<script>`, any `-inset` hint and any other prefix.
2. `tests/desktoptheme_paths.py`: add `BAR_METER_HORIZONTAL_SVG = os.path.join(PACKAGE, "widgets",
   "bar_meter_horizontal.svg")` beside `SLIDER_SVG`.
3. `tests/test_desktoptheme.py`: import it, add `("bar_meter_horizontal.svg",
   BAR_METER_HORIZONTAL_SVG, 10, 10)` to `SVG_CANVASES`, and add `os.path.join("widgets",
   "bar_meter_horizontal.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_progressbar.py` with `class TestProgressBar(NineSliceCase, …)`
   (follow `tests/test_desktoptheme_slider.py`), with `SVG_PATH = BAR_METER_HORIZONTAL_SVG` and
   `PREFIXES = ("bar-inactive", "bar-active")`, plus a `TestProgressBarReference` class that reads
   the reference through `tools.png` and calls `reference_image.skip_unless_materialized`
   (follow the `pixel` helper in `tests/splash_fixtures.py`).
5. `README.md`: in the Installing section's desktop-theme inventory, name
   `widgets/bar_meter_horizontal.svg` (the sunken grey Platinum track with a lavender fill for
   `PlasmaComponents.ProgressBar`).

**Files touched.** New: `widgets/bar_meter_horizontal.svg`, `tests/test_desktoptheme_progressbar.py`.
Edited: `tests/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move
this entry to Done). Nothing in the Makefile changes, because `cp -r` already installs new widget
files. No shared assertion helper changes: the tests below use only existing `svg_assertions` exports.

**Acceptance criteria.**
- `make check` exits 0. The new module passes, and so do the package, install and other widget suites.
- The inherited `NineSliceCase` tests pass for both prefixes: `test_slice_ids_present`,
  `test_tiles_placed_by_margins`, `test_tiles_stay_within_their_margins` and
  `test_no_script_elements`. `test_progressbar_ids_are_unique` runs `assert_unique_ids`.
- `test_progressbar_hint_geometry` runs `assert_hint_geometry(self, tree, ["bar-inactive",
  "bar-active"], 3, 4, extra={"hint-bar-size": ("0", "0", "10", "10")})`.
- `test_track_pixels` and `test_fill_pixels` use `render_slices` and pin every pixel of each
  prefix's nine slices, using `assert_edge_band_pixels` (size 4) for the four edges,
  `assert_corner_pixels` for the four corners and `assert_center_tile_is(…, size=4)` for the centre.
  The values are the shadow, light and face colours above, including the corner rule (for
  example `bar-inactive-topright` is `("#9A9A9A",)*3 + ("#ADADAD", "#ADADAD", "#B8B8B8")*2`).
- `test_progressbar_colours` asserts `attribute_values(tree, "fill") ==
  {"#9A9A9A", "#ADADAD", "#B8B8B8", "#9B9BEA", "#7878D1"}`, plus whatever fill the hint rects carry.
  Either give the hints one of these five colours, or state the hint colour in the test.
- `TestProgressBarReference.test_colours_match_reference` re-derives all five pixels from
  `boot2_betawiki.png` at the coordinates listed above. It also asserts that each sampled value
  equals the SVG literal the slice tests pin, defined once as a module constant used by both.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs
  `widgets/bar_meter_horizontal.svg` byte-identical to the source (checked by the extended
  `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a notification file-copy job shows a 10px sunken grey
  track filling from the left with lavender, with no Breeze blue.


### Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-16 by plan.** Independent of every done widget plan and of the planned
`tabbar`/`toolbar` plans: it adds one artwork file to the existing `org.macos8.desktop`
desktop-theme package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new
test module under `tests/` (`test_desktoptheme_arrows.py`) with the `TestArrows` class, one
`SVG_CANVASES` entry and one `TestInstall.INSTALLED_FILES` tuple entry in
`tests/test_desktoptheme.py`, and the README inventory lines. It touches no other `widgets/*.svg`,
`dialogs/background.svg`, `metadata.json`, or the color scheme.

**Goal.** Ship `widgets/arrows.svg` so `PlasmaComponents.ComboBox`'s dropdown indicator and
`ButtonContent`'s menu-button indicator draw a solid black Platinum triangle instead of inheriting
Breeze's `arrows.svgz`. Today the theme ships no `widgets/arrows`, so `KSvg` resolves the name to
the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/arrows`).**
- `org.kde.plasma.components/ComboBox.qml`: the `indicator: KSvg.SvgItem` names
  `imagePath: "widgets/arrows"`, `elementId: "down-arrow"`, `colorSet: KSvg.Svg.Button`, sized
  `Kirigami.Units.iconSizes.small` square and anchored to the right edge.
- `org.kde.plasma.components/private/ButtonContent.qml`: an `KSvg.SvgItem` names
  `imagePath: "widgets/arrows"` and `elementId: "down-arrow"`, sized
  `Kirigami.Units.iconSizes.small` square, `visible` only when
  `Accessible.role === Accessible.ButtonMenu`.

Both render the element by its own bounds scaled into the item's `Kirigami.Units.iconSizes.small`
square, so the element's bounding rect must be square and the triangle drawn inside it (the
default's 14x14 bounding rect is the same trick).

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/arrows.svgz` is a 44x44
canvas holding four element ids -- `up-arrow`, `down-arrow`, `left-arrow`, `right-arrow` -- each a
group with a 14x14 invisible bounding rect plus one `class="ColorScheme-Text"` / `fill="currentColor"`
chevron path; the four groups are the same chevron under a rotation transform. The package test's
`assert_no_style_elements` forbids `<style>`, so the artwork's colours must sit on literal `fill`
attributes the pixel and palette tests can read; the Platinum file paints the fill literally.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a combo box or menu button (the set is
  desktop, boot/splash, installer, About/System Profiler, Finder/dialogs, photographs and the 8.5
  supplement), so the arrows have no per-pixel reference. Their fill reuses the grounded
  Platinum black (`#000000`) that `tests/test_desktoptheme_checkmarks.py` already pins, and the SVG
  comment records that provenance, as `dialogs/background.svg` records its palette.
- Mac OS 8.6 popup buttons and combo boxes show a solid down triangle, unlike Breeze's open
  chevron, so the artwork is a filled path (no stroke), not a stroked one.

**Approach.**
1. Add `widgets/arrows.svg` to the package: a 16x16 canvas
   (`width="16" height="16" viewBox="0 0 16 16"`) holding four groups at the origin, each with an
   invisible 16x16 bounding `<rect>` (`fill="none"`, no `id`) and one solid `fill="#000000"`
   triangle path:
   - `down-arrow`: `M 4,5 L 12,5 L 8,11 Z`
   - `up-arrow`: `M 4,11 L 12,11 L 8,5 Z`
   - `left-arrow`: `M 11,4 L 11,12 L 5,8 Z`
   - `right-arrow`: `M 5,4 L 5,12 L 11,8 Z`

   The bounding rect pins each element's KSvg bounds to a full 16x16 square so the consumer scales
   the triangle into its square `iconSizes.small` item without stretching (the
   `widgets/checkmarks.svg` groups use the same trick). Give
   the file a header comment naming `widgets/arrows`, the two consumers and the provenance above.
   Use no `class`, `currentColor`, `<style>`, `<script>` or external reference.
2. Add `ARROWS_SVG = os.path.join(PACKAGE, "widgets", "arrows.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new module `tests/test_desktoptheme_arrows.py` with
   `TestArrows(SvgCase, unittest.TestCase)`, `SVG_PATH = ARROWS_SVG`, modelled on
   `tests/test_desktoptheme_checkmarks.py`:
   - `test_arrows_contract`: `assert_ids_present(self, self.tree, ("down-arrow", "up-arrow",
     "left-arrow", "right-arrow"))`; `attribute_values(self.tree, "fill") == {"none", "#000000"}`;
     `assert_no_script_elements`.
   - `test_arrows_geometry`: `elements_by_id(self.tree)`; for each of the four ids assert the group
     holds exactly one `rect` and one `path`, that the rect's `(x, y, width, height, fill)` is
     `("0", "0", "16", "16", "none")`, and that the path's `d` is the exact string above with
     `fill == "#000000"`.
4. Add `("arrows.svg", ARROWS_SVG, 16, 16)` to `SVG_CANVASES` and
   `os.path.join("widgets", "arrows.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`, so `TestSvgRootCanvas`, the id/uniqueness and self-containment
   checks, the registry-coverage check and `TestInstall` cover the new file.
5. Name `widgets/arrows.svg` in README.md's status-block widget list and its Installing inventory
   paragraph.

**Acceptance criteria.**
- `make check` exits 0 with `TestArrows` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the four element ids; each element holds one invisible 16x16 bounding
  rect and one solid `#000000` triangle path with the exact `d` above; the parsed `fill` attribute
  values are exactly `none` and `#000000`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/arrows.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a `ComboBox` dropdown and a button whose
  `Accessible.role` is `ButtonMenu` draw a solid black Platinum triangle; every other widget is
  unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no combo-box / menu-button screenshot, so the arrows have no per-pixel
  reference and reuse the grounded Platinum black by semantic role; the triangle geometry is a
  KDE-required shape the reference set does not show, pinned exactly by the test.
- The file ships one fill for all states; the default also ships no disabled variant, so a disabled
  `ComboBox` arrow stays black rather than Mac OS 8.6's grey (Plasma applies no separate disabled
  colour to a literal fill).

### Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-15 by plan; implemented 2026-10-17 by the feature role.** The follow-up the done menubaritem plan named alongside
`tabbar`/`tooltip`/`actionbutton`/`busy`/`switch`. Independent of every done widget plan and of the
planned `tabbar` plan: it adds one artwork file to the existing `org.macos8.desktop` desktop-theme
package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new test module
under `tests/` (`test_desktoptheme_toolbar.py`) with the `TestToolBar` class, one `SVG_CANVASES` entry and one
`TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the README inventory
lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`, `metadata.json`, or the color
scheme.

**Goal.** Ship `widgets/toolbar.svg` so the `PlasmaComponents.ToolBar` background draws the raised
grey Platinum surface instead of inheriting Breeze's `toolbar.svgz`. Today the theme ships no
`widgets/toolbar`, so `KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/toolbar`).**
- `org.kde.plasma.components/ToolBar.qml` sets `imagePath: "widgets/toolbar"` on its background
  `KSvg.FrameSvgItem` (`implicitHeight: 40`) and reads that frame's margins for its padding. Its
  child separator `KSvg.SvgItem` reads `widgets/listitem` element `separator`; the theme's
  `widgets/listitem.svg` deliberately ships no `separator`, so no separator draws and this plan
  leaves that file unchanged.
- Installed QML that instantiates a `ToolBar`: kickoff `contents/ui/Footer.qml` (the
  Applications/Places strip), `private/systemtray` `contents/ui/ExpandedRepresentation.qml` (the
  expanded-tray bottom bar), the desktop shell's `WidgetExplorer.qml` and
  `configuration/ShellContainmentConfiguration.qml`.

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/toolbar.svgz` is an
unprefixed nine-slice on a 40x40 canvas: `hint-tile-center` plus `top`/`bottom`/`left`/`right`/
`center`/`topleft`/`topright`/`bottomleft`/`bottomright` and the four margin hints, painted a flat
`ColorScheme-Background` with no bevel and no outline.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a Plasma toolbar (it is a Plasma-only
  surface with no Mac OS 8.6 counterpart), so the toolbar has no per-pixel reference. Its fills
  reuse the grounded raised Platinum window-body palette (`#000000` outline, `#FFFFFF` highlight,
  `#999999` shadow, `#DDDDDD` face) that `tests/test_desktoptheme_dialog.py` already pins, and the
  SVG comment records that provenance, as `dialogs/background.svg` records it.
- The raised grey surface is exactly `dialogs/background.svg`'s body: the same
  `[Colors:Window] BackgroundNormal=221,221,221` face and the same bevel rule. A Plasma desktop
  theme cannot alias one SVG to another `imagePath`, so the toolbar needs its own file even though
  the two share geometry.

**Approach.**
1. Add `widgets/toolbar.svg` to the package: one unprefixed nine-slice on the same 16x16 canvas as
   `dialogs/background.svg` -- 3px border, 10px centre tile, square corners -- a raised #DDDDDD
   face with the 1px #000000 outline and the 1px bevel inside it (`#FFFFFF` on top/left, `#999999`
   on bottom/right). Copy `dialogs/background.svg`'s slice geometry and give the file its own
   header comment naming `widgets/toolbar` and the provenance above.
2. Add `TOOLBAR_SVG = os.path.join(PACKAGE, "widgets", "toolbar.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new module under `tests/` (`test_desktoptheme_toolbar.py`) with `TestToolBar(NineSliceCase, unittest.TestCase)`,
   `SVG_PATH = TOOLBAR_SVG`, `PREFIXES = ("",)`, modelled on `tests/test_desktoptheme_dialog.py`:
   - `test_toolbar_hint_geometry`: `assert_hint_geometry(self, self.tree, [""], 3, 10)`.
   - `test_toolbar_frame_bevel`: `assert_face_bevel(self, render_slices(self.tree), "", FACE,
     "raised", size=10)`.
   - `test_toolbar_colours`: `assert_fill_palette(self, self.tree)`.
4. Add `("toolbar.svg", TOOLBAR_SVG, 16, 16)` to `SVG_CANVASES` and
   `os.path.join("widgets", "toolbar.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/toolbar.svg` in README.md's status block widget list and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestToolBar` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the nine unprefixed slice ids and the five hint ids; the centre tile
  is a solid #DDDDDD 10x10; the four edge bands and four corners paint the raised bevel; the parsed
  `fill` attribute values are exactly #000000, #FFFFFF, #999999 and #DDDDDD.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/toolbar.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): the Widget Explorer's toolbar strip and the expanded
  system tray's bottom bar draw a raised grey Platinum surface with no Breeze translucent/rounded
  background; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no toolbar screenshot, so the surface has no per-pixel reference and reuses
  the grounded raised Platinum grey window-body palette by semantic role.
- The file ships no `separator` element and `widgets/listitem.svg` gains none, so `ToolBar`'s child
  separator stays undrawn (Mac OS 8.6 has no row separators).

### Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-15 by plan.** The next follow-up the done menubaritem plan named ("then
`tabbar`, `tooltip`, and the `actionbutton`/`busy`/`switch` surfaces"). Independent of every
done widget plan: it adds one artwork file to the existing `org.macos8.desktop` desktop-theme
package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new
test module under `tests/` (`test_desktoptheme_tabbar.py`) with the `TestTabBar` class, one `SVG_CANVASES`
entry and one `TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the
README inventory lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`,
`metadata.json`, or the color scheme.

**Goal.** Ship `widgets/tabbar.svg` so the Plasma active-tab / expanded-applet highlights draw a
Platinum raised tab instead of inheriting Breeze's `tabbar.svgz`. Today the theme ships no
`tabbar.svg`, so `KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/tabbar`).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/TabBar.qml` and `TabButton.qml`:
  prefix `"north-active-tab"` for `TabBar.position === Header`, else `"south-active-tab"`.
  `TabButton` also sets `enabledBorders` (left/right plus top and/or bottom).
- `/usr/share/plasma/plasmoids/org.kde.plasma.kickoff/contents/ui/Footer.qml`: the
  Applications/Places tab highlight, north/south by `tabBar.position`.
- `CurrentItemHighLight.qml` (systemtray), `showdesktop/contents/ui/main.qml`,
  `shells/org.kde.plasma.desktop/contents/applet/CompactApplet.qml` and `.../views/Panel.qml`:
  a directional prefix by `Plasmoid.location` / `containment.plasmoid.location`
  (`west`/`north`/`east`/`south`), each followed by `if (!hasElementPrefix(prefix)) prefix =
  "active-tab"`.
- A missing prefix or slice renders nothing, and once this file exists there is no cross-theme
  fallback, so all four directional prefixes ship. Shipping all four keeps the `active-tab`
  fallback dead, exactly as the default theme does (it ships the same four and no `active-tab`).

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/tabbar.svgz` carries
the nine-slice ids
`{north,south,east,west}-active-tab-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}`
with per-state margin hints; each state's **inner** edge -- the one facing the panel content
(bottom for north, top for south, right for west, left for east) -- is its distinctive edge
(Breeze paints it with `ColorScheme-ButtonFocus`), so the four directions are not
interchangeable.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a tab control, so the tab has no
  per-pixel reference. Its fills reuse the grounded Platinum raised-face palette (`#000000`
  outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face) that
  `tests/test_desktoptheme_frame.py` already pins, and the SVG comment records that provenance,
  as the tooltip token records its KDE-required-role provenance.
- The raised bevel is the same 1px-outline-plus-bevel `widgets/frame.svg`'s `raised` state
  paints, so the active tab is the Platinum raised surface; the inner edge is left open (face
  only, no outline) so the tab merges with the content the way a Platinum tab does.

**Approach.**
1. Add the tab-bar artwork to the package's `widgets/` directory as `tabbar.svg`: four directional nine-slices
   on the tight 12x12 canvas, 3px border, 6x6 centre tile (the `widgets/frame.svg` /
   `widgets/menubaritem.svg` grid), one shared `hint-tile-center` and four margin hints per
   prefix.
   - Each prefix is a raised Platinum tab: `#DDDDDD` face, a 1px `#000000` outline on the three
     outer edges, a 1px `#FFFFFF` highlight inside the top/left outline and a 1px `#999999`
     shadow inside the bottom/right outline, square corners.
   - The inner edge is open (face only): `north-active-tab` bottom, `south-active-tab` top,
     `west-active-tab` right, `east-active-tab` left.
   - The closed edges use the `face_edge_bands("#DDDDDD", "raised")` bands -- top/left
     `("#000000", "#FFFFFF", "#DDDDDD")`, bottom/right `("#DDDDDD", "#999999", "#000000")`;
     the two fully-raised corners use `face_corners("#DDDDDD", "raised")`; each mixed corner
     where the open edge meets a raised edge extends that raised edge's band across its 3x3 tile
     (so a north `bottomleft` is three `#000000 #FFFFFF #DDDDDD` rows, a north `bottomright`
     three `#DDDDDD #999999 #000000` rows, and east/west transpose the same rule).
2. Add `TABBAR_SVG = os.path.join(PACKAGE, "widgets", "tabbar.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new test module `test_desktoptheme_tabbar.py` under `tests/` with `TestTabBar(NineSliceCase, unittest.TestCase)`,
   `SVG_PATH = TABBAR_SVG`, `PREFIXES = ("north-active-tab", "south-active-tab",
   "east-active-tab", "west-active-tab")`, modelled on `tests/test_desktoptheme_frame.py`:
   - `test_tabbar_hint_geometry`: `assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)`.
   - `test_tabbar_centres_are_the_face`: `assert_center_tile_is` on each `-center` slice,
     `"#DDDDDD"`, 6.
   - `test_tabbar_closed_edges_are_raised` / `test_tabbar_inner_edges_are_open`:
     `assert_edge_band_pixels` for each edge with the raised band or the flat `("#DDDDDD",) * 3`.
   - `test_tabbar_corners`: `assert_corner_pixels` for each corner with the raised table or the
     band-extended table above.
   - `test_tabbar_colours`: `assert_fill_palette(self, self.tree)` from `platinum_palette`.
4. Add `("tabbar.svg", TABBAR_SVG, 12, 12)` to `SVG_CANVASES` and
   `os.path.join("widgets", "tabbar.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/tabbar.svg` in README.md's status block widget list and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestTabBar` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the 36 `{north,south,east,west}-active-tab-{slice}` ids, the 16
  per-prefix margin-hint ids and `hint-tile-center`; each prefix's centre tile is a solid #DDDDDD
  6x6; the three closed edges and their corners paint the raised bevel; each inner edge is solid
  #DDDDDD; the parsed `fill` attribute values are exactly #000000, #FFFFFF, #999999 and #DDDDDD.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): Kickoff's Applications/Places tab highlight and the
  `PC3.TabBar` highlight draw a square Platinum raised tab with no Breeze blue line or rounded
  corner; a top/bottom panel's expanded applet and the system-tray current-item highlight draw
  the same; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no tab-control screenshot, so the four directions have no per-pixel
  reference and reuse the grounded Platinum raised palette by semantic role.
- `Panel.qml` may pass an empty prefix (`""`) when there is no containment; the file ships no
  unprefixed slices, exactly as the default theme does, so that case draws nothing.

### Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09)

**Planned 2026-10-09 by plan.** The follow-up the done viewitem plan left unplanned.
Independent of every done widget plan: it adds one artwork file to the existing
`org.macos8.desktop` desktop-theme package under `widgets/`, one path constant in
`tests/desktoptheme_paths.py`, a new `tests/test_desktoptheme_menubaritem.py` module with
the `TestMenuBarItem` class, one `SVG_CANVASES` entry and one
`TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the README
inventory lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`,
`metadata.json`, or the color scheme.

**Goal.** Ship `widgets/menubaritem.svg` so the Plasma menu-bar titles -- the
`org.kde.plasma.appmenu` applet's application-menu titles and the
`org.kde.plasma.windowlist` task-menu button -- draw the Platinum menu-bar behaviour (no
hover highlight; a flat #CCCCFF fill only while the title's menu is open) instead of
inheriting Breeze's `menubaritem.svgz`. Today the theme ships no `menubaritem.svg`, so
`KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.plasma.appmenu/contents/ui/MenuDelegate.qml`:
  `background` is a `KSvg.FrameSvgItem` with `imagePath: "widgets/menubaritem"` and
  `prefix` `"pressed"` when `down`, `"hover"` when `hovered && !menuIsOpen`, else
  `"normal"`; `topPadding`/`leftPadding`/`rightPadding`/`bottomPadding` all come from
  that item's `rest.margins`. `main.qml` sets `down: pressed || Plasmoid.currentIndex ===
  index`, so a title takes `pressed` while its menu is open and `hover` only while merely
  hovered.
- `/usr/share/plasma/plasmoids/org.kde.plasma.windowlist/contents/ui/MenuButton.qml`:
  three stacked `KSvg.FrameSvgItem`s read `widgets/menubaritem` with `prefix` `"normal"`,
  `"hover"` and `"pressed"`.
- No other consumer names `widgets/menubaritem` (a grep over `/usr/share/plasma` and
  `/usr/lib/x86_64-linux-gnu/qt6/qml`).
- A missing prefix or slice renders nothing and there is no cross-theme fallback once the
  file exists, so all three prefixes ship.

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/menubaritem.svgz`
carries the nine-slice ids
`{normal,hover,pressed}-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}`,
one shared `hint-tile-center`, and four margin hints per state, on a 112x34 canvas with a
uniform 6px border and a 22x22 centre tile.

**Grounding.**
- The Mac OS 8.6 menu bar is a flat light-grey strip (`desktop_betawiki.png` samples
  `#DDDDDD` at (5,5)); the landed `widgets/panel-background.svg` already paints it, so
  `normal` paints nothing perceptible and the panel shows through.
- Mac OS 8.6 highlights a menu-bar title only while its menu is open, not on hover, so
  `hover` also paints nothing perceptible; the appmenu label still switches to
  `Kirigami.Theme.highlightedTextColor` (= `[Colors:Selection] ForegroundNormal=0,0,0`,
  black) on hover, the same black it already uses, so the hovered title does not change.
- `pressed` is the flat `[Colors:Selection] BackgroundNormal=204,204,255` (#CCCCFF) fill,
  square corners, no bevel and no outline. `[Colors:Selection] ForegroundNormal=0,0,0` is
  the label colour while `pressed`, so black text stays readable on #CCCCFF.
- The reference set has no screenshot with a menu pulled down (scanning the light
  menu-bar rows of `desktop_betawiki.png`, `desktop_archiveorg8.6hd.png` and the rest for a
  dark full-width run finds none), so the pressed fill reuses the project's sampled
  selection token by semantic role -- as `widgets/viewitem.svg` and `widgets/listitem.svg`
  already do -- rather than a per-pixel menu sample. The SVG comment records that
  provenance.

**Approach.**
1. Add `theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg`: one `normal`,
   one `hover` and one `pressed` nine-slice on a tight 12x12 canvas, 3px border, 6x6 centre
   tile (the `widgets/listitem.svg` / `widgets/viewitem.svg` grid).
   - `pressed-*`: every slice a `#CCCCFF` rect filling its tile.
   - `normal-*` and `hover-*`: every slice a `style="fill:#FFFFFF" fill-opacity="0.01"`
     rect with no `fill` attribute (so `render_slices` reads it as `None`) filling its tile.
   - hints: `hint-tile-center` at (3,3,6,6) and
     `{normal,hover,pressed}-hint-{top,bottom,left,right}-margin` at the 3px edges,
     identical for all three states.
2. Add `MENUBARITEM_SVG = os.path.join(PACKAGE, "widgets", "menubaritem.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add `tests/test_desktoptheme_menubaritem.py` with
   `TestMenuBarItem(NineSliceCase, unittest.TestCase)`, `SVG_PATH = MENUBARITEM_SVG`,
   `PREFIXES = ("normal", "hover", "pressed")`, modelled on
   `tests/test_desktoptheme_viewitem.py`:
   - `test_menubaritem_hint_geometry`: `assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)`.
   - `test_menubaritem_normal_and_hover_have_no_fill`: `assert_slices_uniform` with `None`
     for both prefixes, and `attribute_values(self.tree, "fill-opacity") == {"0.01"}`.
   - `test_menubaritem_pressed_is_flat_selection_colour`:
     `assert_slices_uniform(..., "pressed", "#CCCCFF")`.
   - `test_menubaritem_slices_fill_their_tiles`:
     `assert_slices_fill_their_tiles(..., (("normal", None), ("hover", None), ("pressed", "#CCCCFF")), 3, 6)`.
   - `test_menubaritem_colours`: `attribute_values(self.tree, "fill") == {"#CCCCFF"}`.
4. Add `("menubaritem.svg", MENUBARITEM_SVG, 12, 12)` to `SVG_CANVASES` and
   `os.path.join("widgets", "menubaritem.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/menubaritem.svg` in README.md's status block and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestMenuBarItem` passing and `TestSvgRootCanvas`/`TestInstall`
  covering the new file.
- The SVG parses and contains the 27 `{normal,hover,pressed}-{slice}` ids, the 12 per-state
  margin-hint ids and `hint-tile-center`; every `pressed` slice renders entirely #CCCCFF;
  every `normal`/`hover` slice has no `fill` attribute and a `fill-opacity` of 0.01; the
  only parsed `fill` attribute value is #CCCCFF.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`
  byte-identical to source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): the appmenu application-menu titles show no
  highlight while merely hovered and a flat #CCCCFF rectangle with black text while a
  title's menu is open, with square corners and no Breeze bevel; the windowlist task-menu
  button draws the same; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The `windowlist` MenuButton takes its `hover` background from this file, so a hovered
  task-menu button shows no highlight. Mac OS 8.6 has no analogous window-list button, so
  there is no reference for a hovered state and the transparent `hover` is the faithful
  choice for the appmenu titles.
- The uniform 3px margins are the project's tight 12x12 grid; the reference set has no
  menu-open screenshot to measure a per-side menu-title padding from.

- Mac OS 8.6 Platinum view item widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 1e1a455)
- Mac OS 8.6 Platinum slider widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 698e2b2)
- Wire the Mac OS 8.6 window decoration into the global theme defaults (planned 2026-10-09, done 2026-10-09; commit 0063255)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (planned 2026-10-08, done 2026-10-09; commit 91189a7)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (planned 2026-10-08, done 2026-10-08; commit 15bee80)
- Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08, done 2026-10-08; commit 395994f)
- Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 27b7439)
- Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 8df5661)
- Mac OS 8.6 Platinum scroll bar widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 9f51d5b)
- Mac OS 8.6 Platinum list item widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7fe6ddc)
- Mac OS 8.6 Platinum text field widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 0fe5213)
- Mac OS 8.6 Platinum checkmarks widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7313acd)
- Mac OS 8.6 Platinum radio button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit a73c322)
- Mac OS 8.6 Platinum frame widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit ebb65ca)
- Mac OS 8.6 Platinum button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit e553908)
- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)
