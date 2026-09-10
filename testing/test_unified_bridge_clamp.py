"""
testing/test_unified_bridge_clamp.py
Prototype and verify a Single Unified 1-Piece Bridge Clamp that joins the
Left and Right clamps into one monolithic component anchoring both towers.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh
from build_clamp import (
    build_tower_clamp_mesh, get_saddle_polygon_yz, get_side_wall_polygon_yz,
    extrude_xz, extrude_yz, unary_union_meshes, Z_TOP, CLAMP_ROOF_THICK
)

def build_unified_clamp_mesh(in_assembly_coords=True):
    """
    Builds the 1-Piece Unified Bridge Clamp:
    - Left clamp on Left Tower (X in [3.00, 5.375])
    - Right clamp on Right Tower (X in [13.125, 15.50])
    - Rigid Rear Cross-Tie Bar spanning X in [5.375, 13.125] at Y in [12.18, 13.38], Z in [13.70, 14.99]
    """
    c_left = build_tower_clamp_mesh(tower_side='left', in_assembly_coords=True)
    c_right = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)
    
    # 2D cross-section of the rear tie bar in (Y, Z)
    # Rear outer face is Y in [12.18, 13.38]
    # Z in [13.70, 14.99]
    tie_pts_yz = [
        (12.18, 13.70),
        (12.18, 14.99),
        (13.38, 14.99),
        (13.38, 13.70)
    ]
    poly_tie_yz = Polygon(tie_pts_yz)
    
    # Extrude across the central span between Left and Right clamps:
    # X from 5.375 to 13.125 (height = 7.75mm)
    m_tie = extrude_yz(poly_tie_yz, height=13.125 - 5.375, x_offset=5.375)
    
    unified_clamp = unary_union_meshes([c_left, m_tie, c_right])
    
    if in_assembly_coords:
        return unified_clamp
    else:
        # Pre-orient flat on print bed: top roof down at Z = 0.00mm
        m_bed = unified_clamp.copy()
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

if __name__ == '__main__':
    print("Testing Unified 1-Piece Bridge Clamp...")
    u_clamp = build_unified_clamp_mesh(in_assembly_coords=True)
    print("Unified Clamp Watertight:", u_clamp.is_watertight, "Volume:", u_clamp.volume)
    print("Bounds X:", u_clamp.bounds[0,0], "to", u_clamp.bounds[1,0])
    print("Bounds Y:", u_clamp.bounds[0,1], "to", u_clamp.bounds[1,1])
    print("Bounds Z:", u_clamp.bounds[0,2], "to", u_clamp.bounds[1,2])
    
    # Check dynamic rotation collision with rocker
    shaft = build_shaft_rocker_mesh(in_assembly_coords=True)
    angles = [0, 5, 10, 15, 20]
    for deg in angles:
        theta = np.radians(deg)
        R = trimesh.transformations.rotation_matrix(theta, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
        s_rot = shaft.copy()
        s_rot.apply_transform(R)
        
        # Check collision with tie bar between X in [5.375, 13.125]
        v_mid = s_rot.vertices[(s_rot.vertices[:, 0] >= 5.375) & (s_rot.vertices[:, 0] <= 13.125)]
        # Distance to tie bar box: Y in [12.18, 13.38], Z in [13.70, 14.99]
        coll = v_mid[(v_mid[:, 1] >= 12.18) & (v_mid[:, 2] >= 13.70)]
        print(f"  Theta = {deg:2d} deg: Collision points with Rear Tie-Bar: {len(coll)}")
        assert len(coll) == 0, f"Collision detected at theta = {deg} deg!"
        
    print("-> 100% ZERO COLLISION during full dynamic operation!")
