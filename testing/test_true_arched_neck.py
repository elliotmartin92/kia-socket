"""
testing/test_true_arched_neck.py
Tests the goose-neck profile that stays inside Y <= 1.80 mm up to Z = 15.60 mm,
then turns over the top lip at Z >= 15.80 mm to connect to the shaft hub.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box, LineString

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE, HUB_DIAMETER
from testing.model_exact_brass_part import get_brass_contact_2d_profile, D1A, D1B, D2, D4, D5, D3, SHEET_THICK

def get_true_gooseneck_profile():
    r_hub = HUB_DIAMETER / 2.0 # 2.10 mm
    
    # 1. Contact Nose / Drop Finger inside V-funnel:
    # Nose tip at (1.45, 11.20)
    # Front contact face: from (1.45, 11.20) up to (1.45, 15.60)
    # Underside face inside funnel: from (2.05, 11.20) up to (2.05, 15.60) -> clear of rear arm (which is at Y >= 2.40 to 3.60 mm!)
    
    # 2. Over-the-Lip Arch (Z >= 15.80 mm, clearing Z = 15.40 mm lip):
    # Top arch: from (1.45, 15.60) -> (3.50, 17.20) -> (6.50, 16.50) -> (Y_AXLE, Z_AXLE + r_hub) = (9.28, 14.69)
    # Underside arch: from (Y_AXLE - 1.20, Z_AXLE + 1.20) -> (6.00, 15.40) -> (4.20, 16.00) -> (2.05, 15.60)
    
    # Let's define the continuous 2D polygon vertices
    poly_pts = [
        # Hub connection top
        (Y_AXLE, Z_AXLE + r_hub),     # (9.28, 14.69)
        (7.00, 16.60),
        (4.50, 17.20),
        (2.50, 16.80),
        (1.45, 15.60),                 # Entering funnel mouth
        (1.45, 11.20),                 # Nose tip contact on blade
        (1.95, 10.80),                 # Nose bottom
        (2.10, 11.20),                 # Rear of drop finger inside funnel
        (2.10, 15.40),                 # Rising vertically inside funnel (Y=2.10 < Y_rear_arm=3.60)
        (3.85 + 0.60, 16.10),          # Over the lip (clearing 15.40mm lip by 0.70mm)
        (6.50, 15.20),
        (Y_AXLE - 1.20, Z_AXLE + 1.20),# Hub blend
        (Y_AXLE - 1.50, Z_AXLE)
    ]
    
    return np.array(poly_pts)

def run():
    print("Testing true goose-neck profile...")
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    cam_poly = get_true_gooseneck_profile()
    
    t_half = SHEET_THICK / 2.0
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    rear_poly = Polygon(r_poly_pts)
    
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    front_poly = Polygon(f_poly_pts)
    
    # Check clearance at 0 deg
    poly_geom = Polygon(cam_poly)
    dist_rear = poly_geom.distance(rear_poly)
    dist_front = poly_geom.distance(front_poly)
    
    print(f"Clearance at 0 deg: Rear = +{dist_rear:.2f} mm, Front = +{dist_front:.2f} mm")
    
    # Check across 0 to 10 deg rotation
    print("\nRotation Clearance Audit:")
    for ang in range(0, 11):
        rad = np.radians(ang)
        c_a, s_a = np.cos(rad), np.sin(rad)
        vecs = cam_poly - np.array([Y_AXLE, Z_AXLE])
        p_rot = np.zeros_like(cam_poly)
        p_rot[:, 0] = Y_AXLE + c_a * vecs[:, 0] - s_a * vecs[:, 1]
        p_rot[:, 1] = Z_AXLE + s_a * vecs[:, 0] + c_a * vecs[:, 1]
        
        pg = Polygon(p_rot)
        dr = pg.distance(rear_poly)
        df = pg.distance(front_poly)
        print(f"  theta = {ang:2d} deg: Rear Gap = +{dr:.2f} mm, Front Gap = +{df:.2f} mm")

if __name__ == '__main__':
    run()
