"""
testing/test_option1_mesh.py
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
    RIB_FLANK_THICK, HOLE_X_CENTER, X_TOWER_CENTER
)

def build_shaft_rocker_option1(
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
    x_c = X_TOWER_CENTER
    
    r_pin = pin_d / 2.0
    r_hub = hub_d / 2.0
    pin_len = (axle_len - hub_w) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - hub_w/2.0 - pin_len/2.0, y_axle, z_axle])
    
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + hub_w/2.0 + pin_len/2.0, y_axle, z_axle])
    
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=hub_w, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - hub_w/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + hub_w/2.0 - 0.10 - RIB_FLANK_THICK), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    z_tip = -plunger_reach_below_z
    r_tip = 1.00
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
    
    # 4. Direct Straight Option 1 Belly Cam
    poly_pts_cam = [
        (y_axle, z_axle),                  # Center of hub
        (y_axle, z_axle + r_hub + 0.5),    # Above hub
        (5.00, 9.80),                      # Top straight ramp
        (1.50, 7.20),                      # Active contact tip inside 5.0mm belly
        (1.80, 5.00),                      # Rounded nose bottom inside belly
        (4.50, 5.20),                      # Beam underside
        (y_axle - 1.50, z_axle - 2.50)     # Into hub belly
    ]
    poly_cam_arm = Polygon(poly_pts_cam)
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w_x)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (cam_x_c - cam_w_x/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_rib1, mesh_rib3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    
    if not in_assembly_coords:
        mesh_printable = shaft_mesh.copy()
        # Rotate flat on build plate (Rot X = 198.6 deg)
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
    print("Testing Option 1 Mesh Generation...")
    m_asmb = build_shaft_rocker_option1(in_assembly_coords=True)
    print(f"Assembled Mesh:")
    print(f"  Watertight: {m_asmb.is_watertight}")
    print(f"  Volume:     {m_asmb.volume:.2f} mm³")
    print(f"  Bounds:     {m_asmb.bounds.tolist()}")
    
    m_prnt = build_shaft_rocker_option1(in_assembly_coords=False)
    print(f"\nPrintable Mesh:")
    print(f"  Watertight: {m_prnt.is_watertight}")
    print(f"  Z min:      {m_prnt.bounds[0, 2]:.4f} mm")
    print(f"  Z max:      {m_prnt.bounds[1, 2]:.4f} mm")
    print(f"  Bounds:     {m_prnt.bounds.tolist()}")

if __name__ == '__main__':
    run()
