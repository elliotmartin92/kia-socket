import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, CLIP_ARM_WIDTH, CLIP_ANGLES
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import matplotlib.pyplot as plt

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

# Let's inspect the perimeter between Right Ear and Bottom-Right Tab:
# Right Ear bottom corner:
# Right ear has X = 18.206 to 20.200, Y in [-4.10, +4.10].
# Bottom edge of right ear is at Y = -4.10mm.
# The perimeter curve starts at (18.206, -4.100) and curves down to the bottom-right tab.
# Bottom-right tab starts around (9.6, -15.8) or where the wall drops straight down to Y = -18.539.

print("--- Perimeter vertices in bottom-right quadrant (X > 0, Y < -4.0) ---")
br_pts = []
for idx, (x, y) in enumerate(coords):
    if x > 0 and y < -4.0:
        print(f"[{idx:3d}] X={x:7.3f}, Y={y:7.3f}")
        br_pts.append((x, y))

print("\n--- Perimeter vertices in bottom-left quadrant (X < 0, Y < -4.0) ---")
bl_pts = []
for idx, (x, y) in enumerate(coords):
    if x < 0 and y < -4.0:
        print(f"[{idx:3d}] X={x:7.3f}, Y={y:7.3f}")
        bl_pts.append((x, y))
