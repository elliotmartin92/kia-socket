"""
Visualize candidate geometry and positions for the new extruded feature between Brackets 3 & 4.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import (
    SCALE, X0, Y0, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

# Coordinates
# Bracket 3 right edge: 4.705 mm, Bracket 4 left edge: 7.853 mm
# Center X = 6.279 mm
# Width in X = 4.30 mm -> X in [4.129, 8.429] mm
cx = 6.279
w_x = 4.30
h_y = 1.62

x_min = cx - w_x / 2.0  # 4.129 mm
x_max = cx + w_x / 2.0  # 8.429 mm

y_bot_inner = -17.339
datum_y = y_bot_inner + 11.27  # -6.069 mm

fig, axes = plt.subplots(1, 2, figsize=(16, 8), dpi=160)

for idx, (ax, direction_label, y_range) in enumerate([
    (axes[0], "Extending in +Y from Datum (Y: -6.07 to -4.45 mm)", (datum_y, datum_y + h_y)),
    (axes[1], "Centered on Datum / Extending in -Y (Y: -7.69 to -6.07 mm)", (datum_y - h_y, datum_y))
]):
    # Plot Brackets 3 & 4
    b3x, b3y = b3.exterior.xy
    b4x, b4y = b4.exterior.xy
    ax.plot(b3x, b3y, 'g-', linewidth=2, label='Bracket 3 (4.60mm)')
    ax.plot(b4x, b4y, 'g-', linewidth=2, label='Bracket 4 (4.60mm)')
    
    # Outer box of new feature
    feat_outer = box(x_min, y_range[0], x_max, y_range[1])
    fx, fy = feat_outer.exterior.xy
    ax.plot(fx, fy, 'm-', linewidth=2.5, label='New Feature Outer Box (4.3x1.62mm)')
    
    # Hollow box with 0.6mm wall + central internal rib (0.6mm thick)
    wall_t = 0.50
    feat_inner_left = box(x_min + wall_t, y_range[0] + wall_t, cx - wall_t/2, y_range[1] - wall_t)
    feat_inner_right = box(cx + wall_t/2, y_range[0] + wall_t, x_max - wall_t, y_range[1] - wall_t)
    feat_frame = feat_outer.difference(unary_union([feat_inner_left, feat_inner_right]))
    
    for geom in (feat_frame.geoms if hasattr(feat_frame, 'geoms') else [feat_frame]):
        gx, gy = geom.exterior.xy
        ax.fill(gx, gy, color='#ab47bc', alpha=0.35)
        for interior in geom.interiors:
            ix, iy = interior.xy
            ax.plot(ix, iy, 'm--', linewidth=1.2)
            
    # Datum line
    ax.axhline(datum_y, color='red', linestyle='-.', linewidth=1.5, label=f'Datum: 11.27mm from bottom (Y = {datum_y:.2f}mm)')
    
    ax.set_xlim(1, 12)
    ax.set_ylim(-9, -3)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title(f'Option {chr(65+idx)}: {direction_label}', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
plt.savefig('new_feature_candidates.png', dpi=160)
print("Saved new_feature_candidates.png")
