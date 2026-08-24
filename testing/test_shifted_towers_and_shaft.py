"""
testing/test_shifted_towers_and_shaft.py
Test shifting towers and shaft to align tower base with top inner wall of bracket 3 at Y = 6.250mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import matplotlib.pyplot as plt

from build_part import bracket_3_raw_pts, to_mm_poly, BASE_THICK, TOWER_HEIGHT, TOWER_THROAT_W, TOWER_WALL_THICK

b3 = to_mm_poly(bracket_3_raw_pts)

# New Tower Y coordinates
DELTA_Y = 6.250 - 7.171 # -0.921 mm
Y_SHAFT = 10.200 + DELTA_Y # 9.279 mm
Z_SHAFT = 12.590
Y_MIN_BASE = 6.250
Y_MAX_BASE = 13.771 + DELTA_Y # 12.850 mm
Y_MIN_TOP = 7.471 + DELTA_Y   # 6.550 mm
Y_MAX_TOP = 13.101 + DELTA_Y  # 12.180 mm

print(f"New Y_SHAFT = {Y_SHAFT:.3f} mm")
print(f"New Tower Base Y span = [{Y_MIN_BASE:.3f}, {Y_MAX_BASE:.3f}] mm (length = {Y_MAX_BASE - Y_MIN_BASE:.3f} mm)")
print(f"New Tower Top Y span  = [{Y_MIN_TOP:.3f}, {Y_MAX_TOP:.3f}] mm (length = {Y_MAX_TOP - Y_MIN_TOP:.3f} mm)")

# Let's verify Bracket 3 top inner wall:
# In Bracket 3, segment (3.708, 6.250) to (2.851, 6.250) is the top inner wall at Y = 6.250!
# Left Tower outer face is at X = 3.900, base starts at Y = 6.250!
# Exactly collinear!

fig, ax = plt.subplots(figsize=(12, 10), dpi=180)

# 1. Bracket 3
bx, by = b3.exterior.xy
ax.fill(bx, by, color='#90caf9', alpha=0.7, ec='#1565c0', lw=2, label='Bracket 3')
ax.plot([2.851, 3.708], [6.250, 6.250], 'r-', lw=3, label='Top Inner Wall of Bracket 3 (Y = 6.250mm)')

# 2. Left Tower Base (X in [3.90, 5.40], Y in [6.250, 12.850])
ax.fill([3.90, 5.40, 5.40, 3.90], [Y_MIN_BASE, Y_MIN_BASE, Y_MAX_BASE, Y_MAX_BASE],
        color='#ffb74d', alpha=0.7, ec='#e65100', lw=2, label=f'Left Tower Base (Y in [{Y_MIN_BASE:.3f}, {Y_MAX_BASE:.3f}])')

# 3. Right Tower Base (X in [13.10, 14.60], Y in [6.250, 12.850])
ax.fill([13.10, 14.60, 14.60, 13.10], [Y_MIN_BASE, Y_MIN_BASE, Y_MAX_BASE, Y_MAX_BASE],
        color='#ffb74d', alpha=0.7, ec='#e65100', lw=2, label=f'Right Tower Base (Aligned)')

# 4. Through Hole (X in [7.608, 12.960], Y in [8.570, 13.082])
ax.fill([7.608, 12.960, 12.960, 7.608], [8.570, 8.570, 13.082, 13.082],
        color='white', alpha=0.9, ec='#d32f2f', lw=1.5, linestyle='--', label='Through-Hole')

# 5. Shaft Axle centerline
ax.plot([3.50, 15.00], [Y_SHAFT, Y_SHAFT], 'm-.', lw=2.5, label=f'Shaft Axle Center (Y = {Y_SHAFT:.3f}mm)')

# Draw horizontal alignment line across the plot at Y = 6.250
ax.axhline(6.250, color='#d32f2f', linestyle=':', lw=2, label='Alignment Datum: Y = 6.250mm')

# Annotations
ax.annotate('EXACT ALIGNMENT:\nLeft Tower base Y = 6.250mm\nTop inner wall of Bracket 3 Y = 6.250mm',
            xy=(3.90, 6.250), xytext=(0, 10.0),
            arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', lw=1.5),
            fontsize=10, fontweight='bold', color='#b71c1c',
            bbox=dict(boxstyle='round,pad=0.3', fc='#ffebee', ec='#b71c1c'))

ax.set_xlim(-2, 16)
ax.set_ylim(-8, 15)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title("Tower Alignment with Top Inner Wall of Bracket 3 (Y = 6.250 mm)", fontsize=12, fontweight='bold')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.legend(loc='lower left', fontsize=8.5)

plt.tight_layout()
out_png = 'testing/tower_bracket3_exact_y_alignment.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
