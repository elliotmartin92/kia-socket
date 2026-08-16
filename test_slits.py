"""
Test placement and orientation of the two bottom slits/holes.
"""
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union

from build_part import get_exact_base_polygon, create_all_brackets_poly, create_grid_ribs_poly, SCALE, X0, Y0

base_poly, hole_info = get_exact_base_polygon()
brackets_poly = create_all_brackets_poly()

# Slit parameters
SLIT_LEN = 3.00
SLIT_W = 1.10
# 4.22mm down from bottom of brackets (bottom of brackets is Y = -7.20mm)
SLIT_Y = -7.20 - 4.22  # Y = -11.42mm

# Let's test two plausible X placements and orientations:
# Placement 1: Horizontal slits at X = +/- 6.5mm (centered in the bottom-left & bottom-right floor bays)
# Placement 2: Horizontal slits at X = +/- 8.5mm (under outer brackets)
# Placement 3: Vertical slits

fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)

for idx, (title, is_horizontal, x_pos) in enumerate([
    ("Option A: Horizontal Slits (3.0 x 1.1mm) at X = ±6.5mm", True, 6.5),
    ("Option B: Horizontal Slits (3.0 x 1.1mm) at X = ±8.0mm", True, 8.0),
]):
    ax = axes[idx]
    
    # Plot base perimeter
    x, y = base_poly.exterior.xy
    ax.plot(x, y, color='#1f77b4', linewidth=2, label='Outer Wall')
    for interior in base_poly.interiors:
        ix, iy = interior.xy
        ax.plot(ix, iy, color='#1f77b4', linewidth=1.5)
        
    # Plot brackets
    for geom in (brackets_poly.geoms if hasattr(brackets_poly, 'geoms') else [brackets_poly]):
        bx, by = geom.exterior.xy
        ax.plot(bx, by, color='#2ca02c', linewidth=1.5)
        
    # Create the two slits
    if is_horizontal:
        s_left = box(-x_pos - SLIT_LEN/2, SLIT_Y - SLIT_W/2, -x_pos + SLIT_LEN/2, SLIT_Y + SLIT_W/2)
        s_right = box(x_pos - SLIT_LEN/2, SLIT_Y - SLIT_W/2, x_pos + SLIT_LEN/2, SLIT_Y + SLIT_W/2)
    else:
        s_left = box(-x_pos - SLIT_W/2, SLIT_Y - SLIT_LEN/2, -x_pos + SLIT_W/2, SLIT_Y + SLIT_LEN/2)
        s_right = box(x_pos - SLIT_W/2, SLIT_Y - SLIT_LEN/2, x_pos + SLIT_W/2, SLIT_Y + SLIT_LEN/2)
        
    for s, name in [(s_left, 'Left Slit'), (s_right, 'Right Slit')]:
        sx, sy = s.exterior.xy
        ax.fill(sx, sy, color='#d62728', alpha=0.9, edgecolor='black', linewidth=1.2)
        
    # Dimension Callouts
    ax.annotate(f'4.22mm down\nfrom brackets', 
                xy=(-x_pos, -7.20), xytext=(-x_pos - 4, -9.5),
                fontsize=8, fontweight='bold',
                arrowprops=dict(arrowstyle='<->', color='purple'))
                
    ax.annotate(f'Slit: {SLIT_LEN}x{SLIT_W}mm\nY = {SLIT_Y:.2f}mm\nX = ±{x_pos:.1f}mm', 
                xy=(x_pos, SLIT_Y), xytext=(x_pos + 2.5, SLIT_Y - 2.5),
                fontsize=8, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red'))

    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(-22, 22)
    ax.set_ylim(-22, 22)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')

plt.tight_layout()
plt.savefig('slits_preview.png', dpi=150)
print("Saved slits_preview.png")
