"""Pins for the mimetypes family: the generic file-type icons and the
per-type exact-name drawings the file types resolve to.

Every entry is a ``os.path.join(size, "mimetypes", name.svg)`` key holding
the pinned tuple of drawing elements for that shipped file, in document
order. The pins live beside ``theme_inventory``; the geometry tests in
``test_icon_theme_geometry`` compare each shipped SVG with its tuple.

The family's pins live in one group module per icon series (documents,
executables, archives, media, certificates, disks); this ``__init__``
merges them into the family ``PINS`` the same way ``shape_pins/__init__``
merges the families into ``ICON_SHAPES``.
"""

from support.icon.shape_pins.mimetypes.archives import PINS as _ARCHIVES
from support.icon.shape_pins.mimetypes.certificates import PINS as _CERTIFICATES
from support.icon.shape_pins.mimetypes.disks import PINS as _DISKS
from support.icon.shape_pins.mimetypes.documents import PINS as _DOCUMENTS
from support.icon.shape_pins.mimetypes.executables import PINS as _EXECUTABLES
from support.icon.shape_pins.mimetypes.media import PINS as _MEDIA

PINS = {
    **_ARCHIVES,
    **_CERTIFICATES,
    **_DISKS,
    **_DOCUMENTS,
    **_EXECUTABLES,
    **_MEDIA,
}
