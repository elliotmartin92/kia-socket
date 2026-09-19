import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import build_part
from build_shaft import X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()

print(f"Base poly bounds: {base_poly.bounds}")
print(f"Outer body bounds: {outer_body_poly.bounds}")
print(f"Towers X bounds: [{X_LEFT_TOWER_OUTER}, {X_RIGHT_TOWER_OUTER}], Y span: [6.25, 12.85]")

for angle_deg in build_part.CLIP_ANGLES:
    p, n, t = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    print(f"Clip at {angle_deg:5.1f} deg: pos = ({p[0]:6.2f}, {p[1]:6.2f}), norm = ({n[0]:5.2f}, {n[1]:5.2f})")
