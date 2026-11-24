"""The drawing-element pins for every shipped icon, in document order.

``test_icon_theme_geometry`` imports this package and holds the tests that
compare each shipped SVG with its pinned tuple; the pins live in one module
per icon family -- with the shared drawing-element helpers in ``_shared`` --
so the test module stays readable in one sitting and an icon plan's edit
lands beside its own family's case data. One entry per shipped file: a
tuple of ``_shape`` elements, the tag and attributes of each drawing
element in document order. The icon art
is our own, so nothing else re-derives it; the size, palette and structural
tests in test_icon_theme would all pass if a path's `d`, a rect's geometry,
an element's order or an element's fill changed -- an icon could silently
lose its outline, bevel, plate or ribs -- so pin each element exactly. The
`folder` name owns the pinned folder tuple, and the `inode-directory`,
`user-home` and `user-desktop` aliases share it at every size (Mac OS 8.6
draws one folder for a directory); the alias test in
``test_icon_theme_geometry`` cross-checks the files themselves.

The registry is one dict per icon family, mirroring the shipped tree's
family directories; a family that outgrows one module becomes a package of
per-series group modules merged by its own ``__init__`` (the mimetypes
family does). ``SHAPE_PIN_FAMILIES`` names them so the guard tests
can visit every family module. This package merges them into one
``ICON_SHAPES`` dict beside the inventory it pins.
"""

from support.icon.shape_pins.actions import PINS as _ACTIONS
from support.icon.shape_pins.devices import PINS as _DEVICES
from support.icon.shape_pins.mimetypes import PINS as _MIMETYPES
from support.icon.shape_pins.places import PINS as _PLACES

SHAPE_PIN_FAMILIES = ("actions", "devices", "mimetypes", "places")

ICON_SHAPES = {**_ACTIONS, **_DEVICES, **_MIMETYPES, **_PLACES}
