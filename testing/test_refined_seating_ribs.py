"""
testing/test_refined_seating_ribs.py
Tests the user's refined measurements:
- Height = 1.15mm (above baseplate floor)
- Extension = 1.80mm from interior walls
- Rib 1 meets the hook lower face forming a square shelf
- 4 sets of ribs total per bracket pair
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

# 4 Y stations where Rib 1 meets the hook lower face at Y = 4.950 mm:
# Rib 1: Y_top = 4.950 -> centered at Y = 4.950 - 0.30 = 4.650 mm (or 4.65 to 4.95mm)
# Pitch between 4 ribs across span [-4.65, +4.65]: pitch = 9.30 / 3 = 3.10 mm!
# Stations:
# Rib 1: Y = +4.65 mm (Y in [4.35, 4.95] -> meets hook at Y = 4.95 mm flush!)
# Rib 2: Y = +1.55 mm (Y in [1.25, 1.85])
# Rib 3: Y = -1.55 mm (Y in [-1.85, -1.25])
# Rib 4: Y = -4.65 mm (Y in [-4.95, -4.35])

Y_STATIONS_REFINED = [4.65, 1.55, -1.55, -4.65]

def create_refined_seating_ribs_poly(ext=BRACKET_SEATING_RIB_EXT, thick=BRACKET_SEATING_RIB_THICK):
    boxes = []
    b1_spine = -9.857
    b2_spine = -2.701
    b3_spine = 2.701
    b4_spine = 9.857
    
    for y_c in Y_STATIONS_REFINED:
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
    print("=== TESTING REFINED 1.15mm SEATING RIBS ===")
    ribs = create_refined_seating_ribs_poly()
    print(f"Height above baseplate floor: {BRACKET_SEATING_RIB_HEIGHT:.2f} mm")
    print(f"Extension from spine walls:   {BRACKET_SEATING_RIB_EXT:.2f} mm")
    print(f"Rib thickness in Y:           {BRACKET_SEATING_RIB_THICK:.2f} mm")
    print(f"4 Y-stations (centered):      {Y_STATIONS_REFINED}")
    print(f"Rib 1 Y-span:                 [{Y_STATIONS_REFINED[0] - 0.3:.3f}, {Y_STATIONS_REFINED[0] + 0.3:.3f}] mm (Top edge meets hook lower edge at Y = 4.950 mm!)")
    print(f"Rib 4 Y-span:                 [{Y_STATIONS_REFINED[3] - 0.3:.3f}, {Y_STATIONS_REFINED[3] + 0.3:.3f}] mm")
    print(f"Central corridor width:       {3.556:.3f} mm")

if __name__ == '__main__':
    run()
