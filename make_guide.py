"""
Regenerate tower measurement guide with Right Tower placed 5.4mm from the curved outer rim wall.
"""
import matplotlib.pyplot as plt
from shapely.geometry import box, LineString
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

# Right tower positioned 5.4mm from curved outer wall:
# At Y = 10.826mm, outer wall X = 16.198mm
y_mid = 10.826
ray_mid = LineString([(-5, y_mid), (30, y_mid)])
inter_outer = base_poly.exterior.intersection(ray_mid)
x_outer_at_ymid = max(p.x for p in (inter_outer.geoms if hasattr(inter_outer, 'geoms') else [inter_outer]))

x_right_outer = x_outer_at_ymid - 5.4  # ~10.80mm
x_right_inner = x_right_outer - TOWER_WALL_THICK  # ~9.80mm

x_left_inner = x_right_inner - TOWER_INTERNAL_GAP  # ~1.94mm
x_left_outer = x_left_inner - TOWER_WALL_THICK  # ~0.94mm

y_min = y_mid - TOWER_Y_LEN / 2.0  # 8.50mm
y_max = y_mid + TOWER_Y_LEN / 2.0  # 13.15mm

tower_left_box = box(x_left_outer, y_min, x_left_inner, y_max)
tower_right_box = box(x_right_inner, y_min, x_right_outer, y_max)

fig, ax = plt.subplots(figsize=(15, 15), dpi=180)

# 1. Base Perimeter Walls
x, y = base_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Curved Outer Perimeter Wall')
ix, iy = inner_wall_poly.exterior.xy
ax.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.5, label='Inner Perimeter Wall')

# 2. Holes & Slits
for interior in base_poly.interiors:
    hx, hy = interior.xy
    ax.plot(hx, hy, color='#d62728', linewidth=2, label='Floor Through-Holes' if interior == base_poly.interiors[0] else "")

# 3. Brackets
brackets_poly = create_all_brackets_poly()
for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
    bx, by = geom.exterior.xy
    ax.plot(bx, by, color='#2ca02c', linewidth=2, label='Guide Brackets' if geom == brackets_poly.geoms[0] else "")

# 4. Draw Support Towers (shaded magenta)
for tbox in [tower_left_box, tower_right_box]:
    tx, ty = tbox.exterior.xy
    ax.fill(tx, ty, color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=2, label='Support Towers' if tbox == tower_left_box else "")

# Draw shaft axis line across towers
ax.plot([x_left_outer - 1.5, x_right_outer + 1.5], [y_mid, y_mid], color='#ff7f0e', linestyle='-.', linewidth=2, label='Shaft Center Axis')

# Annotations & Callouts
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

ax.text(3.24, 2.0, "Bracket 3\n(Left component of right pair)", fontsize=10, fontweight='bold', color='#2ca02c', ha='center')
ax.text(9.32, 2.0, "Bracket 4\n(Right component of right pair)", fontsize=10, fontweight='bold', color='#2ca02c', ha='center')
ax.text(0, 20.6, "Top Tab (Y = 20.0 mm)", fontsize=11, fontweight='bold', color='#1f77b4', ha='center')
ax.text(14.0, 11.5, "Top-Right\nThrough-Hole", fontsize=10, fontweight='bold', color='#d62728', ha='left')

# [X4] Applied: 5.4mm from Curved Outer Rim Wall
ax.annotate('', xy=(x_right_outer, y_mid), xytext=(x_outer_at_ymid, y_mid),
            arrowprops=dict(arrowstyle='<->', color='#d62728', lw=3))
ax.text((x_right_outer + x_outer_at_ymid)/2, y_mid - 0.7, "[ X4 = 5.4 mm ]\n(Curved Outer Wall to Right Tower)",
        fontsize=10, fontweight='bold', color='#d62728', ha='center', va='top')

# [X3] Internal span: 7.86mm
ax.annotate('', xy=(x_left_inner, y_mid + 1.5), xytext=(x_right_inner, y_mid + 1.5),
            arrowprops=dict(arrowstyle='<->', color='#bcbd22', lw=2.5))
ax.text((x_left_inner + x_right_inner)/2, y_mid + 2.0, "[ X3 ] Internal Span = 7.86 mm",
        fontsize=10, fontweight='bold', color='#8c8d00', ha='center')

# [X1] Center spine (X=0) to Left Tower
ax.annotate('', xy=(0, y_mid - 2.0), xytext=(x_left_outer, y_mid - 2.0),
            arrowprops=dict(arrowstyle='<->', color='#ff7f0e', lw=2.5))
ax.text(x_left_outer/2, y_mid - 2.8, "[ X1 ] Center (X=0)\nto Left Tower",
        fontsize=9, fontweight='bold', color='#ff7f0e', ha='center')

# [Y1] Top Edge of Part (Y=20) to Top of Left Tower
ax.annotate('', xy=(x_left_inner, 20.0), xytext=(x_left_inner, y_max),
            arrowprops=dict(arrowstyle='<->', color='#9467bd', lw=2.5))
ax.text(x_left_inner - 0.4, (20.0 + y_max)/2, "[ Y1 ] Distance from\nTop Wall Outer Edge",
        fontsize=10, fontweight='bold', color='#9467bd', ha='right', va='center')

# [Y2] Top of Bracket 3 (Y=7.17) to Bottom of Left Tower
ax.annotate('', xy=(x_left_inner, 7.17), xytext=(x_left_inner, y_min),
            arrowprops=dict(arrowstyle='<->', color='#e377c2', lw=2.5))
ax.text(x_left_inner - 0.4, (7.17 + y_min)/2, "[ Y2 ] From Top of\nBracket 3 (Y=7.17)",
        fontsize=10, fontweight='bold', color='#c51b7d', ha='right', va='center')

# [Y3] Tower Length in Y
ax.annotate('', xy=(x_right_outer + 1.2, y_min), xytext=(x_right_outer + 1.2, y_max),
            arrowprops=dict(arrowstyle='<->', color='#17becf', lw=2))
ax.text(x_right_outer + 1.6, (y_min + y_max)/2, "[ Y3 ] Tower Y Length\n(4.65 mm)",
        fontsize=9, fontweight='bold', color='#17becf', va='center')

ax.set_xlim(-8, 22)
ax.set_ylim(0, 22)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title('Updated Shaft Support Towers Measurement Guide\n(Right Tower placed at X4 = 5.4 mm from Curved Outer Wall)', fontsize=13, fontweight='bold', pad=15)
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.savefig('tower_measurement_guide.png', dpi=180)
print("Saved updated tower_measurement_guide.png")
