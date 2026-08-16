"""
Inspect geometry of right bracket pair and top-right hole to analyze shaft support positioning.
"""
from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, SCALE, X0, Y0
)

b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
hole_x, hole_y, hole_w, hole_h = hole_info

print(f"Bracket 3 bounds (X_min, Y_min, X_max, Y_max): {b3.bounds}")
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0
b3_spine_x = b3.bounds[0] + 0.5  # Left spine
print(f"Bracket 3 center X: {b3_center_x:.3f} mm, bounds: [{b3.bounds[0]:.3f}, {b3.bounds[2]:.3f}]")

print(f"Bracket 4 bounds: {b4.bounds}")
b4_center_x = (b4.bounds[0] + b4.bounds[2]) / 2.0
print(f"Bracket 4 center X: {b4_center_x:.3f} mm, bounds: [{b4.bounds[0]:.3f}, {b4.bounds[2]:.3f}]")

print(f"Top-right hole: center=({hole_x:.3f}, {hole_y:.3f}), size=({hole_w:.3f}, {hole_h:.3f})")
print(f"Hole X range: [{hole_x - hole_w/2:.3f}, {hole_x + hole_w/2:.3f}]")
print(f"Hole Y range: [{hole_y - hole_h/2:.3f}, {hole_y + hole_h/2:.3f}]")
