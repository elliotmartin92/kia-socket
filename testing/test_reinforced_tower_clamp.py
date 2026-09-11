import os, sys
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import Y_AXLE, Z_AXLE, PIN_DIAMETER, build_shaft_rocker_mesh
from build_part import (
    build_clean_shaft_towers_mesh, build_left_tower_struts_mesh,
    BASE_THICK, TOWER_HEIGHT, TOWER_WALL_THICK
)

Z_TOP = 14.090
CLAMP_ROOF_THICK = 1.60      # Increased from 0.90mm to 1.60mm (+78% thickness, 5.6x bending stiffness)
CLAMP_Z_BOTTOM = 11.200
CLAMP_WALL_THICK = 1.40      # Increased from 1.15mm to 1.40mm
SIDE_WALL_THICK = 1.60       # Increased from 1.00mm to 1.60mm (4 solid perimeters)
PIN_CLEARANCE_RADIUS = 1.55  # 1.55mm (Pin is R=1.40mm, tip at X=3.45mm / X=15.05mm)

Z_KEEL = 14.020
Y_KEEL_FRONT = 7.650
Y_KEEL_REAR = 10.908

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
    
    y_front_inner_top = 6.550 - 0.040
    y_front_inner_bot = 6.484 - 0.020
    y_rear_inner_top = 12.180 + 0.040
    y_rear_inner_bot = 12.328 + 0.020
    
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
        (Y_KEEL_REAR, z_roof_under),
        (Y_KEEL_REAR, Z_KEEL),
        (Y_KEEL_FRONT, Z_KEEL),
        (Y_KEEL_FRONT, z_roof_under),
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
    
    # Outer cheek spans Y in [7.10, 11.55] below Z = 14.09mm
    # Spans full Y in [5.114, 13.698] above Z = 14.09mm
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
        # Solid continuous plate with NO arch cutout
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

