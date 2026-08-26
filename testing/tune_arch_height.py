"""
testing/tune_arch_height.py
"""
import os
import sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
t_half = SHEET_THICK / 2.0
r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
rear_poly = Polygon(r_poly_pts)
f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
front_poly = Polygon(f_poly_pts)

r_hub = HUB_DIAMETER / 2.0

for lip_z in [16.8, 17.2, 17.5]:
    poly_pts = [
        (Y_AXLE, Z_AXLE + r_hub),     # (9.28, 14.69)
        (6.80, lip_z + 0.6),
        (4.20, lip_z + 0.8),
        (2.00, lip_z + 0.2),
        (1.45, 13.00),                 # Nose tip
        (2.05, 12.80),
        (2.20, 13.40),
        (2.20, lip_z - 0.5),          # Rising inside funnel
        (4.20, lip_z),                # Over the lip
        (6.80, lip_z - 1.2),
        (Y_AXLE - 1.20, Z_AXLE + 1.00),
        (Y_AXLE - 1.50, Z_AXLE)
    ]
    cam_poly = np.array(poly_pts)
    
    min_r = 999
    min_f = 999
    print(f"\n--- Testing lip_z = {lip_z:.1f} mm ---")
    for ang in range(0, 11):
        rad = np.radians(ang)
        c_a, s_a = np.cos(rad), np.sin(rad)
        vecs = cam_poly - np.array([Y_AXLE, Z_AXLE])
        p_rot = np.zeros_like(cam_poly)
        p_rot[:, 0] = Y_AXLE + c_a * vecs[:, 0] - s_a * vecs[:, 1]
        p_rot[:, 1] = Z_AXLE + s_a * vecs[:, 0] + c_a * vecs[:, 1]
        
        pgr = Polygon(p_rot)
        dr = pgr.distance(rear_poly)
        df = pgr.distance(front_poly)
        min_r = min(min_r, dr)
        min_f = min(min_f, df)
        if ang in [0, 3, 6, 9]:
            print(f"  theta = {ang:2d} deg: Rear = +{dr:.3f} mm, Front = +{df:.3f} mm")
    print(f"  >> ALL-ANGLE MIN: Rear = +{min_r:.3f} mm, Front = +{min_f:.3f} mm")
