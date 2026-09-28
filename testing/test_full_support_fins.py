import trimesh
import numpy as np
from shapely.geometry import Polygon
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model

def test_support_fins(base_mesh):
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    fin_components = []
    
    # 1. Monolithic Bed Adhesion Pad
    # Footprint: X in [-24.0, 24.0], Y in [-19.0, 14.0], Z in [0, 0.60]
    pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
    pad_mesh.apply_translation([0.0, -2.50, 0.30])
    fin_components.append(pad_mesh)
    
    # 2. Main Twin Support Fins under Backplate (Full length from Y = -11.5 up to Y = +12.30)
    fin_thick_x = 0.80  # 2 perimeters
    standoff = 0.20     # 0.20mm release gap (Slant3D spec)
    z_bed = 0.60
    
    y_start = -11.50
    y_end = 12.30
    z_start = y_start - z_min - standoff
    z_end = y_end - z_min - standoff
    
    print(f"Main Fins: Y in [{y_start:.2f}, {y_end:.2f}], Fin top Z in [{z_start:.2f}, {z_end:.2f}]")
    print(f"Part Underside Z in [{y_start - z_min:.2f}, {y_end - z_min:.2f}] (standoff = {standoff:.2f}mm)")
    
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
            
            # Horizontal breakaway tines along this fin
            y_tine_stations = np.arange(y_start + 1.5, y_end - 0.5, 3.2)
            print(f"Tine stations count for X={x_pos}: {len(y_tine_stations)}, from Y={y_tine_stations[0]:.2f} to Y={y_tine_stations[-1]:.2f}")
            for yt in y_tine_stations:
                zt_underside = yt - z_min
                tine = trimesh.creation.box([fin_thick_x, 0.60, standoff + 0.35])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.10])
                fin_components.append(tine)
                
    # 3. Upgraded Lateral Sway Braces
    # Left sway wall
    sway_l = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_l.apply_translation([-22.20, -1.0, 9.30])
    fin_components.append(sway_l)
    for z_t in [10.0, 14.0, 17.5]:
        tine_l = trimesh.creation.box([2.00, 1.00, 0.40])
        tine_l.apply_translation([-21.70, -1.0, z_t])
        fin_components.append(tine_l)
        
    # Right sway wall
    sway_r = trimesh.creation.box([1.00, 8.0, 17.40])
    sway_r.apply_translation([21.32, -1.0, 9.30])
    fin_components.append(sway_r)
    for z_t in [10.0, 14.0, 17.5]:
        tine_r = trimesh.creation.box([2.00, 1.00, 0.40])
        tine_r.apply_translation([20.82, -1.0, z_t])
        fin_components.append(tine_r)
        
    all_fins = trimesh.util.concatenate(fin_components)
    combined = trimesh.util.concatenate([m_tilted, all_fins])
    return combined, m_tilted

part_flat, _ = build_exact_3d_model()
comb, tilted = test_support_fins(part_flat)
print(f"Combined mesh bounds:\n  X: {comb.bounds[0, 0]:.2f} to {comb.bounds[1, 0]:.2f}\n  Y: {comb.bounds[0, 1]:.2f} to {comb.bounds[1, 1]:.2f}\n  Z: {comb.bounds[0, 2]:.2f} to {comb.bounds[1, 2]:.2f}")
print("Combined is watertight:", comb.is_watertight)
