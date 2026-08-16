"""
Calculate tower positions using X4 = 5.4mm from Right Inner Wall.
"""
from shapely.geometry import LineString, Point
import numpy as np

from build_part import (
    get_exact_base_polygon, bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_INTERNAL_GAP, TOWER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

# Top-right hole bounds:
hole_x, hole_y, hole_w, hole_h = hole_info
print(f"Top-right hole bounds: X in [{hole_x - hole_w/2:.3f}, {hole_x + hole_w/2:.3f}], Y in [{hole_y - hole_h/2:.3f}, {hole_y + hole_h/2:.3f}]")

# Let's find the inner wall X coordinate at various Y heights around the tower/hole (e.g. Y = 8.5 to 13.0)
for y_test in [8.57, 10.0, 10.826, 12.0, 13.08]:
    ray = LineString([(-5, y_test), (30, y_test)])
    inter_inner = inner_wall_poly.exterior.intersection(ray)
    inter_outer = base_poly.exterior.intersection(ray)
    
    # Get rightmost intersection
    x_inner_right = max(p.x for p in (inter_inner.geoms if hasattr(inter_inner, 'geoms') else [inter_inner]))
    x_outer_right = max(p.x for p in (inter_outer.geoms if hasattr(inter_outer, 'geoms') else [inter_outer]))
    
    x_right_tower_outer = x_inner_right - 5.4
    x_right_tower_inner = x_right_tower_outer - TOWER_WALL_THICK
    x_left_tower_inner = x_right_tower_inner - TOWER_INTERNAL_GAP
    x_left_tower_outer = x_left_tower_inner - TOWER_WALL_THICK
    
    print(f"\nAt Y = {y_test:.3f} mm:")
    print(f"  Outer Wall X: {x_outer_right:.3f} mm, Inner Wall X: {x_inner_right:.3f} mm")
    print(f"  Right Tower X outer: {x_right_tower_outer:.3f} mm, inner: {x_right_tower_inner:.3f} mm")
    print(f"  Left Tower X inner: {x_left_tower_inner:.3f} mm, outer: {x_left_tower_outer:.3f} mm")

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)
print(f"\nBracket 3 X bounds: [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}], center X = {(b3.bounds[0]+b3.bounds[2])/2:.3f}")
print(f"Bracket 4 X bounds: [{b4.bounds[0]:.3f}, {b4.bounds[2]:.3f}], center X = {(b4.bounds[0]+b4.bounds[2])/2:.3f}")
