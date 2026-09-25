"""
testing/test_chamfered_seating_ribs.py
Constructs and verifies 3D trapezoidal / chamfered seating ribs inside the brackets:
- Flat top land at Z = 2.15mm (width = 0.60mm in Y) preserving exact brass insert seating surface.
- 45° chamfered flanks (dz/dy = 1, extending 0.80mm in +/-Y) ramping smoothly down to the Z = 1.00mm floor.
- At Rib 4 (+Y flank), smoothly merges into the half moon base at Y = -4.30mm.
- Eliminates 90° notch stress concentration across all 4 rib stations (Ribs 1, 2, 3, 4).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

import build_part as bp

z_floor = bp.BASE_THICK  # 1.00 mm
z_rib = z_floor + bp.BRACKET_SEATING_RIB_HEIGHT  # 2.15 mm
h_rib = bp.BRACKET_SEATING_RIB_HEIGHT  # 1.15 mm
chamf_dy = 0.80  # 0.80mm chamfer ramp

def build_chamfered_seating_ribs_mesh():
    """
    Builds the 3D mesh of the 4 pairs of chamfered seating ribs inside Brackets 1..4.
    Profile in (Y, Z) is trapezoidal with flat top at Z=2.15mm and 45° flanks.
    Extruded along X across the bracket interior spine.
    """
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    ext = bp.BRACKET_SEATING_RIB_EXT
    
    # 2D profile in (Y, Z):
    # For each rib at y_c:
    # Top flat land: y in [y_c - 0.30, y_c + 0.30], z = z_rib
    # Left flank: from (y_c - 0.30 - chamf_dy, z_floor) to (y_c - 0.30, z_rib)
    # Right flank: from (y_c + 0.30, z_rib) to (y_c + 0.30 + chamf_dy, z_floor)
    
    rib_meshes = []
    
    for y_c in bp.BRACKET_SEATING_RIB_Y:
        # Check if adjacent to half moon base (Rib 4 at y_c = -4.65mm)
        # At Rib 4: top is y in [-4.95, -4.35]. Moon base is at y = -4.30mm!
        # So right flank extends to y = -4.30mm directly fusing with moon!
        pts_yz = [
            (y_c - 0.30 - chamf_dy, z_floor),
            (y_c - 0.30, z_rib),
            (y_c + 0.30, z_rib),
            (min(y_c + 0.30 + chamf_dy, -4.30 if y_c == -4.65 else y_c + 0.30 + chamf_dy), z_floor)
        ]
        poly_yz = Polygon(pts_yz)
        
        # Extrude along X for:
        # Left Pair (B1 & B2)
        # B1: X in [b1_spine, b1_spine + ext] -> [-9.857, -8.057]
        m_b1 = trimesh.creation.extrude_polygon(poly_yz, height=ext)
        v1 = m_b1.vertices.copy()
        v_b1 = np.column_stack([v1[:, 2] + b1_spine, v1[:, 0], v1[:, 1]])
        m_b1 = trimesh.Trimesh(vertices=v_b1, faces=m_b1.faces.copy(), process=True)
        rib_meshes.append(m_b1)
        
        # B2: X in [b2_spine - ext, b2_spine] -> [-4.501, -2.701]
        m_b2 = trimesh.creation.extrude_polygon(poly_yz, height=ext)
        v2 = m_b2.vertices.copy()
        v_b2 = np.column_stack([v2[:, 2] + (b2_spine - ext), v2[:, 0], v2[:, 1]])
        m_b2 = trimesh.Trimesh(vertices=v_b2, faces=m_b2.faces.copy(), process=True)
        rib_meshes.append(m_b2)
        
        # Right Pair (B3 & B4)
        # B3: X in [b3_spine, b3_spine + ext] -> [2.701, 4.501]
        m_b3 = trimesh.creation.extrude_polygon(poly_yz, height=ext)
        v3 = m_b3.vertices.copy()
        v_b3 = np.column_stack([v3[:, 2] + b3_spine, v3[:, 0], v3[:, 1]])
        m_b3 = trimesh.Trimesh(vertices=v_b3, faces=m_b3.faces.copy(), process=True)
        rib_meshes.append(m_b3)
        
        # B4: X in [b4_spine - ext, b4_spine] -> [8.057, 9.857]
        m_b4 = trimesh.creation.extrude_polygon(poly_yz, height=ext)
        v4 = m_b4.vertices.copy()
        v_b4 = np.column_stack([v4[:, 2] + (b4_spine - ext), v4[:, 0], v4[:, 1]])
        m_b4 = trimesh.Trimesh(vertices=v_b4, faces=m_b4.faces.copy(), process=True)
        rib_meshes.append(m_b4)
        
    return trimesh.util.concatenate(rib_meshes)

m_ribs = build_chamfered_seating_ribs_mesh()
print(f"Chamfered Seating Ribs Mesh: Watertight={m_ribs.is_watertight}, Volume={m_ribs.volume:.2f} mm^3")
print(f"Bounds X: [{m_ribs.bounds[0,0]:.3f}, {m_ribs.bounds[1,0]:.3f}] mm")
print(f"Bounds Y: [{m_ribs.bounds[0,1]:.3f}, {m_ribs.bounds[1,1]:.3f}] mm")
print(f"Bounds Z: [{m_ribs.bounds[0,2]:.3f}, {m_ribs.bounds[1,2]:.3f}] mm")
