"""
Generate a comprehensive, beautifully labeled part preview diagram
with all named features, dimensions, and callouts.
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
    find_boundary_point_and_normal
)

# 1. Build 3D mesh and base poly
part_mesh, base_poly = build_exact_3d_model()
base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

# Setup Figure
fig = plt.figure(figsize=(26, 12), dpi=200)

# ==============================================================================
# PANEL 1: 2D TOP-DOWN SCHEMATIC WITH ALL NAMED FEATURE CALLOUTS
# ==============================================================================
ax1 = fig.add_subplot(1, 2, 1)

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
for angle_deg in [45, 135, 225, 315]:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    ax1.plot(p[0], p[1], 'o', color='#17becf', markersize=7)

# Shaft centerline axis
ax1.plot([left_t_x - 4, right_t_x + 3], [7.666, 7.666], color='#8c564b', linestyle='-.', linewidth=1.8)

# ------------------------------------------------------------------------------
# ANNOTATIONS & FEATURE LABELS (2D)
# ------------------------------------------------------------------------------
# 1. Top Tab
ax1.annotate('Top Tab\n(Width: 8.22mm)', xy=(0, 20.0), xytext=(-16, 21.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=10, fontweight='bold', color='#1f77b4', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1f77b4'))

# 2. Side Ears / Tabs
ax1.annotate('Left Side Ear', xy=(-20.5, 0), xytext=(-28, 0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#1f77b4', va='center')
ax1.annotate('Right Side Ear', xy=(20.5, 0), xytext=(22, 0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#1f77b4', va='center')

# 3. 4x Snap Clips
ax1.annotate('Snap Clip (45°)\nFlush with Inner Wall (1.20mm)\n1.59mm Radial Hook', xy=(13.5, 13.5), xytext=(17, 16.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#0e8188', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#0e8188'))
ax1.annotate('Snap Clip (135°)', xy=(-13.5, 13.5), xytext=(-22, 15.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#0e8188')
ax1.annotate('Snap Clip (225°)', xy=(-13.5, -13.5), xytext=(-24, -13.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#0e8188')
ax1.annotate('Snap Clip (315°)', xy=(13.5, -13.5), xytext=(16, -13.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#0e8188')

# 4. Guide Brackets
ax1.text(-6.0, 0, 'Bracket Pair 1 & 2\n(Height: 4.60mm)', color='#2ca02c', fontsize=9.5, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.2', fc='#e8f5e9', ec='#2ca02c'))
ax1.text(3.2, -2.0, 'Bracket 3', color='#2ca02c', fontsize=9, fontweight='bold', ha='center')
ax1.text(9.3, -2.0, 'Bracket 4', color='#2ca02c', fontsize=9, fontweight='bold', ha='center')

# 4b. Center Curved Feature (10.5mm tall)
curved_feat_poly = create_center_curved_feature_poly()
for geom in (curved_feat_poly.geoms if hasattr(curved_feat_poly, 'geoms') else [curved_feat_poly]):
    cx_pts, cy_pts = geom.exterior.xy
    ax1.fill(cx_pts, cy_pts, color='#ab47bc', alpha=0.6)
    ax1.plot(cx_pts, cy_pts, color='#8e24aa', linewidth=2.0)
    for interior in geom.interiors:
        ax1.plot(*interior.xy, color='#8e24aa', linewidth=1.5)

ax1.annotate('Center Curved Feature (10.50mm tall)\n(4.30mm wide x 1.62mm in Y\nInternal center rib, 2mm above bracket step)', xy=(6.28, -3.2), xytext=(-6.0, -2.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#6a1b9a', bbox=dict(boxstyle='round,pad=0.2', fc='#f3e5f5', ec='#8e24aa'))

# 5. Shaft Support Towers
ax1.annotate('Left Tower (12.59mm tall)\nThick: 1.25mm\nØ2mm Shaft Cradle', xy=(4.87, 8.5), xytext=(-5.0, 12.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9.5, fontweight='bold', color='#c51b7d', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#c51b7d'))

ax1.annotate('Right Tower (12.59mm tall)\nThick: 1.25mm\n0.40mm Right of Hole', xy=(13.98, 8.5), xytext=(16.5, 12.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9.5, fontweight='bold', color='#c51b7d', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#c51b7d'))

# 6. Triangular Buttress Struts
ax1.annotate('Steep Triangular Struts (2x)\nBase: 2.35mm outreach\nDirect slope into tower\n(2mm below apex, no top flat)', xy=(2.6, 9.6), xytext=(-12, 8.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#d62728', bbox=dict(boxstyle='round,pad=0.2', fc='#fbe9e7', ec='#d62728'))

# 7. Reinforced Bridge Rib
ax1.annotate('Reinforcing Bridge Rib\n(Extruded to full 6.77mm\nouter wall height)', xy=(15.5, 7.5), xytext=(17.0, 5.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#d62728', bbox=dict(boxstyle='round,pad=0.2', fc='#fbe9e7', ec='#d62728'))

# 8. Top-Right Floor Through-Hole
ax1.annotate('Top-Right Through-Hole\n5.35mm x 4.51mm', xy=(10.28, 10.83), xytext=(3.0, 16.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#d62728', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#d62728'))

# 9. Internal clearance span
ax1.annotate('Internal Clearance: 7.86mm', xy=(9.43, 6.0), xytext=(9.43, 6.0),
             fontsize=8.5, fontweight='bold', color='#8c564b', ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.15', fc='#fff3e0', ec='#8c564b'))

# 10. Floor Grid Ribs
ax1.annotate('Floor Stiffener Ribs (0.5mm tall)\n5.20mm x 3.20mm Grid\nDirectly connected to outer walls', xy=(-15, 6.4), xytext=(-26, 7.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#e65100', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#e65100'))

# Arch Wall (6.77mm)
arch_poly = create_arch_wall_poly()
ax1.plot(*arch_poly.exterior.xy, color='#1f77b4', linewidth=2.0)

# 11. Bottom Central Arch Wall
ax1.annotate('Bottom Central Arch Wall\n(5.00mm Interior Width at Base\nHeight: 6.77mm, Thick: 1.20mm)', xy=(0, -11.0), xytext=(-22, -7.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#1f77b4', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#1f77b4'))

# 12. Backside Slit Walls
ax1.annotate('Backside Slit Walls (2x)\n(Protrude 2.47mm on -Z side\naround 1.1x3.0mm slits)', xy=(-8.4, -14.8), xytext=(-26, -18.5),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#6a1b9a', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#6a1b9a'))

# 13. Bottom Inset Wall & Floor
ax1.annotate('Inset Bottom Exterior Wall\n(1.88mm inset at Y = -16.66mm\nSolid Floor within wall)', xy=(0, -16.66), xytext=(5, -21.0),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
             fontsize=9, fontweight='bold', color='#333333', bbox=dict(boxstyle='round,pad=0.2', fc='#e0f2f1', ec='#00695c'))

ax1.set_xlim(-29, 29)
ax1.set_ylim(-23, 24)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title('Top-Down 2D Dimensioned Feature Map', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('X (mm)', fontsize=10)
ax1.set_ylabel('Y (mm)', fontsize=10)

# ==============================================================================
# PANEL 2: 3D ISOMETRIC TOP VIEW WITH 3D CALLOUTS
# ==============================================================================
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
vertices = part_mesh.vertices
faces = part_mesh.faces
mesh_col = Poly3DCollection(vertices[faces], alpha=0.85, edgecolor='#333333', linewidths=0.15)
mesh_col.set_facecolor('#4A90E2')
ax2.add_collection3d(mesh_col)

# 3D Feature text tags
ax2.text(4.87, 7.67, 14.5, "Left Shaft Tower\n(12.59mm)", color='#c51b7d', fontsize=9.5, fontweight='bold', ha='center')
ax2.text(13.98, 7.67, 14.5, "Right Shaft Tower\n(12.59mm)", color='#c51b7d', fontsize=9.5, fontweight='bold', ha='center')
ax2.text(1.5, 7.67, 6.0, "Triangular\nStruts", color='#d62728', fontsize=9, fontweight='bold', ha='center')
ax2.text(16.5, 6.0, 7.5, "Bridge Rib\n(6.77mm)", color='#d62728', fontsize=9, fontweight='bold', ha='center')
ax2.text(-6.0, 0, 6.5, "Guide Brackets (4.6mm)", color='#2ca02c', fontsize=9, fontweight='bold', ha='center')
ax2.text(6.28, -3.2, 11.8, "Center Curved Feature\n(10.50mm)", color='#6a1b9a', fontsize=9, fontweight='bold', ha='center')
ax2.text(0, 20.0, 8.0, "Top Tab (6.77mm wall)", color='#1f77b4', fontsize=9, fontweight='bold', ha='center')
ax2.text(13.5, 13.5, 8.5, "Snap Clip (45°)", color='#0e8188', fontsize=9, fontweight='bold')
ax2.text(0, -18.0, 4.0, "Bottom Arch & Tab", color='#1f77b4', fontsize=9, fontweight='bold', ha='center')
ax2.text(-8.0, -15.0, -3.5, "Backside Slit Walls\n(2.47mm)", color='#6a1b9a', fontsize=9, fontweight='bold', ha='center')

ax2.set_xlim(-24, 24)
ax2.set_ylim(-24, 24)
ax2.set_zlim(-4, 16)
ax2.view_init(elev=26, azim=220)
ax2.set_title('3D Isometric Perspective of Complete Assembly', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('X (mm)', fontsize=10)
ax2.set_ylabel('Y (mm)', fontsize=10)
ax2.set_zlabel('Z (mm)', fontsize=10)

plt.tight_layout()
plt.savefig('labeled_part_preview.png', dpi=200)
print("Saved labeled_part_preview.png successfully!")
