import sys
sys.path.insert(0, '.')
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
import build_part
from build_part import get_exact_base_polygon, OUTER_WALL_THICK
import build_clamp

base_poly, outer_body_poly, _ = get_exact_base_polygon()

cx, cy = -0.166, 0.298
r_safe = 18.80

pts = build_part.outer_pts[(build_part.outer_pts[:, 0] > 10) & (build_part.outer_pts[:, 1] > 4)]
dists = np.sqrt((pts[:, 0] - cx)**2 + (pts[:, 1] - cy)**2)
print("Min radius of actual outer wall from (cx, cy):", dists.min())
print("Max radius of actual outer wall from (cx, cy):", dists.max())
print(f"Margin between r_safe={r_safe} and min wall radius: {dists.min() - r_safe:.3f} mm")
