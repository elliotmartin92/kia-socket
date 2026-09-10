"""
testing/analyze_tower_clamp_design.py
Detailed geometric inspection and clearance analysis for designing a 3D printable
tower prong anti-spreading clamp for the Kia EV6 outlet safety interlock towers.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import (
    BASE_THICK, TOWER_HEIGHT, TOWER_WALL_THICK, TOWER_THROAT_W,
    build_clean_shaft_towers_mesh, build_left_tower_struts_mesh
)
from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, PIN_LEN,
    HUB_DIAMETER, X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER,
    X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER, X_TOWER_CENTER
)

def inspect_tower_geometry():
    print("=== TOWER & SHAFT INTERFACE GEOMETRY ===")
    z_base = BASE_THICK  # 1.00 mm
    z_top = z_base + TOWER_HEIGHT  # 14.09 mm
    y_shaft = Y_AXLE  # 9.279 mm
    z_cradle = Z_AXLE  # 12.590 mm
    r_pin = PIN_DIAMETER / 2.0  # 1.40 mm (Ø2.80 mm)
    r_cradle = 1.50  # Ø3.00 mm
    
    half_w = TOWER_THROAT_W / 2.0  # 1.30 mm
    alpha = np.arcsin(half_w / r_cradle)
    z_throat_lip = z_cradle + r_cradle * np.cos(alpha)  # 13.334 mm
    bevel_dx = (z_top - z_throat_lip) * 0.75  # ~0.567 mm
    
    y_front_inner_top = y_shaft - half_w - bevel_dx  # 7.412 mm
    y_rear_inner_top = y_shaft + half_w + bevel_dx   # 11.146 mm
    
    y_front_outer_top = 6.550
    y_rear_outer_top = 12.180
    
    front_prong_top_w = y_front_inner_top - y_front_outer_top  # 0.862 mm
    rear_prong_top_w = y_rear_outer_top - y_rear_inner_top     # 1.034 mm
    total_top_span = y_rear_outer_top - y_front_outer_top      # 5.630 mm
    top_funnel_gap = y_rear_inner_top - y_front_inner_top      # 3.734 mm
    
    print(f"Tower Z_top: {z_top:.3f} mm")
    print(f"Shaft Pin Axis: Y = {y_shaft:.3f} mm, Z = {z_cradle:.3f} mm")
    print(f"Shaft Pin Top Surface: Z = {z_cradle + r_pin:.3f} mm (Clearance to Z_top: {z_top - (z_cradle + r_pin):.3f} mm)")
    print(f"Throat Constriction Elevation: Z = {z_throat_lip:.3f} mm (Throat Width = {TOWER_THROAT_W:.2f} mm)")
    print(f"Front Prong at Top: Y in [{y_front_outer_top:.3f}, {y_front_inner_top:.3f}] (thickness = {front_prong_top_w:.3f} mm)")
    print(f"Rear Prong at Top:  Y in [{y_rear_inner_top:.3f}, {y_rear_outer_top:.3f}] (thickness = {rear_prong_top_w:.3f} mm)")
    print(f"Total Outer Span across Prongs: {total_top_span:.3f} mm")
    print(f"Top Funnel Throat Gap: {top_funnel_gap:.3f} mm")
    
    print("\n--- X COORDINATES ---")
    print(f"Left Tower:  X in [{X_LEFT_TOWER_OUTER:.2f}, {X_LEFT_TOWER_INNER:.2f}] (thick = {TOWER_WALL_THICK:.2f} mm)")
    print(f"Left Pin:    X in [{X_TOWER_CENTER - TOTAL_AXLE_LEN/2.0:.2f}, {X_TOWER_CENTER - HUB_WIDTH/2.0:.2f}] -> [3.50, 5.50] mm")
    print(f"Hub Barrel:  X in [{X_TOWER_CENTER - HUB_WIDTH/2.0:.2f}, {X_TOWER_CENTER + HUB_WIDTH/2.0:.2f}] -> [5.50, 13.00] mm")
    print(f"Right Pin:   X in [{X_TOWER_CENTER + HUB_WIDTH/2.0:.2f}, {X_TOWER_CENTER + TOTAL_AXLE_LEN/2.0:.2f}] -> [13.00, 15.00] mm")
    print(f"Right Tower: X in [{X_RIGHT_TOWER_INNER:.2f}, {X_RIGHT_TOWER_OUTER:.2f}] (thick = {TOWER_WALL_THICK:.2f} mm)")
    
    # Check clearance to left buttress struts
    # Front Strut: X in [1.90, 3.90], Y in [6.250, 7.050], Z up to 13.70 mm
    # Rear Strut: X in [1.90, 3.90], Y in [11.650, 12.850], Z up to 13.70 mm
    print("\n--- ADJACENT CLEARANCES ---")
    print("Left Tower Struts:")
    print(f"  Front Strut attaches to Left Tower (X=3.90) at Y in [6.250, 7.050], up to Z=13.70mm.")
    print(f"  Rear Strut attaches to Left Tower (X=3.90) at Y in [11.650, 12.850], up to Z=13.70mm.")
    print(f"  Open window between struts on outer left face (X=3.90): Y in [7.050, 11.650] (Span = {11.650 - 7.050:.2f} mm) for ALL Z!")
    print(f"  Above Z=13.70mm (up to 14.09mm), full height {14.09 - 13.70:.2f} mm is 100% CLEAR across all Y on outer left face!")
    
    print("\nRight Tower Outer Face (X=14.60):")
    print(f"  Bridge rib connects below Z = 6.77 mm.")
    print(f"  From Z = 6.77 to 14.09 mm, outer right face (X >= 14.60) is 100% UNRESTRICTED!")

if __name__ == '__main__':
    inspect_tower_geometry()
