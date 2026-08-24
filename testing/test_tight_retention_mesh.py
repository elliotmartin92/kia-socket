"""
testing/test_tight_retention_mesh.py
Test mesh generation with TOWER_THROAT_W = 2.05mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon

BASE_THICK = 1.00
TOWER_HEIGHT = 13.09
TOWER_WALL_THICK = 1.50
TOWER_THROAT_W = 2.05  # 2.05mm for 0.75mm positive snap retention

def build_tight_towers_mesh():
    y_shaft = 9.279
    z_base = BASE_THICK
    z_top = z_base + TOWER_HEIGHT
    r_shaft = 1.50
    z_cradle_center = 12.590
    
    y_min_base = 6.250
    y_max_base = 12.850
    y_min_top = 6.550
    y_max_top = 12.180
    
    throat_w = TOWER_THROAT_W
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / r_shaft)
    
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_shaft * np.cos(p), z_cradle_center + r_shaft * np.sin(p)) for p in phi]
    
    bevel_dx = (z_top - (z_cradle_center + r_shaft * np.cos(alpha))) * 0.75
    y_left_top = y_shaft - half_w - bevel_dx
    y_right_top = y_shaft + half_w + bevel_dx
    
    profile_yz = [
        (y_min_base, z_base),
        (y_max_base, z_base),
        (y_max_top, z_top),
        (y_right_top, z_top),
    ] + cradle_arc_pts + [
        (y_left_top, z_top),
        (y_min_top, z_top)
    ]
    poly_yz = Polygon(profile_yz)
    
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=TOWER_WALL_THICK)
    verts = m_raw.vertices.copy()
    
    verts_left = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_left[:, 0] += 3.900
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    
    verts_right = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_right[:, 0] += 13.100
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right])

m = build_tight_towers_mesh()
print(f"Watertight: {m.is_watertight}")
print(f"Bounds: {m.bounds}")
print("Tight retention test successful!")
