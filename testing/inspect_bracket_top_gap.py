import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, X0, Y0, SCALE, get_exact_base_polygon, OUTER_WALL_THICK
)
from build_shaft import (
    X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER,
    X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER,
    Y_AXLE, Z_AXLE
)
import numpy as np
import shapely.geometry as sg
import matplotlib.pyplot as plt

b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=160)

# Panel 1: Overview of All 4 Brackets
ax = axes[0]
ax.plot(*b1.exterior.xy, 'g-', lw=2, label='Bracket 1')
ax.plot(*b2.exterior.xy, 'g--', lw=2, label='Bracket 2')
ax.plot(*b3.exterior.xy, 'b-', lw=2, label='Bracket 3')
ax.plot(*b4.exterior.xy, 'b--', lw=2, label='Bracket 4')

# Left Tower
tower_l = plt.Rectangle((X_LEFT_TOWER_OUTER, 5.67), X_LEFT_TOWER_INNER - X_LEFT_TOWER_OUTER, 4.0, fill=True, color='#fce4ec', ec='#ad1457', lw=1.5, alpha=0.7, label='Left Tower (X: 4.25-5.50, Y: 5.67-9.67)')
ax.add_patch(tower_l)

ax.set_xlim(-13, 13)
ax.set_ylim(-9, 10)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('All 4 Brackets & Tower Alignment', fontsize=12, fontweight='bold')
ax.legend(loc='lower center', fontsize=9)

# Panel 2: Closeup of Bracket 3 & Left Tower Overlap & Top Gap
ax = axes[1]
ax.plot(*b3.exterior.xy, 'b-o', lw=2, markersize=4, label='Bracket 3')
ax.plot(*b4.exterior.xy, 'k-o', lw=2, markersize=4, label='Bracket 4')

tower_l_zoom = plt.Rectangle((X_LEFT_TOWER_OUTER, 5.67), X_LEFT_TOWER_INNER - X_LEFT_TOWER_OUTER, 4.0, fill=True, color='#fce4ec', ec='#ad1457', lw=2, alpha=0.5, label='Left Tower (X: 4.25-5.50)')
ax.add_patch(tower_l_zoom)

# Annotate the overlap and gaps
# Bracket 3 top notch: X in [3.725, 4.705], Y in [4.582, 6.051]
ax.annotate('Top Gap Notch\nX: 3.73-4.71mm\nY: 4.58-6.05mm', xy=(3.725, 5.3), xytext=(0.5, 4.0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=1.5), fontsize=9, fontweight='bold', color='blue')

ax.annotate('Overlap Region\nwith Left Tower\n(X: 4.25-4.71mm)', xy=(4.5, 6.5), xytext=(5.5, 8.5),
            arrowprops=dict(arrowstyle='->', color='#ad1457', lw=1.5), fontsize=9, fontweight='bold', color='#ad1457')

ax.set_xlim(0, 12)
ax.set_ylim(3, 11)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Bracket 3 Top Gap & Left Tower Overlap Detail', fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig('testing/bracket_top_gap_inspection.png', dpi=160)
print("Saved testing/bracket_top_gap_inspection.png")
