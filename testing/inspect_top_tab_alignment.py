import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, X0, Y0, SCALE
import numpy as np

print("Raw SVG points around top tab:")
for idx in range(185, 198):
    x, y = outer_pts[idx]
    print(f"Index {idx:3d}: X = {x:7.3f}, Y = {y:7.3f}")

print(f"\nTab Left: X = {outer_pts[190][0]:.3f}")
print(f"Tab Right: X = {outer_pts[191][0]:.3f}")
print(f"Tab Center: X = {(outer_pts[190][0] + outer_pts[191][0])/2.0:.3f}")
print(f"Tab Width: {outer_pts[191][0] - outer_pts[190][0]:.3f}")
