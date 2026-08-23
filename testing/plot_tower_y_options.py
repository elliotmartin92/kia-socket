"""
Plot comparison of Option A (top edge 6.77mm from interior wall) vs
Option B (cradle center 6.77mm from interior wall).
"""
import matplotlib.pyplot as plt
from shapely.geometry import box
from shapely.ops import unary_union
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, to_mm_poly, OUTER_WALL_THICK,
    TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

b3 = to_mm_poly(bracket_3_raw_pts)
b3_center_x = (b3.bounds[0] + b3.bounds[2]) / 2.0  # 3.236mm

x_left_min = b3_center_x - TOWER_WALL_THICK / 2.0
x_left_max = b3_center_x + TOWER_WALL_THICK / 2.0

x_right_min = x_left_max + TOWER_INTERNAL_GAP
x_right_max = x_right_min + TOWER_WALL_THICK

# Closest point on inner wall above left tower center
y_inner_wall = 17.395

# Option A: Top edge of tower is 6.77mm from inner wall (Y_top = 10.625mm)
y_top_A = y_inner_wall - 6.77
y_bot_A = y_top_A - TOWER_Y_LEN
box_left_A = box(x_left_min, y_bot_A, x_left_max, y_top_A)
box_right_A = box(x_right_min, y_bot_A, x_right_max, y_top_A)

# Option B: Center axis of cradle is 6.77mm from inner wall (Y_mid = 10.625mm)
y_mid_B = y_inner_wall - 6.77
y_top_B = y_mid_B + TOWER_Y_LEN / 2.0
y_bot_B = y_mid_B - TOWER_Y_LEN / 2.0
box_left_B = box(x_left_min, y_bot_B, x_left_max, y_top_B)
box_right_B = box(x_right_min, y_bot_B, x_right_max, y_top_B)

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=150)

for idx, (title, l_box, r_box, y_cradle, desc) in enumerate([
    ("Option A: Top Edge of Tower is 6.77mm from Interior Wall", box_left_A, box_right_A, (y_top_A + y_bot_A)/2, f"Top Y = {y_top_A:.2f}mm, Bot Y = {y_bot_A:.2f}mm"),
    ("Option B: Cradle Center/Shaft is 6.77mm from Interior Wall", box_left_B, box_right_B, y_mid_B, f"Top Y = {y_top_B:.2f}mm, Bot Y = {y_bot_B:.2f}mm (Centered over hole)")
]):
    ax = axes[idx]
    
    # Outer & Inner Wall
    x, y = base_poly.exterior.xy
    ax.plot(x, y, color='#1f77b4', linewidth=2, label='Outer Perimeter')
    ix, iy = inner_wall_poly.exterior.xy
    ax.plot(ix, iy, color='#1f77b4', linestyle=':', linewidth=1.5, label='Interior Wall')
    
    for interior in base_poly.interiors:
        hx, hy = interior.xy
        ax.plot(hx, hy, color='#d62728', linewidth=1.5)
        
    brackets_poly = create_all_brackets_poly()
    for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
        bx, by = geom.exterior.xy
        ax.plot(bx, by, color='#2ca02c', linewidth=1.5)
        
    for t_box in [l_box, r_box]:
        tx, ty = t_box.exterior.xy
        ax.fill(tx, ty, color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=1.5)
        
    # Draw dimension line from inner wall to feature
    ref_y = y_top_A if idx == 0 else y_mid_B
    ax.plot([b3_center_x, b3_center_x], [ref_y, y_inner_wall], color='purple', linestyle='--', linewidth=1.5)
    ax.annotate(f'6.77 mm', xy=(b3_center_x + 0.3, (ref_y + y_inner_wall)/2), fontsize=9, fontweight='bold', color='purple')
    
    # Draw shaft axis line
    ax.plot([x_left_min - 1, x_right_max + 1], [y_cradle, y_cradle], color='#ff7f0e', linestyle='-', linewidth=2, label='Shaft Axis')
    
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-5, 20)
    ax.set_ylim(0, 22)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.legend(loc='lower left', fontsize=8)

plt.tight_layout()
plt.savefig('tower_options_comparison.png', dpi=150)
print("Saved tower_options_comparison.png")
