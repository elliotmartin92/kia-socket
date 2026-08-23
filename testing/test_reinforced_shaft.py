import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_shaft import (
    Y_AXLE, Z_AXLE, X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER,
    X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    HOLE_X_CENTER, HOLE_X_WIDTH, HOLE_Y_CENTER, HOLE_Y_LEN,
    AXLE_DIAMETER, COLLAR_DIAMETER, COLLAR_THICK
)
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, create_all_brackets_poly

def build_heavy_duty_shaft_v2(
    trunk_d=3.20,              # Increased from 2.80mm to 3.20mm (1.7x higher torsional stiffness)
    collar_root_r=2.20,         # Increased from 1.50mm to 2.20mm (Ø4.40mm heavy root sleeve)
    plunger_w_x=4.60,           # Plunger width in X widened (centered or stepped to right)
    plunger_root_t_y=3.20,      # Thickened root in Y (was 2.00mm)
    plunger_tip_t_y=2.00,       # Tip thickness in Y (2.00mm)
    cam_w_x=2.50,               # Cam width in X
    cam_x_center=6.55,          # Aligned in bracket channel
    in_assembly_coords=True
):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    r_axle = AXLE_DIAMETER / 2.0
    
    # 1. Bearing Axle (Ø1.90mm)
    x_min = X_LEFT_TOWER_OUTER - COLLAR_THICK - 0.40   # 3.05 mm
    x_max = X_RIGHT_TOWER_OUTER + COLLAR_THICK + 0.40  # 15.81 mm
    axle_len = x_max - x_min
    cyl_mesh = trimesh.creation.cylinder(radius=r_axle, height=axle_len, sections=32)
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    cyl_mesh.apply_transform(rot_x)
    cyl_mesh.apply_translation([(x_min + x_max)/2.0, y_axle, z_axle])
    
    # 2. Central Structural Trunk Sleeve (Ø3.20mm between towers)
    x_trunk_min = X_LEFT_TOWER_INNER + 0.10   # 5.60 mm
    x_trunk_max = X_RIGHT_TOWER_INNER - 0.10  # 13.26 mm
    trunk_len = x_trunk_max - x_trunk_min
    trunk_mesh = trimesh.creation.cylinder(radius=trunk_d/2.0, height=trunk_len, sections=32)
    trunk_mesh.apply_transform(rot_x)
    trunk_mesh.apply_translation([(x_trunk_min + x_trunk_max)/2.0, y_axle, z_axle])
    
    # 3. Retaining Collars (Ø3.00mm x 0.80mm)
    col_left = trimesh.creation.cylinder(radius=COLLAR_DIAMETER/2.0, height=COLLAR_THICK, sections=32)
    col_left.apply_transform(rot_x)
    col_left.apply_translation([X_LEFT_TOWER_OUTER - COLLAR_THICK/2.0, y_axle, z_axle])
    
    col_right = trimesh.creation.cylinder(radius=COLLAR_DIAMETER/2.0, height=COLLAR_THICK, sections=32)
    col_right.apply_transform(rot_x)
    col_right.apply_translation([X_RIGHT_TOWER_OUTER + COLLAR_THICK/2.0, y_axle, z_axle])
    
    # 4. Reinforced Output Plunger Arm:
    # 2D profile with thickened root (plunger_root_t_y = 3.20mm) and smooth continuous fillets
    z_tip = -6.50
    r_tip = plunger_tip_t_y / 2.0
    plunger_y_center = 11.40
    
    collar_disc = Point(y_axle, z_axle).buffer(collar_root_r)
    
    N = 25
    t = np.linspace(0, 1, N)
    # Spine (outer +Y curve)
    spine_y = (1-t)**2 * (y_axle + collar_root_r) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
    spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
    
    tip_angles = np.linspace(0, np.pi, 33)
    tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
    
    # Belly (inner -Y curve)
    belly_y = (1-t)**2 * (y_axle - collar_root_r) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
    belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50
    
    pts_arm_body = (
        list(zip(spine_y, spine_z)) +
        [(plunger_y_center + r_tip, z_tip + r_tip)] +
        tip_pts +
        [(plunger_y_center - r_tip, z_tip + r_tip)] +
        list(reversed(list(zip(belly_y, belly_z))))
    )
    poly_plunger_body = Polygon(pts_arm_body)
    poly_plunger = unary_union([collar_disc, poly_plunger_body])
    
    # Plunger width in X:
    # Through hole is at X in [7.608, 12.960].
    # Plunger lower portion (Z <= 1.0) must fit in hole: let X span [8.00, 12.60] (width = 4.60mm, 0.39mm and 0.36mm clearances)
    # Plunger upper portion (Z > 1.0) can extend all the way to the right tower inner wall (X = 13.26mm)!
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=plunger_w_x)
    v_p = m_plunger_raw.vertices.copy()
    
    # Position plunger centered in hole or shifted slightly to maximize width
    x_p_min = HOLE_X_CENTER - plunger_w_x/2.0
    v_plunger = np.column_stack([
        v_p[:, 2] + x_p_min,
        v_p[:, 0],
        v_p[:, 1]
    ])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # 5. Reinforced Input Cam Arm
    y_input_tip = y_axle - 4.50  # 3.17 mm
    z_input_tip = z_axle - 6.00  # 6.59 mm
    
    cam_collar = Point(y_axle, z_axle).buffer(collar_root_r)
    profile_cam_pts = [
        (y_axle + 1.20, z_axle + 1.00),
        (y_input_tip, z_input_tip + 2.00),
        (y_input_tip, z_input_tip),
        (y_input_tip + 3.00, z_input_tip),
        (y_axle, z_axle - 3.20)
    ]
    poly_cam = unary_union([cam_collar, Polygon(profile_cam_pts)])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=cam_w_x)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([
        v_c[:, 2] + (cam_x_center - cam_w_x/2.0),
        v_c[:, 0],
        v_c[:, 1]
    ])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    # 6. Monolithic Gusset Web spanning between Cam and Plunger right up to Right Tower (X in [5.60, 13.20])
    web_y_min = y_axle - 1.80
    web_y_max = y_axle + 2.40
    web_z_min = z_axle - 2.60
    web_z_max = z_axle + 1.50
    web_box = box(web_y_min, web_z_min, web_y_max, web_z_max)
    
    # Web spans from left cam edge to right plunger edge:
    web_x_start = cam_x_center - cam_w_x/2.0
    web_x_end = x_p_min + plunger_w_x
    web_span_x = web_x_end - web_x_start
    
    m_web_raw = trimesh.creation.extrude_polygon(web_box, height=web_span_x)
    v_w = m_web_raw.vertices.copy()
    v_web = np.column_stack([
        v_w[:, 2] + web_x_start,
        v_w[:, 0],
        v_w[:, 1]
    ])
    mesh_web = trimesh.Trimesh(vertices=v_web, faces=m_web_raw.faces.copy(), process=True)
    
    # Combined assembly
    shaft_mesh = trimesh.util.concatenate([cyl_mesh, trunk_mesh, col_left, col_right, mesh_plunger, mesh_cam, mesh_web])
    
    return shaft_mesh

