"""
testing/test_front_buttress_y625.py
Test 3D mesh creation for front buttress starting at Y = 6.250mm and main towers at Y = 10.200mm shaft axis.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

BASE_THICK = 1.00
TOWER_HEIGHT = 13.09
TOWER_WALL_THICK = 1.50
TOWER_THROAT_W = 2.45

def build_towers_with_aligned_buttress():
    y_shaft = 10.200
    z_base = BASE_THICK
    z_top = z_base + TOWER_HEIGHT
    r_shaft = 1.50
    z_cradle_center = 12.590
    
    y_min_base = 7.171
    y_max_base = 13.771
    y_min_top = 7.471
    y_max_top = 13.101
    
    throat_w = TOWER_THROAT_W
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / r_shaft)
    
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_shaft * np.cos(p), z_cradle_center + r_shaft * np.sin(p)) for p in phi]
    
    y_left_top = y_shaft - half_w - 0.40
    y_right_top = y_shaft + half_w + 0.40
    
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
    
    # Buttress Struts
    x_left_outer = 3.900
    z_strut_top = 13.70
    
    strut_pts_xz = [
        (1.90, z_base),
        (x_left_outer, z_base),
        (x_left_outer, z_strut_top)
    ]
    poly_xz = Polygon(strut_pts_xz)
    
    # 1. Front Strut starting at Y = 6.250mm (top inner wall of Bracket 3!) and extending to Y = 7.971mm (thickness = 1.721mm in Y)
    front_strut_y_min = 6.250
    front_strut_y_max = 7.971
    front_strut_thick_y = front_strut_y_max - front_strut_y_min # 1.721 mm
    m_front_raw = trimesh.creation.extrude_polygon(poly_xz, height=front_strut_thick_y)
    v_front = m_front_raw.vertices.copy()
    v_front = np.column_stack([v_front[:, 0], v_front[:, 2] + front_strut_y_min, v_front[:, 1]])
    mesh_front = trimesh.Trimesh(vertices=v_front, faces=m_front_raw.faces.copy(), process=True)
    
    # 2. Rear Strut at Y in [12.571, 13.771]
    m_rear_raw = trimesh.creation.extrude_polygon(poly_xz, height=1.20)
    v_rear = m_rear_raw.vertices.copy()
    v_rear = np.column_stack([v_rear[:, 0], v_rear[:, 2] + 12.571, v_rear[:, 1]])
    mesh_rear = trimesh.Trimesh(vertices=v_rear, faces=m_rear_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right, mesh_front, mesh_rear])

t_mesh = build_towers_with_aligned_buttress()
print(f"Towers Mesh Watertight: {t_mesh.is_watertight}, Bounds: {t_mesh.bounds}")
print(f"Lowest Y extent of entire tower assembly = {t_mesh.bounds[0, 1]:.3f} mm")
assert abs(t_mesh.bounds[0, 1] - 6.250) < 1e-4, "Lowest Y must be exactly 6.250mm!"
print("Buttress alignment verified successfully!")
