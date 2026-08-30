"""
testing/test_corner_aligned_ribs.py
Tests the seating ribs where Rib 1's bottom corner meets the corner/tip of the hook at Y = 4.950mm.
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
    to_mm_poly, get_exact_base_polygon, OUTER_WALL_THICK, BASE_THICK, BRACKET_HEIGHT
)

# 1. Looser Bracket Coordinates
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

BRACKET_SEATING_RIB_HEIGHT = 1.15   # 1.15mm protrusion above floor (Z: 1.00 to 2.15mm)
BRACKET_SEATING_RIB_EXT = 1.80      # 1.80mm extension from interior spine walls
BRACKET_SEATING_RIB_THICK = 0.60    # 0.60mm thick in Y

# Rib 1 bottom edge at Y = 4.950 mm -> Y span [4.950, 5.550] mm, center Y = 5.250 mm
# 4 stations with 3.30mm pitch: [5.25, 1.95, -1.35, -4.65] mm
Y_STATIONS = [5.25, 1.95, -1.35, -4.65]

def create_seating_ribs_poly(ext=BRACKET_SEATING_RIB_EXT, thick=BRACKET_SEATING_RIB_THICK):
    boxes = []
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    
    for y_c in Y_STATIONS:
        y_min = y_c - thick / 2.0
        y_max = y_c + thick / 2.0
        
        # Left Pair
        boxes.append(box(b1_spine, y_min, b1_spine + ext, y_max))
        boxes.append(box(b2_spine - ext, y_min, b2_spine, y_max))
        
        # Right Pair
        boxes.append(box(b3_spine, y_min, b3_spine + ext, y_max))
        boxes.append(box(b4_spine - ext, y_min, b4_spine, y_max))
        
    return unary_union(boxes)

def run():
    print("=== TESTING CORNER-ALIGNED 1.15mm SEATING RIBS ===")
    ribs = create_seating_ribs_poly()
    print(f"Height: {BRACKET_SEATING_RIB_HEIGHT:.2f} mm")
    print(f"Extension: {BRACKET_SEATING_RIB_EXT:.2f} mm")
    print(f"Thickness: {BRACKET_SEATING_RIB_THICK:.2f} mm")
    print(f"Stations (centers): {Y_STATIONS}")
    print(f"Rib 1 Y-span: [{Y_STATIONS[0] - 0.3:.3f}, {Y_STATIONS[0] + 0.3:.3f}] mm -> Bottom edge = 4.950 mm (meets hook tip corner at Y=4.950mm!)")
    print(f"Rib 2 Y-span: [{Y_STATIONS[1] - 0.3:.3f}, {Y_STATIONS[1] + 0.3:.3f}] mm")
    print(f"Rib 3 Y-span: [{Y_STATIONS[2] - 0.3:.3f}, {Y_STATIONS[2] + 0.3:.3f}] mm")
    print(f"Rib 4 Y-span: [{Y_STATIONS[3] - 0.3:.3f}, {Y_STATIONS[3] + 0.3:.3f}] mm")

if __name__ == '__main__':
    run()
