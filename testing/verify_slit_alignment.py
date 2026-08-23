"""
Verify exact alignment of slits with bracket walls.
"""
from shapely.geometry import Polygon, box
import numpy as np

SCALE = 8.22 / 23.5
X0 = 128.65
Y0 = 124.20

# Bracket 1 (leftmost)
bracket_1_raw_pts = [
    (97.8, 103.8), (106.2, 103.8), (106.2, 111.1), (103.4, 111.1),
    (103.4, 106.9), (100.9, 106.9), (100.9, 141.6), (105.8, 141.6),
    (105.8, 144.7), (97.8, 144.7), (97.8, 103.8)
]

# Bracket 4 (rightmost)
bracket_4_raw_pts = [
    (159.5, 103.7), (151.1, 103.7), (151.1, 111.1), (154.0, 111.1),
    (154.0, 106.8), (156.4, 106.8), (156.4, 141.5), (151.6, 141.5),
    (151.6, 144.6), (159.5, 144.6), (159.5, 103.7)
]

b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]

b1_poly = Polygon(b1_pts)
b4_poly = Polygon(b4_pts)

b1_rightmost_x = max(p[0] for p in b1_pts)
b4_leftmost_x = min(p[0] for p in b4_pts)

print(f"Bracket 1 (leftmost bracket) rightmost X: {b1_rightmost_x:.3f} mm")
print(f"Bracket 4 (rightmost bracket) leftmost X:  {b4_leftmost_x:.3f} mm")

SLIT_W_X = 1.10
SLIT_LEN_Y = 3.00
SLIT_Y_TOP = -7.20 - 4.22 # -11.42 mm
SLIT_Y_BOT = SLIT_Y_TOP - SLIT_LEN_Y # -14.42 mm

# Left Slit: right wall aligns with Bracket 1 rightmost X
left_slit_x_max = b1_rightmost_x
left_slit_x_min = left_slit_x_max - SLIT_W_X

# Right Slit: left wall aligns with Bracket 4 leftmost X
right_slit_x_min = b4_leftmost_x
right_slit_x_max = right_slit_x_min + SLIT_W_X

print(f"\nLeft Slit X range:  [{left_slit_x_min:.3f}, {left_slit_x_max:.3f}] mm (Right edge = {left_slit_x_max:.3f} mm)")
print(f"Right Slit X range: [{right_slit_x_min:.3f}, {right_slit_x_max:.3f}] mm (Left edge = {right_slit_x_min:.3f} mm)")
print(f"Slit Y range:       [{SLIT_Y_BOT:.3f}, {SLIT_Y_TOP:.3f}] mm")