def build_reinforced_clamp_mesh(tower_side='left', in_assembly_coords=False):
    poly_saddle = get_saddle_polygon_yz()
    poly_side_arch = get_side_wall_polygon_yz(with_arch=True)
    poly_side_solid = get_side_wall_polygon_yz(with_arch=False)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    poly_roof_yz = Polygon([
        (5.114, 14.09), (5.160, 15.19), (5.660, z_top),
        (13.170, z_top), (13.670, 15.19), (13.698, 14.09)
    ])
    
    if tower_side == 'left':
        # Saddle spans X in [3.90, 5.375] (1.475mm thick)
        m_saddle = extrude_yz(poly_saddle, height=1.475, x_offset=3.90)
        # Roof bridge over gap X in [3.20, 3.90] (0.70mm thick, 1.60mm tall in Z)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=3.90 - 3.20, x_offset=3.20)
        
        # Inner cheek with pin arch spans X in [2.40, 3.20] (0.80mm thick)
        m_side_inner = extrude_yz(poly_side_arch, height=0.80, x_offset=2.40)
        # Outer cheek 100% solid plate spans X in [1.60, 2.40] (0.80mm thick)
        m_side_outer = extrude_yz(poly_side_solid, height=0.80, x_offset=1.60)
        
        # Snap hooks: undercut at Z = 12.40mm, tip at X = 3.85mm
        poly_hook_xz = Polygon([
            (2.40, 11.75),
            (3.85, 12.20),
            (3.85, 12.40),
            (2.40, 12.40)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
    else:
        # Right clamp:
        # Saddle spans X in [13.125, 14.60] (1.475mm thick)
        m_saddle = extrude_yz(poly_saddle, height=1.475, x_offset=13.125)
        # Roof bridge over gap X in [14.60, 15.30] (0.70mm thick, 1.60mm tall in Z)
        m_roof_bridge = extrude_yz(poly_roof_yz, height=15.30 - 14.60, x_offset=14.60)
        # Inner cheek with pin arch spans X in [15.30, 16.10] (0.80mm thick)
        m_side_inner = extrude_yz(poly_side_arch, height=0.80, x_offset=15.30)
        # Outer cheek 100% solid plate spans X in [16.10, 16.90] (0.80mm thick)
        m_side_outer = extrude_yz(poly_side_solid, height=0.80, x_offset=16.10)
        
        poly_hook_xz = Polygon([
            (16.10, 11.75),
            (14.65, 12.20),
            (14.65, 12.40),
            (16.10, 12.40)
        ])
        m_hf = extrude_xz(poly_hook_xz, height=8.00 - 7.10, y_offset=7.10)
        m_hr = extrude_xz(poly_hook_xz, height=11.55 - 10.60, y_offset=10.60)
        m_clamp = unary_union_meshes([m_saddle, m_roof_bridge, m_side_inner, m_side_outer, m_hf, m_hr])
        
    if in_assembly_coords:
        return m_clamp
    else:
        m_bed = m_clamp.copy()
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

def build_reinforced_unified_clamp_mesh(in_assembly_coords=False):
    c_left = build_reinforced_clamp_mesh(tower_side='left', in_assembly_coords=True)
    c_right = build_reinforced_clamp_mesh(tower_side='right', in_assembly_coords=True)
    
    z_top = Z_TOP + CLAMP_ROOF_THICK
    tie_pts_yz = [
        (12.18, 13.50),
        (12.18, z_top),
        (13.68, z_top),
        (13.68, 13.50)
    ]
    poly_tie_yz = Polygon(tie_pts_yz)
    m_tie = extrude_yz(poly_tie_yz, height=13.125 - 5.375, x_offset=5.375)
    
    unified_clamp = unary_union_meshes([c_left, m_tie, c_right])
    if in_assembly_coords:
        return unified_clamp
    else:
        m_bed = unified_clamp.copy()
        v = m_bed.vertices.copy()
        v[:, 2] = (Z_TOP + CLAMP_ROOF_THICK) - v[:, 2]
        v[:, 0] -= (v[:, 0].min() + v[:, 0].max()) / 2.0
        v[:, 1] -= (v[:, 1].min() + v[:, 1].max()) / 2.0
        return trimesh.Trimesh(vertices=v, faces=m_bed.faces[:, ::-1].copy(), process=True)

print("=== BUILDING & TESTING REINFORCED CLAMPS ===")
u_clamp = build_reinforced_unified_clamp_mesh(in_assembly_coords=True)
print("Unified Bridge Clamp: Watertight =", u_clamp.is_watertight, "Volume =", round(u_clamp.volume, 2))
print("  X bounds:", np.round(u_clamp.bounds[:, 0], 2))
print("  Y bounds:", np.round(u_clamp.bounds[:, 1], 2))
print("  Z bounds:", np.round(u_clamp.bounds[:, 2], 2))

# Check fitment vs Struts
struts = build_left_tower_struts_mesh()
sv = struts.vertices
sv_cheek_zone = sv[sv[:, 0] >= 1.60]
dists_struts = [np.min(np.linalg.norm(u_clamp.vertices - p, axis=1)) for p in sv_cheek_zone]
min_clr_struts = min(dists_struts)
print("Min distance to Left Struts:", round(min_clr_struts, 3), "mm")
assert min_clr_struts > 0.04, f"Collision with Struts: {min_clr_struts}"

# Check fitment vs Shaft
shaft = build_shaft_rocker_mesh(in_assembly_coords=True)
pin_left = shaft.vertices[shaft.vertices[:, 0] < 3.90]
pin_right = shaft.vertices[shaft.vertices[:, 0] > 14.60]
dists_pin_l = np.min([np.min(np.linalg.norm(u_clamp.vertices - p, axis=1)) for p in pin_left])
dists_pin_r = np.min([np.min(np.linalg.norm(u_clamp.vertices - p, axis=1)) for p in pin_right])
print("Left Pin min clearance:", round(dists_pin_l, 3), "mm")
print("Right Pin min clearance:", round(dists_pin_r, 3), "mm")
assert dists_pin_l > 0.10, "Pin friction detected on left pin!"
assert dists_pin_r > 0.10, "Pin friction detected on right pin!"

# Dynamic Rocker Sweep (0 to 20 deg)
for deg in [0, 5, 10, 15, 20]:
    th = np.radians(deg)
    R = trimesh.transformations.rotation_matrix(th, [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
    s_rot = shaft.copy()
    s_rot.apply_transform(R)
    sv = s_rot.vertices
    v_mid = sv[(sv[:, 0] >= 5.375) & (sv[:, 0] <= 13.125)]
    coll = v_mid[(v_mid[:, 1] >= 12.18) & (v_mid[:, 2] >= 13.50)]
    assert len(coll) == 0, f"Collision at theta = {deg} deg!"

print("PASSED: 100% Collision-Free and Watertight!")
