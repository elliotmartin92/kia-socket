"""
Inspect top wall coordinates at X = 3.24mm and analyze Y position of the cradle with 6.77mm distance.
"""
from shapely.geometry import Point, LineString
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, to_mm_poly, OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
hole_x, hole_y, hole_w, hole_h = hole_info

b3 = to_mm_poly(bracket_3_raw_pts)
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0  # 3.236mm

# Ray from (3.236, 0) straight up in +Y
ray = LineString([(b3_center_x, 0), (b3_center_x, 30)])
inter = base_poly.exterior.intersection(ray)
y_outer_top = inter.y if hasattr(inter, 'y') else max(p.y for p in inter.geoms)
y_inner_top = y_outer_top - OUTER_WALL_THICK

print(f"At X = {b3_center_x:.3f} mm:")
print(f"Outer top wall Y: {y_outer_top:.3f} mm")
print(f"Inner top wall Y: {y_inner_top:.3f} mm")

# Distance 6.77mm from top wall:
y_from_outer = y_outer_top - 6.77
y_from_inner = y_inner_top - 6.77

print(f"If 6.77mm from outer top wall: Y = {y_from_outer:.3f} mm")
print(f"If 6.77mm from inner top wall: Y = {y_from_inner:.3f} mm")
print(f"Top-right hole Y bounds: [{hole_y - hole_h/2:.3f}, {hole_y + hole_h/2:.3f}] (Center Y: {hole_y:.3f} mm)")
print(f"Bracket 3 top edge Y: {b3.bounds[3]:.3f} mm")
