"""
testing/diagnose_rocker_test_b.py
Detailed geometric check of the rocker arm alone inside the baseplate without PCB:
1. Does the plunger collide with the through-hole edges?
2. Does the cam collide with the baseplate floor or bracket walls?
3. Does the cam profile bottom out or wedged against the blade?
4. Does the axle / hub bind against the towers?
5. What is the maximum possible rotation of the rocker arm in the baseplate?
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
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN,
    X_TOWER_CENTER
)
from build_part import (
    BASE_THICK, TOWER_HEIGHT, OUTER_WALL_HEIGHT,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    get_exact_base_polygon
)
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK

def diagnose():
    print("================================================================================")
    print("DIAGNOSIS: TEST B ISOLATION (ROCKER + BASEPLATE ALONE)")
    print("================================================================================")
    
    # 1. Baseplate Through-Hole bounds:
    # X in [7.608, 12.960], Y in [8.570, 13.082], Z in [0.00, 1.00]
    hole_y_min = HOLE_Y_CENTER - HOLE_Y_LEN / 2.0  # 8.570
    hole_y_max = HOLE_Y_CENTER + HOLE_Y_LEN / 2.0  # 13.082
    hole_x_min = HOLE_X_CENTER - HOLE_X_WIDTH / 2.0 # 7.608
    hole_x_max = HOLE_X_CENTER + HOLE_X_WIDTH / 2.0 # 12.960
    
    print(f"Through-Hole in Floor (Z in [0, 1] mm):")
    print(f"  X in [{hole_x_min:.3f}, {hole_x_max:.3f}] mm (Width = {HOLE_X_WIDTH:.3f} mm)")
    print(f"  Y in [{hole_y_min:.3f}, {hole_y_max:.3f}] mm (Length = {HOLE_Y_LEN:.3f} mm)")
    
    # 2. Plunger Geometry in build_shaft.py:
    # Centered in X at HOLE_X_CENTER = 10.284, width PLUNGER_WIDTH_X = 4.40 mm
    # X span: [10.284 - 2.2, 10.284 + 2.2] = [8.084, 12.484] mm.
    # Lateral clearance in hole: (5.352 - 4.40)/2 = 0.476 mm per side.
    
    # Let's trace the full plunger 2D polygon in Y-Z:
    y_axle = Y_AXLE  # 9.279
    z_axle = Z_AXLE  # 12.590
    r_hub = HUB_DIAMETER / 2.0  # 2.10
    
    z_tip = -PLUNGER_REACH_BELOW_Z  # -6.50
    r_tip = 1.00
    plunger_y_center = 10.479
    
    N = 50
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + r_hub) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - r_hub) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    plunger_poly_home = Polygon(pts_plunger)
    
    # 3. Check Plunger clearance in through hole across angles:
    print("\n--- PLUNGER POSITION AT FLOOR LEVEL (Z = 0.00 to 1.00 mm) ---")
    print("theta (deg) | Plunger Y_min at Z=0 | Plunger Y_max at Z=0 | Rear Clearance to Hole (Y=13.08) | Hole Clash?")
    
    clash_theta = None
    for theta in np.linspace(0, 20, 201):
        rad = np.radians(theta)
        c, s = np.cos(rad), np.sin(rad)
        
        # Rotate plunger points
        rot_pts = []
        for py, pz in pts_plunger:
            dy, dz = py - y_axle, pz - z_axle
            ry = y_axle + c * dy - s * dz
            rz = z_axle + s * dy + c * dz
            rot_pts.append((ry, rz))
            
        p_poly = Polygon(rot_pts)
        
        # Intersection with floor slice Z in [0, 1]
        floor_slice = box(-20, 0.0, 30, 1.0)
        inter = p_poly.intersection(floor_slice)
        
        if not inter.is_empty:
            bounds = inter.bounds # (minx, miny, maxx, maxy) -> here (min_y, min_z, max_y, max_z)
            p_y_min_floor = bounds[0]
            p_y_max_floor = bounds[2]
            rear_margin = hole_y_max - p_y_max_floor
            front_margin = p_y_min_floor - hole_y_min
            
            clash = (p_y_max_floor > hole_y_max) or (p_y_min_floor < hole_y_min)
            if clash and clash_theta is None:
                clash_theta = theta
                
            if theta in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20] or (clash and clash_theta == theta):
                status = "CLASH / SOLID STOP!" if clash else f"{rear_margin:.2f} mm margin"
                print(f"{theta:10.1f}° | {p_y_min_floor:19.2f} | {p_y_max_floor:19.2f} | {rear_margin:27.2f} mm | {status}")
                
    # 4. Check Cam tab bottoming out vs Baseplate Floor (Z = 1.00 mm):
    poly_pts_cam = [
        (Y_AXLE, Z_AXLE),
        (Y_AXLE, Z_AXLE + r_hub + 0.5),
        (5.00, 9.80),
        (1.50, 7.20),
        (1.80, 5.00),
        (4.50, 5.20),
        (Y_AXLE - 1.50, Z_AXLE - 2.50)
    ]
    
    print("\n--- CAM TAB POSITION VS BASEPLATE & BLADE ---")
    print("theta (deg) | Cam Min Z (mm) | Cam Top Contact Face Z (at Y=2.5mm) | Underside Clearance to Floor (Z=1.0mm)")
    for theta in [0, 2, 4, 6, 8, 10, 12, 14, 16]:
        rad = np.radians(theta)
        c, s = np.cos(rad), np.sin(rad)
        
        rot_cam = []
        for cy, cz in poly_pts_cam:
            dy, dz = cy - y_axle, cz - z_axle
            ry = y_axle + c * dy - s * dz
            rz = z_axle + s * dy + c * dz
            rot_cam.append((ry, rz))
            
        c_arr = np.array(rot_cam)
        min_z = c_arr[:, 1].min()
        floor_clearance = min_z - BASE_THICK  # distance above Z=1.0mm
        
        # Cam top ramp at blade center Y = 2.5 mm:
        # Interpolate along top spine (between rot_cam[2] and rot_cam[3])
        p2 = rot_cam[2] # was (5.0, 9.8)
        p3 = rot_cam[3] # was (1.5, 7.2)
        # linear interpolation at Y = 2.5
        t_25 = (2.50 - p3[0]) / (p2[0] - p3[0]) if (p2[0] != p3[0]) else 0.5
        z_contact_at_25 = p3[1] + t_25 * (p2[1] - p3[1])
        
        print(f"{theta:10.1f}° | {min_z:13.2f} mm | {z_contact_at_25:31.2f} mm | {floor_clearance:29.2f} mm")

if __name__ == '__main__':
    diagnose()
