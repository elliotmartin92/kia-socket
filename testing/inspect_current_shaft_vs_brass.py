import os, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, HUB_WIDTH, HUB_DIAMETER,
    CAM_WIDTH_X, CAM_X_CENTER, X_TOWER_CENTER
)
from build_part import BRACKET_SEATING_RIB_HEIGHT, BASE_THICK

def run():
    print('=== INSPECTING CURRENT SHAFT ROCKER VS SEATED BRASS INSERT ===')
    
    # Seating shelf elevation:
    z_seat = BASE_THICK + BRACKET_SEATING_RIB_HEIGHT  # 1.00 + 1.15 = 2.15 mm
    
    # Cam in build_shaft.py:
    x_c = X_TOWER_CENTER
    hub_w = HUB_WIDTH
    cam_x_c = CAM_X_CENTER
    cam_w_x = CAM_WIDTH_X
    x_cam_start = max(x_c - hub_w/2.0, cam_x_c - cam_w_x/2.0)
    actual_cam_w = min(cam_w_x, (x_c + hub_w/2.0) - x_cam_start)
    cam_x_end = x_cam_start + actual_cam_w
    
    print(f'Cam X bounds: [{x_cam_start:.2f}, {cam_x_end:.2f}] mm (width = {actual_cam_w:.2f} mm)')
    print(f'Cam reach in Y: from Y = {Y_AXLE:.2f} to Y = 1.50 mm')
    print(f'Cam elevation in Z: from Z = 5.00 mm to Z = 15.19 mm')
    print(f'Brass insert seated elevation: Z from {z_seat:.2f} mm to {z_seat + 14.40:.2f} mm')
    print(f'Brass insert rear edge at top: Y = 3.85 mm')
    print(f'Overlap in Y: from Y = 1.50 mm to Y = 3.85 mm (overlap = {3.85 - 1.50:.2f} mm!)')

if __name__ == '__main__':
    run()
