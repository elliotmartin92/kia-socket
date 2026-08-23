import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, X0, Y0, SCALE
)
from build_shaft import X_LEFT_TOWER_INNER, X_LEFT_TOWER_OUTER
import numpy as np
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

def get_bracket_mm_pts(raw_pts):
    return [((x - X0) * SCALE, -(y - Y0) * SCALE) for x, y in raw_pts]

b1_orig_pts = get_bracket_mm_pts(bracket_1_raw_pts)
b2_orig_pts = get_bracket_mm_pts(bracket_2_raw_pts)
b3_orig_pts = get_bracket_mm_pts(bracket_3_raw_pts)
b4_orig_pts = get_bracket_mm_pts(bracket_4_raw_pts)

# Let us design the updated bracket points:
# Adjustment parameters:
# 1. General tolerance for Brackets 1, 2, 4:
#    - Hook lower edge raised by +0.25mm in +Y (from 4.582 to 4.832mm)
#    - Pocket top raised by +0.20mm in +Y (from 6.051 to 6.251mm)
#    - Flange tip trimmed by 0.15mm (wider entrance)
# 2. Bracket 3 (Left tower interference resolution):
#    - Top right hook tip pulled back from X = 4.705mm to X = 4.150mm (0.10mm clearance from Left Tower X=4.250mm!)
#    - Hook lower edge at Y = 4.832mm
#    - Hook inner step at X = 3.450mm (was 3.725mm)
#    - Pocket top at Y = 6.251mm

# B1 updated
b1_new_pts = [
    [-10.791,  7.136],
    [ -7.950,  7.136], # slightly trimmed tip (was -7.853)
    [ -7.950,  4.800], # raised lower edge (was 4.582)
    [ -8.900,  4.800], # inner step (was -8.832)
    [ -8.900,  6.250], # raised pocket top (was 6.051)
    [ -9.707,  6.250], # spine pocket top
    [ -9.707, -6.086],
    [ -7.993, -6.086],
    [ -7.993, -7.171],
    [-10.791, -7.171],
    [-10.791,  7.136]
]

# B2 updated
b2_new_pts = [
    [ -1.766,  7.171],
    [ -4.550,  7.171], # slightly trimmed tip (was -4.670)
    [ -4.550,  4.800], # raised lower edge (was 4.582)
    [ -3.600,  4.800], # inner step (was -3.690)
    [ -3.600,  6.250], # raised pocket top (was 6.051)
    [ -2.851,  6.250], # spine pocket top
    [ -2.851, -6.051],
    [ -4.530, -6.051],
    [ -4.530, -7.136],
    [ -1.766, -7.136],
    [ -1.766,  7.171]
]

# B3 updated (Clear of Left Tower at X=4.250mm)
b3_new_pts = [
    [  1.766,  7.171],
    [  4.150,  7.171], # pulled back from 4.705 to 4.150 to clear Left Tower (X=4.250)!
    [  4.150,  4.800], # raised lower edge (was 4.582)
    [  3.400,  4.800], # inner step (was 3.725)
    [  3.400,  6.250], # raised pocket top (was 6.051)
    [  2.851,  6.250], # spine pocket top
    [  2.851, -6.086],
    [  4.565, -6.086],
    [  4.565, -7.171],
    [  1.766, -7.171],
    [  1.766,  7.171]
]

# B4 updated
b4_new_pts = [
    [ 10.791,  7.171],
    [  7.950,  7.171], # slightly trimmed tip (was 7.853)
    [  7.950,  4.800], # raised lower edge (was 4.582)
    [  8.950,  4.800], # inner step (was 8.867)
    [  8.950,  6.250], # raised pocket top (was 6.086)
    [  9.707,  6.250], # spine pocket top
    [  9.707, -6.051],
    [  8.028, -6.051],
    [  8.028, -7.136],
    [ 10.791, -7.136],
    [ 10.791,  7.171]
]

poly_b1 = Polygon(b1_new_pts)
poly_b2 = Polygon(b2_new_pts)
poly_b3 = Polygon(b3_new_pts)
poly_b4 = Polygon(b4_new_pts)

fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=160)

# Panel 1: Left Pair (B1 & B2) Comparison
ax = axes[0]
ax.plot(*Polygon(b1_orig_pts).exterior.xy, 'k--', lw=1.5, label='Original B1')
ax.plot(*Polygon(b2_orig_pts).exterior.xy, 'k:', lw=1.5, label='Original B2')
ax.plot(*poly_b1.exterior.xy, 'g-', lw=2, label='Adjusted B1 (+0.22mm vertical gap)')
ax.plot(*poly_b2.exterior.xy, 'm-', lw=2, label='Adjusted B2 (+0.22mm vertical gap)')
ax.set_xlim(-12, 0)
ax.set_ylim(2, 9)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Left Bracket Pair 1 & 2: Top Gap Tolerance Adjustment', fontsize=11, fontweight='bold')
ax.legend(loc='lower left')

# Panel 2: Right Pair (B3 & B4) & Left Tower Clearance
ax = axes[1]
ax.plot(*Polygon(b3_orig_pts).exterior.xy, 'k--', lw=1.5, label='Original B3 (overlaps Left Tower)')
ax.plot(*Polygon(b4_orig_pts).exterior.xy, 'k:', lw=1.5, label='Original B4')
ax.plot(*poly_b3.exterior.xy, 'b-', lw=2, label='Adjusted B3 (X tip=4.15mm, clears Tower)')
ax.plot(*poly_b4.exterior.xy, 'c-', lw=2, label='Adjusted B4 (+0.22mm vertical gap)')

# Left Tower
tower_l = plt.Rectangle((X_LEFT_TOWER_OUTER, 5.67), X_LEFT_TOWER_INNER - X_LEFT_TOWER_OUTER, 4.0, fill=True, color='#fce4ec', ec='#ad1457', lw=2, alpha=0.7, label='Left Tower (X: 4.25-5.50mm)')
ax.add_patch(tower_l)

ax.annotate('Left Tower Wall\nX = 4.250mm', xy=(4.25, 6.5), xytext=(5.5, 8.0),
            arrowprops=dict(arrowstyle='->', color='#ad1457', lw=1.5), fontsize=9, fontweight='bold', color='#ad1457')
ax.annotate('B3 Tip Pulled Back to X=4.150mm\n(0.10mm Clearance to Tower!)', xy=(4.15, 6.8), xytext=(0.5, 8.5),
            arrowprops=dict(arrowstyle='->', color='blue', lw=1.5), fontsize=9, fontweight='bold', color='blue')

ax.set_xlim(0, 12)
ax.set_ylim(2, 10)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Right Bracket Pair 3 & 4: Zero Tower Interference', fontsize=11, fontweight='bold')
ax.legend(loc='lower right')

plt.tight_layout()
plt.savefig('testing/bracket_gap_adjusted_comparison.png', dpi=160)
print("Saved testing/bracket_gap_adjusted_comparison.png")
