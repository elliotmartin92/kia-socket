import os, sys
import trimesh
import numpy as np
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh
from build_part import (
    build_clean_shaft_towers_mesh, build_left_tower_struts_mesh,
    BASE_THICK, TOWER_HEIGHT, TOWER_WALL_THICK
)

Z_TOP = 14.090
CLAMP_ROOF_THICK = 1.60      # Z_top = 15.690mm
CLAMP_Z_BOTTOM = 11.200
CLAMP_WALL_THICK = 1.40
SIDE_WALL_THICK = 1.60       # Total cheek thickness = 1.60mm (X: 1.60 to 3.20)
PIN_CLEARANCE_RADIUS = 1.85  # Increased from 1.55 to 1.85mm (+0.45mm radial air gap!)
Z_PIN_RELIEF = 14.500        # +0.51mm clear air gap above pin top (13.990mm)

def extrude_xz(poly_xz, height, y_offset=0.0):
    m_raw = trimesh.creation.extrude_polygon(poly_xz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 0], v[:, 2] + y_offset, v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces[:, ::-1].copy(), process=True)

def extrude_yz(poly_yz, height, x_offset=0.0):
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=height)
    v = m_raw.vertices.copy()
    v_new = np.column_stack([v[:, 2] + x_offset, v[:, 0], v[:, 1]])
    return trimesh.Trimesh(vertices=v_new, faces=m_raw.faces.copy(), process=True)

def unary_union_meshes(meshes):
    m_res = meshes[0]
    for m in meshes[1:]:
        m_res = m_res.union(m, engine='manifold')
    return m_res

def get_saddle_polygon_yz():
    z_top = Z_TOP + CLAMP_ROOF_THICK  # 15.690 mm
    z_roof_under = Z_TOP             # 14.090 mm
    z_bot = CLAMP_Z_BOTTOM           # 11.200 mm
    
    y_front_inner_top = 6.530
    y_front_inner_bot = 6.474
    y_rear_inner_top = 12.200
    y_rear_inner_bot = 12.338
    
    y_front_outer_top = y_front_inner_top - CLAMP_WALL_THICK
    y_front_outer_bot = y_front_inner_bot - CLAMP_WALL_THICK
    y_rear_outer_top = y_rear_inner_top + CLAMP_WALL_THICK
    y_rear_outer_bot = y_rear_inner_bot + CLAMP_WALL_THICK
    
    saddle_pts_yz = [
        (y_front_outer_bot, z_bot),
        (y_front_outer_top, z_top - 0.50),
        (y_front_outer_top + 0.50, z_top),
        (y_rear_outer_top - 0.50, z_top),
        (y_rear_outer_top, z_top - 0.50),
        (y_rear_outer_bot, z_bot),
        (y_rear_inner_bot, z_bot),
        (y_rear_inner_top, z_roof_under),
        (11.20, z_roof_under),
        (11.00, Z_PIN_RELIEF),  # Upward relief pocket: +0.51mm air gap over pin
        (7.55, Z_PIN_RELIEF),
        (7.35, z_roof_under),
        (y_front_inner_top, z_roof_under),
        (y_front_inner_bot, z_bot),
    ]
    return Polygon(saddle_pts_yz)

def get_side_wall_polygon_yz(with_arch=True):
    z_top = Z_TOP + CLAMP_ROOF_THICK
    y_c = Y_AXLE
    z_c = Z_AXLE
    R = PIN_CLEARANCE_RADIUS
    z_bot = 11.75
    
    if with_arch:
        arch_pts = []
        for p in np.linspace(0, np.pi, 32):
            arch_pts.append((y_c + R * np.cos(p), z_c + R * np.sin(p)))
            
        side_pts_yz = [
            (7.10, z_bot),
            (7.10, 14.09),
            (5.114, 14.09),
            (5.160, 15.19),
            (5.660, z_top),
            (13.170, z_top),
            (13.670, 15.19),
            (13.698, 14.09),
            (11.55, 14.09),
            (11.55, z_bot),
            (y_c + R, z_bot),
        ] + arch_pts + [
            (y_c - R, z_bot)
        ]
    else:
        side_pts_yz = [
            (7.10, z_bot),
            (7.10, 14.09),
            (5.114, 14.09),
            (5.160, 15.19),
            (5.660, z_top),
            (13.170, z_top),
            (13.670, 15.19),
            (13.698, 14.09),
            (11.55, 14.09),
            (11.55, z_bot),
        ]
    return Polygon(side_pts_yz)

