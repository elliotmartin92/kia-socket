"""
Inspect the side ear / inset side wall coordinates in SVG and mm.
"""
import numpy as np
import re
from build_part import outer_pts, SCALE, X0, Y0

# In SVG outer_pts, let's find the left and right side features:
pts = outer_pts.copy()

print("Points on Right Side (X > 17mm):")
for idx, (x, y) in enumerate(pts):
    if x > 17.0:
        print(f"  Index {idx:2d}: X = {x:7.3f}, Y = {y:7.3f}")

print("\nPoints on Left Side (X < -17mm):")
for idx, (x, y) in enumerate(pts):
    if x < -17.0:
        print(f"  Index {idx:2d}: X = {x:7.3f}, Y = {y:7.3f}")
