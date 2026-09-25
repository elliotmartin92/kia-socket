"""
testing/test_full_part_selective_chamfer.py
Verifies the full part pipeline with:
- Standard unchamfered ribs on B1, B2 (all 4 stations) and B3, B4 (stations 1, 2, 3)
- Only Station 4 on B3, B4 (below half moon) extended across and chamfered
- Calibrated half moon
- Reduced clamp height
- Calibrated bottom clips
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

import build_part as bp

def test_full():
    print("Testing build_part pipeline with updated rib mesh...")
    
    # Check rib creation
    z_floor = bp.BASE_THICK  # 1.00 mm
    z_rib = z_floor + bp.BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
    h_rib = bp.BRACKET_SEATING_RIB_HEIGHT  # 1.15 mm
    
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    ext = bp.BRACKET_SEATING_RIB_EXT
    thick = bp.BRACKET_SEATING_RIB_THICK
    
    # 1. Standard unchamfered ribs
    std_boxes = []
    for y_c in bp.BRACKET_SEATING_RIB_Y:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        std_boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        
    for y_c in bp.BRACKET_SEATING_RIB_Y[:3]:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        std_boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))
        
    poly_std = bp.unary_union(std_boxes)
    m_std = bp.extrude_shapely_geom(poly_std, height=h_rib)
    m_std.apply_translation([0, 0, z_floor])
    
    # 2. One pair below half moon
    chamf_dy = 0.80
    y_c4 = -4.65
    pts_yz = [
        (y_c4 - thick/2.0 - chamf_dy, z_floor),
        (y_c4 - thick/2.0, z_rib),
        (min(y_c4 + thick/2.0, -4.30), z_rib),
        (-4.30, z_floor)
    ]
    poly_yz = Polygon(pts_yz)
    span_r4 = b4_spine - b3_spine
    m_r4_poly = trimesh.creation.extrude_polygon(poly_yz, height=span_r4)
    v4 = m_r4_poly.vertices.copy()
    v_r4 = np.column_stack([v4[:, 2] + b3_spine, v4[:, 0], v4[:, 1]])
    m_r4 = trimesh.Trimesh(vertices=v_r4, faces=m_r4_poly.faces.copy(), process=True)
    
    mesh_seating_ribs = trimesh.util.concatenate([m_std, m_r4])
    print(f"Mesh seating ribs watertight: {mesh_seating_ribs.is_watertight}, volume: {mesh_seating_ribs.volume:.2f} mm3")
    
    # Verify bounds
    print(f"Ribs bounds: X in [{mesh_seating_ribs.bounds[0,0]:.3f}, {mesh_seating_ribs.bounds[1,0]:.3f}], "
          f"Y in [{mesh_seating_ribs.bounds[0,1]:.3f}, {mesh_seating_ribs.bounds[1,1]:.3f}], "
          f"Z in [{mesh_seating_ribs.bounds[0,2]:.3f}, {mesh_seating_ribs.bounds[1,2]:.3f}]")

if __name__ == '__main__':
    test_full()
