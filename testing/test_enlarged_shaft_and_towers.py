"""
testing/test_enlarged_shaft_and_towers.py
Parametric prototype and verification for enlarged shaft/rocker and reinforced towers.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import (
    BASE_THICK, OUTER_WALL_HEIGHT, OUTER_WALL_THICK,
    get_exact_base_polygon, create_all_brackets_poly
)

# ==============================================================================
# PARAMETRIC SPECS FOR ENLARGED SHAFT & TOWERS
# ==============================================================================
Y_AXLE = 10.200       # Aligned directly over through-hole center (Y in [8.570, 13.082])
Z_AXLE = 12.590       # Pivot axis elevation

PIN_DIAMETER = 2.80   # Ø2.80mm pin (+47% diameter, 4.7x torsional stiffness over Ø1.90mm)
CRADLE_DIAMETER = 3.00 # Ø3.00mm cradle (0.20mm total rotation clearance / 0.10mm per side)
HUB_DIAMETER = 4.20   # Ø4.20mm heavy-duty structural hub barrel (+27% over Ø3.30mm)
TOTAL_AXLE_LEN = 11.50 # 11.50mm total length tip-to-tip
HUB_WIDTH = 7.50      # 7.50mm hub barrel (0.10mm clearance per side inside 7.70mm tower gap)
PIN_LEN = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0  # 2.00mm pin length per side

TOWER_THROAT_W = 2.45 # 2.45mm retention throat (0.35mm firm positive snap with Ø2.80mm pin, >250 deg wrap)
TOWER_HEIGHT = 13.09  # 13.09mm protrusion above floor (Total Z_top = 14.09mm, cradle center Z = 12.59mm)

X_LEFT_TOWER_OUTER = 3.900
X_LEFT_TOWER_INNER = 5.400
X_RIGHT_TOWER_INNER = 13.100
X_RIGHT_TOWER_OUTER = 14.600
X_TOWER_CENTER = (X_LEFT_TOWER_INNER + X_RIGHT_TOWER_INNER) / 2.0  # 9.25 mm

HOLE_X_CENTER = 10.284
HOLE_X_WIDTH = 5.352
HOLE_Y_CENTER = 10.826
HOLE_Y_LEN = 4.512

PLUNGER_WIDTH_X = 4.40 # 4.40mm wide plunger (centered in 5.35mm hole with ~0.48mm lateral clearance)
CAM_WIDTH_X = 2.70     # 2.70mm wide input cam tab
CAM_X_CENTER = 7.05    # Centered in slider guide track

def build_enlarged_shaft_rocker_mesh(in_assembly_coords=True):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER
    
    r_pin = PIN_DIAMETER / 2.0
    r_hub = HUB_DIAMETER / 2.0
    
    # 1. Stepped Cylindrical Axle & Hub
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # Left pin: [3.50, 5.50]
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - HUB_WIDTH/2.0 - PIN_LEN/2.0, y_axle, z_axle])
    
    # Right pin: [13.00, 15.00]
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + HUB_WIDTH/2.0 + PIN_LEN/2.0, y_axle, z_axle])
    
    # Central Hub Barrel: [5.50, 13.00]
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=HUB_WIDTH, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. Flank Ribs & Plunger
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    rib_flank_thick = 1.00 # 1.00mm flank rib thickness
    # Rib 1 (Left Flank): X in [5.60, 6.60]
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=rib_flank_thick)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    # Rib 3 (Right Flank): X in [11.90, 12.90]
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=rib_flank_thick)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + HUB_WIDTH/2.0 - 0.10 - rib_flank_thick), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    # Rib 2 (Center Plunger Blade) reaching Z = -6.50mm
    z_tip = -6.50
    r_tip = 1.00 # 2.00mm tip thickness in Y
    plunger_y_center = 11.40
    
    N = 25
    t = np.linspace(0, 1, N)
    spine_y = (1-t)**2 * (y_axle + r_hub) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    belly_y = (1-t)**2 * (y_axle - r_hub) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_plunger = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=PLUNGER_WIDTH_X)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 3. Structural Gusset Web tying ribs together
    web_y_min = y_axle - 1.50
    web_y_max = y_axle + 2.50
    web_z_min = z_axle - 3.20
    web_z_max = z_axle + 1.00
    web_poly = box(web_y_min, web_z_min, web_y_max, web_z_max)
    web_span_x = (x_c + HUB_WIDTH/2.0 - 0.10) - (x_c - HUB_WIDTH/2.0 + 0.10)
    m_web_raw = trimesh.creation.extrude_polygon(web_poly, height=web_span_x)
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([v_w[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_w[:, 0], v_w[:, 1]])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # 4. Angled Input Cam Tab
    y_cam_tip = y_axle - 4.50  # Reaches Y = 5.70mm
    z_cam_tip = z_axle - 5.80  # Drops to Z = 6.79mm
    
    cam_collar = Point(y_axle, z_axle).buffer(r_hub)
    cam_pts = [
        (y_axle + 1.50, z_axle + 1.50),
        (y_cam_tip, z_cam_tip + 2.40),
        (y_cam_tip, z_cam_tip),
        (y_cam_tip + 3.00, z_cam_tip),
        (y_axle + 0.20, z_axle - 2.80)
    ]
    poly_cam = unary_union([cam_collar, Polygon(cam_pts)])
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=CAM_WIDTH_X)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (CAM_X_CENTER - CAM_WIDTH_X/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_rib1, mesh_rib3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    
    if not in_assembly_coords:
        mesh_printable = shaft_mesh.copy()
        rot_bed = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
        mesh_printable.apply_transform(rot_bed)
        bounds = mesh_printable.bounds
        mesh_printable.apply_translation([
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ])
        return mesh_printable
        
    return shaft_mesh

def build_enlarged_towers_mesh():
    y_shaft = Y_AXLE
    z_base = BASE_THICK  # 1.0mm
    z_top = z_base + TOWER_HEIGHT  # 14.09mm
    r_cradle = CRADLE_DIAMETER / 2.0  # 1.50mm
    z_cradle_center = Z_AXLE  # 12.59mm
    
    y_min_base = 7.171
    y_max_base = 13.771
    y_min_top = 7.471
    y_max_top = 13.101
    
    throat_w = TOWER_THROAT_W  # 2.45mm
    half_w = throat_w / 2.0
    alpha = np.arcsin(half_w / r_cradle)
    
    # Circular arc around shaft cradle from right retention tip to left retention tip
    phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
    cradle_arc_pts = [(y_shaft + r_cradle * np.cos(p), z_cradle_center + r_cradle * np.sin(p)) for p in phi]
    
    # Lead-in bevel from retention tips up to top edge (Z = z_top)
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
    
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=1.50)
    verts = m_raw.vertices.copy()
    
    # Left tower mesh: X in [3.90, 5.40]
    verts_left = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_left[:, 0] += 3.900
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    
    # Right tower mesh: X in [13.10, 14.60]
    verts_right = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_right[:, 0] += 13.100
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right])

if __name__ == '__main__':
    shaft_m = build_enlarged_shaft_rocker_mesh(in_assembly_coords=True)
    tower_m = build_enlarged_towers_mesh()
    
    print("Enlarged Shaft Assembled Bounds:")
    print("  X:", shaft_m.bounds[:, 0])
    print("  Y:", shaft_m.bounds[:, 1])
    print("  Z:", shaft_m.bounds[:, 2])
    print(f"Watertight: {shaft_m.is_watertight}")
    
    print("\nEnlarged Towers Bounds:")
    print("  X:", tower_m.bounds[:, 0])
    print("  Y:", tower_m.bounds[:, 1])
    print("  Z:", tower_m.bounds[:, 2])
    print(f"Watertight: {tower_m.is_watertight}")
    
    # Check printable orientation
    shaft_print = build_enlarged_shaft_rocker_mesh(in_assembly_coords=False)
    print("\nPrintable Shaft Bounds (Z=0 datum):")
    print("  X:", shaft_print.bounds[:, 0])
    print("  Y:", shaft_print.bounds[:, 1])
    print("  Z:", shaft_print.bounds[:, 2])
    print(f"Watertight: {shaft_print.is_watertight}")
