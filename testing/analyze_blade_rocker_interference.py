"""
testing/analyze_blade_rocker_interference.py
Investigates all possible geometric interference mechanisms between the rocker arm
and the AC plug blade during full insertion/seating.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN
)
from build_part import (
    BASE_THICK, TOWER_HEIGHT
)
from testing.model_exact_brass_part import (
    get_brass_contact_2d_profile, D1A, D1B, D2, D4, D5, D3, SHEET_THICK
)

def analyze():
    print("================================================================================")
    print("GEOMETRIC AUDIT: BLADE SEATING & ROCKER ARM INTERFERENCE ANALYSIS")
    print("================================================================================")
    
    # 1. Coordinate Frames & Landmarks
    print(f"Pivot Axle:  Y = {Y_AXLE:.3f} mm, Z = {Z_AXLE:.3f} mm")
    print(f"Baseplate:   Floor at Z in [0.00, {BASE_THICK:.2f}] mm")
    print(f"Tower Top:   Z = {BASE_THICK + TOWER_HEIGHT:.2f} mm")
    
    # 2. Blade Specifications (NEMA 1-15 / 5-15 Standard)
    # Hot Blade (Right side):
    # Length: 15.88 mm (5/8 in) to 17.50 mm
    # Width (Y): 6.35 mm (1/4 in) nominal
    # Thickness (X): 1.52 mm (0.060 in) nominal
    # Blade centerline in X = 6.28 mm
    # Plug insertion travels along -Z.
    
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
    cam_pts = np.array(poly_pts_cam)
    
    print("\n--- CAM TAB AT REST (theta = 0 deg) ---")
    print(f"  X span: [{CAM_X_CENTER - CAM_WIDTH_X/2:.2f}, {CAM_X_CENTER + CAM_WIDTH_X/2:.2f}] mm (Width = {CAM_WIDTH_X:.2f} mm)")
    print(f"  Y span: [{cam_pts[:, 0].min():.2f}, {cam_pts[:, 0].max():.2f}] mm")
    print(f"  Z span: [{cam_pts[:, 1].min():.2f}, {cam_pts[:, 1].max():.2f}] mm")
    print(f"  Lowest tip of Cam: Y = 1.80 mm, Z = 5.00 mm")
    print(f"  Leading contact ramp: from (5.00, 9.80) to (1.50, 7.20)")
    
    print("\n--- KINEMATIC SWEEP (Rotation theta: 0 to 14 deg) ---")
    print("theta(deg) | Cam Min Z (mm) | Cam Min Y (mm) | Plunger Tip (Y, Z) | Plunger Y at Z=0 (mm)")
    
    for theta in [0, 2, 4, 6, 8, 10, 12, 14]:
        rad = np.radians(theta)
        c, s = np.cos(rad), np.sin(rad)
        
        # Cam rotation
        cam_rot = np.zeros_like(cam_pts)
        for i, (y, z) in enumerate(cam_pts):
            dy, dz = y - Y_AXLE, z - Z_AXLE
            cam_rot[i, 0] = Y_AXLE + c * dy - s * dz
            cam_rot[i, 1] = Z_AXLE + s * dy + c * dz
            
        # Plunger tip
        dy_p, dz_p = 10.479 - Y_AXLE, -6.50 - Z_AXLE
        y_tip = Y_AXLE + c * dy_p - s * dz_p
        z_tip = Z_AXLE + s * dy_p + c * dz_p
        
        t_z0 = (0.0 - Z_AXLE) / (z_tip - Z_AXLE)
        y_z0 = Y_AXLE + t_z0 * (y_tip - Y_AXLE)
        
        print(f"{theta:10.1f} | {cam_rot[:, 1].min():14.2f} | {cam_rot[:, 0].min():14.2f} | ({y_tip:5.2f}, {z_tip:6.2f}) | {y_z0:15.2f}")

if __name__ == '__main__':
    analyze()
