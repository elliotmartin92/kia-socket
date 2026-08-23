"""
Plot options for shifting towers to the right so right tower sits to the right of the hole.
"""
import matplotlib.pyplot as plt
from shapely.geometry import box
import numpy as np

from build_part import (
    get_exact_base_polygon, create_all_brackets_poly,
    bracket_3_raw_pts, bracket_4_raw_pts, to_mm_poly,
    OUTER_WALL_THICK, TOWER_Y_LEN, TOWER_WALL_THICK, TOWER_INTERNAL_GAP
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

hole_right_x = hole_x + hole_w / 2.0  # 12.960mm
print(f"Top-right hole right edge X: {hole_right_x:.3f} mm")

y_min = -17.339 + 22.68  # 5.341mm
y_max = y_min + TOWER_Y_LEN  # 9.991mm
y_shaft = (y_min + y_max) / 2.0  # 7.666mm

# Test offsets where right tower inner face is:
# Option 1: Right tower inner face exactly at hole right edge (X = 12.960mm, gap = 0mm)
# Option 2: Right tower inner face 0.5mm to the right of hole (X = 13.460mm)
# Option 3: Right tower inner face 1.0mm to the right of hole (X = 13.960mm)

offsets = [
    ("Shift +0.40mm (Right tower flush with hole edge: X_inner=12.96mm)", 12.960),
    ("Shift +0.80mm (Right tower 0.4mm right of hole: X_inner=13.36mm)", 13.360),
    ("Shift +1.20mm (Right tower 0.8mm right of hole: X_inner=13.76mm)", 13.760),
]

fig, axes = plt.subplots(1, 3, figsize=(21, 8), dpi=160)

for idx, (title, x_r_inner) in enumerate(offsets):
    ax = axes[idx]
    
    x_r_outer = x_r_inner + TOWER_WALL_THICK
    x_l_inner = x_r_inner - TOWER_INTERNAL_GAP
    x_l_outer = x_l_inner - TOWER_WALL_THICK
    
    l_box = box(x_l_outer, y_min, x_l_inner, y_max)
    r_box = box(x_r_inner, y_min, x_r_outer, y_max)
    
    # Base and rim
    x, y = base_poly.exterior.xy
    ax.plot(x, y, color='#1f77b4', linewidth=2)
    ix, iy = inner_wall_poly.exterior.xy
    ax.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.2)
    
    # Holes
    for interior in base_poly.interiors:
        hx, hy = interior.xy
        ax.plot(hx, hy, color='#d62728', linewidth=2)
        
    # Brackets
    brackets_poly = create_all_brackets_poly()
    for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
        bx, by = geom.exterior.xy
        ax.plot(bx, by, color='#2ca02c', linewidth=1.8)
        
    # Towers
    for tbox in [l_box, r_box]:
        tx, ty = tbox.exterior.xy
        ax.fill(tx, ty, color='#e377c2', alpha=0.85, edgecolor='#c51b7d', linewidth=2)
        
    ax.plot([x_l_outer - 1, x_r_outer + 1], [y_shaft, y_shaft], color='#ff7f0e', linestyle='-.', linewidth=2)
    
    ax.set_xlim(-2, 18)
    ax.set_ylim(0, 18)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_title(title, fontsize=9.5, fontweight='bold')
    
    print(f"\n{title}:")
    print(f"  Left Tower X: [{x_l_outer:.3f}, {x_l_inner:.3f}]")
    print(f"  Right Tower X: [{x_r_inner:.3f}, {x_r_outer:.3f}]")
    print(f"  Clearance to hole right edge ({hole_right_x:.3f}mm): {x_r_inner - hole_right_x:.3f}mm")

plt.tight_layout()
plt.savefig('tower_shift_options.png', dpi=160)
print("Saved tower_shift_options.png")
