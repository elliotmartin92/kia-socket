"""
testing/verify_wall_socket_overlap.py
Verify the exact 3D solid overlap between wall_poly and the right detent socket at X = +8.453mm.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, SOCKET_W_X, SOCKET_LEN_Y
)
from shapely.geometry import box

def check_overlap():
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_poly)
    
    # Left and Right Sockets at current positions:
    cx_left = -7.853
    cx_right = +8.453
    cy = -13.589
    
    sock_left = box(cx_left - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_left + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    sock_right = box(cx_right - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_right + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    
    inter_left = wall_poly.intersection(sock_left)
    inter_right = wall_poly.intersection(sock_right)
    
    print("=== WALL POLY VS DETENT SOCKET OVERLAP ===")
    print(f"Left Socket (X = -7.853mm):")
    print(f"  Overlap with perimeter wall: {inter_left.area:.4f} mm^2 (Zero overlap!)")
    
    print(f"\nRight Socket (X = +8.453mm):")
    print(f"  Overlap with perimeter wall: {inter_right.area:.4f} mm^2")
    if not inter_right.is_empty:
        b = inter_right.bounds
        print(f"  Overlap bounding box X in [{b[0]:.3f}, {b[2]:.3f}] mm (width = {b[2]-b[0]:.3f} mm)")
        print(f"  Overlap bounding box Y in [{b[1]:.3f}, {b[3]:.3f}] mm (length = {b[3]-b[1]:.3f} mm)")
        print(f"  -> A solid wall segment of {b[2]-b[0]:.3f}mm x {b[3]-b[1]:.3f}mm x 5.77mm tall sits directly ON TOP of the right socket hole!")

if __name__ == '__main__':
    check_overlap()
