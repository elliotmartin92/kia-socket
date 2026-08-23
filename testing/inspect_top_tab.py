import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon, OUTER_WALL_THICK, SCALE, X0, Y0
import numpy as np

print("--- Top Points in outer_pts (Y > 17.0) ---")
for i, (x, y) in enumerate(outer_pts):
    if y > 17.0:
        print(f"[{i:3d}] X={x:7.3f}, Y={y:7.3f}")

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)
top_coords = coords[coords[:, 1] > 18.0]
print("\n--- Top exterior coords in outer_poly (Y > 18.0) ---")
for x, y in top_coords:
    print(f"  X={x:7.3f}, Y={y:7.3f}")

top_x = top_coords[:, 0]
print(f"\nTop Tab X range: [{np.min(top_x):.3f}, {np.max(top_x):.3f}] mm")
print(f"Top Tab Width in X: {np.max(top_x) - np.min(top_x):.3f} mm")
print(f"Top Tab Center X: {(np.min(top_x) + np.max(top_x))/2.0:.3f} mm")
