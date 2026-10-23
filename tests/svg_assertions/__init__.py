"""SVG inspection helpers shared by the desktop theme test modules.

Test-only: parses the theme's nine-slice SVGs and reads their ids, hints,
transforms and composited pixels, so each widget's test module states only the
artwork it pins instead of re-deriving the KSvg layout rules.

The helpers are split by concern and re-exported here, so a test module
imports every public helper from ``svg_assertions`` regardless of which submodule
defines it: ``tree`` traverses the parsed document and reads its attributes,
``safety`` guards the artwork a pixel test cannot see, ``render`` composites a
nine-slice group into pixels and builds the expected-slice maps, ``faces``,
``paths``, ``elements`` and ``nine_slice`` hold the face, path, element and
nine-slice arithmetic, and ``pixels`` and ``layout`` hold the pixel-comparison
and the id, layout and arc assertions.
"""

from __future__ import annotations

from .tree import (
    SLICE_IDS,
    attribute_values,
    children_named,
    elements_by_id,
    groups_with_id,
    local_name,
)

from .safety import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
)

from .render import (
    _MAX_RENDERED_PIXELS,
    bevel_corner_maps,
    bevel_edge_maps,
    corner_map,
    edge_map,
    pixel_map,
    render_slices,
)

from .faces import (
    RAISED_FACE_CORNERS,
    face_corners,
    face_edge_bands,
    flat_face_corners,
    sunken_face_corners,
    sunken_outside_face_corners,
)

from .paths import (
    arc_center,
    path_arcs,
)

from .elements import (
    circle_geometry,
    circle_geometry_and_fill,
    rect_geometry,
)

from .nine_slice import (
    nine_slice_hint_geometry,
    nine_slice_inset_hints,
    nine_slice_margins,
    nine_slice_tile_sizes,
    tile_origins,
)

from .layout import (
    assert_arcs_share_center,
    assert_bounds_rect,
    assert_diagonal_half_disc,
    assert_hint_geometry,
    assert_ids_present,
    assert_root_canvas,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
)

from .pixels import (
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_edge_bevels,
    assert_face_bevel,
    assert_face_corners,
    assert_slice_pixels,
    assert_slices_fill_their_tiles,
    assert_slices_have_no_fill,
    assert_slices_uniform,
    assert_sunken_outside_field,
)
