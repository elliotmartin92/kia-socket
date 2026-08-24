"""
testing/inspect_buttress_alignment.py
Visualize and analyze the front buttress starting at Y = 6.250mm (top inner wall of Bracket 3)
and sloping into the Left Tower at Y = 7.171mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from build_part import bracket_3_raw_pts, to_mm_poly

b3 = to_mm_poly(bracket_3_raw_pts)

# Shaft Axis
Y_SHAFT = 10.200
Z_SHAFT = 12.590

# Tower Main Columns (Left: X in [3.90, 5.40], Right: X in [13.10, 14.60])
# Base Y in [7.171, 13.771]
# Top Y in [7.471, 13.101]

# Left Tower Front Buttress Strut:
# Extends from X in [1.90, 3.90]
# Bottom of buttress in Y = 6.250 mm (EXACTLY ALIGNED with top inner wall of Bracket 3!)
# Top/back of buttress in Y = 7.171 mm (meets front face of Left Tower)
# Height: Z in [1.00, 13.70] (or sloping from Bracket 3 top Z=4.60 to tower Z=13.70)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5), dpi=180)

# Panel 1: Top-Down 2D Map (X-Y Plane)
bx, by = b3.exterior.xy
ax1.fill(bx, by, color='#90caf9', alpha=0.7, ec='#1565c0', lw=2, label='Bracket 3 Body')
ax1.plot([2.851, 3.708], [6.250, 6.250], 'r-', lw=3, label='Top Inner Wall of Bracket 3 (Y = 6.250mm)')
ax1.plot([1.766, 4.705], [7.171, 7.171], 'b--', lw=1.5, label='Top Outer Wall of Bracket 3 (Y = 7.171mm)')

# Front Buttress Footprint: X in [1.90, 3.90], Y in [6.250, 7.171]
ax1.fill([1.90, 3.90, 3.90, 1.90], [6.250, 6.250, 7.171, 7.171],
         color='#ab47bc', alpha=0.85, ec='#6a1b9a', lw=2, label='Front Buttress Base (Y: 6.250 to 7.171mm)')

# Left Tower Column Base: X in [3.90, 5.40], Y in [7.171, 13.771]
ax1.fill([3.90, 5.40, 5.40, 3.90], [7.171, 7.171, 13.771, 13.771],
         color='#ffb74d', alpha=0.7, ec='#e65100', lw=2, label='Left Tower Column (Y: 7.171 to 13.771mm)')

# Right Tower Column Base: X in [13.10, 14.60], Y in [7.171, 13.771]
ax1.fill([13.10, 14.60, 14.60, 13.10], [7.171, 7.171, 13.771, 13.771],
         color='#ffb74d', alpha=0.7, ec='#e65100', lw=2, label='Right Tower Column')

# Shaft Centerline (Y = 10.200mm)
ax1.plot([3.50, 15.00], [10.200, 10.200], 'm-.', lw=2.5, label='Shaft Pivot Axis (Y = 10.200mm)')

# Through-hole (X in [7.608, 12.960], Y in [8.570, 13.082])
ax1.fill([7.608, 12.960, 12.960, 7.608], [8.570, 8.570, 13.082, 13.082],
         color='white', alpha=0.9, ec='#d32f2f', lw=1.5, linestyle='--', label='Through-Hole')

ax1.axhline(6.250, color='#d32f2f', linestyle=':', lw=2, label='Alignment Datum: Y = 6.250mm')

ax1.annotate('ALIGNMENT:\nBottom of Buttress = Y = 6.250mm\nTop inner wall of Bracket 3 = Y = 6.250mm',
            xy=(2.851, 6.250), xytext=(-0.5, 9.5),
            arrowprops=dict(facecolor='#d32f2f', edgecolor='#b71c1c', lw=1.5),
            fontsize=9.5, fontweight='bold', color='#b71c1c',
            bbox=dict(boxstyle='round,pad=0.3', fc='#ffebee', ec='#b71c1c'))

ax1.set_xlim(-1, 16)
ax1.set_ylim(-8, 15)
ax1.set_aspect('equal')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_title("1. Top-Down Map: Buttress Aligned to Inner Bracket Wall", fontsize=11, fontweight='bold')
ax1.set_xlabel('X (mm)')
ax1.set_ylabel('Y (mm)')
ax1.legend(loc='lower left', fontsize=7.5)

# Panel 2: 3D Side Elevation / Sloping Buttress
ax2.plot([6.250, 7.171, 7.171, 6.250], [1.0, 1.0, 13.70, 1.0], color='#ab47bc', lw=2.5, label='Front Buttress Triangular Profile in Y-Z')
ax2.fill([6.250, 7.171, 7.171, 6.250], [1.0, 1.0, 13.70, 1.0], color='#ab47bc', alpha=0.4)

# Tower profile in Y-Z
ax2.plot([7.171, 13.771, 13.101, 7.471, 7.171], [1.0, 1.0, 14.09, 14.09, 1.0], color='#e65100', lw=2.5, label='Tower Column Profile in Y-Z')
ax2.fill([7.171, 13.771, 13.101, 7.471, 7.171], [1.0, 1.0, 14.09, 14.09, 1.0], color='#ffb74d', alpha=0.4)

# Shaft circle at (10.200, 12.590)
phi = np.linspace(0, 2*np.pi, 64)
ax2.plot(10.200 + 1.5*np.cos(phi), 12.590 + 1.5*np.sin(phi), 'b-', lw=1.5, label='Shaft Cradle (Ø3.0mm)')
ax2.plot(10.200, 12.590, 'ro', markersize=6, label='Pivot Axis (Y=10.20, Z=12.59)')

# Bracket 3 top level (Z = 4.60mm, Y <= 7.171)
ax2.fill([2.0, 7.171, 7.171, 2.0], [1.0, 1.0, 4.60, 4.60], color='#90caf9', alpha=0.5, label='Bracket 3 (Z=4.60mm)')
ax2.plot([6.250, 6.250], [0, 15], 'r:', lw=2, label='Inner Wall Datum: Y = 6.250mm')

ax2.set_xlim(2, 15)
ax2.set_ylim(0, 16)
ax2.set_aspect('equal')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_title("2. Side Profile (Y-Z): Sloping Buttress from Y = 6.250mm to Tower", fontsize=11, fontweight='bold')
ax2.set_xlabel('Y (mm)')
ax2.set_ylabel('Z (mm)')
ax2.legend(loc='lower left', fontsize=7.5)

plt.tight_layout()
out_png = 'testing/buttress_exact_alignment_preview.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