# Build mesh and test
part_mesh = trimesh.load('part.stl')
new_shaft = build_heavy_duty_shaft_v2()

print("--- Reinforced Shaft Bounds ---")
print(f"X range: [{new_shaft.bounds[0, 0]:.3f}, {new_shaft.bounds[1, 0]:.3f}] mm (Total Span: {new_shaft.bounds[1, 0] - new_shaft.bounds[0, 0]:.3f} mm)")
print(f"Y range: [{new_shaft.bounds[0, 1]:.3f}, {new_shaft.bounds[1, 1]:.3f}] mm")
print(f"Z range: [{new_shaft.bounds[0, 2]:.3f}, {new_shaft.bounds[1, 2]:.3f}] mm")

# Test kinematic rotation sweep from 0 to 12 degrees
print("\n--- Kinematic Rotation Interference Check ---")
y_ax = Y_AXLE
z_ax = Z_AXLE

for deg in [0.0, 3.0, 6.0, 9.0, 11.5]:
    # Rotate around X-axis at (Y_AXLE, Z_AXLE)
    rad = np.radians(deg)
    # Rotation matrix around X axis centered at [0, y_ax, z_ax]
    rot = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, y_ax, z_ax])
    s_rot = new_shaft.copy()
    s_rot.apply_transform(rot)
    
    # Check bounds of plunger tip (Z < 0) vs through-hole [7.608, 12.960] x [8.570, 13.082]
    tip_verts = s_rot.vertices[s_rot.vertices[:, 2] < 1.0]
    x_min_tip = np.min(tip_verts[:, 0])
    x_max_tip = np.max(tip_verts[:, 0])
    y_min_tip = np.min(tip_verts[:, 1])
    y_max_tip = np.max(tip_verts[:, 1])
    
    hole_x_min, hole_x_max = 7.608, 12.960
    hole_y_min, hole_y_max = 8.570, 13.082
    
    x_ok = (x_min_tip >= hole_x_min) and (x_max_tip <= hole_x_max)
    y_ok = (y_min_tip >= hole_y_min) and (y_max_tip <= hole_y_max)
    
    print(f"Rotation {deg:4.1f}°: Tip X=[{x_min_tip:.2f}, {x_max_tip:.2f}] (Clearances: L={x_min_tip-hole_x_min:.2f}mm, R={hole_x_max-x_max_tip:.2f}mm) | Tip Y=[{y_min_tip:.2f}, {y_max_tip:.2f}] | Hole Pass: {x_ok and y_ok}")

