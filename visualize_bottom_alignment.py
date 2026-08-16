"""
Visualize aligned bottom arch and inset exterior wall notch options.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import (
    outer_pts, SCALE, X0, Y0, OUTER_WALL_THICK,
    create_arch_wall_poly, get_exact_base_polygon
)

# Base points converted to mm
raw_mm_pts = [((x - X0) * SCALE, -(y - Y0) * SCALE) for x, y in outer_pts]

def build_aligned_perimeter_poly(notch_x_left, notch_x_right):
    """Replaces the bottom notch coordinates in raw_mm_pts with exact aligned coordinates."""
    new_pts = []
    # Bottom points in raw_mm_pts:
    # We find the indices around the bottom tabs and notch
    for x, y in raw_mm_pts:
        if y < -16.0:
            continue
        new_pts.append((x, y))
        
    # Reconstruct bottom perimeter cleanly:
    # Right side: from (9.812, -15.95) down to (9.812, -18.539), then to (notch_x_right, -18.539),
    # up to (notch_x_right, -16.65), across to (notch_x_left, -16.65), down to (notch_x_left, -18.539),
    # across to (-10.686, -18.539), up to (-10.686, -15.95)
    
    # We find the insertion point in the loop
    # Let's do it precisely on the polygon coordinates:
    poly = Polygon(raw_mm_pts)
    coords = list(poly.exterior.coords)
    
    # Replace bottom notch segment
    # In coords, find index where y < -16.0
    idx_start = None
    idx_end = None
    for i, (x, y) in enumerate(coords):
        if y < -16.0 and idx_start is None:
            idx_start = i
        if idx_start is not None and y >= -16.0:
            idx_end = i
            break
            
    # New bottom segment:
    # Depending on traversal order (clockwise or ccw):
    p_before = coords[idx_start - 1]
    if p_before[0] > 0: # Right to left traversal
        bottom_seg = [
            (9.812, -18.539),
            (notch_x_right, -18.539),
            (notch_x_right, -16.650),
            (notch_x_left, -16.650),
            (notch_x_left, -18.539),
            (-10.686, -18.539)
        ]
    else:
        bottom_seg = [
            (-10.686, -18.539),
            (notch_x_left, -18.539),
            (notch_x_left, -16.650),
            (notch_x_right, -16.650),
            (notch_x_right, -18.539),
            (9.812, -18.539)
        ]
        
    new_coords = coords[:idx_start] + bottom_seg + coords[idx_end:]
    return Polygon(new_coords)

poly_outer_align = build_aligned_perimeter_poly(-3.70, 3.70)  # Aligned to outer wall of arch (X = ±3.70mm)
poly_inner_align = build_aligned_perimeter_poly(-2.50, 2.50)  # Aligned to inner wall of arch (X = ±2.50mm)
arch_poly = create_arch_wall_poly()

fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=160)

# Option A: Aligned to outer wall of arch (X = ±3.70mm)
axes[0].plot(*poly_outer_align.exterior.xy, 'b-o', markersize=3, label='Exterior Perimeter Wall')
axes[0].plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch (5mm inner)')
axes[0].set_xlim(-12, 12)
axes[0].set_ylim(-20, -8)
axes[0].set_aspect('equal')
axes[0].grid(True)
axes[0].set_title('Option A: Inset Notch Aligns with OUTER Walls of Arch (X = ±3.70mm)', fontsize=11, fontweight='bold')
axes[0].legend(loc='upper right')

# Option B: Aligned to inner wall of arch (X = ±2.50mm)
axes[1].plot(*poly_inner_align.exterior.xy, 'b-o', markersize=3, label='Exterior Perimeter Wall')
axes[1].plot(*arch_poly.exterior.xy, 'r-', linewidth=2, label='Bottom Central Arch (5mm inner)')
axes[1].set_xlim(-12, 12)
axes[1].set_ylim(-20, -8)
axes[1].set_aspect('equal')
axes[1].grid(True)
axes[1].set_title('Option B: Inset Notch Aligns with INNER Walls of Arch (X = ±2.50mm)', fontsize=11, fontweight='bold')
axes[1].legend(loc='upper right')

plt.tight_layout()
plt.savefig('aligned_bottom_notch_options.png', dpi=160)
print("Saved aligned_bottom_notch_options.png")
