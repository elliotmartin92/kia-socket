"""
testing/verify_hd_cam_kinematics.py
Verifies non-penetration, rotation stroke, and clearances for the heavy-duty reinforced cam.
"""

import os
import sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK
from testing.analyze_rocker_stiffness import get_heavy_duty_cam_poly

def run():
    print("Testing Heavy-Duty Reinforced Cam Kinematics...")
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    cam_poly_hd = get_heavy_duty_cam_poly()
    
    t_half = SHEET_THICK / 2.0
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    rear_poly = Polygon(r_poly_pts)
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    front_poly = Polygon(f_poly_pts)
    
    print("\nRotation Clearance Audit (0° to 10°):")
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
        
    print(f"\nMinimum Clearances across full stroke:")
    print(f"  Rear Brass Arm:  +{min_r:.3f} mm")
    print(f"  Front Brass Arm: +{min_f:.3f} mm")

if __name__ == '__main__':
    run()
