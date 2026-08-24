"""
testing/test_full_pipeline_with_y625.py
Test the entire pipeline with tower base aligned to top inner wall of Bracket 3 (Y = 6.250mm).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

Y_AXLE = 9.279
Z_AXLE = 12.590
PIN_DIAMETER = 2.80
HUB_DIAMETER = 4.20
TOTAL_AXLE_LEN = 11.50
HUB_WIDTH = 7.50
PIN_LEN = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0
PLUNGER_REACH_BELOW_Z = 6.50
PLUNGER_WIDTH_X = 4.40
CAM_WIDTH_X = 2.70
CAM_X_CENTER = 7.05
X_TOWER_CENTER = 9.25
HOLE_X_CENTER = 10.284

# 1. Build Shaft
def build_test_shaft():
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER
    r_pin = PIN_DIAMETER / 2.0
    r_hub = HUB_DIAMETER / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - HUB_WIDTH/2.0 - PIN_LEN/2.0, y_axle, z_axle])
    
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + HUB_WIDTH/2.0 + PIN_LEN/2.0, y_axle, z_axle])
    
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=HUB_WIDTH, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    rib_thick = 1.00
    
    m_r1 = trimesh.creation.extrude_polygon(poly_flank, height=rib_thick)
    v_r1 = m_r1.vertices.copy()
    v_r1 = np.column_stack([v_r1[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_r1 = trimesh.Trimesh(vertices=v_r1, faces=m_r1.faces.copy(), process=True)
    
    m_r3 = trimesh.creation.extrude_polygon(poly_flank, height=rib_thick)
    v_r3 = m_r3.vertices.copy()
    v_r3 = np.column_stack([v_r3[:, 2] + (x_c + HUB_WIDTH/2.0 - 0.10 - rib_thick), v_r3[:, 0], v_r3[:, 1]])
    mesh_r3 = trimesh.Trimesh(vertices=v_r3, faces=m_r3.faces.copy(), process=True)
    
    z_tip = -PLUNGER_REACH_BELOW_Z
    r_tip = 1.00
    plunger_y_center = 10.479
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
    m_p = trimesh.creation.extrude_polygon(poly_plunger, height=PLUNGER_WIDTH_X)
    v_p = m_p.vertices.copy()
    v_p = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_p, faces=m_p.faces.copy(), process=True)
    
    theta_cam = np.radians(-161.40)
    u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up
        
    cam_reach = 6.80
    cam_arm_thick = 2.80
    
    p_tangent_top = np.array([y_axle, z_axle]) + u_perp_up * r_hub
    p_top_tip = p_tangent_top + u_dir * cam_reach
    p_bot_tip = p_top_tip - u_perp_up * cam_arm_thick
    p_tangent_bot = p_tangent_top - u_perp_up * cam_arm_thick
    
    half_t = cam_arm_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
        
    poly_cam_arm = Polygon([p_tangent_top] + cam_tip_pts + [p_tangent_bot, p_tangent_top])
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=CAM_WIDTH_X)
    v_c = m_cam_raw.vertices.copy()
    v_cam = np.column_stack([v_c[:, 2] + (CAM_X_CENTER - CAM_WIDTH_X/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)
    
    web_y_min = y_axle - 1.50
    web_y_max = y_axle + 2.50
    web_z_min = z_axle - 3.20
    web_z_max = z_axle + 1.00
    web_poly = box(web_y_min, web_z_min, web_y_max, web_z_max)
    web_span_x = (x_c + HUB_WIDTH/2.0 - 0.10) - (x_c - HUB_WIDTH/2.0 + 0.10)
    m_web = trimesh.creation.extrude_polygon(web_poly, height=web_span_x)
    v_w = m_web.vertices.copy()
    v_w = np.column_stack([v_w[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_w[:, 0], v_w[:, 1]])
    mesh_web = trimesh.Trimesh(vertices=v_w, faces=m_web.faces.copy(), process=True)
    
    shaft_mesh = trimesh.util.concatenate([
        pin_l, pin_r, hub_mesh,
        mesh_r1, mesh_r3, mesh_plunger, mesh_web,
        mesh_cam
    ])
    return shaft_mesh

# 2. Build Towers
def build_test_towers():
    y_shaft = Y_AXLE
    z_base = 1.00
    z_top = z_base + 13.09 # 14.09mm
    r_shaft = 1.50
    z_cradle_center = 12.590
    
    y_min_base = 6.250
    y_max_base = 12.850
    y_min_top = 6.550
    y_max_top = 12.180
    
    throat_w = 2.45
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
    
    m_raw = trimesh.creation.extrude_polygon(poly_yz, height=1.50)
    verts = m_raw.vertices.copy()
    
    verts_left = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_left[:, 0] += 3.900
    mesh_left = trimesh.Trimesh(vertices=verts_left, faces=m_raw.faces.copy(), process=True)
    
    verts_right = np.column_stack([verts[:, 2], verts[:, 0], verts[:, 1]])
    verts_right[:, 0] += 13.100
    mesh_right = trimesh.Trimesh(vertices=verts_right, faces=m_raw.faces.copy(), process=True)
    
    return trimesh.util.concatenate([mesh_left, mesh_right])

s_mesh = build_test_shaft()
t_mesh = build_test_towers()
print(f"Shaft Watertight: {s_mesh.is_watertight}, Bounds: {s_mesh.bounds}")
print(f"Towers Watertight: {t_mesh.is_watertight}, Bounds: {t_mesh.bounds}")
print("Test completed successfully!")
