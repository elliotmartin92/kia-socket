"""
testing/test_crowned_cam.py
Test implementation of Option 3: Convex Crowned Cam Profile for continuous rolling tangency with straight blade.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, RIB_FLANK_THICK, HOLE_X_CENTER
)

def build_crowned_shaft_rocker_mesh(crown_height=0.45, in_assembly_coords=True):
    y_axle = Y_AXLE
    z_axle = Z_AXLE
    x_c = 9.25  # X_TOWER_CENTER
    
    r_pin = PIN_DIAMETER / 2.0
    r_hub = HUB_DIAMETER / 2.0
    pin_len = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0
    
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    
    # 1. Pivot pins
    pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_l.apply_transform(rot_x)
    pin_l.apply_translation([x_c - HUB_WIDTH/2.0 - pin_len/2.0, y_axle, z_axle])
    
    pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
    pin_r.apply_transform(rot_x)
    pin_r.apply_translation([x_c + HUB_WIDTH/2.0 + pin_len/2.0, y_axle, z_axle])
    
    hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=HUB_WIDTH, sections=32)
    hub_mesh.apply_transform(rot_x)
    hub_mesh.apply_translation([x_c, y_axle, z_axle])
    
    # 2. Flanks
    flank_collar = Point(y_axle, z_axle).buffer(r_hub)
    flank_pts = [
        (y_axle - 1.50, z_axle + 0.60),
        (y_axle + 3.20, z_axle - 1.50),
        (y_axle + 2.50, z_axle - 4.50),
        (y_axle + 0.20, z_axle - 4.20),
        (y_axle - 1.60, z_axle - 1.00)
    ]
    poly_flank = unary_union([flank_collar, Polygon(flank_pts)])
    
    m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r1 = m_rib1_raw.vertices.copy()
    v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
    mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)
    
    m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
    v_r3 = m_rib3_raw.vertices.copy()
    v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + HUB_WIDTH/2.0 - 0.10 - RIB_FLANK_THICK), v_r3[:, 0], v_r3[:, 1]])
    mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)
    
    # 3. Center Plunger Blade
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
    m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=PLUNGER_WIDTH_X)
    v_p = m_plunger_raw.vertices.copy()
    v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0), v_p[:, 0], v_p[:, 1]])
    mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)
    
    # Structural Web
    from shapely.geometry import box
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
    
    # 4. CONVEX CROWNED INPUT CAM TAB
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
    
    # Generate smooth convex crowned top surface (33 points)
    t_crown = np.linspace(0, 1, 33)
    cam_top_crowned = []
    for tc in t_crown:
        # Parabolic convex crown: peak +crown_height at midpoint tc=0.5
        pt = (1-tc)*p_tangent_top + tc*p_top_tip + 4*tc*(1-tc)*u_perp_up*crown_height
        cam_top_crowned.append((pt[0], pt[1]))
        
    half_t = cam_arm_thick / 2.0
    p_tip_mid = (p_top_tip + p_bot_tip) / 2.0
    cam_tip_pts = []
    for a in np.linspace(np.pi/2, -np.pi/2, 17):
        pt = p_tip_mid + u_dir * (half_t * np.cos(a)) + u_perp_up * (half_t * np.sin(a))
        cam_tip_pts.append((pt[0], pt[1]))
        
    poly_cam_arm = Polygon(cam_top_crowned + cam_tip_pts + [p_tangent_bot, p_tangent_top])
    poly_cam = unary_union([flank_collar, poly_cam_arm])
    
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
        rot_bed = trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])
        mesh_printable.apply_transform(rot_bed)
        bounds = mesh_printable.bounds
        mesh_printable.apply_translation([
            -(bounds[0, 0] + bounds[1, 0])/2.0,
            -(bounds[0, 1] + bounds[1, 1])/2.0,
            -bounds[0, 2]
        ])
        return mesh_printable
        
    return shaft_mesh, poly_cam

print("=== Testing Convex Crowned Cam Mesh Generation ===")
shaft_asmb, poly_cam = build_crowned_shaft_rocker_mesh(crown_height=0.45, in_assembly_coords=True)
print(f"Assembled mesh watertight: {shaft_asmb.is_watertight}")
print(f"Assembled mesh volume: {shaft_asmb.volume:.2f} mm³")

shaft_print = build_crowned_shaft_rocker_mesh(crown_height=0.45, in_assembly_coords=False)
print(f"Printable mesh watertight: {shaft_print.is_watertight}")
print(f"Printable bounds: Z = [{shaft_print.bounds[0,2]:.2f}, {shaft_print.bounds[1,2]:.2f}] mm")

# Plot Dynamic Kinematics through 0° to 10° stroke
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=180)

# Left: 2D Multi-Angle Dynamic Stroke
blade_y = 5.25
ax1.fill([blade_y - 0.75, blade_y + 0.75, blade_y + 0.75, blade_y - 0.75], [10.0, 10.0, 18.0, 18.0],
         color='#b0bec5', alpha=0.6, ec='#37474f', lw=1.5, label='Straight Blade (1.5mm thick)')

# Draw crowned cam at 0°, 3°, 6°, 9°
angles = [0, 3, 6, 9]
colors = ['#1565c0', '#2e7d32', '#f57c00', '#c62828']
poly_pts = np.array(poly_cam.exterior.coords)

for deg, col in zip(angles, colors):
    rad = np.radians(deg)
    rot = np.array([[np.cos(rad), np.sin(rad)], [-np.sin(rad), np.cos(rad)]])
    rot_pts = np.array([Y_AXLE, Z_AXLE]) + (rot @ (poly_pts - np.array([Y_AXLE, Z_AXLE])).T).T
    ax1.plot(rot_pts[:, 0], rot_pts[:, 1], color=col, lw=2.5, label=f'Crowned Cam @ {deg}° stroke')

ax1.set_xlim(-1.0, 14.0)
ax1.set_ylim(8.0, 18.0)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title("Dynamic Stroke: Smooth Tangent Contact Across 0°-9° Rotation", fontsize=11, fontweight='bold')
ax1.set_xlabel("Y (mm)")
ax1.set_ylabel("Z (mm)")
ax1.legend(loc='lower right', fontsize=8.5)

# Right: Contact Comparison (Flat Ramp vs Crowned Arc)
cx, cy = poly_cam.exterior.xy
ax2.plot(cx, cy, color='#2e7d32', lw=3, label='New Option 3: Convex Crowned Cam (+0.45mm Crown)')

# Flat ramp for comparison
theta_cam = np.radians(-161.40)
u_dir = np.array([np.cos(theta_cam), np.sin(theta_cam)])
u_perp = np.array([u_dir[1], -u_dir[0]])
if u_perp[1] < 0: u_perp = -u_perp
p_tan = np.array([Y_AXLE, Z_AXLE]) + u_perp * 2.10
p_top = p_tan + u_dir * 6.80
ax2.plot([p_tan[0], p_top[0]], [p_tan[1], p_top[1]], 'r--', lw=2, label='Old: Linear Flat Ramp')

ax2.annotate('Convex Crowning (+0.45mm)\n• Acts as true kinematic cam against flat blade\n• Contact smoothly rolls across face\n• Eliminates point-digging and corner scraping\n• Constant progressive mechanical advantage',
             xy=(5.5, 14.3), xytext=(0.2, 15.6),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=9, fontweight='bold', color='#1b5e20',
             bbox=dict(boxstyle='round,pad=0.4', fc='#e8f5e9', ec='#2e7d32', lw=1.5))

ax2.set_xlim(-1.0, 14.0)
ax2.set_ylim(8.0, 18.0)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_title("Profile Comparison: Linear Ramp vs Convex Crown", fontsize=11, fontweight='bold')
ax2.set_xlabel("Y (mm)")
ax2.set_ylabel("Z (mm)")
ax2.legend(loc='lower right', fontsize=8.5)

plt.tight_layout()
plt.savefig('testing/crowned_cam_dynamic_verification.png', dpi=180)
print("Saved testing/crowned_cam_dynamic_verification.png")
