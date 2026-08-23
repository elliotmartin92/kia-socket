import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon
import numpy as np

print("Total points in outer_pts:", len(outer_pts))

# Check Right side points (X > 16.0)
print("\n--- Right side points (X > 16.0) ---")
for i, (x, y) in enumerate(outer_pts):
    if x > 16.0:
        print(f"[{i:3d}] X={x:7.3f}, Y={y:7.3f}")

# Check Left side points (X < -16.0)
print("\n--- Left side points (X < -16.0) ---")
for i, (x, y) in enumerate(outer_pts):
    if x < -16.0:
        print(f"[{i:3d}] X={x:7.3f}, Y={y:7.3f}")
