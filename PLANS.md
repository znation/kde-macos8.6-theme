# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-18 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-three widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document and
Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic`, our own mark rather than
Apple's; `PLACEHOLDERS.md` is empty); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-18 by the plan
role): a **Qt widget style** for KDE applications (the desktop theme styles only Plasma shell
widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

### Checker unreadable-input mutations: manufacture a register, asset or reference that cannot be read so the checker's own diagnostic is observable (planned 2026-10-19 by the steward role; from the recurring `no-fake` validation gap in four Fixed entries)

**Goal.** Four Fixed entries share one shape: a record checker reads an input that cannot be read
-- a register path that is a directory, a text asset under `theme/` that is a dangling symlink
resolving inside the root, a register reference containing a NUL byte, or a reference to a test
file that cannot be decoded -- and the read raises a bare `OSError`/`ValueError` that names
neither the checker nor the offending row, aborting the check with an unrelated traceback. Each
was confirmed only by hand-building a shim the suite did not have (its `no-fake` gap).
`tests/support/checker_mutations.py` already manufactures the malformed register and theme inputs
the shipped data never holds; extend it with the four unreadable-input shapes so confirming the
next bug of this kind reuses the scratch fixture instead of a one-off.

**From (the `no-fake` Fixed entries).**
- `tests/placeholders.py` lets an unreadable register escape as a bare `OSError`.
- `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare
  `FileNotFoundError`.
- `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception.
- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated
  exception.

**Approach.**
- `tests/support/checker_mutations.py`: teach `Scratch` to clean up a directory it wrote (its
  `reset` only unlinks files today), then add four `Mutation` entries: `unreadable-register`
  (replace the register path with a directory so `register_entries`' `OSError` arm fires;
  diagnostic `cannot be read`), `dangling-symlink-inside-theme` (a text asset under `theme/`
  symlinked to a missing path inside the root; diagnostic `cannot be read`),
  `reference-with-nul-byte` (`_replace_first_reference` with a `\x00` in the path; diagnostic
  `NUL byte`), and `unreadable-test-file` (point the first row's reference at a scratch file
  written as undecodable bytes; diagnostic `cannot be read as Python`).
- `tests/placeholders.py` and `tests/invariants.py`: add each new name to `REJECTION_SHAPES` in
  the same commit, so `test_checker_mutations.py`'s two set-equality guards keep each checker's
  boundary list and the mutation table in step.

**Files touched.** `tests/support/checker_mutations.py`, `tests/placeholders.py`,
`tests/invariants.py`.

**Acceptance criteria.**
- `tests/test_checker_mutations.py` drives each of the four new mutations, and each makes its
  checker raise the named `AssertionError`; the two unreadable-read mutations fail if the
  checker's `OSError` arm is removed.
- The two `REJECTION_SHAPES` set-equality guards pass with the four new names.
- `make check` is green.

## Done
