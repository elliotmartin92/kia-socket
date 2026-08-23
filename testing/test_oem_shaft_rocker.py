"""
testing/test_oem_shaft_rocker.py
Prototype and validation script for the OEM 3-rib shaft rocker mechanism.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt

# Baseplate Datum & Tower Coordinates
Y_AXLE = 7.666
Z_AXLE = 12.590

# Tower Coordinates
X_LEFT_TOWER_OUTER = 3.900
X_LEFT_TOWER_INNER = 5.400
X_RIGHT_TOWER_INNER = 13.100
X_RIGHT_TOWER_OUTER = 14.600
X_TOWER_CENTER = (X_LEFT_TOWER_INNER + X_RIGHT_TOWER_INNER) / 2.0  # 9.25 mm

# Through-Hole bounds: X in [7.608, 12.960], Y in [8.570, 13.082], Z in [0.00, 1.00]
HOLE_X_CENTER = 10.284
HOLE_X_WIDTH = 5.352
HOLE_Y_CENTER = 10.826
HOLE_Y_LEN = 4.512

# OEM Dimensions
TOTAL_AXLE_LEN = 11.50
HUB_WIDTH = 7.60             # 7.71mm nominal, 7.60mm for 0.05mm rotation clearance
PIN_LEN = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0  # 1.95 mm per side
PIN_DIAMETER = 1.90          # 1.90mm for snap-fit into 2.00mm tower cradle (or 2.27mm OEM)
HUB_DIAMETER = 3.30          # 3.30mm central hub barrel
PLUNGER_REACH_BELOW_Z = 6.50 # Reaches Z = -6.50mm

def build_oem_shaft_rocker_mesh(
    axle_len=TOTAL_AXLE_LEN,
    hub_w=HUB_WIDTH,
    pin_d=PIN_DIAMETER,
    hub_d=HUB_DIAMETER,
    plunger_reach=PLUNGER_REACH_BELOW_Z,
    in_assembly_coords=True
):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER  # 9.25 mm
    
    # 1. Cylindrical Axle (Total Length 11.50mm, X in [3.50, 15.00])
    r_pin = pin_d / 2.0
    x_min = x_c - axle_len / 2.0  # 3.50 mm
    x_max = x_c + axle_len / 2.0  # 15.00 mm
    
    # Left pin: [3.50, 3.50 + pin_len] -> [3.50, 5.45]
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.1, sections=32)
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_min + PIN_LEN/2.0, y_axle, z_axle])
    
    # Right pin: [13.05, 15.00]
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.1, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_max - PIN_LEN/2.0, y_axle, z_axle])
    
    # Central Hub Barrel: [5.45, 13.05]
    hub_mesh = trimesh.creation.cylinder(radius=hub_d/2.0, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. OEM 3-Rib Plunger & Flank Array
    # Side Flank Profile (Ribs 1 & 3): Triangular brace extending down towards baseplate
    # (Y in [y_axle - 1.2, y_axle + 2.8], Z in [z_axle - 4.5, z_axle + 1.2])
    flank_collar = Point(y_axle, z_axle).buffer(hub_d / 2.0)
    flank_pts = [
        (y_axle - 1.20, z_axle + 0.50),
        (y_axle + 2.80, z_axle - 1.50),
        (y_axle + 2.20, z_axle - 4.20),
        (y_axle + 0.20, z_axle - 4.00),
        (y_axle - 1.40, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    # Rib 1 (Left Flank): X in [5.55, 6.45] (0.90mm thick)
    rib1_w = 0.90
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=rib1_w)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - hub_w/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    # Rib 3 (Right Flank): X in [12.05, 12.95] (0.90mm thick)
    rib3_w = 0.90
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=rib3_w)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + hub_w/2.0 - 0.10 - rib3_w), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    # Rib 2 (Center Plunger Blade): Extended reach to Z = -6.50mm
    # Aligned over the through-hole: centered at HOLE_X_CENTER (10.284mm)
    plunger_w = 2.40  # 2.40mm wide central plunger blade (well within 5.35mm hole)
    z_tip = -plunger_reach  # -6.50 mm
    r_tip = 1.00            # 2.00mm tip thickness in Y
    plunger_y_center = 11.40
    
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + hub_d/2.0) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - hub_d/2.0) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=plunger_w)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - plunger_w/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 3. Connecting Structural Gusset Web across the 3 ribs (X in [5.55, 12.95])
    # Rib web tying the 3 ribs into a solid monolithic structural core
    web_y_min = y_axle - 1.20
    web_y_max = y_axle + 2.20
    web_z_min = z_axle - 3.20
    web_z_max = z_axle + 0.80
    web_poly = box(web_y_min, web_z_min, web_y_max, web_z_max)
    web_span_x = (x_c + hub_w/2.0 - 0.10) - (x_c - hub_w/2.0 + 0.10)
    m_web_raw = trimesh.creation.extrude_polygon(web_poly, height=web_span_x)
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([v_w[:, 2] + (x_c - hub_w/2.0 + 0.10), v_w[:, 0], v_w[:, 1]])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # 4. Angled Input Cam Tab with Underside Coring (Bellcrank Angle ~105°)
    # Located at X in [5.70, 8.40] (centered at X = 7.05mm, aligned with slider track)
    cam_w = 2.70
    cam_x_c = 7.05
    y_cam_tip = y_axle - 4.20  # Reaches Y = 3.47mm
    z_cam_tip = z_axle - 5.80  # Drops to Z = 6.79mm
    
    cam_collar = Point(y_axle, z_axle).buffer(hub_d / 2.0)
    cam_pts = [
        (y_axle + 1.20, z_axle + 1.20),
        (y_cam_tip, z_cam_tip + 2.20),
        (y_cam_tip, z_cam_tip),
        (y_cam_tip + 2.80, z_cam_tip),
        (y_axle + 0.20, z_axle - 2.50)
    ]
    poly_cam = unary_union([cam_collar, Polygon(cam_pts)])
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (cam_x_c - cam_w/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    # Combine All Components
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_rib1, mesh_rib3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    
    if not in_assembly_coords:
        # Orient flat on print bed: rotate 90 deg so spine / belly lays flat on build plate
        mesh_printable = shaft_mesh.copy()
        rot_bed = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
        mesh_printable.apply_transform(rot_bed)
        bounds = mesh_printable.bounds
        mesh_printable.apply_translation([
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ])
        return mesh_printable
        
    return shaft_mesh

if __name__ == '__main__':
    print("Testing OEM Shaft Rocker mesh generation...")
    m_assembled = build_oem_shaft_rocker_mesh(in_assembly_coords=True)
    print(f"Assembled mesh bounds: {m_assembled.bounds}")
    print(f"Mesh is watertight: {m_assembled.is_watertight}")
    print(f"Mesh volume: {m_assembled.volume:.2f} mm^3")
    
    m_printable = build_oem_shaft_rocker_mesh(in_assembly_coords=False)
    print(f"Printable mesh bounds: {m_printable.bounds}")
    print(f"Printable base at Z = {m_printable.bounds[0, 2]:.2f} mm")
    
    # Verify clearances
    print("\n--- Clearance Checks ---")
    print(f"Left Pin X-span: [{m_assembled.bounds[0, 0]:.2f}, 5.45] mm (Tower outer: {X_LEFT_TOWER_OUTER:.2f}, inner: {X_LEFT_TOWER_INNER:.2f})")
    print(f"Right Pin X-span: [13.05, {m_assembled.bounds[1, 0]:.2f}] mm (Tower inner: {X_RIGHT_TOWER_INNER:.2f}, outer: {X_RIGHT_TOWER_OUTER:.2f})")
    print(f"Through-Hole Clearance: Plunger at X = [{HOLE_X_CENTER - 1.2:.2f}, {HOLE_X_CENTER + 1.2:.2f}] mm (Hole: [{HOLE_X_CENTER - HOLE_X_WIDTH/2:.2f}, {HOLE_X_CENTER + HOLE_X_WIDTH/2:.2f}])")
    print(f"Plunger Reach: Z_min = {m_assembled.bounds[0, 2]:.2f} mm (Target <= -6.50 mm)")
