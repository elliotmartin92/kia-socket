import os, sys
import numpy as np
from shapely.geometry import Polygon, Point
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

reinf_pts = [
    (y_axle, z_axle),
    (y_axle, z_axle + r_hub),
    (8.20, z_axle + r_hub - 0.20),   # (8.20, 13.090)
    (6.80, 11.60),                   # (6.80, 11.600)
    (5.00, 9.20),
    (1.50, 7.40),
    (1.80, 5.10),
    (4.50, 5.30),
    (7.50, 8.40),
    (y_axle, z_axle - r_hub)
]

cam_poly_0 = Polygon(reinf_pts)

front_pts, rear_pts, y_c = get_brass_contact_2d_profile()
t_half = SHEET_THICK / 2.0
f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]

front_poly = Polygon(f_poly_pts)
rear_poly = Polygon(r_poly_pts)

print("Checking clearance against brass contact leaves during rotation 0 to 15 deg:")
for theta in [0, 2, 4, 6, 8, 10, 12, 14]:
    rad = np.radians(theta)
    c, s = np.cos(rad), np.sin(rad)
    
    rot_pts = []
    for cy, cz in reinf_pts:
        dy, dz = cy - y_axle, cz - z_axle
        rot_pts.append((y_axle + c * dy - s * dz, z_axle + s * dy + c * dz))
        
    cam_poly = Polygon(rot_pts)
    
    f_inter = cam_poly.intersects(front_poly)
    r_inter = cam_poly.intersects(rear_poly)
    dist_f = cam_poly.distance(front_poly)
    dist_r = cam_poly.distance(rear_poly)
    
    print(f"theta = {theta:4.1f}° | Front Intersect: {f_inter} (dist={dist_f:.2f}mm) | Rear Intersect: {r_inter} (dist={dist_r:.2f}mm)")
