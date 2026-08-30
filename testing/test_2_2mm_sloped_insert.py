"""
testing/test_2_2mm_sloped_insert.py
Tests the user-specified 2.2mm wide tip slope and expanded internal slit tolerances.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box

# Base Dimensions
SLIT_BOSS_HEIGHT = 2.47
KEY_H = 0.85

# Shroud Body Dimensions
BODY_W_BASE = 3.60   # 3.60mm at shoulder Z = 2.47mm
BODY_L_BASE = 5.40   # 5.40mm at shoulder Z = 2.47mm

BODY_W_TIP = 2.20    # Exact 2.20mm wide at outer end Z = 0.00mm as requested by user
BODY_L_TIP = 4.40    # 4.40mm long at outer end Z = 0.00mm

# Indexing Key Dimensions (Z = 2.47 to 3.32mm)
KEY_W_BASE = 2.00
KEY_L_BASE = 4.30
KEY_W_TOP = 1.50     # 0.25mm lead-in taper per side
KEY_L_TOP = 3.80     # 0.25mm lead-in taper per side

# Expanded Slit / Through-Hole Dimensions (More tolerance for 0.77 x 3.10mm brass blade)
SLIT_W_EXPANDED = 1.35   # 1.35mm (provides +0.58mm total sliding clearance for 0.77mm brass blade)
SLIT_L_EXPANDED = 3.65   # 3.65mm (provides +0.55mm total sliding clearance for 3.10mm brass blade)

# Baseplate Socket Dimensions (Relaxed 0.50mm clearance)
SOCKET_W_NEW = 2.50  # 2.50mm in floor
SOCKET_L_NEW = 4.80  # 4.80mm in floor

def create_frustum_mesh(w_bot, l_bot, w_top, l_top, z_bot, z_top):
    v_bot = np.array([
        [-w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2,  l_bot/2, z_bot],
        [-w_bot/2,  l_bot/2, z_bot],
    ])
    v_top = np.array([
        [-w_top/2, -l_top/2, z_top],
        [ w_top/2, -l_top/2, z_top],
        [ w_top/2,  l_top/2, z_top],
        [-w_top/2,  l_top/2, z_top],
    ])
    verts = np.vstack([v_bot, v_top])
    faces = [
        [0, 3, 2], [0, 2, 1],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ]
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)

def build_sloped_insert_solid():
    z0 = 0.00
    z1 = SLIT_BOSS_HEIGHT  # 2.47mm
    z2 = z1 + KEY_H        # 3.32mm
    
    m_body = create_frustum_mesh(BODY_W_TIP, BODY_L_TIP, BODY_W_BASE, BODY_L_BASE, z0, z1)
    m_key = create_frustum_mesh(KEY_W_BASE, KEY_L_BASE, KEY_W_TOP, KEY_L_TOP, z1, z2)
    m_solid = m_body.union(m_key, engine='manifold')
    
    hole_cutter = trimesh.creation.box([SLIT_W_EXPANDED, SLIT_L_EXPANDED, z2 + 2.0])
    hole_cutter.apply_translation([0, 0, (z2 + 2.0)/2.0 - 0.5])
    return m_solid.difference(hole_cutter, engine='manifold')

def run():
    print("=== TESTING 2.2mm TIP SLOPED INSERT & EXPANDED SLIT ===")
    mesh = build_sloped_insert_solid()
    print(f"Watertight: {mesh.is_watertight}")
    print(f"Volume:     {mesh.volume:.3f} mm^3")
    print(f"Bounds X:   [{mesh.bounds[0,0]:.3f}, {mesh.bounds[1,0]:.3f}] mm (Tip width: {BODY_W_TIP:.2f}mm, Base width: {BODY_W_BASE:.2f}mm)")
    print(f"Bounds Y:   [{mesh.bounds[0,1]:.3f}, {mesh.bounds[1,1]:.3f}] mm (Tip length: {BODY_L_TIP:.2f}mm, Base length: {BODY_L_BASE:.2f}mm)")
    print(f"Bounds Z:   [{mesh.bounds[0,2]:.3f}, {mesh.bounds[1,2]:.3f}] mm")
    
    # Wall thickness checks
    tip_wall_x = (BODY_W_TIP - SLIT_W_EXPANDED) / 2.0
    tip_wall_y = (BODY_L_TIP - SLIT_L_EXPANDED) / 2.0
    base_wall_x = (BODY_W_BASE - SLIT_W_EXPANDED) / 2.0
    base_wall_y = (BODY_L_BASE - SLIT_L_EXPANDED) / 2.0
    
    print(f"\nWall Thicknesses:")
    print(f"  At Tip (Z=0.00mm):  X wall = {tip_wall_x:.3f} mm, Y wall = {tip_wall_y:.3f} mm")
    print(f"  At Base (Z=2.47mm): X wall = {base_wall_x:.3f} mm, Y wall = {base_wall_y:.3f} mm")
    
    # Contact Blade Clearances
    blade_thick = 0.77
    blade_len = 3.10
    print(f"\nBrass Contact Blade Clearances (0.77 x 3.10mm OEM blade):")
    print(f"  Slit Hole Size: {SLIT_W_EXPANDED:.2f} x {SLIT_L_EXPANDED:.2f} mm")
    print(f"  Thickness Clearance (X): +{SLIT_W_EXPANDED - blade_thick:.3f} mm (+{(SLIT_W_EXPANDED - blade_thick)/2:.3f} mm per side)")
    print(f"  Length Clearance (Y):    +{SLIT_L_EXPANDED - blade_len:.3f} mm (+{(SLIT_L_EXPANDED - blade_len)/2:.3f} mm per side)")
    
    assert mesh.is_watertight, "Mesh is not watertight!"
    print("\nSUCCESS: All tests passed!")

if __name__ == '__main__':
    run()
