"""SVG inspection helpers shared by the desktop theme test modules.

Test-only: parses the theme's nine-slice SVGs and reads their ids, hints,
transforms and composited pixels, so each widget's test module states only the
artwork it pins instead of re-deriving the KSvg layout rules.

The helpers are split by concern and re-exported here, so a test module
imports every helper from ``svg_assertions`` regardless of which submodule
defines it: ``tree`` traverses the parsed document and reads its attributes,
``safety`` guards the artwork a pixel test cannot see, ``render`` composites a
nine-slice group into pixels, ``geometry`` holds the face, path and nine-slice
arithmetic, and ``checks`` holds the pixel and layout assertions.
"""

from __future__ import annotations

from .tree import (
    SLICE_IDS,
    _numeric_attribute,
    assert_ids_present,
    assert_slice_ids_present,
    attribute_values,
    children_named,
    elements_by_id,
    groups_with_id,
    local_name,
)

from .safety import (
    _URL_REFERENCE,
    _local_attribute_name,
    _url_targets,
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
)

from .render import (
    _slice_extent,
    _slice_offset,
    _slice_where,
    pixel_map,
    render_slices,
)

from .geometry import (
    RAISED_FACE_CORNERS,
    _PATH_COMMAND,
    _PATH_COMMAND_ARITY,
    _PATH_LETTER,
    _SUPPORTED_PATH_COMMANDS,
    _TRANSLATE,
    _circle_dimension,
    _path_commands,
    _rect_dimension,
    _require_known_bevel,
    _state_margin_hints,
    arc_center,
    circle_geometry,
    circle_geometry_and_fill,
    face_corners,
    face_edge_bands,
    flat_face_corners,
    nine_slice_hint_geometry,
    nine_slice_margins,
    nine_slice_tile_sizes,
    path_arcs,
    rect_geometry,
    sunken_face_corners,
    tile_origins,
)

from .checks import (
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_hint_geometry,
    assert_root_canvas,
    assert_slice_pixels,
    assert_slices_fill_their_tiles,
    assert_slices_stay_within_their_tiles,
    assert_slices_uniform,
    assert_tiles_placed_by_margins,
)

