"""
testing/test_watertight_sloped_insert.py
Builds and verifies 100% watertight, manifold sloped slit insert mesh.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
from shapely.geometry import Polygon, box

SLIT_W_X = 1.20
SLIT_LEN_Y = 3.50
SLIT_BOSS_HEIGHT = 2.47
INSERT_BODY_W_X = 3.60
INSERT_BODY_LEN_Y = 5.40
INSERT_KEY_W_X = 2.00
INSERT_KEY_LEN_Y = 4.30
INSERT_KEY_HEIGHT = 0.85

def create_frustum_mesh(w_bot, l_bot, w_top, l_top, z_bot, z_top):
    """Creates a solid watertight 6-faced rectangular frustum."""
    v_bot = np.array([
        [-w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2, -l_bot/2, z_bot],
        [ w_bot/2,  l_bot/2, z_bot],
        [-w_bot/2,  l_bot/2, z_bot],
    ])
    v_top = np.array([
        [-w_top/2, -l_top/2, z_top],
        [ w_top/2, -l_top/2, z_top],
        [ w_top/2,  l_top/2, z_top],
        [-w_top/2,  l_top/2, z_top],
    ])
    verts = np.vstack([v_bot, v_top])
    
    # Faces with outward pointing normals:
    # Bottom face (Z = z_bot, normal -Z): 0, 3, 2, 1 -> [0, 3, 2], [0, 2, 1]
    # Top face (Z = z_top, normal +Z): 4, 5, 6, 7 -> [4, 5, 6], [4, 6, 7]
    # Front face (-Y): 0, 1, 5, 4 -> [0, 1, 5], [0, 5, 4]
    # Right face (+X): 1, 2, 6, 5 -> [1, 2, 6], [1, 6, 5]
    # Back face (+Y): 2, 3, 7, 6 -> [2, 3, 7], [2, 7, 6]
    # Left face (-X): 3, 0, 4, 7 -> [3, 0, 4], [3, 4, 7]
    faces = [
        [0, 3, 2], [0, 2, 1],       # Bottom
        [4, 5, 6], [4, 6, 7],       # Top
        [0, 1, 5], [0, 5, 4],       # Front (-Y)
        [1, 2, 6], [1, 6, 5],       # Right (+X)
        [2, 3, 7], [2, 7, 6],       # Back (+Y)
        [3, 0, 4], [3, 4, 7],       # Left (-X)
    ]
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)

def build_sloped_insert_solid(draft_deg=5.0, key_taper=0.25):
    z0 = 0.00
    z1 = SLIT_BOSS_HEIGHT  # 2.47mm
    z2 = z1 + INSERT_KEY_HEIGHT  # 3.32mm
    
    # 1. Shroud body frustum (sloped walls from shoulder z1 down to bottom face z0)
    dx_body = z1 * np.tan(np.radians(draft_deg))  # ~0.22mm per side
    w_bot = INSERT_BODY_W_X - 2 * dx_body   # ~3.16mm
    l_bot = INSERT_BODY_LEN_Y - 2 * dx_body # ~4.96mm
    
    m_body = create_frustum_mesh(w_bot, l_bot, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, z0, z1)
    
    # 2. Male key frustum (tapered top from base z1 up to top z2)
    w_key_top = INSERT_KEY_W_X - 2 * key_taper   # 1.50mm
    l_key_top = INSERT_KEY_LEN_Y - 2 * key_taper # 3.80mm
    
    m_key = create_frustum_mesh(INSERT_KEY_W_X, INSERT_KEY_LEN_Y, w_key_top, l_key_top, z1, z2)
    
    # Union solid body and key
    m_solid = m_body.union(m_key, engine='manifold')
    
    # 3. Internal through-hole (1.20mm x 3.50mm) cut all the way through Z in [-0.5, 4.0]
    hole_cutter = trimesh.creation.box([SLIT_W_X, SLIT_LEN_Y, z2 + 2.0])
    hole_cutter.apply_translation([0, 0, (z2 + 2.0)/2.0 - 0.5])
    
    m_insert = m_solid.difference(hole_cutter, engine='manifold')
    return m_insert

def test():
    mesh = build_sloped_insert_solid()
    print("=== WATERTIGHT SLOPED INSERT TEST ===")
    print(f"Is Watertight: {mesh.is_watertight}")
    print(f"Volume: {mesh.volume:.3f} mm^3")
    print(f"Euler Number: {mesh.euler_number} (Expected 0 for torus/through-hole)")
    print(f"Bounds X: [{mesh.bounds[0,0]:.3f}, {mesh.bounds[1,0]:.3f}] mm")
    print(f"Bounds Y: [{mesh.bounds[0,1]:.3f}, {mesh.bounds[1,1]:.3f}] mm")
    print(f"Bounds Z: [{mesh.bounds[0,2]:.3f}, {mesh.bounds[1,2]:.3f}] mm")
    assert mesh.is_watertight, "Mesh is not watertight!"
    assert mesh.volume > 0, "Volume must be positive!"
    print("SUCCESS: 100% Watertight, Manifold Sloped Slit Insert created!")

if __name__ == '__main__':
    test()
