import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import outer_pts, get_exact_base_polygon, OUTER_WALL_THICK
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

def update_ears_in_pts(pts_in, ear_width=8.20):
    half_w = ear_width / 2.0
    pts = pts_in.copy()
    
    # 1. Right Ear (indices 0..4, 242..243)
    # Original Right ear:
    # [  0] X= 18.206, Y=  4.442
    # [  1] X= 20.200, Y=  4.442
    # [  2] X= 20.200, Y= -0.000
    # [  3] X= 20.200, Y= -4.442
    # [  4] X= 18.206, Y= -4.442
    pts[0] = [18.206, half_w]
    pts[1] = [20.200, half_w]
    pts[2] = [20.200, 0.0]
    pts[3] = [20.200, -half_w]
    pts[4] = [18.206, -half_w]
    if len(pts) > 242:
        pts[242] = [18.206, half_w]
        pts[243] = [18.206, half_w]
        
    # 2. Left Ear (indices 111..139)
    # Original Left ear:
    # [111] X=-19.081, Y=-4.407
    # [136] X=-21.075, Y=-4.407
    # [137] X=-21.075, Y= 0.035
    # [138] X=-21.075, Y= 4.477
    # [139] X=-19.081, Y= 4.477
    pts[111] = [-19.081, -half_w]
    for k in range(112, 136):
        pts[k] = [-21.075, -half_w]
    pts[136] = [-21.075, -half_w]
    pts[137] = [-21.075, 0.0]
    pts[138] = [-21.075, half_w]
    pts[139] = [-19.081, half_w]
    
    return pts

# Test with 8.30mm and 8.20mm
for w in [8.30, 8.20, 8.10]:
    pts_mod = update_ears_in_pts(outer_pts, w)
    poly = Polygon(pts_mod)
    print(f"Ear width = {w:.2f}mm: Polygon is valid = {poly.is_valid}, Area = {poly.area:.3f} mm²")
    inner = poly.buffer(-OUTER_WALL_THICK)
    print(f"  Inner buffer is valid = {inner.is_valid}, Area = {inner.area:.3f} mm²")

