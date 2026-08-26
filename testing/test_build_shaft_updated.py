"""
testing/test_build_shaft_updated.py
Tests generating the complete updated shaft_rocker mesh with the arched full-width cam.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, RIB_FLANK_THICK, HOLE_X_CENTER, X_TOWER_CENTER
)

def build_shaft_rocker_mesh_updated(
    axle_len=TOTAL_AXLE_LEN,
    hub_w=HUB_WIDTH,
    pin_d=PIN_DIAMETER,
    hub_d=HUB_DIAMETER,
    plunger_reach_below_z=PLUNGER_REACH_BELOW_Z,
    plunger_w_x=PLUNGER_WIDTH_X,
    cam_w_x=2.70,
    cam_x_c=6.28,
    in_assembly_coords=True
):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER  # 9.25 mm
    
    # 1. Stepped Cylindrical Axle & Hub
    r_pin = pin_d / 2.0
    r_hub = hub_d / 2.0
    pin_len = (axle_len - hub_w) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # Left pin: [3.50, 5.50]
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - hub_w/2.0 - pin_len/2.0, y_axle, z_axle])
    
    # Right pin: [13.00, 15.00]
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + hub_w/2.0 + pin_len/2.0, y_axle, z_axle])
    
    # Central Hub Barrel: [5.50, 13.00]
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. OEM 3-Rib Flanks & Plunger Array
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    # Rib 1 (Left Flank): X in [5.60, 6.60]
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - hub_w/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    # Rib 3 (Right Flank): X in [11.90, 12.90]
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + hub_w/2.0 - 0.10 - RIB_FLANK_THICK), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    # Rib 2 (Center Plunger Blade): Reaching Z = -6.50mm
    z_tip = -plunger_reach_below_z  # -6.50 mm
    r_tip = 1.00                    # 2.00mm tip thickness in Y
    plunger_y_center = 10.479
    
    N = 25
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
    poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=plunger_w_x)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - plunger_w_x/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 3. Structural Web tying the 3 ribs together (X in [5.60, 12.90])
    web_y_min = y_axle - 1.50
    web_y_max = y_axle + 2.50
    web_z_min = z_axle - 3.20
    web_z_max = z_axle + 1.00
    web_poly = box(web_y_min, web_z_min, web_y_max, web_z_max)
    web_span_x = (x_c + hub_w/2.0 - 0.10) - (x_c - hub_w/2.0 + 0.10)
    m_web_raw = trimesh.creation.extrude_polygon(web_poly, height=web_span_x)
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([v_w[:, 2] + (x_c - hub_w/2.0 + 0.10), v_w[:, 0], v_w[:, 1]])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # 4. Arched Full-Width Input Cam Tab
    lip_z = 17.20
    poly_pts_cam = [
        (y_axle, z_axle + r_hub),     # (9.28, 14.69)
        (6.80, lip_z + 0.6),
        (4.20, lip_z + 0.8),
        (2.00, lip_z + 0.2),
        (1.45, 13.00),                 # Nose tip contact on blade
        (2.05, 12.80),                 # Nose bottom rounded
        (2.20, 13.40),                 # Nose rear in upper funnel
        (2.20, lip_z - 0.5),          # Rising inside funnel
        (4.20, lip_z),                # Over the lip (Z = 17.2 mm > 15.4 mm)
        (6.80, lip_z - 1.2),
        (y_axle - 1.20, z_axle + 1.00),
        (y_axle - 1.50, z_axle)
    ]
    poly_cam_arm = Polygon(poly_pts_cam)
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w_x)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (cam_x_c - cam_w_x/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    # Assembly mesh
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_rib1, mesh_rib3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    
    if not in_assembly_coords:
        mesh_printable = shaft_mesh.copy()
        # Rotate so the flat plunger back or cam flat rests on the print bed
        rot_bed = trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])
        mesh_printable.apply_transform(rot_bed)
        bounds = mesh_printable.bounds
        mesh_printable.apply_translation([
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ])
        return mesh_printable
        
    return shaft_mesh

def run():
    print("Testing updated shaft rocker mesh creation...")
    m_asmb = build_shaft_rocker_mesh_updated(in_assembly_coords=True)
    print(f"Assembled Mesh:")
    print(f"  Watertight: {m_asmb.is_watertight}")
    print(f"  Volume:     {m_asmb.volume:.2f} mm³")
    print(f"  Bounds:     {m_asmb.bounds.tolist()}")
    
    m_prnt = build_shaft_rocker_mesh_updated(in_assembly_coords=False)
    print(f"\nPrintable Mesh:")
    print(f"  Watertight: {m_prnt.is_watertight}")
    print(f"  Z min:      {m_prnt.bounds[0, 2]:.4f} mm")
    print(f"  Z max:      {m_prnt.bounds[1, 2]:.4f} mm")
    print(f"  Bounds:     {m_prnt.bounds.tolist()}")

if __name__ == '__main__':
    run()
