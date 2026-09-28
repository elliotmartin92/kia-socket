import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
from test_full_monolithic_assembly import build_monolithic_part_model

part_mono, base_poly_clean = build_monolithic_part_model()

# Now run 45 deg tilt and support generation with insert clearance
def build_45deg_supported_part_mesh_updated(base_mesh):
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    fin_components = []
    
    # 1. Monolithic Bed Adhesion Pad (48mm wide x 33mm long x 0.60mm thick on bed Z in [0, 0.60]mm)
    pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
    pad_mesh.apply_translation([0.0, -2.50, 0.30])
    
    # In-place shroud tip relief windows to prevent tip fusing into bed pad
    cx_left, cx_right = -7.853, 8.453
    relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_l.apply_translation([cx_left, -9.5, 0.30])
    relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
    relief_r.apply_translation([cx_right, -9.5, 0.30])
    pad_mesh = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
    fin_components.append(pad_mesh)
    
    # 2. Main Twin Support Fins (from Y = -5.80mm to Y = +12.30mm, clear of in-place shrouds)
    fin_thick_x = 0.80
    standoff = 0.20
    z_bed = 0.60
    y_start = -5.80
    y_end = 12.30
    z_start = y_start - z_min - standoff
    z_end = y_end - z_min - standoff
    
    from shapely.geometry import Polygon
    for x_pos in [-8.0, 8.0]:
        pts_yz = [
            (y_start, z_bed),
            (y_start, z_start),
            (y_end, z_end),
            (y_end, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            y_tine_stations = np.arange(y_start + 1.5, y_end, 3.1)
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([fin_thick_x, 0.60, standoff + 0.35])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.10])
                fin_components.append(tine)
                
    # 3. Sway Braces
    sway_l = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_l.apply_translation([-22.20, -1.0, 9.30])
    fin_components.append(sway_l)
    for z_t in [10.0, 14.0, 17.5]:
        tine_l = trimesh.creation.box([2.00, 1.00, 0.40])
        tine_l.apply_translation([-21.70, -1.0, z_t])
        fin_components.append(tine_l)
        
    sway_r = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_r.apply_translation([21.32, -1.0, 9.30])
    fin_components.append(sway_r)
    for z_t in [10.0, 14.0, 17.5]:
        tine_r = trimesh.creation.box([2.00, 1.00, 0.40])
        tine_r.apply_translation([20.82, -1.0, z_t])
        fin_components.append(tine_r)

    all_fins = trimesh.util.concatenate(fin_components)
    combined = trimesh.util.concatenate([m_tilted, all_fins])
    return combined, m_tilted, all_fins

comb, tilted, fins = build_45deg_supported_part_mesh_updated(part_mono)
print("Comb bounds:\n", comb.bounds)
print("Comb watertight:", comb.is_watertight)
print("All bodies:", len(comb.split(only_watertight=False)))
