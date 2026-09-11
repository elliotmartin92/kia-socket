"""
testing/verify_brass_contact_vs_cam_stroke.py
Checks if the rotating cam collides with the brass contact spring leaves during rotation.
"""

import os
import sys
import numpy as np
from shapely.geometry import Polygon, Point, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

def run():
    print("=== CAM ROTATION VS BRASS CONTACT LEAVES ===")
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    t_half = SHEET_THICK / 2.0
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    
    front_poly = Polygon(f_poly_pts)
    rear_poly = Polygon(r_poly_pts)
    
    r_hub = HUB_DIAMETER / 2.0
    poly_pts_cam = [
        (Y_AXLE, Z_AXLE),
        (Y_AXLE, Z_AXLE + r_hub + 0.5),
        (5.00, 9.80),
        (1.50, 7.20),
        (1.80, 5.00),
        (4.50, 5.20),
        (Y_AXLE - 1.50, Z_AXLE - 2.50)
    ]
    
    for theta in [0, 2, 4, 6, 8, 10, 12, 14]:
        rad = np.radians(theta)
        c, s = np.cos(rad), np.sin(rad)
        
        rot_pts = []
        for cy, cz in poly_pts_cam:
            dy, dz = cy - Y_AXLE, cz - Z_AXLE
            rot_pts.append((Y_AXLE + c * dy - s * dz, Z_AXLE + s * dy + c * dz))
            
        cam_poly = Polygon(rot_pts)
        
        f_inter = cam_poly.intersects(front_poly)
        r_inter = cam_poly.intersects(rear_poly)
        
        dist_f = cam_poly.distance(front_poly)
        dist_r = cam_poly.distance(rear_poly)
        
        print(f"theta = {theta:4.1f}° | Front Intersect: {f_inter} (dist={dist_f:.2f}mm) | Rear Intersect: {r_inter} (dist={dist_r:.2f}mm)")

if __name__ == '__main__':
    run()
