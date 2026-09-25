"""
testing/test_selective_rib_chamfer.py
Tests updating seating ribs so that:
1. ONLY the one pair below the half moon (Right side, Y = -4.65) is chamfered and extended all the way across.
2. ALL other ribs (Left side Y = 5.25, 1.95, -1.35, -4.65; Right side Y = 5.25, 1.95, -1.35) are standard unchamfered rectangular ribs.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
import matplotlib.pyplot as plt

import build_part as bp

def test_build_ribs():
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
    # Left side: all 4 stations
    # Right side: top 3 stations (5.25, 1.95, -1.35)
    std_boxes = []
    # Left pair (B1 & B2) - all 4 stations
    for y_c in bp.BRACKET_SEATING_RIB_Y:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        std_boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        
    # Right pair (B3 & B4) - only top 3 stations
    for y_c in bp.BRACKET_SEATING_RIB_Y[:3]:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        std_boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        std_boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))
        
    poly_std = bp.unary_union(std_boxes)
    m_std = bp.extrude_shapely_geom(poly_std, height=h_rib)
    m_std.apply_translation([0, 0, z_floor])
    
    # 2. The ONE pair below the half moon (Right pair, y_c = -4.65)
    # Extends all the way across from b3_spine (2.701) to b4_spine (9.857) to become one
    # Chamfered on -Y flank
    chamf_dy = 0.80  # 0.80mm ramp (or 1.15mm for 45 deg)
    y_c4 = -4.65
    pts_yz = [
        (y_c4 - thick/2.0 - chamf_dy, z_floor), # -5.75, 1.00
        (y_c4 - thick/2.0, z_rib),              # -4.95, 2.15
        (min(y_c4 + thick/2.0, -4.30), z_rib),  # -4.35, 2.15
        (-4.30, z_floor)                        # -4.30, 1.00 (meets half moon base)
    ]
    poly_yz = Polygon(pts_yz)
    span_r4 = b4_spine - b3_spine
    m_r4_poly = trimesh.creation.extrude_polygon(poly_yz, height=span_r4)
    v4 = m_r4_poly.vertices.copy()
    v_r4 = np.column_stack([v4[:, 2] + b3_spine, v4[:, 0], v4[:, 1]])
    m_r4 = trimesh.Trimesh(vertices=v_r4, faces=m_r4_poly.faces.copy(), process=True)
    
    # Combine
    m_combined_ribs = trimesh.util.concatenate([m_std, m_r4])
    print(f"Combined ribs: watertight={m_combined_ribs.is_watertight}, volume={m_combined_ribs.volume:.2f} mm3")
    
    # Plot top-down and 3D comparison
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot bracket outlines
    for b_pts, name in [(bp.bracket_1_raw_pts, 'B1'), (bp.bracket_2_raw_pts, 'B2'),
                        (bp.bracket_3_raw_pts, 'B3'), (bp.bracket_4_raw_pts, 'B4')]:
        arr = np.array(b_pts)
        ax.plot(arr[:, 0], arr[:, 1], 'k--', alpha=0.5, label=f'{name} outline')
        
    # Plot standard ribs (blue)
    for b in std_boxes:
        bx, by = b.exterior.xy
        ax.fill(bx, by, color='royalblue', alpha=0.6)
        
    # Plot Rib 4 continuous chamfered rib (green)
    r4_poly_2d = box(b3_spine, y_c4 - thick/2.0 - chamf_dy, b4_spine, -4.30)
    rx, ry = r4_poly_2d.exterior.xy
    ax.fill(rx, ry, color='limegreen', alpha=0.7, label='One Pair Below Half Moon (Extended Across & Chamfered)')
    
    # Plot half moon (magenta)
    hm_poly = bp.create_center_curved_feature_poly()
    hx, hy = hm_poly.exterior.xy
    ax.fill(hx, hy, color='magenta', alpha=0.7, label='Half Moon')
    
    ax.set_aspect('equal')
    ax.set_title('Updated Rib Configuration:\nOnly One Pair Below Half Moon Extended Across & Chamfered', fontsize=12, fontweight='bold')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('testing/updated_ribs_topdown.png', dpi=200)
    print("Saved testing/updated_ribs_topdown.png")

if __name__ == '__main__':
    test_build_ribs()
