"""
testing/debug_rear_gap.py
"""
import os
import sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import nearest_points

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
poly_pts = [
    (Y_AXLE, Z_AXLE + r_hub),     # (9.28, 14.69)
    (6.80, 16.80),
    (4.20, 17.20),
    (2.00, 16.50),
    (1.45, 13.00),                 # Nose tip (blade contact)
    (2.05, 12.80),                 # Nose bottom
    (2.35, 13.40),                 # Nose rear in upper funnel
    (2.35, 15.80),                 # Going UP inside funnel before crossing!
    (4.50, 16.30),                 # Over the lip (clearing 15.40 by 0.90 mm!)
    (6.80, 15.00),
    (Y_AXLE - 1.20, Z_AXLE + 1.00),
    (Y_AXLE - 1.50, Z_AXLE)
]
cam_poly = np.array(poly_pts)
pg = Polygon(cam_poly)

print("Intersection with rear_poly:", pg.intersects(rear_poly))
print(f"Clearance at 0 deg: Rear = +{pg.distance(rear_poly):.3f} mm, Front = +{pg.distance(front_poly):.3f} mm")

print("\nRotation Clearance Audit (0 to 10 deg):")
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
    print(f"  theta = {ang:2d} deg: Rear Gap = +{dr:.3f} mm, Front Gap = +{df:.3f} mm")
