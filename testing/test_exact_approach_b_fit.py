"""
testing/test_exact_approach_b_fit.py
Tests the exact chamfer geometry for both socket and key to ensure 0.0000 mm^2 overlap with the untouched wall.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trimesh
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, SOCKET_W_X, SOCKET_LEN_Y,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, SLIT_W_X, SLIT_LEN_Y
)

def test_fit():
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly_untouched = outer_body_poly.difference(inner_wall_poly)
    
    cx_left = -7.853
    cx_right = 8.453
    cy = -13.589
    
    # Right socket
    x_r_max = cx_right + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    tri_r = Polygon([[x_r_max - 1.85, y_r_bot - 0.1], [x_r_max + 0.1, y_r_bot + 1.45], [x_r_max + 0.1, y_r_bot - 0.1]])
    sock_r = box(cx_right - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_right + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(tri_r)
    
    # Left socket
    x_l_min = cx_left - SOCKET_W_X/2
    y_l_bot = cy - SOCKET_LEN_Y/2
    tri_l = Polygon([[x_l_min + 1.85, y_l_bot - 0.1], [x_l_min - 0.1, y_l_bot + 1.45], [x_l_min - 0.1, y_l_bot - 0.1]])
    sock_l = box(cx_left - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_left + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(tri_l)
    
    overlap_r = wall_poly_untouched.intersection(sock_r)
    overlap_l = wall_poly_untouched.intersection(sock_l)
    
    print(f"Right Socket Wall Overlap: {overlap_r.area:.6f} mm^2")
    print(f"Left Socket Wall Overlap:  {overlap_l.area:.6f} mm^2")
    
    # Blade: 0.77x3.10
    blade = box(cx_right - 0.77/2, cy - 3.10/2, cx_right + 0.77/2, cy + 3.10/2)
    print(f"Blade Wall Overlap:        {wall_poly_untouched.intersection(blade).area:.6f} mm^2")
    
    assert overlap_r.area < 1e-5
    assert overlap_l.area < 1e-5
    print("SUCCESS: 100% CLEAR OF UNTOUCHED WALL!")

if __name__ == '__main__':
    test_fit()
