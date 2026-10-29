# Placeholders

Temporary stand-in assets shipped so the theme's plumbing works end to end. Each
is our own generic art, not a reproduction of Apple's Platinum artwork (see the
2026-10-18 answer in QUESTIONS.md). A placeholder asset carries a `PLACEHOLDER:`
comment marker naming what it stands in for; `tests/support/placeholders.py`
cross-checks this table against those markers, so a new placeholder added
without a row fails `make check`.

**Decision 2026-10-29, recorded by the director role:** The user requires original
placeholder graphics for now. This supersedes the earlier designation of the icon
art as final. The queued Platinum graphics plans in PLANS.md restore per-asset
tracking and replace the reference-cropped wallpaper.

| Placeholder | Stands in for |
| --- | --- |
| `theme/wallpapers/org.macos8.desktop/metadata.json` | original neutral stand-in pending user-approved artwork. |
| `theme/look-and-feel/org.macos8.desktop/contents/splash/images/macos-logo.svg` | original geometric startup logo pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder.svg` | original generic folder illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` | original submenu-arrow illustration pending user-approved artwork. |
