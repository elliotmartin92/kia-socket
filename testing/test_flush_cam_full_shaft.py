"""
testing/test_flush_cam_full_shaft.py
Test complete shaft mesh generation with 100% flush top input cam.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

Y_AXLE = 10.200
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

def build_shaft_rocker_mesh_flush(in_assembly_coords=True):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = X_TOWER_CENTER
    r_pin = PIN_DIAMETER / 2.0
    r_hub = HUB_DIAMETER / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # 1. Pivot pins
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - HUB_WIDTH/2.0 - PIN_LEN/2.0, y_axle, z_axle])
    
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=PIN_LEN + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + HUB_WIDTH/2.0 + PIN_LEN/2.0, y_axle, z_axle])
    
    # 2. Central Hub Barrel
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=HUB_WIDTH, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 3. Flank Ribs
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
    
    # 4. Center Plunger Blade
    z_tip = -PLUNGER_REACH_BELOW_Z
    r_tip = 1.00
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
    m_p = trimesh.creation.extrude_polygon(poly_plunger, height=PLUNGER_WIDTH_X)
    v_p = m_p.vertices.copy()
    v_p = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_p, faces=m_p.faces.copy(), process=True)
    
    # 5. Direct 105° Input Cam - 100% FLUSH with top of shaft
    # Centerline of plunger is at angle theta_p = atan2(-19.09, 1.20) = -86.40°
    # 105° bellcrank angle -> angle of cam centerline = -86.40° - 75.0° = -161.40°
    theta_cam = np.radians(-161.40)
    u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)]) # [-0.948, -0.319]
    u_perp_up = np.array([u_dir[1], -u_dir[0]])
    if u_perp_up[1] < 0:
        u_perp_up = -u_perp_up # [-0.319, 0.948] -> points up and forward
        
    cam_reach = 6.80     # Total length from shaft center
    cam_arm_thick = 2.80 # Solid 2.80mm beam thickness
    
    # Top line starts TANGENT to cylinder top (flush with shaft apex at Z = z_axle + r_hub)
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
    
    # 6. Connecting Structural Web
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

if __name__ == '__main__':
    mesh_asmb = build_shaft_rocker_mesh_flush(in_assembly_coords=True)
    print(f"Assembled mesh bounds: {mesh_asmb.bounds}")
    print(f"Mesh is watertight: {mesh_asmb.is_watertight}")
    print(f"Mesh volume: {mesh_asmb.volume:.2f} mm^3")
    
    # Check max Z at cam X [5.70, 8.40]:
    v_cam_zone = mesh_asmb.vertices[(mesh_asmb.vertices[:, 0] >= 5.70) & (mesh_asmb.vertices[:, 0] <= 8.40)]
    max_z_cam = np.max(v_cam_zone[:, 2])
    print(f"Max Z in cam zone = {max_z_cam:.3f} mm (Shaft top = {Z_AXLE + 2.10:.3f} mm)")
    assert abs(max_z_cam - (Z_AXLE + 2.10)) < 0.05, "Cam should be flush with shaft top!"
    print("Flush check passed!")
