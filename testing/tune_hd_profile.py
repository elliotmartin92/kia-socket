"""
testing/tune_hd_profile.py
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

poly_pts_hd = [
    # Hub barrel top connection (solid blend)
    (Y_AXLE, Z_AXLE + r_hub),          # (9.28, 14.69)
    (7.20, 18.50),
    (4.50, 19.80),                     # Top arch summit (Z = 19.80 mm)
    (1.80, 18.60),
    (0.80, 16.20),
    (0.80, 13.00),                     # Sturdy front contact face
    (1.45, 12.00),                     # Rounded contact nose apex
    (2.10, 12.60),                     # Deep structural wedge underside
    (2.10, 16.20),                     # Rising vertically inside funnel (Y=2.10 < Y_rear=3.60)
    (4.20, 17.20),                     # Arch underside (clearing 15.40 mm lip by 1.80 mm!)
    (6.80, 15.50),
    (Y_AXLE - 1.20, Z_AXLE + 1.20),    # Solid hub root blend
    (Y_AXLE - 1.80, Z_AXLE)
]

cam_poly_hd = np.array(poly_pts_hd)
pg = Polygon(cam_poly_hd)
print("Intersection with rear_poly:", pg.intersects(rear_poly))
print(f"Clearance at 0 deg: Rear = +{pg.distance(rear_poly):.3f} mm, Front = +{pg.distance(front_poly):.3f} mm")

print("\nRotation Clearance Audit (0 to 10 deg):")
min_r = 999
min_f = 999
for ang in range(0, 11):
    rad = np.radians(ang)
    c_a, s_a = np.cos(rad), np.sin(rad)
    vecs = cam_poly_hd - np.array([Y_AXLE, Z_AXLE])
    p_rot = np.zeros_like(cam_poly_hd)
    p_rot[:, 0] = Y_AXLE + c_a * vecs[:, 0] - s_a * vecs[:, 1]
    p_rot[:, 1] = Z_AXLE + s_a * vecs[:, 0] + c_a * vecs[:, 1]
    
    pgr = Polygon(p_rot)
    dr = pgr.distance(rear_poly)
    df = pgr.distance(front_poly)
    min_r = min(min_r, dr)
    min_f = min(min_f, df)
    print(f"  theta = {ang:2d} deg: Rear Gap = +{dr:.3f} mm, Front Gap = +{df:.3f} mm")

print(f"\n>> ALL-ANGLE MIN: Rear = +{min_r:.3f} mm, Front = +{min_f:.3f} mm")
print(f">> Beam thickness at arch summit: Z_top - Z_bot = 19.80 - 17.20 = {19.80 - 17.20:.2f} mm solid plastic!")
