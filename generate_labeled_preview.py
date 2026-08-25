"""
Generate a comprehensive, beautifully labeled part preview diagram
with all named features, dimensions, subpart callouts, shaft/rocker kinematics, and Y-axis button actuation.
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import shapely.geometry as sg
from shapely.ops import unary_union

from build_part import (
    build_exact_3d_model, get_exact_base_polygon, create_all_brackets_poly,
    create_grid_ribs_poly, create_shaft_support_towers_poly,
    create_backside_slit_bosses_poly, build_left_tower_struts_mesh,
    create_arch_wall_poly,
    create_center_curved_feature_poly,
    OUTER_WALL_HEIGHT, OUTER_WALL_THICK, BASE_THICK, BRACKET_HEIGHT,
    TOWER_HEIGHT, TOWER_WALL_THICK, TOWER_INTERNAL_GAP, SLIT_BOSS_HEIGHT,
    find_boundary_point_and_normal, CLIP_ANGLES
)
from build_shaft import build_shaft_rocker_mesh

# 1. Build 3D meshes and base poly
part_mesh, base_poly = build_exact_3d_model()
base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

shaft_assembled_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)

# Setup Figure (3 panels: 2D Feature Map, 3D Isometric Assembly, Y-Axis Kinematic Stroke Cross-Section)
fig = plt.figure(figsize=(32, 11.5), dpi=200)

# ==============================================================================
# PANEL 1: 2D TOP-DOWN SCHEMATIC WITH ALL NAMED SUBPART CALLOUTS
# ==============================================================================
ax1 = fig.add_subplot(1, 3, 1)

# Outer and Inner Perimeter Wall
x, y = outer_body_poly.exterior.xy
ax1.plot(x, y, color='#1565c0', linewidth=2.5, label='Perimeter Wall (6.77mm H)')
ix, iy = inner_wall_poly.exterior.xy
ax1.plot(ix, iy, color='#1976d2', linestyle='--', linewidth=1.2, label='Inner Wall Face (1.2mm thick)')

# Through Holes (Floor cutouts)
for interior in base_poly.interiors:
    hx, hy = interior.xy
    ax1.plot(hx, hy, color='#d32f2f', linewidth=2.0)

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax1.plot(bx, by, color='#2e7d32', linewidth=2.0)

# Ribs (Connected Grid)
all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)
for geom in (all_ribs_poly.geoms if hasattr(all_ribs_poly, 'geoms') else [all_ribs_poly]):
    rx, ry = geom.exterior.xy
    ax1.plot(rx, ry, color='#ef6c00', linewidth=0.9, alpha=0.8)

# Shaft Towers (Bounding box)
left_t_x = 3.90
right_t_x = 13.10
y_min = 7.171
y_max = 13.771
ax1.fill([left_t_x, left_t_x + 1.50, left_t_x + 1.50, left_t_x], [y_min, y_min, y_max, y_max],
         color='#e91e63', alpha=0.85, edgecolor='#ad1457', linewidth=1.5)
ax1.fill([right_t_x, right_t_x + 1.50, right_t_x + 1.50, right_t_x], [y_min, y_min, y_max, y_max],
         color='#e91e63', alpha=0.85, edgecolor='#ad1457', linewidth=1.5)

# Left Tower Buttress Struts (Footprint)
ax1.fill([1.90, left_t_x, left_t_x, 1.90], [7.171, 7.171, 7.971, 7.971],
         color='#c2185b', alpha=0.9, edgecolor='#880e4f', linewidth=1.2)
ax1.fill([1.90, left_t_x, left_t_x, 1.90], [12.571, 12.571, 13.771, 13.771],
         color='#c2185b', alpha=0.9, edgecolor='#880e4f', linewidth=1.2)

# Bridge Rib (Right of right tower)
bridge_box = sg.box(13.10, 8.5, 25.0, 14.0)
bridge_ribs_poly = all_ribs_poly.intersection(bridge_box)
for geom in (bridge_ribs_poly.geoms if hasattr(bridge_ribs_poly, 'geoms') else [bridge_ribs_poly]):
    bx, by = geom.exterior.xy
    ax1.fill(bx, by, color='#f48fb1', alpha=0.9, edgecolor='#ad1457', linewidth=1.5)

# Backside Slit Bosses (Dashed purple)
bosses_poly = create_backside_slit_bosses_poly()
for geom in (bosses_poly.geoms if hasattr(bosses_poly, 'geoms') else [bosses_poly]):
    bx, by = geom.exterior.xy
    ax1.plot(bx, by, color='#7b1fa2', linestyle='--', linewidth=1.8)

# Center Curved Feature
curved_feat_poly = create_center_curved_feature_poly()
for geom in (curved_feat_poly.geoms if hasattr(curved_feat_poly, 'geoms') else [curved_feat_poly]):
    cx_pts, cy_pts = geom.exterior.xy
    ax1.fill(cx_pts, cy_pts, color='#ce93d8', alpha=0.6)
    ax1.plot(cx_pts, cy_pts, color='#8e24aa', linewidth=2.0)

# Bottom Arch
arch_poly = create_arch_wall_poly()
ax1.plot(*arch_poly.exterior.xy, color='#0d47a1', linewidth=2.0)

# Snap Clip positions
clip_pts = {}
for angle_deg in CLIP_ANGLES:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    clip_pts[angle_deg] = p
    ax1.plot(p[0], p[1], 'o', color='#0097a7', markersize=8, markeredgecolor='#006064', markeredgewidth=1.5)

# Shaft Axle & Plunger Top-Down Footprint
ax1.plot([3.50, 15.00], [9.279, 9.279], color='#ff6f00', linewidth=3.5, label='Ø2.80mm Shaft Axle (Y=9.28mm)')
ax1.fill([10.284 - 2.2, 10.284 + 2.2, 10.284 + 2.2, 10.284 - 2.2],
         [9.279, 9.279, 12.48, 12.48], color='#e65100', alpha=0.85, label='Output Plunger (Through Hole)')
ax1.fill([7.05 - 1.35, 7.05 + 1.35, 7.05 + 1.35, 7.05 - 1.35],
         [2.83, 2.83, 9.279, 9.279], color='#ffb300', alpha=0.9, edgecolor='#ff8f00', linewidth=1.5, label='Direct 105° Input Cam')

# ------------------------------------------------------------------------------
# COMPREHENSIVE 2D SUBPART CALLOUT ANNOTATIONS
# ------------------------------------------------------------------------------

# Top Tab
ax1.annotate('Top Tab (Centered)\n8.20mm W (fits 8.33mm gap)', xy=(0, 20.2), xytext=(-14, 22.8),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#1565c0'),
             fontsize=8.5, fontweight='bold', color='#1565c0', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0'))

# Snap Clip 45°
ax1.annotate('Snap Clip (45.0°)\n4.20mm Beam, 1.59mm Hook', xy=(clip_pts[45.0][0], clip_pts[45.0][1]), xytext=(19.0, 16.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#00838f'),
             fontsize=8, fontweight='bold', color='#00838f', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#00838f'))

# Snap Clip 135°
ax1.annotate('Snap Clip (135.0°)\n4.20mm Beam, 1.59mm Hook', xy=(clip_pts[135.0][0], clip_pts[135.0][1]), xytext=(-30.5, 16.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#00838f'),
             fontsize=8, fontweight='bold', color='#00838f', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#00838f'))

# Snap Clip 211.3°
ax1.annotate('Snap Clip (211.3°)\n4.42mm to Ear, 8.47mm to Tab', xy=(clip_pts[211.3][0], clip_pts[211.3][1]), xytext=(-31.0, -10.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#00838f'),
             fontsize=8, fontweight='bold', color='#00838f', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#00838f'))

# Snap Clip 327.5°
ax1.annotate('Snap Clip (327.5°)\n4.42mm to Ear, 8.47mm to Tab', xy=(clip_pts[327.5][0], clip_pts[327.5][1]), xytext=(17.5, -10.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#00838f'),
             fontsize=8, fontweight='bold', color='#00838f', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f7fa', ec='#00838f'))

# Left Side Ear
ax1.annotate('Left Side Ear\n(8.20mm W, fits 8.3mm gap)', xy=(-21.075, 0.0), xytext=(-30.5, 2.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#0288d1'),
             fontsize=8, fontweight='bold', color='#01579b', bbox=dict(boxstyle='round,pad=0.2', fc='#e1f5fe', ec='#0288d1'))

# Right Side Ear
ax1.annotate('Right Side Ear\n(8.20mm W, fits 8.3mm gap)', xy=(20.200, 0.0), xytext=(22.5, 2.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#0288d1'),
             fontsize=8, fontweight='bold', color='#01579b', bbox=dict(boxstyle='round,pad=0.2', fc='#e1f5fe', ec='#0288d1'))

# Left Tower & Dual Struts
ax1.annotate('Left Tower (14.09mm H)\n+ Dual Buttress Struts', xy=(3.9, 10.20), xytext=(-20.5, 10.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#ad1457'),
             fontsize=8, fontweight='bold', color='#ad1457', bbox=dict(boxstyle='round,pad=0.2', fc='#fce4ec', ec='#ad1457'))

# Right Tower & Bridge Rib
ax1.annotate('Right Tower & Reinforcing\nBridge Rib (to outer wall)', xy=(14.6, 10.20), xytext=(18.5, 11.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#ad1457'),
             fontsize=8, fontweight='bold', color='#ad1457', bbox=dict(boxstyle='round,pad=0.2', fc='#fce4ec', ec='#ad1457'))

# Top-Right Through-Hole
ax1.annotate('Through-Hole (5.35x4.51mm)\nPlunger Reach ≥6.5mm', xy=(10.28, 11.5), xytext=(4.0, 22.8),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#d32f2f'),
             fontsize=8, fontweight='bold', color='#d32f2f', bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#d32f2f'))

# Shaft Rocker Mechanism (Axle, Input Cam, Plunger)
ax1.annotate('Seated Shaft/Rocker:\n• Ø2.80mm Pivot Axle\n• Ø4.20mm Hub Barrel\n• 4.40mm Plunger Arm\n• ≥6.50mm Reach', xy=(7.05, 8.5), xytext=(-10.5, 15.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#e65100'),
             fontsize=7.5, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#e65100'))

# Left Bracket Pair 1 & 2
ax1.annotate('Bracket Pair 1 & 2\n(Height: 4.60mm)', xy=(-7.25, -0.5), xytext=(-21.5, -3.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=8, fontweight='bold', color='#2e7d32', bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))

# Right Bracket Pair 3 & 4
ax1.annotate('Bracket Pair 3 & 4\n(Height: 4.60mm)', xy=(7.25, -0.5), xytext=(17.5, -3.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#2e7d32'),
             fontsize=8, fontweight='bold', color='#2e7d32', bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))

# Center Curved Feature & Dividing Rib
ax1.annotate('Center Curved Feature (10.50mm H)\n+ Internal Dividing Rib (0.6mm)', xy=(6.28, -3.0), xytext=(-9.0, -5.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#6a1b9a'),
             fontsize=8, fontweight='bold', color='#6a1b9a', bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#8e24aa'))

# Internal Floor Stiffener Grid
ax1.annotate('Floor Stiffener Grid\n(0.6mm W x 0.5mm H)', xy=(-13.0, 6.4), xytext=(-28.5, 6.5),
             arrowprops=dict(arrowstyle='->', lw=1.2, color='#ef6c00'),
             fontsize=7.5, fontweight='bold', color='#ef6c00', bbox=dict(boxstyle='round,pad=0.2', fc='#fff3e0', ec='#ef6c00'))

# Bottom Central U-Arch
ax1.annotate('Bottom Central U-Arch (7.95mm H)\n5.00mm Inner Clearance Width', xy=(0, -8.7), xytext=(-27.5, -7.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#0d47a1'),
             fontsize=8, fontweight='bold', color='#0d47a1', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#0d47a1'))

# Bottom Inset Wall Notch
ax1.annotate('Inset Bottom Wall Notch\n(Aligned with Arch Interior)', xy=(0, -16.65), xytext=(-10.0, -22.5),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#0d47a1'),
             fontsize=8, fontweight='bold', color='#0d47a1', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#0d47a1'))

# Left Slit Detent Socket
ax1.annotate('Left Detent Socket\n(2.15x4.45mm for Insert)', xy=(-8.38, -13.66), xytext=(-29.5, -17.0),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#7b1fa2'),
             fontsize=7.5, fontweight='bold', color='#7b1fa2', bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#7b1fa2'))

# Right Slit Detent Socket
ax1.annotate('Right Detent Socket\n(2.15x4.45mm for Insert)', xy=(8.38, -13.66), xytext=(17.5, -17.0),
             arrowprops=dict(arrowstyle='->', lw=1.5, color='#7b1fa2'),
             fontsize=7.5, fontweight='bold', color='#7b1fa2', bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#7b1fa2'))

# Bottom Tabs
ax1.annotate('Bottom-Left Tab', xy=(-14.0, -18.54), xytext=(-26.0, -22.0),
             arrowprops=dict(arrowstyle='->', lw=1.2, color='#1565c0'),
             fontsize=7.5, fontweight='bold', color='#1565c0', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0'))
ax1.annotate('Bottom-Right Tab', xy=(14.0, -18.54), xytext=(17.0, -22.0),
             arrowprops=dict(arrowstyle='->', lw=1.2, color='#1565c0'),
             fontsize=7.5, fontweight='bold', color='#1565c0', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1565c0'))

ax1.set_xlim(-32, 32)
ax1.set_ylim(-24, 25)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title('1. Top-Down 2D Dimensioned Feature & Subpart Map', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')


# ==============================================================================
# PANEL 2: 3D ISOMETRIC VIEW WITH SUBPART CALLOUT LEADER TAGS
# ==============================================================================
ax2 = fig.add_subplot(1, 3, 2, projection='3d')

# Baseplate mesh
v_base = part_mesh.vertices
f_base = part_mesh.faces
mesh_col = Poly3DCollection(v_base[f_base], alpha=0.55, edgecolor='#2c3e50', linewidths=0.08)
mesh_col.set_facecolor('#4A90E2')
ax2.add_collection3d(mesh_col)

# Seated shaft mechanism (gold/orange)
v_shaft = shaft_assembled_mesh.vertices
f_shaft = shaft_assembled_mesh.faces
mesh_shaft = Poly3DCollection(v_shaft[f_shaft], alpha=0.95, edgecolor='#b71c1c', linewidths=0.25)
mesh_shaft.set_facecolor('#ff9800')
ax2.add_collection3d(mesh_shaft)

# Helper function to draw 3D leader line and text tag
def add_3d_callout(ax, pt_model, pt_text, text, color='#000000', bgcolor='white', fontsize=8.0):
    ax.plot([pt_model[0], pt_text[0]], [pt_model[1], pt_text[1]], [pt_model[2], pt_text[2]],
            color=color, linestyle='-', linewidth=1.3, alpha=0.9)
    ax.scatter([pt_model[0]], [pt_model[1]], [pt_model[2]], color=color, s=25, depthshade=False)
    ax.text(pt_text[0], pt_text[1], pt_text[2], text, color=color, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', bbox=dict(boxstyle='round,pad=0.25', fc=bgcolor, ec=color, alpha=0.95, lw=1.2))

# 3D Subpart Callouts with carefully placed leader lines around perimeter
add_3d_callout(ax2, [0, 20.0, 6.77], [0.0, 33.0, 24.0], "Top Tab (Centered)\n(8.20mm W, fits 8.33mm gap)", color='#1565c0', bgcolor='white')
add_3d_callout(ax2, [4.65, 10.20, 14.09], [-22.0, 22.0, 26.0], "Left Tower & Cradle\n(Z=14.09mm)", color='#ad1457', bgcolor='#fce4ec')
add_3d_callout(ax2, [13.85, 10.20, 14.09], [22.0, 22.0, 26.0], "Right Tower & Bridge Rib\n(Z=14.09mm)", color='#ad1457', bgcolor='#fce4ec')
add_3d_callout(ax2, [2.5, 7.67, 4.0], [-29.0, 14.0, 14.0], "Left Buttress Struts\n(0.8mm & 1.2mm)", color='#c2185b', bgcolor='#fce4ec')
add_3d_callout(ax2, [7.05, 6.5, 8.0], [-3.0, 4.0, 20.0], "Enlarged Shaft Rocker\n(Ø2.8mm Pin, 4.4mm Plunger)", color='#e65100', bgcolor='#fff3e0')
add_3d_callout(ax2, [clip_pts[135.0][0], clip_pts[135.0][1], 6.77], [-30.0, 16.0, 6.0], "Snap Clip 135°\n(1.59mm Hook)", color='#00838f', bgcolor='#e0f7fa')
add_3d_callout(ax2, [clip_pts[45.0][0], clip_pts[45.0][1], 6.77], [30.0, 16.0, 6.0], "Snap Clip 45°\n(1.59mm Hook)", color='#00838f', bgcolor='#e0f7fa')
add_3d_callout(ax2, [-7.25, 0.0, 4.60], [-28.0, -12.0, 14.0], "Guide Brackets 1 & 2\n(4.60mm H)", color='#2e7d32', bgcolor='#e8f5e9')
add_3d_callout(ax2, [7.25, 0.0, 4.60], [28.0, -12.0, 14.0], "Guide Brackets 3 & 4\n(4.60mm H)", color='#2e7d32', bgcolor='#e8f5e9')
add_3d_callout(ax2, [-21.075, 0.0, 3.5], [-30.0, -2.0, -2.0], "Left Side Ear\n(8.20mm W, fits 8.3mm gap)", color='#0288d1', bgcolor='#e1f5fe')
add_3d_callout(ax2, [20.200, 0.0, 3.5], [30.0, -2.0, -2.0], "Right Side Ear\n(8.20mm W, fits 8.3mm gap)", color='#0288d1', bgcolor='#e1f5fe')
add_3d_callout(ax2, [6.28, -3.2, 10.50], [16.0, 0.0, 20.0], "Center Curved Feature\n(10.50mm H + Rib)", color='#6a1b9a', bgcolor='#f3e5f5')
add_3d_callout(ax2, [0, -8.7, 6.77], [0.0, -34.0, -6.0], "Bottom Central U-Arch\n(7.95mm H, 5mm Inner W)", color='#0d47a1', bgcolor='white')
add_3d_callout(ax2, [-8.38, -13.66, 0.0], [-17.0, -28.0, -6.0], "Left Slit Detent Socket\n(Press-Fit Insert)", color='#7b1fa2', bgcolor='#f3e5f5')
add_3d_callout(ax2, [8.38, -13.66, 0.0], [17.0, -28.0, -6.0], "Right Slit Detent Socket\n(Press-Fit Insert)", color='#7b1fa2', bgcolor='#f3e5f5')

ax2.set_xlim(-33, 33)
ax2.set_ylim(-33, 33)
ax2.set_zlim(-12, 26)
ax2.view_init(elev=30, azim=225)
ax2.set_title('2. 3D Isometric View (Assembly & All Subparts)', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')


# ==============================================================================
# PANEL 3: SIDE CROSS-SECTION (Y-Z PLANE) & Y-AXIS BUTTON ACTUATION
# ==============================================================================
ax3 = fig.add_subplot(1, 3, 3)

# Tower profile in Y-Z
y_tower_min, y_tower_max = 7.171, 13.771
z_tower_top = 14.09
ax3.fill([y_tower_min, y_tower_max, y_tower_max, y_tower_min],
         [1.0, 1.0, z_tower_top, z_tower_top], color='#cfd8dc', alpha=0.6, label='Tower Support Profile (14.09mm)')

# Baseplate floor (Z: 0 to 1.0mm)
ax3.fill([0, 18, 18, 0], [0, 0, 1.0, 1.0], color='#78909c', alpha=0.7, label='Base Floor (1.00mm thick, Z=0 datum)')
# Through-hole cutout in floor
ax3.fill([8.570, 13.082, 13.082, 8.570], [-0.1, -0.1, 1.1, 1.1], color='white')
ax3.plot([8.570, 8.570], [-0.1, 1.1], 'r--', linewidth=1.5)
ax3.plot([13.082, 13.082], [-0.1, 1.1], 'r--', linewidth=1.5)

# Shaft Pivot Center
y_axle, z_axle = 9.279, 12.590
ax3.plot(y_axle, z_axle, 'r+', markersize=14, markeredgewidth=2.5, label='Shaft Axis (Y=9.28, Z=12.59)')

# Plunger Arm Profile (Rest Position - Z = -6.50mm, Y = 10.48mm)
y_rest, z_rest = 10.479, -6.50
ax3.plot([y_axle, y_rest, y_rest], [z_axle, 4.0, z_rest], color='#e65100', linewidth=4.5, label='Output Plunger (Rest: Y=10.48mm)')

# Plunger Arm Profile (Actuated Position - rotated 7 deg CW)
theta_act = np.radians(7)
c_a, s_a = np.cos(theta_act), np.sin(theta_act)
rot_mat = np.array([[c_a, s_a], [-s_a, c_a]])
p_arm_home = np.array([y_rest - y_axle, z_rest - z_axle])
p_arm_act = rot_mat @ p_arm_home
y_act = y_axle + p_arm_act[0]
z_act = z_axle + p_arm_act[1]
ax3.plot([y_axle, y_act], [z_axle, z_act], color='#d32f2f', linestyle='--', linewidth=3.0, label=f'Actuated Plunger (Swings -Y to {y_act:.2f}mm)')

# Input Cam Profile (105° Bellcrank Angle, direct off shaft)
y_input, z_input = 2.83, 10.42
ax3.plot([y_axle, y_input], [z_axle, z_input], color='#ffb300', linewidth=4.5, label='Direct 105° Input Cam')

# Y-Axis Oriented Switch (Right-angle switch facing +Y at Z = -6.5mm)
ax3.fill([5.5, 8.5, 8.5, 5.5], [-7.5, -7.5, -5.5, -5.5], color='#4caf50', alpha=0.85, label='Y-Axis Switch Body')
ax3.fill([8.5, 9.2, 9.2, 8.5], [-6.8, -6.8, -6.2, -6.2], color='#2e7d32', alpha=0.9, label='Switch Actuator Stem (Faces +Y)')
ax3.plot([2.0, 10.0], [-7.8, -7.8], color='#1b5e20', linewidth=3, label='PCB Surface (Z = -7.8mm)')

# Annotations
ax3.annotate('Plug Prong Insertion Push\n(Right Blade Moves +Y)', xy=(y_input, z_input), xytext=(y_input - 3.5, z_input + 2.5),
             arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', width=2.2, headwidth=7),
             fontweight='bold', color='#b71c1c', fontsize=8.5, bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#b71c1c'))

ax3.annotate('Optimized Snap-Fit Cradle (2.60mm Throat)\nØ3.00mm Socket / Ø2.80mm Axle Snap (0.20mm Lock)', xy=(y_axle, z_axle + 0.6), xytext=(y_axle - 4.5, z_axle + 2.2),
             arrowprops=dict(arrowstyle='->', color='#ad1457', lw=1.5),
             fontweight='bold', color='#ad1457', fontsize=8, bbox=dict(boxstyle='round,pad=0.2', fc='#fce4ec', ec='#ad1457'))

ax3.annotate('Through-Hole Cutout\n(Y in [8.57, 13.08] mm)', xy=(10.826, 0.5), xytext=(13.2, 2.5),
             arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.5),
             fontweight='bold', color='#d32f2f', fontsize=8.5, bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#d32f2f'))

ax3.annotate(f'Kinematic Stroke: {y_rest - y_act:.2f}mm in -Y\n(Presses Y-axis switch stem)', xy=(y_act, z_act), xytext=(10.5, -9.8),
             arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', width=1.8, headwidth=6),
             fontweight='bold', color='#d32f2f', fontsize=8.5, bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#d32f2f'))

ax3.annotate('Tactile Switch Stem\nActuation Point (Z=-6.5mm)', xy=(8.85, -6.5), xytext=(0.5, -9.8),
             arrowprops=dict(arrowstyle='->', color='#2e7d32', lw=1.5),
             fontweight='bold', color='#2e7d32', fontsize=8.5, bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2e7d32'))

ax3.set_xlim(-2.0, 19.5)
ax3.set_ylim(-11.5, 17.0)
ax3.set_aspect('equal')
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.set_title("3. Y-Axis Kinematic Stroke: Plunger Swings Horizontally into Switch", fontsize=13, fontweight='bold', pad=12)
ax3.set_xlabel("Y (mm)")
ax3.set_ylabel("Z (mm)")
ax3.legend(loc='upper right', fontsize=7.5)

plt.tight_layout()
plt.savefig('labeled_part_preview.png', dpi=200)
print("Saved labeled_part_preview.png successfully!")

