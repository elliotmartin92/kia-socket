"""
testing/test_option2_side_clamp.py
Prototype and verify Option 2: Additive External Side Ledges on Tower Prongs
with Side-Ears Snap Clamp (Zero Pin Friction, 100% Solid Prongs).
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import BASE_THICK, TOWER_HEIGHT, build_clean_shaft_towers_mesh, build_left_tower_struts_mesh
from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh

def extrude_xz(poly_xz, height, y_offset=0.0):
    m_raw = trimesh.creation.extrude_polygon(poly_xz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 0], v[:, 2] + y_offset, v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces[:, ::-1].copy(), process=True)

def extrude_yz(poly_yz, height, x_offset=0.0):
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 2] + x_offset, v[:, 0], v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces.copy(), process=True)

def build_additive_side_beads():
    """
    Creates additive retention ledges on the outer lateral faces of Left (X=3.90) and Right (X=14.60) towers.
    Protrudes 0.30mm outward in X.
    Top surface has a 35 deg lead-in ramp; bottom surface is a horizontal undercut shelf at Z = 12.60mm.
    """
    # Left bead: X in [3.60, 3.90] (protrudes in -X from 3.90)
    poly_xz_left = Polygon([
        (3.90, 12.60),
        (3.60, 12.60),  # Horizontal undercut shelf
        (3.60, 12.85),
        (3.90, 13.15),  # 35 deg lead-in ramp
    ])
    mesh_lf = extrude_xz(poly_xz_left, height=7.75 - 7.15, y_offset=7.15)
    mesh_lr = extrude_xz(poly_xz_left, height=11.40 - 10.80, y_offset=10.80)
    
    # Right bead: X in [14.60, 14.90] (protrudes in +X from 14.60)
    poly_xz_right = Polygon([
        (14.60, 12.60),
        (14.90, 12.60),  # Horizontal undercut shelf
        (14.90, 12.85),
        (14.60, 13.15),  # 35 deg lead-in ramp
    ])
    mesh_rf = extrude_xz(poly_xz_right, height=7.75 - 7.15, y_offset=7.15)
    mesh_rr = extrude_xz(poly_xz_right, height=11.40 - 10.80, y_offset=10.80)
    
    return trimesh.util.concatenate([mesh_lf, mesh_lr, mesh_rf, mesh_rr])

def build_option2_clamp(tower_side='left'):
    """
    Builds the 3D watertight mesh for the Option 2 Clamp:
    - Main U-saddle in (Y, Z) covering the 1.50mm tower.
    - Outer side wall (0.90mm thick) extending down the outer face.
    - Central clearance arch (R = 1.70mm) leaving >= 0.30mm air gap around the pin (zero friction!).
    - Front and rear snap ears with inward locking hooks at Z = 12.60mm.
    """
    z_top = 14.990
    z_roof_under = 14.090
    z_bot = 11.200
    y_front_inner_top = 6.550 - 0.040
    y_front_inner_bot = 6.484 - 0.020
    y_rear_inner_top = 12.180 + 0.040
    y_rear_inner_bot = 12.328 + 0.020
    
    y_front_outer_top = y_front_inner_top - 1.15
    y_front_outer_bot = y_front_inner_bot - 1.15
    y_rear_outer_top = y_rear_inner_top + 1.15
    y_rear_outer_bot = y_rear_inner_bot + 1.15
    
    ENTRY_CHAMFER = 0.350
    Y_KEEL_FRONT = 7.650
    Y_KEEL_REAR = 10.908
    Z_KEEL = 14.020
    
    saddle_pts_yz = [
        (y_front_outer_bot, z_bot),
        (y_front_outer_top, z_top - 0.40),
        (y_front_outer_top + 0.40, z_top),
        (y_rear_outer_top - 0.40, z_top),
        (y_rear_outer_top, z_top - 0.40),
        (y_rear_outer_bot, z_bot),
        (y_rear_inner_bot + ENTRY_CHAMFER, z_bot),
        (y_rear_inner_bot, z_bot + ENTRY_CHAMFER),
        (y_rear_inner_top, z_roof_under),
        (Y_KEEL_REAR + 0.30, z_roof_under),
        (Y_KEEL_REAR, Z_KEEL + 0.15),
        (Y_KEEL_REAR - 0.15, Z_KEEL),
        (Y_KEEL_FRONT + 0.15, Z_KEEL),
        (Y_KEEL_FRONT, Z_KEEL + 0.15),
        (Y_KEEL_FRONT - 0.30, z_roof_under),
        (y_front_inner_top, z_roof_under),
        (y_front_inner_bot, z_bot + ENTRY_CHAMFER),
        (y_front_inner_bot - ENTRY_CHAMFER, z_bot)
    ]
    poly_saddle_yz = Polygon(saddle_pts_yz)
    
    # Outer side cheek polygon in (Y, Z)
    # Arch centered at Y = 9.279, Z = 12.590, Radius = 1.70mm
    arch_pts = []
    r_arch = 1.70
    y_c = Y_AXLE
    z_c = Z_AXLE
    for p in np.linspace(np.pi, 0, 32):
        arch_pts.append((y_c + r_arch * np.cos(p), z_c + r_arch * np.sin(p)))
        
    side_pts_yz = [
        (y_front_outer_bot, 12.10),
        (y_front_outer_top, z_top - 0.40),
        (y_front_outer_top + 0.40, z_top),
        (y_rear_outer_top - 0.40, z_top),
        (y_rear_outer_top, z_top - 0.40),
        (y_rear_outer_bot, 12.10),
        (10.75, 12.10),
    ] + arch_pts + [
        (7.80, 12.10)
    ]
    poly_side_yz = Polygon(side_pts_yz)
    
    if tower_side == 'left':
        # Saddle: X in [3.90, 5.375] (1.475mm thick)
        m_saddle = extrude_yz(poly_saddle_yz, height=1.475, x_offset=3.90)
        # Side wall: X in [3.00, 3.90] (0.90mm thick)
        m_side = extrude_yz(poly_side_yz, height=0.90, x_offset=3.00)
        
        # Inward snap hooks on inner face of side wall (X in [3.60, 3.90])
        # Hooks under shelf at Z = 12.60mm
        poly_hook_xz = Polygon([
            (3.00, 12.10),
            (3.60, 12.40),  # 45 deg entry chamfer
            (3.60, 12.60),  # Hook shelf top
            (3.00, 12.60)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=7.80 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.45 - 10.75, y_offset=10.75)
        
        m_clamp = unary_union_meshes([m_saddle, m_side, m_hf, m_hr])
        return m_clamp
    else:
        # Right clamp: X_saddle in [13.125, 14.60], X_side in [14.60, 15.50]
        m_saddle = extrude_yz(poly_saddle_yz, height=1.475, x_offset=13.125)
        m_side = extrude_yz(poly_side_yz, height=0.90, x_offset=14.60)
        
        poly_hook_xz = Polygon([
            (15.50, 12.10),
            (14.90, 12.40),
            (14.90, 12.60),
            (15.50, 12.60)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=7.80 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.45 - 10.75, y_offset=10.75)
        
        m_clamp = unary_union_meshes([m_saddle, m_side, m_hf, m_hr])
        return m_clamp

def unary_union_meshes(meshes):
    """Robust union of multiple touching/overlapping manifold meshes."""
    m_res = meshes[0]
    for m in meshes[1:]:
        m_res = m_res.union(m, engine='manifold')
    return m_res

if __name__ == '__main__':
    print("Testing Option 2 clamp construction...")
    c_left = build_option2_clamp('left')
    c_right = build_option2_clamp('right')
    print("Left clamp watertight:", c_left.is_watertight, "Volume:", c_left.volume)
    print("Right clamp watertight:", c_right.is_watertight, "Volume:", c_right.volume)
    
    beads = build_additive_side_beads()
    print("Side beads watertight:", beads.is_watertight, "Volume:", beads.volume)
    
    shaft = build_shaft_rocker_mesh(in_assembly_coords=True)
    # Check distance from pin to clamp arch
    pin_pts = shaft.vertices[(shaft.vertices[:, 0] < 3.90) | (shaft.vertices[:, 0] > 14.60)]
    print("Pin vertices in outer zone:", len(pin_pts))
    
    d_left = trimesh.proximity.closest_point(c_left, pin_pts[pin_pts[:, 0] < 3.90])[1]
    print("Minimum clearance from Left Pin to Left Clamp:", d_left.min(), "mm")
    
    d_right = trimesh.proximity.closest_point(c_right, pin_pts[pin_pts[:, 0] > 14.60])[1]
    print("Minimum clearance from Right Pin to Right Clamp:", d_right.min(), "mm")
