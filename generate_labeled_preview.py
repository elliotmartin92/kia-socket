"""
Generate a comprehensive, beautifully labeled part preview diagram
with all named features, dimensions, shaft/rocker kinematics, and Y-axis button actuation.
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

# 1. Build 3D mesh and base poly
part_mesh, base_poly = build_exact_3d_model()
base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

shaft_assembled_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)

# Setup Figure (3 panels: 2D Feature Map, 3D Isometric Assembly, Y-Axis Kinematic Stroke Cross-Section)
fig = plt.figure(figsize=(30, 11), dpi=200)

# ==============================================================================
# PANEL 1: 2D TOP-DOWN SCHEMATIC WITH ALL NAMED FEATURE CALLOUTS
# ==============================================================================
ax1 = fig.add_subplot(1, 3, 1)

# Outer and Inner Perimeter Wall
x, y = outer_body_poly.exterior.xy
ax1.plot(x, y, color='#1f77b4', linewidth=2.5, label='Perimeter Wall (6.77mm)')
ix, iy = inner_wall_poly.exterior.xy
ax1.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.2, label='Inner Wall Face (1.2mm thick)')

# Through Holes (Floor cutouts)
for interior in base_poly.interiors:
    hx, hy = interior.xy
    ax1.plot(hx, hy, color='#d62728', linewidth=2.0)

# Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax1.plot(bx, by, color='#2ca02c', linewidth=2.0)

# Ribs (Connected Grid)
all_ribs_poly = create_grid_ribs_poly(base_poly, outer_body_poly)
for geom in (all_ribs_poly.geoms if hasattr(all_ribs_poly, 'geoms') else [all_ribs_poly]):
    rx, ry = geom.exterior.xy
    ax1.plot(rx, ry, color='#ff7f0e', linewidth=0.9, alpha=0.8)

# Shaft Towers (Bounding box)
left_t_x = 4.25
right_t_x = 13.36
y_min = 5.341
y_max = 9.991
ax1.fill([left_t_x, left_t_x + 1.25, left_t_x + 1.25, left_t_x], [y_min, y_min, y_max, y_max],
         color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=1.5)
ax1.fill([right_t_x, right_t_x + 1.25, right_t_x + 1.25, right_t_x], [y_min, y_min, y_max, y_max],
         color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=1.5)

# Left Tower Struts (Footprint)
ax1.fill([left_t_x - 2.35, left_t_x, left_t_x, left_t_x - 2.35], [y_min, y_min, y_min + 0.8, y_min + 0.8],
         color='#d62728', alpha=0.85, edgecolor='#880000', linewidth=1.2)
ax1.fill([left_t_x - 2.35, left_t_x, left_t_x, left_t_x - 2.35], [y_max - 0.8, y_max - 0.8, y_max, y_max],
         color='#d62728', alpha=0.85, edgecolor='#880000', linewidth=1.2)

# Bridge Rib (Right of right tower)
bridge_box = sg.box(13.36, 6.0, 25.0, 10.0)
bridge_ribs_poly = all_ribs_poly.intersection(bridge_box)
for geom in (bridge_ribs_poly.geoms if hasattr(bridge_ribs_poly, 'geoms') else [bridge_ribs_poly]):
    bx, by = geom.exterior.xy
    ax1.fill(bx, by, color='#ff9896', alpha=0.9, edgecolor='#d62728', linewidth=1.5)

# Backside Slit Bosses (Dashed purple)
bosses_poly = create_backside_slit_bosses_poly()
for geom in (bosses_poly.geoms if hasattr(bosses_poly, 'geoms') else [bosses_poly]):
    bx, by = geom.exterior.xy
    ax1.plot(bx, by, color='#9467bd', linestyle='--', linewidth=1.8)

# Snap Clip positions
for angle_deg in CLIP_ANGLES:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    ax1.plot(p[0], p[1], 'o', color='#17becf', markersize=7)

# Shaft Axle & Plunger Top-Down Footprint
ax1.plot([3.05, 15.81], [7.666, 7.666], color='#ff6f00', linewidth=3.5, label='Ø1.90mm Shaft Axle')
ax1.fill([10.284 - 1.5, 10.284 + 1.5, 10.284 + 1.5, 10.284 - 1.5],
         [7.666, 7.666, 12.35, 12.35], color='#e65100', alpha=0.8, label='Output Plunger (Through Hole)')
ax1.fill([6.60 - 1.0, 6.60 + 1.0, 6.60 + 1.0, 6.60 - 1.0],
         [3.17, 3.17, 7.666, 7.666], color='#ffd54f', alpha=0.9, edgecolor='#ff8f00', linewidth=1.5, label='Input Cam (Bar Contact)')

# Annotations
ax1.annotate('Top Tab\n(Width: 8.22mm)', xy=(0, 20.0), xytext=(-16, 21.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9.5, fontweight='bold', color='#1f77b4', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1f77b4'))

ax1.annotate('Snap Clip (45°)\n1.59mm Radial Hook', xy=(13.5, 13.5), xytext=(17, 16.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#0e8188', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#0e8188'))

ax1.text(-6.0, 0, 'Bracket Pair 1 & 2\n(Height: 4.60mm)', color='#2ca02c', fontsize=9, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2ca02c'))

curved_feat_poly = create_center_curved_feature_poly()
for geom in (curved_feat_poly.geoms if hasattr(curved_feat_poly, 'geoms') else [curved_feat_poly]):
    cx_pts, cy_pts = geom.exterior.xy
    ax1.fill(cx_pts, cy_pts, color='#ab47bc', alpha=0.6)
    ax1.plot(cx_pts, cy_pts, color='#8e24aa', linewidth=2.0)

ax1.annotate('Center Curved Feature (10.50mm)', xy=(6.28, -3.2), xytext=(-6.0, -3.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#6a1b9a', bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#8e24aa'))

ax1.annotate('Shaft Support Towers (12.59mm)\nØ2mm Cradle with 1.65mm Throat', xy=(4.87, 8.5), xytext=(-8.0, 13.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#c51b7d', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#c51b7d'))

ax1.annotate('Top-Right Through-Hole (5.35x4.51mm)\nPlunger Reaches ≥6.5mm Below Floor', xy=(10.28, 10.83), xytext=(4.0, 17.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#d62728', bbox=dict(boxstyle='round,pad=0.2', fc='#ffebee', ec='#d62728'))

arch_poly = create_arch_wall_poly()
ax1.plot(*arch_poly.exterior.xy, color='#1f77b4', linewidth=2.0)

ax1.annotate('Bottom Central Arch Wall (7.95mm H)\n(5.00mm Inner Width at Base)', xy=(0, -8.7), xytext=(-24, -7.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#1f77b4', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1f77b4'))

ax1.annotate('Through Slits 1.05x3.35mm (2x)\n(Flat Z=0; Separate Inserts)', xy=(-8.4, -14.8), xytext=(-26, -18.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#6a1b9a', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#6a1b9a'))

ax1.set_xlim(-29, 29)
ax1.set_ylim(-23, 24)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title('1. Top-Down 2D Dimensioned Feature Map', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')

# ==============================================================================
# PANEL 2: 3D ISOMETRIC TOP VIEW WITH SEATED SHAFT MECHANISM
# ==============================================================================
ax2 = fig.add_subplot(1, 3, 2, projection='3d')

# Baseplate mesh
v_base = part_mesh.vertices
f_base = part_mesh.faces
mesh_col = Poly3DCollection(v_base[f_base], alpha=0.65, edgecolor='#2c3e50', linewidths=0.15)
mesh_col.set_facecolor('#4A90E2')
ax2.add_collection3d(mesh_col)

# Seated shaft mechanism (gold/orange)
v_shaft = shaft_assembled_mesh.vertices
f_shaft = shaft_assembled_mesh.faces
mesh_shaft = Poly3DCollection(v_shaft[f_shaft], alpha=0.95, edgecolor='#b71c1c', linewidths=0.3)
mesh_shaft.set_facecolor('#ff9800')
ax2.add_collection3d(mesh_shaft)

# 3D Feature text tags
ax2.text(4.87, 7.67, 15.0, "Shaft & Towers\n(Z=12.59mm)", color='#c51b7d', fontsize=9, fontweight='bold', ha='center')
ax2.text(10.28, 10.83, -7.5, "Plunger Reach\n(Z ≤ -6.50mm)", color='#d32f2f', fontsize=9, fontweight='bold', ha='center')
ax2.text(-6.0, 0, 6.5, "Guide Brackets", color='#2ca02c', fontsize=9, fontweight='bold', ha='center')
ax2.text(6.28, -3.2, 11.8, "Center Feature (10.5mm)", color='#6a1b9a', fontsize=9, fontweight='bold', ha='center')
ax2.text(0, 20.0, 8.0, "Top Tab", color='#1f77b4', fontsize=9, fontweight='bold', ha='center')
ax2.text(0, -18.0, 4.0, "Bottom Arch", color='#1f77b4', fontsize=9, fontweight='bold', ha='center')

ax2.set_xlim(-24, 24)
ax2.set_ylim(-24, 24)
ax2.set_zlim(-8, 16)
ax2.view_init(elev=28, azim=225)
ax2.set_title('2. 3D Isometric View (Baseplate + Seated Shaft Rocker)', fontsize=13, fontweight='bold', pad=12)
ax2.set_xlabel('X (mm)')
ax2.set_ylabel('Y (mm)')
ax2.set_zlabel('Z (mm)')

# ==============================================================================
# PANEL 3: SIDE CROSS-SECTION (Y-Z PLANE) & Y-AXIS BUTTON ACTUATION
# ==============================================================================
ax3 = fig.add_subplot(1, 3, 3)

# Tower profile in Y-Z
y_tower_min, y_tower_max = 5.341, 9.991
z_tower_top = 13.59
ax3.fill([y_tower_min, y_tower_max, y_tower_max, y_tower_min],
         [1.0, 1.0, z_tower_top, z_tower_top], color='#cfd8dc', alpha=0.6, label='Tower Support Profile')

# Baseplate floor (Z: 0 to 1.0mm)
ax3.fill([0, 18, 18, 0], [0, 0, 1.0, 1.0], color='#78909c', alpha=0.7, label='Base Floor (1.0mm)')
# Through-hole cutout in floor
ax3.fill([8.570, 13.082, 13.082, 8.570], [-0.1, -0.1, 1.1, 1.1], color='white')
ax3.plot([8.570, 8.570], [-0.1, 1.1], 'r--', linewidth=1.5)
ax3.plot([13.082, 13.082], [-0.1, 1.1], 'r--', linewidth=1.5)

# Shaft Pivot Center
y_axle, z_axle = 7.666, 12.590
ax3.plot(y_axle, z_axle, 'r+', markersize=12, markeredgewidth=2.2, label='Shaft Axis (Y=7.67, Z=12.59)')

# Plunger Arm Profile (Rest Position - Z = -6.50mm, Y = 11.60mm)
y_rest, z_rest = 11.60, -6.50
ax3.plot([y_axle, y_rest, y_rest], [z_axle, 4.0, z_rest], color='#e65100', linewidth=4.5, label='Output Plunger (Rest: Y=11.60mm)')

# Plunger Arm Profile (Actuated Position - rotated 7 deg CW)
theta_act = np.radians(7)
c_a, s_a = np.cos(theta_act), np.sin(theta_act)
rot_mat = np.array([[c_a, s_a], [-s_a, c_a]])
p_arm_home = np.array([y_rest - y_axle, z_rest - z_axle])
p_arm_act = rot_mat @ p_arm_home
y_act = y_axle + p_arm_act[0]
z_act = z_axle + p_arm_act[1]
ax3.plot([y_axle, y_act], [z_axle, z_act], color='#d32f2f', linestyle='--', linewidth=3.0, label=f'Actuated Plunger (Swings -Y to {y_act:.2f}mm)')

# Input Cam Profile (Pushed +Y by key)
y_input, z_input = 3.17, 6.59
ax3.plot([y_axle, y_input], [z_axle, z_input], color='#ffb300', linewidth=4.5, label='Input Cam (Bar Contact)')

# Y-Axis Oriented Switch (Right-angle switch facing +Y at Z = -6.5mm)
ax3.fill([5.5, 8.5, 8.5, 5.5], [-7.5, -7.5, -5.5, -5.5], color='#4caf50', alpha=0.85, label='Y-Axis Switch Body')
ax3.fill([8.5, 9.2, 9.2, 8.5], [-6.8, -6.8, -6.2, -6.2], color='#2e7d32', alpha=0.9, label='Switch Actuator Stem (Faces +Y)')
ax3.plot([2.0, 10.0], [-7.8, -7.8], color='#1b5e20', linewidth=3, label='PCB Surface (Z = -7.8mm)')

# Annotations
ax3.annotate('Key Insertion Push\n(Moves along +Y)', xy=(y_input, z_input), xytext=(y_input - 3.2, z_input + 2.5),
             arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', width=2.5, headwidth=8),
             fontweight='bold', color='#b71c1c', fontsize=9.5)

ax3.annotate('Through-Hole\n(Y in [8.57, 13.08])', xy=(10.826, 0.5), xytext=(14.0, 2.5),
             arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.5),
             fontweight='bold', color='#d32f2f', fontsize=9.5)

ax3.annotate(f'Horizontal Stroke: {y_rest - y_act:.2f}mm in -Y\n(Presses Y-axis switch stem)', xy=(y_act, z_act), xytext=(11.5, -9.0),
             arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', width=2, headwidth=7),
             fontweight='bold', color='#d32f2f', fontsize=9.5)

ax3.set_xlim(-1.0, 19.0)
ax3.set_ylim(-11.0, 16.0)
ax3.set_aspect('equal')
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.set_title("3. Y-Axis Kinematic Stroke: Plunger Swings Horizontally into Switch", fontsize=13, fontweight='bold', pad=12)
ax3.set_xlabel("Y (mm)")
ax3.set_ylabel("Z (mm)")
ax3.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('labeled_part_preview.png', dpi=200)
print("Saved labeled_part_preview.png successfully!")
