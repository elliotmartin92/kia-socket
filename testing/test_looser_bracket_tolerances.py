"""
testing/test_looser_bracket_tolerances.py
Proposes and validates looser interior bracket tolerances.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, BASE_THICK, BRACKET_HEIGHT
)

# Proposed Looser Tolerance Bracket Coordinates:
# 1. Lateral (X) Expansion:
#    - Spine walls widened by 0.15mm per side -> Channel width expands from 6.856mm to 7.156mm (+0.30mm looser).
#    - B1 spine: X = -9.857 mm (was -9.707)
#    - B2 spine: X = -2.701 mm (was -2.851)
#    - B3 spine: X = +2.701 mm (was +2.851)
#    - B4 spine: X = +9.857 mm (was +9.707)
#
# 2. Top Pocket & Hook (X & Y):
#    - Pocket top ceiling raised from Y = 6.250 mm to Y = 6.400 mm (+0.15mm).
#    - Hook lower face raised from Y = 4.800 mm to Y = 4.950 mm (+0.15mm).
#    - Hook pocket step adjusted:
#      B1: X = -8.900 mm (slot width = 0.957mm)
#      B2: X = -3.650 mm (slot width = 0.949mm)
#      B3: X = +3.650 mm (slot width = 0.949mm)
#      B4: X = +8.900 mm (slot width = 0.957mm)
#    - Hook tips trimmed for wider entrance (3.50mm vs 3.15mm):
#      B1: X = -8.000 mm (was -7.853)
#      B2: X = -4.500 mm (was -4.670)
#      B3: X = +4.500 mm (was +4.705)
#      B4: X = +8.000 mm (was +7.853)
#
# 3. Bottom Step & Shelf (X & Y):
#    - Bottom step lowered from Y = -6.086/-6.051 mm to Y = -6.200 mm (+0.11-0.15mm extra vertical span).
#    - Bottom step inner opening widened (3.80mm vs 3.46mm for S-curve leg clearance):
#      B1: X = -8.150 mm (was -7.993)
#      B2: X = -4.350 mm (was -4.530)
#      B3: X = +4.350 mm (was +4.565)
#      B4: X = +8.150 mm (was +8.028)

b1_looser_pts = [
    (-10.791,  7.136), (-8.000,  7.136), (-8.000,  4.950), (-8.900,  4.950),
    (-8.900,  6.400), (-9.857,  6.400), (-9.857, -6.200), (-8.150, -6.200),
    (-8.150, -7.171), (-10.791, -7.171), (-10.791,  7.136)
]

b2_looser_pts = [
    (-1.766,  7.171), (-4.500,  7.171), (-4.500,  4.950), (-3.650,  4.950),
    (-3.650,  6.400), (-2.701,  6.400), (-2.701, -6.200), (-4.350, -6.200),
    (-4.350, -7.136), (-1.766, -7.136), (-1.766,  7.171)
]

b3_looser_pts = [
    (1.766,  7.171), (4.500,  7.171), (4.500,  4.950), (3.650,  4.950),
    (3.650,  6.400), (2.701,  6.400), (2.701, -6.200), (4.350, -6.200),
    (4.350, -7.171), (1.766, -7.171), (1.766,  7.171)
]

b4_looser_pts = [
    (10.791,  7.171), (8.000,  7.171), (8.000,  4.950), (8.900,  4.950),
    (8.900,  6.400), (9.857,  6.400), (9.857, -6.200), (8.150, -6.200),
    (8.150, -7.136), (10.791, -7.136), (10.791,  7.171)
]

def analyze_and_plot():
    p1_orig = Polygon(bracket_1_raw_pts)
    p2_orig = Polygon(bracket_2_raw_pts)
    p3_orig = Polygon(bracket_3_raw_pts)
    p4_orig = Polygon(bracket_4_raw_pts)

    p1_new = Polygon(b1_looser_pts)
    p2_new = Polygon(b2_looser_pts)
    p3_new = Polygon(b3_looser_pts)
    p4_new = Polygon(b4_looser_pts)

    print("=== COMPARISON OF BRACKET TOLERANCES ===")
    print(f"Spine Channel Width (X):")
    print(f"  Left Pair  (B1-B2): {p2_orig.bounds[0] - p1_orig.bounds[2]:.3f} mm -> {-2.701 - (-9.857):.3f} mm (+{-2.701 - (-9.857) - 6.856:.3f} mm, +0.416mm clearance vs 6.74mm brass)")
    print(f"  Right Pair (B3-B4): {p4_orig.bounds[0] - p3_orig.bounds[2]:.3f} mm -> {9.857 - 2.701:.3f} mm (+{9.857 - 2.701 - 6.856:.3f} mm, +0.416mm clearance vs 6.74mm brass)")

    print(f"\nTop Entrance Opening (X):")
    print(f"  Left Pair:  {-4.670 - (-7.853):.3f} mm -> {-4.500 - (-8.000):.3f} mm (+{-4.500 - (-8.000) - (-4.670 - (-7.853)):.3f} mm)")
    print(f"  Right Pair: {7.853 - 4.705:.3f} mm -> {8.000 - 4.500:.3f} mm (+{8.000 - 4.500 - (7.853 - 4.705):.3f} mm)")

    print(f"\nBottom Entrance Opening (X):")
    print(f"  Left Pair:  {-4.530 - (-7.993):.3f} mm -> {-4.350 - (-8.150):.3f} mm (+{-4.350 - (-8.150) - (-4.530 - (-7.993)):.3f} mm)")
    print(f"  Right Pair: {8.028 - 4.565:.3f} mm -> {8.150 - 4.350:.3f} mm (+{8.150 - 4.350 - (8.028 - 4.565):.3f} mm)")

    print(f"\nInternal Vertical Span (Y):")
    print(f"  6.250 - (-6.086) = 12.336 mm -> 6.400 - (-6.200) = 12.600 mm (+0.264 mm roomier)")

    # Plot Comparison
    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)

    for idx, (ax, title, orig_pair, new_pair, xlim) in enumerate([
        (axes[0], "Left Bracket Pair (Brackets 1 & 2)", (p1_orig, p2_orig), (p1_new, p2_new), (-12, 0)),
        (axes[1], "Right Bracket Pair (Brackets 3 & 4)", (p3_orig, p4_orig), (p3_new, p4_new), (0, 12))
    ]):
        # Original dashed gray
        ax.plot(*orig_pair[0].exterior.xy, 'k--', lw=1.5, alpha=0.5, label='Previous Geometry')
        ax.plot(*orig_pair[1].exterior.xy, 'k--', lw=1.5, alpha=0.5)

        # New solid
        ax.plot(*new_pair[0].exterior.xy, '#2980b9', lw=2.2, label='Looser Tolerance Outer Wall')
        ax.plot(*new_pair[1].exterior.xy, '#27ae60', lw=2.2, label='Looser Tolerance Inner Wall')

        ax.fill(*new_pair[0].exterior.xy, color='#2980b9', alpha=0.15)
        ax.fill(*new_pair[1].exterior.xy, color='#27ae60', alpha=0.15)

        ax.set_xlim(xlim)
        ax.set_ylim(-8.5, 8.5)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.legend(loc='lower left' if idx == 0 else 'lower right', fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'bracket_looser_tolerance_comparison.png')
    plt.savefig(out_path, dpi=180)
    print(f"\nSaved comparison plot to: {out_path}")

if __name__ == '__main__':
    analyze_and_plot()