def build_test_clamp(tower_side='left'):
    poly_saddle = get_saddle_polygon_yz()
    poly_side_arch = get_side_wall_polygon_yz(with_arch=True)
    poly_side_solid = get_side_wall_polygon_yz(with_arch=False)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    poly_roof_yz = Polygon([
        (5.114, 14.09), (5.160, 15.19), (5.660, z_top),
        (13.170, z_top), (13.670, 15.19), (13.698, 14.09)
    ])
    
    if tower_side == 'left':
        # Saddle spans X in [3.90, 5.30] (0.20mm axial margin to hub at 5.50)
        m_saddle = extrude_yz(poly_saddle, height=5.30 - 3.90, x_offset=3.90)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=3.90 - 3.20, x_offset=3.20)
        # Inner arched cheek: X in [2.20, 3.20] (1.00mm deep clearance cavity)
        m_side_inner = extrude_yz(poly_side_arch, height=1.00, x_offset=2.20)
        # Outer solid backplate: X in [1.60, 2.20] (0.60mm solid continuous wall)
        m_side_outer = extrude_yz(poly_side_solid, height=0.60, x_offset=1.60)
        
        poly_hook_xz = Polygon([
            (2.20, 11.75),
            (3.85, 12.15),
            (3.85, 12.35),
            (2.20, 12.35)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
    else:
        # Right clamp: Saddle spans X in [13.20, 14.60] (0.20mm axial margin to hub at 13.00)
        m_saddle = extrude_yz(poly_saddle, height=14.60 - 13.20, x_offset=13.20)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=15.30 - 14.60, x_offset=14.60)
        m_side_inner = extrude_yz(poly_side_arch, height=1.00, x_offset=15.30)
        m_side_outer = extrude_yz(poly_side_solid, height=0.60, x_offset=16.30)
        
        poly_hook_xz = Polygon([
            (16.30, 11.75),
            (14.65, 12.15),
            (14.65, 12.35),
            (16.30, 12.35)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
        
    return m_clamp

def build_test_unified():
    c_left = build_test_clamp('left')
    c_right = build_test_clamp('right')
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    tie_pts_yz = [
        (12.18, 13.50),
        (12.18, z_top),
        (13.68, z_top),
        (13.68, 13.50)
    ]
    poly_tie_yz = Polygon(tie_pts_yz)
    m_tie = extrude_yz(poly_tie_yz, height=13.20 - 5.30, x_offset=5.30)
    return unary_union_meshes([c_left, m_tie, c_right])

u_clamp = build_test_unified()
print("Watertight:", u_clamp.is_watertight, "Volume:", round(u_clamp.volume, 2))

# Comprehensive Pin Clearance & Kinematic Check
shaft = build_shaft_rocker_mesh(in_assembly_coords=True)

for deg in [0, 5, 10, 15, 20]:
    th = np.radians(deg)
    R = trimesh.transformations.rotation_matrix(th, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
    s_rot = shaft.copy()
    s_rot.apply_transform(R)
    
    dists = [np.min(np.linalg.norm(u_clamp.vertices - p, axis=1)) for p in s_rot.vertices]
    print(f"Rocker @ {deg:2d} deg: Min overall clearance to clamp = {min(dists):.3f} mm")

# Specific Pin Top Clearance:
pin_top_pts = shaft.vertices[(shaft.vertices[:, 2] > 13.5) & ((shaft.vertices[:, 0] < 5.4) | (shaft.vertices[:, 0] > 13.1))]
dists_top = [np.min(np.linalg.norm(u_clamp.vertices - p, axis=1)) for p in pin_top_pts]
print(f"Pin Top Clearance: min = {min(dists_top):.3f} mm, max = {max(dists_top):.3f} mm")
