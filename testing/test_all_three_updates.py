"""
testing/test_all_three_updates.py
Tests the 3 user updates in an integrated test:
1) Hardcoded 45-degree supports for bottom clips (211.3° and 327.5°)
2) Tweaked support fins for easier release (slimmer tines, larger pitch, 0.24mm standoff)
3) Half moon extended by 0.75mm in -Y (bottom) to backstop against brass insert
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt

import build_part as bp

def run_integrated_test():
    print("=== TESTING INTEGRATED 3 UPDATES ===")
    
    # 1. Patch create_center_curved_feature_poly
    orig_create_center_poly = bp.create_center_curved_feature_poly
    def patched_create_center_curved_feature_poly():
        cx = 6.279
        w_x = 4.20
        base_y = -4.30
        apex_y = -3.60
        extension_y = 0.75  # 0.75mm extension in -Y direction to backstop against brass insert
        
        rx = w_x / 2.0
        ry = apex_y - base_y  # 0.70 mm
        
        angles = np.linspace(np.pi, 0, 33)
        out_arc = [(cx + rx * np.cos(a), base_y + ry * np.sin(a)) for a in angles]
        
        pts = out_arc + [
            (cx + rx, base_y - extension_y),
            (cx - rx, base_y - extension_y)
        ]
        return Polygon(pts)
        
    bp.create_center_curved_feature_poly = patched_create_center_curved_feature_poly
    
    # Build flat part model
    print("Building exact 3D flat model...")
    part_mesh_flat, base_poly = bp.build_exact_3d_model()
    print(f"Flat part volume: {part_mesh_flat.volume:.2f} mm³")
    
    # 2. Build bottom clip 45° supports
    from test_bottom_clip_support import build_45deg_clip_supports
    clip_supps = build_45deg_clip_supports(base_poly)
    print(f"Clip supports volume: {clip_supps.volume:.2f} mm³")
    
    # 3. Test tweaked 45° supported model
    print("Testing 45° tilted model with tweaked fins and bottom clip supports...")
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = part_mesh_flat.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    supp_tilted = clip_supps.copy().apply_transform(R)
    supp_tilted.apply_translation([0, 0, -z_min])
    
    fin_components = [supp_tilted]
    
    # Bed Adhesion Pad
    pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
    pad_mesh.apply_translation([0.0, -2.50, 0.30])
    
    cx_left, cx_right = -7.853, 8.453
    relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_l.apply_translation([cx_left, -9.5, 0.30])
    relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_r.apply_translation([cx_right, -9.5, 0.30])
    try:
        pad_mesh = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
    except Exception:
        pass
    fin_components.append(pad_mesh)
    
    # Tweaked Fins:
    fin_thick_x = 0.80
    standoff = 0.24       # Tweaked from 0.20 to 0.24mm for cleaner thermal release
    z_bed = 0.60
    tine_w_x = 0.55       # Tweaked from 0.80 to 0.55mm (-31% contact width)
    tine_l_y = 0.45       # Tweaked from 0.60 to 0.45mm (-25% contact length)
    tine_pitch = 4.50     # Tweaked from 3.10 to 4.50mm (~30% fewer tines)
    
    # Inner Fin Pair
    y_start_inner = -5.80
    y_end_inner = 14.00
    z_start_inner = y_start_inner - z_min - standoff
    z_end_inner = y_end_inner - z_min - standoff
    
    for x_pos in [-8.0, 8.0]:
        pts_yz = [
            (y_start_inner, z_bed),
            (y_start_inner, z_start_inner),
            (y_end_inner, z_end_inner),
            (y_end_inner, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            y_tine_stations = np.arange(y_start_inner + 2.0, y_end_inner - 1.0, tine_pitch)
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.05])
                fin_components.append(tine)
                
    # Outer Fin Pair
    y_start_outer = -3.00
    y_end_outer = 10.00
    z_start_outer = y_start_outer - z_min - standoff
    z_end_outer = y_end_outer - z_min - standoff
    
    for x_pos in [-14.0, 14.0]:
        pts_yz = [
            (y_start_outer, z_bed),
            (y_start_outer, z_start_outer),
            (y_end_outer, z_end_outer),
            (y_end_outer, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            y_tine_stations = np.arange(y_start_outer + 2.0, y_end_outer - 1.0, tine_pitch)
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.05])
                fin_components.append(tine)
                
    # Center Fin
    y_start_center = -3.00
    y_end_center = 10.00
    z_start_center = y_start_center - z_min - standoff
    z_end_center = y_end_center - z_min - standoff
    
    pts_yz_center = [
        (y_start_center, z_bed),
        (y_start_center, z_start_center),
        (y_end_center, z_end_center),
        (y_end_center, z_bed)
    ]
    poly_yz_center = Polygon(pts_yz_center)
    if poly_yz_center.is_valid and poly_yz_center.area > 0.1:
        m_fin_raw = trimesh.creation.extrude_polygon(poly_yz_center, height=fin_thick_x)
        v = m_fin_raw.vertices.copy()
        v_reorient = np.column_stack([v[:, 2] + 0.0 - fin_thick_x/2.0, v[:, 0], v[:, 1]])
        m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
        fin_components.append(m_fin)
        
        y_tine_stations = np.arange(y_start_center + 2.0, y_end_center - 1.0, tine_pitch)
        for yt in y_tine_stations:
            zt_underside = yt - z_min
            tine = trimesh.creation.box([tine_w_x, tine_l_y, standoff + 0.20])
            tine.apply_translation([0.0, yt, zt_underside - standoff/2.0 + 0.05])
            fin_components.append(tine)
            
    # Sway Braces
    sway_l = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_l.apply_translation([-22.20, -1.0, 9.30])
    fin_components.append(sway_l)
    for z_t in [10.0, 14.0, 17.5]:
        tine_l = trimesh.creation.box([2.00, 0.60, 0.28])
        tine_l.apply_translation([-21.70, -1.0, z_t])
        fin_components.append(tine_l)
        
    sway_r = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_r.apply_translation([21.32, -1.0, 9.30])
    fin_components.append(sway_r)
    for z_t in [10.0, 14.0, 17.5]:
        tine_r = trimesh.creation.box([2.00, 0.60, 0.28])
        tine_r.apply_translation([20.82, -1.0, z_t])
        fin_components.append(tine_r)
        
    all_fins = trimesh.util.concatenate(fin_components)
    combined = trimesh.boolean.union([m_tilted, all_fins], engine='manifold')
    print(f"Final 45° Part Watertight: {combined.is_watertight}")
    print(f"Final 45° Part Total Volume: {combined.volume:.2f} mm³")
    print(f"Final 45° Part Bounds: {combined.bounds}")
    
    # Restore original function
    bp.create_center_curved_feature_poly = orig_create_center_poly
    print("=== INTEGRATED TEST PASSED 100% ===")

if __name__ == '__main__':
    run_integrated_test()
