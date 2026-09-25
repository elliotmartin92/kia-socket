"""
testing/plot_detailed_bracket_and_moon.py
Plots high-res view of Bracket 3, Bracket 4, Seating Ribs, current Moon, and potential extension zones.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box

import build_part as bp

b3 = bp.to_mm_poly(bp.bracket_3_raw_pts)
b4 = bp.to_mm_poly(bp.bracket_4_raw_pts)
curved = bp.create_center_curved_feature_poly()
ribs = bp.create_bracket_seating_ribs_poly()

fig, ax = plt.subplots(figsize=(10, 12), dpi=200)

# Draw base floor
ax.set_facecolor('#f5f5f5')

# Draw brackets
ax.fill(*b3.exterior.xy, color='#2e7d32', alpha=0.35, label='Bracket 3 (4.6mm tall)')
ax.plot(*b3.exterior.xy, color='#1b5e20', lw=2)

ax.fill(*b4.exterior.xy, color='#2e7d32', alpha=0.35, label='Bracket 4 (4.6mm tall)')
ax.plot(*b4.exterior.xy, color='#1b5e20', lw=2)

# Draw seating ribs
if hasattr(ribs, 'geoms'):
    for g in ribs.geoms:
        ax.fill(*g.exterior.xy, color='#ff9800', alpha=0.5, label='Seating Ribs (1.15mm tall)' if g == ribs.geoms[0] else "")
        ax.plot(*g.exterior.xy, color='#e65100', lw=1.5)
else:
    ax.fill(*ribs.exterior.xy, color='#ff9800', alpha=0.5, label='Seating Ribs')
    ax.plot(*ribs.exterior.xy, color='#e65100', lw=1.5)

# Draw current curved feature
ax.fill(*curved.exterior.xy, color='#9c27b0', alpha=0.6, label='Current Half Moon (10.5mm tall)')
ax.plot(*curved.exterior.xy, color='#4a148c', lw=2)

# Seating Rib 4 lines
ax.axhline(-4.65, color='red', linestyle='--', alpha=0.7, label='Rib 4 Center (Y = -4.65mm)')
ax.axhline(-4.35, color='red', linestyle=':', alpha=0.7, label='Rib 4 Top Edge (Y = -4.35mm)')

# Centerline X = 6.279mm
ax.axvline(6.279, color='blue', linestyle='-.', alpha=0.7, label='Blade/Cam Centerline (X = 6.28mm)')

# Blade representations
# Standard NEMA blade: W = 6.35mm, T = 1.52mm
# Centered at X = 6.28mm
# What if blade is centered at Y = 0.50mm?
y_blade_c = 0.50
blade_box = box(6.279 - 1.52/2, y_blade_c - 6.35/2, 6.279 + 1.52/2, y_blade_c + 6.35/2)
ax.fill(*blade_box.exterior.xy, color='#607d8b', alpha=0.5, label=f'Blade (W=6.35mm, Center Y={y_blade_c:.2f})')
ax.plot(*blade_box.exterior.xy, color='#263238', lw=2)

ax.set_xlim(0, 12)
ax.set_ylim(-8, 8)
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_title('Right Bracket Set (Brackets 3 & 4), Seating Ribs, and Half Moon', fontsize=12, fontweight='bold')
ax.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('testing/detailed_bracket_and_moon.png')
print("Saved testing/detailed_bracket_and_moon.png")
