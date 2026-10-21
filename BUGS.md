# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The lock screen clock is blurred by the Breeze clock's hardcoded drop shadow (found by the director role 2026-10-21)

**Refused 2026-10-21 by bugfix: removing the shadow needs a project-owned lock-screen QML override (a Plasma-version-fragile new surface) that the open question in QUESTIONS.md leaves to the user, so it is not a bugfix.**

**Symptom:** in the supplied photo `/home/zach/Downloads/IMG_6808.heic` (3840x2160, display
scale 1.5), the KDE screen's time (`9:43 PM`) and date (`Monday, October 19, 2026`) have a soft
dark halo and look blurred, while `Zach Nation`, the `Password` placeholder and the
`Sleep`/`Switch User` labels are crisp. The reply called this the login screen, but the reveal
eye inside the password field and the separate arrow unlock button identify Plasma's lock screen
(`kscreenlocker`): Breeze's SDDM `Login.qml` sets `rightActions: []` and draws no reveal eye.

**Reproduction:** lock a Plasma 6 session using the Breeze lock screen and look at the clock;
`kscreen-doctor -o` on this machine reports a 2560x1440 logical geometry at scale 1.5, so the
shadow below is drawn at 9 device pixels. The supplied image is a phone photograph, not a
lossless screenshot, so it is evidence rather than a reference surface.

**Suspected cause:** `LockScreenUi.qml` (under
`/usr/share/plasma/shells/org.kde.plasma.desktop/contents/lockscreen/`) draws a
`DropShadow` behind its `Clock` with `radius: 6`, `samples: 14`, `spread: 0.3` and
`color: "black"`. The clock itself is `org.kde.breeze.components/Clock.qml`, whose two
`PlasmaComponents3.Label`s use plain text at `Math.round(defaultFont.pointSize * 4.8)` for the
time and `* 2.4` for the date; the username sits one point above the body font and has no
shadow. The themed surfaces in `theme/` cannot change this: the clock is shell QML, not a
desktop-theme widget, and the lock screen's `config.xml` exposes only `alwaysShowClock` — there
is no shadow setting.

**Suggested direction:** report the optional-or-removed shadow upstream and document the
limitation instead of copying the Plasma shell package into the repo. A project-owned lock
screen is a new, Plasma-version-fragile surface and needs its own plan and the user's decision;
it is not a bugfix.

## Fixed
