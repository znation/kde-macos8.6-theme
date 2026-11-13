# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: the Platinum theme covers KDE/Qt, GTK 3 and GTK 4, Firefox chrome and content, and cursor surfaces.

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

<a id="navigation"></a>

## Contents

- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Generating the wallpaper](#generating-the-wallpaper)
- [Reference screenshots](#reference-screenshots)
- [Validating the reference set](#validating-the-reference-set)
- [Sampling reference pixels](#sampling-reference-pixels)
- [Fidelity checking](#fidelity-checking)
- [Running checks](#running-checks)
- [Invariants](#invariants)
- [Development team](#development-team)

## Prerequisites

| Task | Requirements |
| --- | --- |
| Use the KDE theme | A KDE Plasma 6 session. Kvantum is a separately installed widget engine; when it is absent, widgets use another style. `kvantummanager` selects the theme in Kvantum. |
| Install packages | GNU Make and standard Linux utilities, including `install` and `flock`. `make install` copies theme files into the data home; it does not change the running user's settings. See [Installing](#installing). |
| Apply the theme | Python 3.10 or newer; `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `kwriteconfig6` and `kreadconfig6`. `make apply` installs the files and changes the running user's settings. |
| Select the GTK theme alone | Python 3.10 or newer, the package-install utilities above, and writable data and config homes. Run `make apply-gtk`; restart GTK applications. See [Installing](#installing) for selection and backup details. |
| Select the cursor theme alone | Python 3.10 or newer, the package-install utilities above, and `plasma-apply-cursortheme` on `PATH`. Run `make apply-cursor`; aggregate `make apply` skips cursor selection with a note when that tool is missing. See [Installing](#installing) for details. |
| Install Firefox sheets alone | Python 3.10 or newer and an existing writable Firefox profile, found automatically or specified as `FIREFOX_PROFILE=/absolute/profile`. Run `make install-firefox`; aggregate `make apply` skips this step with a note when it finds no profile. See [Installing](#installing) for profile selection and restart details. |
| Render headlessly | Python 3.10 or newer; `dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and `spectacle`. Dialog render modes also require `kdialog`; the GTK dialog render mode requires `zenity` instead; the desktop render mode requires `plasmashell`; the splash render mode requires `ksplashqml`. The default applet render also needs the `org.kde.plasma.calculator` applet (Debian packages it in `plasma-widgets-addons`); missing, the render refuses with exit 2 before any session, naming the applet id and the searched locations. See [Rendering a candidate](docs/rendering.md). |
| Run optional GTK 4 probes | Xvfb, `xvfb-run`, `xauth`, and Python GTK 4 introspection bindings. See [Running checks](#running-checks) for isolated commands. |
| Materialize reference images | Git LFS; run `git lfs install` and `git lfs pull`. See [Validating the reference set](#validating-the-reference-set). |
| Sample JPEG screenshots | ImageMagick's `convert` on `PATH`; PNG inputs need no extra tool. The sampler refuses a JPEG input without it. See [Sampling reference pixels](#sampling-reference-pixels). |

## Installing

### Quick start

See [Prerequisites](#prerequisites) for requirements. Choose one route:

```sh
make install
```

This copies the theme files without selecting them. To install and select Platinum for the
running user, use the alternative below. It changes user settings and may replace personal GTK 4
CSS after backing it up; [restoring personal GTK 4 CSS](#restoring-personal-gtk-4-css) explains
how. Existing panels are preserved; applying the optional desktop layout is a separate choice.

```sh
make apply
```

Restart GTK applications and Firefox to pick up their styles; the splash changes at the next
login. For GTK alone, use `make apply-gtk`. See [Removing the theme](#removing-the-theme) to
undo the installation.

### Installation details

[docs/installing.md](docs/installing.md) holds the details: which files each package installs into the data home, what `make apply` changes and selects in the running session, and how the GTK, Firefox and cursor selections, their backups and their removals work. See [Installation details](docs/installing.md).

### Rendering a candidate

[docs/rendering.md](docs/rendering.md) holds the render modes: what `make render` captures and refuses in each of the calculator, dialog, desktop and splash modes, which tools and applet each mode requires, and what every dialog, desktop and splash render gate pins there. See [Rendering a candidate](docs/rendering.md).

### Staging packages

To inspect installed package paths without selecting the theme in your session, stage an install
into a scratch root:

```sh
stage_dir=$(mktemp -d)
make install DESTDIR="$stage_dir" XDG_DATA_HOME=/usr/share INSTALL_PACKAGES='color-scheme gtk'
```

The scheme lands at `$stage_dir/usr/share/color-schemes/MacOS8.colors` and the GTK 3 and GTK 4
sheets and assets land under `$stage_dir/usr/share/themes/org.macos8.desktop/` (`index.theme`,
`gtk-3.0/gtk.css`, `gtk-4.0/gtk.css` and `assets/`). `/usr/share` here is the data-home suffix
inside the scratch root — `DATA_HOME` is `DESTDIR` followed by `XDG_DATA_HOME` — not a request to
install into the live system.

`INSTALL_PACKAGES` takes a space-separated list of the package families the Makefile knows:
`color-scheme`, `look-and-feel`, `desktop-theme`, `aurorae`, `wallpaper`, `icon-theme`,
`kvantum`, `fonts` and `gtk`. Omit the selector and the install copies every family; name a
subset and the install copies only that subset into the scratch root. A subset install is
additive: staging another family into the same scratch root later copies its files beside what
is already there and deletes nothing from earlier installs.

`make install` copies files into the destination and changes no selection or setting anywhere;
applying a selection is `make apply`'s job, which refuses to run with a non-empty `DESTDIR`
because a staged tree is for inspection, not for pointing the running session at. When you are
done inspecting, remove the scratch root yourself (`rm -rf -- "$stage_dir"`); nothing else
tracks it.

### Removing the theme

Choose another global theme in System Settings, then clear the individual selections before
deleting the installed packages. These commands remove this theme's selections or files; they do
not restore earlier settings or backups.

| Command | Effect and remaining action |
| --- | --- |
| `make remove-gtk` | Clears this theme's GTK selection and marker CSS. Existing GTK backups remain; restart GTK applications. |
| `make remove-firefox` | Removes this theme's sheets and preference block from the active profile. To target another profile, use `FIREFOX_PROFILE=/absolute/profile make remove-firefox`. Restart Firefox. |
| `make remove-cursor` | Removes this theme's cursor link but leaves the cursor selection. If it still names `org.macos8.desktop`, reset it with `plasma-apply-cursortheme breeze_cursors`. |
| `make remove-kvantum` | Clears only this theme's Kvantum engine selection (`[General] theme` in `kvantum.kvconfig`). A foreign theme name and the rest of the file remain; restart Qt applications. |
| `make uninstall` | Deletes installed theme packages and leaves user configuration in place. It also removes the theme-id directories it emptied under `themes/` (the shared directory and its `Kvantum/` parent); a directory still holding a file the theme did not install survives. This removes directories the install created, not user configuration. Run after clearing selections; it does not remove the cursor link or change keyboard mappings. |

To reselect the installed Plasma settings without installing packages or applying the other
theme surfaces, run `make apply-plasma`. Install first with `make install`; it requires Python
3.10+, `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and
`kwriteconfig6`. It preserves panels, attempts Kvantum selection when available (a non-default
`${XDG_DATA_HOME}` prints a note naming the limitation, as the Installing section describes),
and the splash change appears at the next login.

#### Restoring personal GTK 4 CSS

When `make apply` replaced a nonempty foreign `gtk-4.0/gtk.css`, it first copied that stylesheet
beside itself and printed a note naming both paths:

```
apply_gtk: note: backed up <your gtk-4.0/gtk.css> to <the new backup> before replacing it
```

`make remove-gtk` keeps them: it deletes only the marker-led sheet this theme wrote and leaves
a foreign `gtk.css` alone, so finish that removal successfully before restoring anything.

Backup candidates are `gtk-4.0/gtk.css.bak` and, when several replacements happened, the
unused-name siblings `gtk.css.bak.1` and up, all under your config home (`$XDG_CONFIG_HOME` when
it is an absolute path, otherwise `$HOME/.config`). A numbered suffix only means the plain name
was already taken when another apply made a backup — it is the next unused filename, not a
chronology, and the largest number is not the newest edition. Read the candidates and choose by
contents.

Copy the chosen backup back at the console; `cp -i --` preserves the backup and prompts before
replacing an existing destination. Quote every path so spaces survive:

```sh
cp -i -- "/absolute/path/to/gtk-4.0/gtk.css.bak" "/absolute/path/to/gtk-4.0/gtk.css"
```

If a foreign `gtk.css` survived the removal, it may hold edits newer than any backup, so read it
before replacing it. Restart running GTK applications afterward so they reload the restored
stylesheet.

This restores the user CSS alone: it does not restore the theme name your `gtk-3.0/settings.ini`
or `gtk-4.0/settings.ini` carried before applying (`make remove-gtk` clears its selection and
leaves the rest of the file alone), so choose a preferred GTK theme separately when you want
one.

## Generating the wallpaper

`python3 tools/make_wallpaper.py` rewrites the wallpaper package's images in
theme/wallpapers/org.macos8.desktop/contents/images/ as a solid `#CCCCCC` tile, an original
neutral placeholder rather than a crop of the reference desktop. The output is deterministic,
so re-running it rewrites identical bytes. It refuses an images directory that resolves outside
the repository — a checked-in symlink — so the generated images stay inside the wallpaper
package. `PLACEHOLDERS.md` tracks this temporary artwork.

## Reference screenshots

`macos8.6-screenshots/` is the visual reference set for this theme: 30 images for **Mac OS 8.6**
(released 1999-05-10) — retail screenshots and beta builds, two 8.1 supplements, one 8.5 supplement and two
photographs — collected from the internet and used as the source of truth when matching menu bar,
window chrome, widget metrics, icons and colour palette in the Plasma 6 port. They are reference
material only — the theme does not ship them.

| Surface | Count | Files |
| --- | --- | --- |
| Desktop | 5 | `desktop_betawiki.png`, `desktop_betawiki86b9.png`, `desktop_fandom.png`, `desktop_archiveorg.jpg`, `desktop_archiveorg8.6hd.png` |
| Boot / splash | 5 | `boot_betawiki.png`, `boot2_betawiki.png`, `boot_archiveorg.jpg`, `bootwhite_archiveorg.jpg`, `splash_macbase.gif` |
| Welcome / first boot / installer | 5 | `welcome_betawiki.png`, `welcome_tomo197707.png`, `firstboot_betawiki.png`, `setup_betawiki.png`, `setup_emaculation.png` |
| About / System Profiler | 7 | `about_betawiki*.png` (3), `aboutsystem_betawiki*.png` (2), `systeminfo_betawiki.png`, `systemprofiler_betawiki.png` |
| Finder / dialogs / apps | 3 | `finder_archiveorg.jpg`, `opendialog_macrumors86.jpg`, `apps_macrumors8.6.jpg` |
| Zoomed window chrome supplement | 2 | `browsers_zoomed_toastytech81.png`, `infocenter_zoomed_toastytech81.png` (Mac OS 8.1) |
| Photos of real hardware | 2 | `boot_powerbookphoto_macrumors.jpg`, `welcome_crtphoto_macrumors.jpg` |
| Non-8.6 supplement | 1 | `sherlock_fandom.jpg` (Mac OS 8.5) |

`sources.txt` records the origin URL and a version label for every file.

- **Labels are evidence-based.** A file is labelled 8.6 only when the version string is legible in
  the image itself (or the source states it). Beta/alpha builds (`8.6a3c2`, `8.6b3`, `8.6b9`,
  `8.6b2c4L8`) and the 8.5 Sherlock supplement are marked as such — they show chrome that differs
  from retail and must not be used as retail reference. One exception is
  recorded: `aboutsystem_betawiki.png` is a beta build, but its title bar, side
  borders and close/collapse boxes are pixel-identical to the retail
  `systemprofiler_betawiki.png`, so it is used as an evidence-backed
  window-chrome proxy where the set has no other lossless window-chrome
  screenshot. That equality is pinned by
  `tests/test_aurorae_reference_equivalence.py`, and the render gate's
  bottom-border crop stays on the beta because the System Profiler window's
  bottom differs (its sunken content field and bottom scrollbar).
- **Two entries are photographs**, not screenshots: real Macs running 8.6, useful for CRT
  colour/gamma and physical bezel context only.
- **Binary assets are stored with Git LFS** (see `.gitattributes`); run `git lfs install` after
  cloning.
- Images are third-party material kept for reference and attribution; copyright remains with the
  original authors.

## Validating the reference set

`.github/workflows/ci.yml` runs `make check` and `make check-references` on
pushes and pull requests, on Python 3.13 with a checkout with Git LFS images
materialized; the Makefile's targets still require Python 3.10 or newer at run
time. Its check job also installs the render gate's five Plasma tools
(`dbus-run-session`, `kwin_wayland`, `plasmawindowed`, `spectacle`,
`plasma-apply-colorscheme`), the `kdialog` client the gate's checkbox, combobox, line-edit, menu,
calendar, color, progressbar, slider and textbox dialog renders open, and the `zenity` client its
GTK
dialog render opens, so `make check` reaches the rendered-pixel gates, including the kdialog and
GTK dialog renders. Their
software-renderer guard still skips captures in the workflow environment; installed tools
are prerequisites, not proof that rendered pixels were compared. See [Running checks](#running-checks)
for the guard conditions and GPU-host guidance. Run those same commands locally for parity
with the workflow's check steps.

`sources.txt` is the provenance record for the images. After adding or renaming a screenshot, run
`python3 tools/check_references.py`: it fails if the record and the files on disk disagree (a
missing file, an unmaterialized Git LFS pointer, a file whose bytes are not a PNG/JPEG/GIF/WebP
image, an image with no entry, a malformed or duplicate entry) or if a source URL is not a
well-formed absolute URL (a bad scheme, raw whitespace or control characters, an authority
naming no host, or a malformed path, query or fragment, except for a `file://` URL).
`python3 tools/check_references.py --self-test` exercises the checker itself.
`make check-references` runs the self-test and then the repository check; it needs the Git LFS
images materialized, so it stays separate from `make check`.

### Troubleshooting the reference set

Each problem is printed on its own line. A record problem names its line as
`macos8.6-screenshots/sources.txt:<line>`; a file problem names the image instead.
Map a diagnostic to its next action:

| Diagnostic | Cause and next action |
| --- | --- |
| `... is an unmaterialized Git LFS pointer ...` | The file holds an LFS pointer, not the image bytes. Run `git lfs install` and `git lfs pull`, then `make check-references` again. |
| `... does not exist in .../macos8.6-screenshots/` | A declared file is absent — an incomplete checkout or a wrong filename in the record. Check the checkout, and compare the declared filename against the file on disk; fix the record only if the filename is genuinely wrong. Do not delete the provenance record to silence this: the record is the attribution trail for the set. |
| `image has no entry in sources.txt` | A file in the reference directory has no provenance record. Add one line for it: `filename \| source URL \| version label`. The filename is a bare name inside `macos8.6-screenshots/` (no path), the URL cites where the image came from, and the label is the evidence-based version string — see [Reference screenshots](#reference-screenshots) for the retail/beta labelling policy rather than restating it here. |
| `expected 3 fields ...`, `empty field in entry`, `duplicate entry for ...`, `source URL ...` | The record line is malformed, duplicate, or cites a URL that is not a well-formed absolute URL. Fix the record line the diagnostic names; it prints `sources.txt:<line>`, and a duplicate names the line of the first entry too. |
| `... is not a PNG, JPEG, GIF or WebP image; it may be an HTML error page or a truncated download` | The file's leading bytes match no known image signature. Inspect the download for an HTML error response or truncation and obtain the intended reference again; changing the file's extension does not change its bytes. |
| `... ends without the PNG IEND trailer`, `... ends without the JPEG EOI marker`, `... ends without the GIF trailer byte`, `... declares N RIFF bytes but holds M`; it may be a truncated download | The file's leading bytes match a known image format, but the stream stops before that format's end marker, so the download was cut short yet still looks like an image to the signature check. This diagnostic is a bounded structural check — the file's last bytes and, for WebP, its declared RIFF size — not a full decode. Obtain the intended reference again with a complete download and re-run the check. |
| `... points outside .../ (a symlink escape)` | A symlink in the reference set leads outside the reference directory, or the reference directory itself resolves outside the repository. Replace the symlink with the real file or directory it should name. |

A file that cannot be read at all — a read error, a non-UTF-8 `sources.txt`, a `sources.txt`
over the 1 MiB record limit, or a missing `sources.txt` — is reported directly; restore the
file it names.

The checker inspects signatures, not pixels: a pass means the bytes match a known image
format and every record line parses. It does not establish that an image decodes completely,
that a retail-labelled image is authentic, or that any pixel matches — those are the
[sampling](#sampling-reference-pixels) and [fidelity](#fidelity-checking) gates' work, on the
evidence each image actually carries. `--self-test` exercises the checker against its built-in
fixtures; it validates the checker, not the repository images. Run it alone or through
`make check-references`, which follows it with the repository check.

Exit statuses differ between callers. Direct `python3 tools/check_references.py` returns 0 when
the check or self-test passes (and for `--help`), 1 when the reference set has problems or a
self-test case misbehaves, and 2 for an unrecognized argument. GNU Make reports its own
recipe-failure status for `make check-references`; the checker's problem lines above appear in
the recipe's output either way.

## Sampling reference pixels

[docs/sampling.md](docs/sampling.md) holds the sampler's user guide: the sampling modes, the option families and
troubleshooting. The most common command samples one pixel:
`python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5` prints its RGB and hex values. See
[Sampling reference pixels](docs/sampling.md).

## Fidelity checking

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares a rendered PNG surface against a
reference screenshot and reports mean absolute error, per-channel mean absolute error
(R, G, B, A), RMSE, worst per-channel delta and where it occurs, and the fraction of
differing pixels.
Pass `--candidate-crop X,Y,W,H` to crop the candidate and `--crop X,Y,W,H` to select a
surface region of the reference.
If a comparison refuses to run, see [Troubleshooting a comparison](docs/fidelity.md#troubleshooting-a-comparison).
A JPEG candidate or reference is decoded once through ImageMagick's `convert` into a
private temporary PNG before the comparison, so the reference set's JPEG screenshots are
comparable directly; other non-PNG formats keep the decode refusal.

[docs/fidelity.md](docs/fidelity.md) holds the fidelity guide: capturing a candidate, troubleshooting
a render or a comparison, choosing a diagnostic and the diagnostic reference. See
[Fidelity checking](docs/fidelity.md).

## Running checks

Run the full project check before submitting changes. Focused runs help with iteration, but do not
replace the full check.

| Scope | Command |
| --- | --- |
| Full project check | `make check` |
| Matching test modules | `make check CHECK_PATTERN='test_colorscheme*.py'` |
| One test class | `make check CHECK_TESTS=test_colorscheme.TestAnchors` |
| Serial discovery | `make check CHECK_PARALLEL=0` |

The hosted check job sets `LIBGL_ALWAYS_SOFTWARE=1`, so its render capture gates skip even
when their tools are installed. A green check with those skips does not establish rendered-pixel
equality. The guard is environment-based, not a KWin-version probe: it triggers when
`LIBGL_ALWAYS_SOFTWARE=1`, or when `MESA_LOADER_DRIVER_OVERRIDE` or `GALLIUM_DRIVER` contains
`llvmpipe`, `softpipe`, `swrast` or `zink` (case-insensitive). The skip reason cites a fix in
KWin 6.8, but upgrading KWin alone does not bypass this guard. To exercise the capture gates,
use a GPU-backed host with the documented render tools and without software-forcing variables.
The isolated headless rendering commands remain available under [Rendering a candidate](docs/rendering.md).

The GTK 4 button, notebook, progressbar, scale, indicator, spin-field and view-census probes skip during routine checks. To opt in
without using your desktop display, run each probe under Xvfb:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_button_probe.TestGtk4ButtonProbe.test_button_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_notebook_probe.TestGtk4NotebookProbe.test_notebook_tab_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_progressbar_probe.TestGtk4ProgressbarProbe.test_progressbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scale_probe.TestGtk4ScaleProbe.test_scale_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scrollbar_probe.TestGtk4ScrollbarProbe.test_scrollbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_indicators_probe.TestGtk4IndicatorsProbe.test_mixed_indicators_draw_black_dashes
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_spin_probe.TestGtk4SpinProbe.test_spin_field_renders_the_mirrored_etch_in_rtl
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk_view_census
```

`xvfb-run -a` allocates and cleans up a separate virtual X server. Unsetting inherited
`DISPLAY` and `WAYLAND_DISPLAY` before starting it prevents these commands from selecting the
desktop display. Missing GTK 4 introspection bindings can still cause a probe to skip for lack of
capability; setting the opt-in variable alone does not mean the probe ran.

Reference image validation is separate: see [Validating the reference set](#validating-the-reference-set)
for `make check-references` and its Git LFS materialization requirement.

## Invariants

`docs/invariants.md` states, per `theme/` subsystem and for the fidelity gate, the guarantee a
surface must keep and the test that pins it. Read the matching row before changing a surface, and
update it in the same change when a guarantee moves. `tests/support/invariants.py` keeps the register
and the repository in step.

## Development team

This theme is developed by a tumwater team of AI roles. How many roles run at once is a tumwater
setting, not a file in this repository: `maxConcurrent` in the primary checkout's `tumwater.json`
(alongside any `maxConcurrentPerProvider` cap) is the most model runs in flight across all roles
at once, merges included, with the director's own runs sitting outside it; it defaults to 6. A
role cannot change that concurrency setting, so the operator sets it from the primary checkout, for example
`tumwater config set maxConcurrent 6` (requested 2026-10-18: run six roles at once).

The project check is `make check`, without `CHECK_PATTERN` or `CHECK_TESTS` overrides.
From the primary checkout, operators can inspect the configured check with
`tumwater doctor check --json` (the `check` row should read `ok`) and
`tumwater status --json` (the output should have no `noDeclaredCheck`). If a clone has no
declared check, configure it from the primary checkout with
`tumwater config set check.command 'make check'`.
The separate reference-image validation remains `make check-references`.
