# Principles — rationale and provenance

Long-form record behind `PRINCIPLES.md`. The principles file is injected into every role's prompt
and stays bullet-only; the reasoning, recordings and user directions that produced each bullet
live here. Keep this file in sync when a principle is added, tightened or retired.

## Standing rules for editing PRINCIPLES.md

- Only the director and steward roles may edit it.
- Phrase new principles positively: state what to do, not what to avoid.
- The list is a starting point that the director and steward own and tune to this project.
- State the directing role and date in the bullet; put the full rationale here.

## Recording format

Append one section per principle, oldest decisions intact:

```
## <short principle name>
Recorded: <date>, by <role>, directed by <user|role>.
Decision text as originally recorded: <verbatim>
Consequence notes: <what it supersedes, what stays eligible>
```

## History

### 2026-11-09 — Routine checks stay off the user's desktop

Original recording: "Keep routine checks quiet on the user's desktop: run GUI probes on an
isolated, non-visible display, or reserve them for explicitly requested occasional runs. Routine
tests must preserve the user's focus and must not present windows on their session. (Directed by
the user 2026-11-09; recorded by the director role.)"

### 2026-11-04 — Keyboard mappings belong to the user

Original recording: "Preserve the user's keyboard mappings when installing or applying Platinum.
Keyboard remapping is outside the theme's scope; remove the shipped modifier-swap feature.
(Directed by the user 2026-11-04; recorded by the director role.)"

### 2026-11-02 — SIGKILL recovery is an accepted Won't Fix

Original recording: "Treat recovery and cleanup after SIGKILL as an accepted Won't Fix limitation
across the project. Roles should close reports whose sole failure requires SIGKILL as covered by
this decision, rather than file duplicates, plan recovery machinery, or reopen them without a new
user direction. Preserve existing guarantees for ordinary failures and catchable signals; bugs
reproducible without SIGKILL remain eligible for triage. The accepted limitation includes partial
publication across files and leftover temporary or backup files after SIGKILL. (Directed by the
user 2026-11-02; recorded by the director role.)"

See `BUGS.md` for the report closed under this decision.

### 2026-10-29 — Platinum branding and placeholder artwork

Original recording: "Present the theme as 'Platinum' using oblique references and original
placeholder graphics for now. Keep Apple graphical assets, logos, and Apple trademarked names or
phrases (including 'MacOS', 'Mac OS' and 'Apple') out of theme-owned UI labels and artwork. Track
placeholder artwork in PLACEHOLDERS.md until the user approves replacement work. Reference
screenshots serve as measurement evidence, never as shipped graphical assets; this constraint
takes precedence over pixel fidelity. Historical provenance and internal compatibility identifiers
are distinct from UI branding; give selectors neutral display names. (Directed by the user
2026-10-29; recorded by the director role.)"

### 2026-10-25 — Reference-derived visual values

Original recording: "Ground each visual value in the reference screenshots: sample palette and
metric values from a lossless image, pin each with a test that re-derives that pixel, and record
the provenance of any platform-required value the reference set does not show (including KDE, GTK
and Firefox). For such adaptations, name the missing reference surface and the source of the
chosen value. (Clarified 2026-10-25 by the steward role for the GTK and Firefox scope approved in
QUESTIONS.md.)"

### 2026-10-30 — Ship widget art at its drawn size

Original recording: "Ship widget art at exactly the size the engine draws it: first try steering
the engine to render at the design's native size (an explicit size setting matching the art's
canvas, as in the Kvantum config's `indicator.size`), so shipped art draws 1:1; only when the
engine cannot be steered do this the other way round — re-derive the art at the size the engine
actually draws and record the resized cell's deviation from the reference. Never leave shipped art
somewhere the engine resamples it. (Directed by the user 2026-10-30; recorded by the director
role.)"

### 2026-11-04 — Unfocused windows match the reference set

Original recording: "Draw unfocused windows exactly as the reference set's unfocused windows
appear: one active window (the frontmost one), every other window inactive with a flat bar and no
title-bar boxes, and no separate focus look. Platinum's model is active=frontmost; KWin already
realizes it, so emulating it needs no focus machinery — only the inactive decoration art.
(Directed by the user 2026-11-04; recorded by the director role.)"
