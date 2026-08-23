import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    outer_pts, OUTER_WALL_THICK, SCALE, X0, Y0,
    bracket_1_raw_pts, bracket_4_raw_pts, SLIT_OFFSET_FROM_WALL,
    SLIT_LEN_Y, SLIT_W_X, SOCKET_W_X, SOCKET_LEN_Y
)
from shapely.geometry import Polygon, box
import numpy as np

EAR_GAP = 8.30
EAR_CLEARANCE = 0.10
EAR_WIDTH_Y = EAR_GAP - EAR_CLEARANCE # 8.20mm
half_w = EAR_WIDTH_Y / 2.0 # 4.10mm

pts = outer_pts.copy()

# Right ear
pts[0] = [18.206, half_w]
pts[1] = [20.200, half_w]
pts[2] = [20.200, 0.0]
pts[3] = [20.200, -half_w]
pts[4] = [18.206, -half_w]
if len(pts) > 242:
    pts[242] = [18.206, half_w]
    pts[243] = [18.206, half_w]

# Left ear
pts[111] = [-19.081, -half_w]
for k in range(112, 136):
    pts[k] = [-21.075, -half_w]
pts[136] = [-21.075, -half_w]
pts[137] = [-21.075, 0.0]
pts[138] = [-21.075, half_w]
pts[139] = [-19.081, half_w]

# Bottom notch
for idx, (x, y) in enumerate(pts):
    if abs(y - (-18.539)) < 0.05:
        if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
            pts[idx] = [2.50, -18.539]
        elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
            pts[idx] = [-2.50, -18.539]
    elif abs(y - (-16.650)) < 0.05:
        if abs(x - 1.382) < 0.05 or abs(x - 3.70) < 0.05:
            pts[idx] = [2.50, -16.650]
        elif abs(x - (-2.291)) < 0.05 or abs(x - (-3.70)) < 0.05:
            pts[idx] = [-2.50, -16.650]

raw_poly = Polygon(pts)
print("Is valid:", raw_poly.is_valid)
print("Bounds:", raw_poly.bounds)

# Measure right ear width in Y:
r_pts = [p for p in raw_poly.exterior.coords if p[0] > 18.5]
r_y = [p[1] for p in r_pts]
print(f"Right ear outer face Y min: {min(r_y):.3f}, max: {max(r_y):.3f}, width: {max(r_y) - min(r_y):.3f} mm")

# Measure left ear width in Y:
l_pts = [p for p in raw_poly.exterior.coords if p[0] < -19.5]
l_y = [p[1] for p in l_pts]
print(f"Left ear outer face Y min: {min(l_y):.3f}, max: {max(l_y):.3f}, width: {max(l_y) - min(l_y):.3f} mm")
