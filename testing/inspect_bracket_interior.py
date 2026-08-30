"""
testing/inspect_bracket_interior.py
Detailed analysis of interior dimensions and tolerances for brackets 1, 2, 3, 4.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import (
    bracket_1_raw_pts, bracket_2_raw_pts, bracket_3_raw_pts, bracket_4_raw_pts,
    to_mm_poly, X0, Y0, SCALE
)
import shapely.geometry as sg
import numpy as np

def analyze():
    brackets = [
        ('Bracket 1 (Left Outer)', bracket_1_raw_pts),
        ('Bracket 2 (Left Inner)', bracket_2_raw_pts),
        ('Bracket 3 (Right Inner)', bracket_3_raw_pts),
        ('Bracket 4 (Right Outer)', bracket_4_raw_pts),
    ]

    for name, pts in brackets:
        print(f"\n==========================================")
        print(f" {name}")
        print(f"==========================================")
        for i, (x, y) in enumerate(pts):
            print(f"  P{i:02d}: X = {x:7.3f}, Y = {y:7.3f}")

    b1 = to_mm_poly(bracket_1_raw_pts)
    b2 = to_mm_poly(bracket_2_raw_pts)
    b3 = to_mm_poly(bracket_3_raw_pts)
    b4 = to_mm_poly(bracket_4_raw_pts)

    print("\n--- Left Pair (B1 & B2) Gap & Channel ---")
    print(f"B1 inner edge X: {max(p[0] for p in bracket_1_raw_pts):.3f}")
    print(f"B2 outer edge X: {min(p[0] for p in bracket_2_raw_pts):.3f}")
    print(f"Left Pair Channel Width (B1 to B2 gap in X): {min(p[0] for p in bracket_2_raw_pts) - max(p[0] for p in bracket_1_raw_pts):.3f} mm")

    print("\n--- Right Pair (B3 & B4) Gap & Channel ---")
    print(f"B3 outer edge X: {max(p[0] for p in bracket_3_raw_pts):.3f}")
    print(f"B4 inner edge X: {min(p[0] for p in bracket_4_raw_pts):.3f}")
    print(f"Right Pair Channel Width (B3 to B4 gap in X): {min(p[0] for p in bracket_4_raw_pts) - max(p[0] for p in bracket_3_raw_pts):.3f} mm")

    print("\n--- Pocket and Hook Details ---")
    for name, pts in brackets:
        p = pts
        print(f"\n{name}:")
        print(f"  Top Flange Span (P0->P1): X in [{min(p[0][0], p[1][0]):.3f}, {max(p[0][0], p[1][0]):.3f}], Y = {p[0][1]:.3f}")
        print(f"  Hook Lower Edge (P2->P3): Y = {p[2][1]:.3f}, X in [{min(p[2][0], p[3][0]):.3f}, {max(p[2][0], p[3][0]):.3f}] (width = {abs(p[3][0]-p[2][0]):.3f} mm)")
        print(f"  Pocket Top Edge (P4->P5): Y = {p[4][1]:.3f}, X in [{min(p[4][0], p[5][0]):.3f}, {max(p[4][0], p[5][0]):.3f}] (width = {abs(p[5][0]-p[4][0]):.3f} mm)")
        print(f"  Hook Overhang / Pocket Depth (Y_pocket_top - Y_hook_lower): {p[4][1] - p[2][1]:.3f} mm")
        print(f"  Main Spine Wall (P5->P6): X = {p[5][0]:.3f}, Y in [{p[6][1]:.3f}, {p[5][1]:.3f}] (height = {p[5][1]-p[6][1]:.3f} mm)")
        print(f"  Bottom Step (P6->P7): Y = {p[6][1]:.3f}, X in [{min(p[6][0], p[7][0]):.3f}, {max(p[6][0], p[7][0]):.3f}] (width = {abs(p[7][0]-p[6][0]):.3f} mm)")
        print(f"  Bottom Flange (P8->P9): Y = {p[8][1]:.3f}, X in [{min(p[8][0], p[9][0]):.3f}, {max(p[8][0], p[9][0]):.3f}]")

if __name__ == '__main__':
    analyze()
