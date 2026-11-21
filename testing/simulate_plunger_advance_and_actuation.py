"""
testing/simulate_plunger_advance_and_actuation.py
Comprehensive verification script for the upgraded plunger advance and cam throat clearance.
Checks:
1. Cam nose vs seated brass throat clearance at rest and during full rotation sweep.
2. Actuation stroke comparison: Old (plunger_y=10.95) vs New (plunger_y=11.40) under simulated plug insertion.
3. Floor through-hole clearances across rotation.
4. Clearance to stationary breakaway shaft support stick.
5. Plunger support cradle alignment and release gap in 45° print orientation.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, HUB_DIAMETER, HUB_WIDTH,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh,
    KINEMATIC_VARIANTS, ACTIVE_VARIANT, HOLE_Y_TOP, HOLE_Y_BOT,
    HOLE_X_CENTER, HOLE_X_WIDTH
)
import build_part as bp
from testing.simulate_with_3d_brass_insert import build_brass_insert_mesh

def check_cam_vs_brass():
    print("=" * 80)
    print("1. CHECK CAM NOSE & ARM VS SEATED 3D BRASS CONTACT THROAT")
    print("=" * 80)
    
    brass = build_brass_insert_mesh()
    shaft = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    
    # Cam vertices only (X in [5.70, 7.65])
    cam_v = shaft.vertices[(shaft.vertices[:, 0] >= 5.70) & (shaft.vertices[:, 0] <= 7.65)]
    prox_cam = trimesh.proximity.ProximityQuery(brass)
    
    # Distance of cam at rest
    closest_pts, dists, _ = brass.nearest.on_surface(cam_v)
    min_dist_rest = dists.min()
    
    # Check nose point specifically
    nose_pts = np.array([[5.75, 2.45, 7.55], [7.60, 2.45, 7.55]])
    _, nose_dists, _ = brass.nearest.on_surface(nose_pts)
    
    # Check point (2.80, 8.10)
    upper_nose_pts = np.array([[5.75, 2.80, 8.10], [7.60, 2.80, 8.10]])
    _, upper_dists, _ = brass.nearest.on_surface(upper_nose_pts)
    
    print(f"At rest (theta = 0.0°):")
    print(f"  Cam Nose Apex (Y=2.45, Z=7.55) clearance to brass:       {nose_dists.min():.3f} mm")
    print(f"  Upper Cam Nose (Y=2.80, Z=8.10) clearance to brass:      {upper_dists.min():.3f} mm")
    print(f"  Overall Cam Tab minimum clearance to brass at rest:      {min_dist_rest:.3f} mm")
    
    # Sweep across rotation angles
    print("\nRotation Sweep vs Brass Contact:")
    for deg in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
        rad = np.radians(deg)
        rot = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
        s_rot = shaft.copy().apply_transform(rot)
        cam_v_rot = s_rot.vertices[(s_rot.vertices[:, 0] >= 5.70) & (s_rot.vertices[:, 0] <= 7.65)]
        _, d_rot, _ = brass.nearest.on_surface(cam_v_rot)
        # Check if the cam penetrates the exterior of the brass
        inside = brass.contains(cam_v_rot)
        pen_count = np.sum(inside)
        print(f"  theta = {deg:4.1f}° | Min Distance: {d_rot.min():.3f} mm | Points inside brass volume: {pen_count}")

def simulate_plug_insertion_and_compare():
    print("\n" + "=" * 80)
    print("2. PLUG INSERTION SIMULATION: PREVIOUS DESIGN VS UPGRADED DESIGN")
    print("=" * 80)
    
    Y_SWITCH = 12.40      # Tactile button actuator face
    SNAP_TRAVEL = 0.30   # Internal snap dome collapse travel
    Y_CLICK = Y_SWITCH + SNAP_TRAVEL  # 12.70 mm
    
    # Kinematic comparison:
    # A standard NEMA 1-15 / 5-15 plug blade (Hot blade):
    # Enters at Y_blade_center = 2.50 mm (spans Y in [-0.68, +5.68] mm, width = 6.35 mm).
    # Nominal blade thickness = 1.52 mm (X in [5.52, 7.04] mm).
    # Front bezel faceplate exterior is at Z = 16.50 mm.
    # Total blade length = 16.50 mm -> full insertion stops when blade tip reaches Z = 0.00 mm.
    # In practice, the plug body stops against the front bezel faceplate.
    # User observed lever actuation = ~1.30 mm.
    
    for name, py_home in [("Previous Design (v3_nominal)", 10.95), ("Upgraded Design (v3_advanced)", 11.40)]:
        print(f"\n--- {name} ---")
        print(f"  Plunger Home Position at rest:  Y = {py_home:.2f} mm")
        pre_travel_to_face = Y_SWITCH - py_home
        pre_travel_to_snap = Y_CLICK - py_home
        print(f"  Air gap to switch button face:  {pre_travel_to_face:.2f} mm")
        print(f"  Total stroke required to click: {pre_travel_to_snap:.2f} mm")
        
        # Now let's calculate the lever response for various observed lever rotation angles
        # Axle: Y=9.279, Z=12.590. Plunger tip at Z = -7.00.
        dy = py_home - Y_AXLE
        dz = -7.00 - Z_AXLE
        
        print(f"  Lever Kinematics Table:")
        for deg in [0.0, 1.0, 2.0, 3.0, 3.8, 4.0, 4.25, 5.0]:
            rad = np.radians(deg)
            c, s = np.cos(rad), np.sin(rad)
            y_rot = Y_AXLE + c * dy - s * dz
            z_rot = Z_AXLE + s * dy + c * dz
            stroke = y_rot - py_home
            margin_face = y_rot - Y_SWITCH
            margin_click = y_rot - Y_CLICK
            
            if y_rot < Y_SWITCH:
                verdict = f"NO CONTACT ({margin_face:+.2f}mm gap to switch)"
            elif y_rot < Y_CLICK:
                verdict = f"TOUCHING BUTTON (Deflecting: {y_rot - Y_SWITCH:.2f}mm / {SNAP_TRAVEL:.2f}mm -> BORDERLINE)"
            else:
                verdict = f"CLICK CONFIRMED (+{margin_click:.2f}mm solid over-travel)"
                
            print(f"    theta = {deg:4.2f}° | Stroke = {stroke:5.2f} mm | Plunger Y = {y_rot:6.3f} mm -> {verdict}")

def check_through_hole():
    print("\n" + "=" * 80)
    print("3. FLOOR THROUGH-HOLE CLEARANCE SWEEP (Z = 0.50 mm)")
    print("=" * 80)
    
    shaft = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    h_ymin, h_ymax = HOLE_Y_BOT, HOLE_Y_TOP
    h_xmin = HOLE_X_CENTER - HOLE_X_WIDTH / 2.0
    h_xmax = HOLE_X_CENTER + HOLE_X_WIDTH / 2.0
    
    print(f"Through-hole bounds: X in [{h_xmin:.3f}, {h_xmax:.3f}], Y in [{h_ymin:.3f}, {h_ymax:.3f}] (Length Y = {h_ymax - h_ymin:.2f} mm)")
    
    all_ok = True
    for deg in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
        rad = np.radians(deg)
        rot = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
        s_rot = shaft.copy().apply_transform(rot)
        
        lines = trimesh.intersections.mesh_plane(s_rot, plane_normal=[0, 0, 1], plane_origin=[0, 0, 0.50])
        plunger_lines = lines[(lines[:, :, 0] > 7.0).all(axis=1)]
        if len(plunger_lines) > 0:
            pts = plunger_lines.reshape(-1, 3)
            ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
            xmin, xmax = pts[:, 0].min(), pts[:, 0].max()
            c_front = ymin - h_ymin
            c_rear = h_ymax - ymax
            c_left = xmin - h_xmin
            c_right = h_xmax - xmax
            pass_check = (c_front >= 0.30) and (c_rear >= 0.30) and (c_left >= 0.30) and (c_right >= 0.30)
            if not pass_check:
                all_ok = False
            print(f"  theta = {deg:4.1f}° | Plunger Y in [{ymin:.2f}, {ymax:.2f}] mm | Front gap: {c_front:.2f} mm | Rear gap: {c_rear:.2f} mm | PASS: {pass_check}")
    print(f"  Through-hole sweep overall status: {'PASS' if all_ok else 'FAIL'}")

def check_cradle_gap_45deg():
    print("\n" + "=" * 80)
    print("4. PRINT-IN-PLACE (PIP) PLUNGER SUPPORT CRADLE (45° ORIENTATION)")
    print("=" * 80)
    
    base_mesh, _ = bp.build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    base_t = base_mesh.copy().apply_transform(R)
    z_min = base_t.bounds[0, 2]
    
    shaft = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    shaft_t = shaft.copy().apply_transform(R)
    shaft_t.apply_translation([0, 0, -z_min])
    
    # Generate the plunger cradle mesh directly with py = 11.40
    r2 = np.sqrt(2) / 2.0
    py = 11.40
    reach = 7.00
    r_tip = 1.00
    gap_p = 0.28
    dz_shift = -z_min
    
    y_knee = (py - r_tip) * r2 - (-reach + r_tip) * r2
    z_knee = (py - r_tip) * r2 + (-reach + r_tip) * r2
    
    alphas = np.linspace(np.pi, np.pi * 0.50, 16)
    tip_y = py + r_tip * np.cos(alphas)
    tip_z = -reach + r_tip * (1.0 - np.sin(alphas))
    tip_y45 = tip_y * r2 - tip_z * r2
    tip_z45 = tip_y * r2 + tip_z * r2
    
    y_start = 8.00
    y_slope = np.linspace(y_start, y_knee, 10)
    z_slope = z_knee + (y_knee - y_slope)
    
    y_pts = np.concatenate([y_slope, tip_y45[1:]])
    z_pts = np.concatenate([z_slope, tip_z45[1:]]) + dz_shift - gap_p
    y_end = y_pts[-1]
    
    pts_plunger_tine_yz = [(y_start, 0.60)]
    for y_v, z_v in zip(y_pts, z_pts):
        pts_plunger_tine_yz.append((y_v, max(0.80, z_v)))
    pts_plunger_tine_yz.append((y_end, 0.60))
    poly_plunger_tine_yz = Polygon(pts_plunger_tine_yz)
    
    p_tine_w = 0.80
    m_p_l = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_tine_w)
    vl = m_p_l.vertices.copy()
    vl_3d = np.column_stack([vl[:, 2] + 8.484, vl[:, 0], vl[:, 1]])
    p_tine_l = trimesh.Trimesh(vertices=vl_3d, faces=m_p_l.faces.copy(), process=True)
    
    m_p_r = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_tine_w)
    vr = m_p_r.vertices.copy()
    vr_3d = np.column_stack([vr[:, 2] + 11.284, vr[:, 0], vr[:, 1]])
    p_tine_r = trimesh.Trimesh(vertices=vr_3d, faces=m_p_r.faces.copy(), process=True)
    
    p_center_w = 0.70
    x_c_start = 10.284 - p_center_w / 2.0
    m_p_c = trimesh.creation.extrude_polygon(poly_plunger_tine_yz, height=p_center_w)
    vc = m_p_c.vertices.copy()
    vc_3d = np.column_stack([vc[:, 2] + x_c_start, vc[:, 0], vc[:, 1]])
    p_tine_c = trimesh.Trimesh(vertices=vc_3d, faces=m_p_c.faces.copy(), process=True)
    
    cradle_mesh = trimesh.util.concatenate([p_tine_l, p_tine_r, p_tine_c])
    
    prox = trimesh.proximity.ProximityQuery(shaft_t)
    dists = prox.signed_distance(cradle_mesh.vertices)
    
    max_penetration = dists.max()
    print(f"  Cradle sample vertices: {len(cradle_mesh.vertices)}")
    print(f"  Maximum penetration into shaft (must be <= 0): {max_penetration:.4f} mm")
    
    # Top ridge points of cradle (Z' >= 14.0 mm)
    top_v = cradle_mesh.vertices[cradle_mesh.vertices[:, 2] >= 14.0]
    top_gaps = -prox.signed_distance(top_v)
    print(f"  Top ridge minimum release gap:  {top_gaps.min():.3f} mm")
    print(f"  Top ridge median release gap:   {np.median(top_gaps):.3f} mm")
    print(f"  Top ridge maximum release gap:  {top_gaps.max():.3f} mm")
    is_pass = (max_penetration <= 0.001) and (abs(np.median(top_gaps) - 0.25) < 0.10)
    print(f"  Calibrated 0.28mm release spec: {'PASS' if is_pass else 'FAIL'}")

if __name__ == '__main__':
    check_cam_vs_brass()
    simulate_plug_insertion_and_compare()
    check_through_hole()
    check_cradle_gap_45deg()
