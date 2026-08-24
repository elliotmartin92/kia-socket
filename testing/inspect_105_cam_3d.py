"""
testing/inspect_105_cam_3d.py
Build and inspect 3D mesh of enlarged shaft with direct 105 degree input cam.
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

def build_shaft_105_direct(in_assembly_coords=True):
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
    
    # 2. Central Hub
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
    
    # 5. Direct 105° Input Cam (Extending directly off the cylindrical shaft)
    # Centerline of plunger is at angle theta_p = atan2(-19.09, 1.20) = -86.40°
    # 105° bellcrank angle -> angle of cam centerline = -86.40° - 75.0° = -161.40°
    theta_cam = np.radians(-161.40)
    dir_cam = np.array([np.cos(theta_cam), np.sin(theta_cam)]) # [-0.948, -0.319]
    norm_cam = np.array([-dir_cam[1], dir_cam[0]])             # [0.319, -0.948]
    
    cam_reach = 6.80  # Total length from shaft center
    cam_arm_thick = 2.80  # Solid 2.80mm beam thickness
    half_t = cam_arm_thick / 2.0
    
    # Arm body points starting directly from the shaft center
    p_center_tip = np.array([y_axle, z_axle]) + dir_cam * cam_reach
    p1 = np.array([y_axle, z_axle]) + norm_cam * half_t
    p2 = p_center_tip + norm_cam * half_t
    p3 = p_center_tip - norm_cam * half_t
    p4 = np.array([y_axle, z_axle]) - norm_cam * half_t
    
    # Rounded nose at contact tip
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_center_tip + dir_cam * (half_t * np.cos(a)) + norm_cam * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
        
    poly_cam_arm = Polygon([p1] + cam_tip_pts + [p4, p1])
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
    m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=CAM_WIDTH_X)
    v_c = m_cam_raw.vertices.copy()
    v_c = np.column_stack([v_c[:, 2] + (CAM_X_CENTER - CAM_WIDTH_X/2.0), v_c[:, 0], v_c[:, 1]])
    mesh_cam = trimesh.Trimesh(vertices=v_c, faces=m_cam_raw.faces.copy(), process=True)
    
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
    
    return shaft_mesh

if __name__ == '__main__':
    mesh = build_shaft_105_direct(in_assembly_coords=True)
    print(f"Mesh bounds: {mesh.bounds}")
    print(f"Watertight: {mesh.is_watertight}")
    print(f"Volume: {mesh.volume:.2f} mm^3")
    
    # Render multi-view inspection
    fig = plt.figure(figsize=(18, 6), dpi=180)
    
    # View 1: 3D Isometric View
    ax1 = fig.add_subplot(1, 3, 1, projection='3d')
    ax1.set_title("1. 3D Isometric: 105° Cam Directly Off Shaft", fontsize=11, fontweight='bold')
    v = mesh.vertices
    f = mesh.faces
    col = Poly3DCollection(v[f], alpha=0.9, facecolor='#ff9800', edgecolor='#e65100', linewidth=0.15)
    ax1.add_collection3d(col)
    ax1.set_xlim(2, 16)
    ax1.set_ylim(2, 14)
    ax1.set_zlim(-7, 15)
    ax1.view_init(elev=25, azim=130)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_zlabel('Z (mm)')
    
    # View 2: Side Profile (Y-Z Plane)
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_title("2. Side Profile: 105° Bellcrank Angle", fontsize=11, fontweight='bold')
    phi = np.linspace(0, 2*np.pi, 64)
    ax2.plot(Y_AXLE + 2.1*np.cos(phi), Z_AXLE + 2.1*np.sin(phi), 'b-', lw=1.5, label='Shaft Hub (Ø4.2mm)')
    ax2.plot(Y_AXLE, Z_AXLE, 'ro', markersize=6, label='Pivot Center')
    
    # Draw plunger line and cam line
    p_tip_y, p_tip_z = 11.40, -6.50
    c_tip_y = Y_AXLE + 6.80 * np.cos(np.radians(-161.4))
    c_tip_z = Z_AXLE + 6.80 * np.sin(np.radians(-161.4))
    ax2.plot([Y_AXLE, p_tip_y], [Z_AXLE, p_tip_z], 'm--', lw=2, label='Plunger Axis')
    ax2.plot([Y_AXLE, c_tip_y], [Z_AXLE, c_tip_z], 'g--', lw=2, label='Input Cam Axis (105° Bellcrank)')
    
    ax2.annotate('105° Bellcrank Angle', xy=(Y_AXLE - 2.0, Z_AXLE - 2.5),
                 fontsize=11, fontweight='bold', color='#1565c0',
                 bbox=dict(boxstyle='round,pad=0.2', fc='#e3f2fd', ec='#1565c0'))
    
    ax2.set_xlim(2, 14)
    ax2.set_ylim(-8, 16)
    ax2.set_aspect('equal')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.set_xlabel('Y (mm)')
    ax2.set_ylabel('Z (mm)')
    ax2.legend(loc='lower left', fontsize=8)
    
    # View 3: Underside 3D Closeup
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    ax3.set_title("3. Underside: Seamless Junction (No Gaps)", fontsize=11, fontweight='bold')
    col3 = Poly3DCollection(v[f], alpha=0.9, facecolor='#2ecc71', edgecolor='#1b5e20', linewidth=0.15)
    ax3.add_collection3d(col3)
    ax3.set_xlim(4, 11)
    ax3.set_ylim(2, 13)
    ax3.set_zlim(3, 15)
    ax3.view_init(elev=-35, azim=145)
    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    ax3.set_zlabel('Z (mm)')
    
    plt.tight_layout()
    out_png = 'testing/direct_105_cam_mesh_inspect.png'
    plt.savefig(out_png, dpi=200)
    print(f"Saved {out_png}")
