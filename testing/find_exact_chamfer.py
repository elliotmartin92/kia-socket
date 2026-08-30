"""
testing/find_exact_chamfer.py
Finds the exact chamfer triangle for the right socket that achieves 0.0000 mm^2 overlap with the untouched wall.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import get_exact_base_polygon, OUTER_WALL_THICK, SOCKET_W_X, SOCKET_LEN_Y
from shapely.geometry import Polygon, box

def find_chamfer():
    _, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_wall_poly)
    
    cx = 8.453
    cy = -13.589
    
    sock_raw = box(cx - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2)
    
    for h_cut in np.linspace(1.0, 2.5, 31):
        for w_cut in np.linspace(0.8, 2.0, 25):
            # Chamfer from (cx + SOCKET_W_X/2 - w_cut, cy - SOCKET_LEN_Y/2) to (cx + SOCKET_W_X/2, cy - SOCKET_LEN_Y/2 + h_cut)
            tri = Polygon([
                [cx + SOCKET_W_X/2 - w_cut, cy - SOCKET_LEN_Y/2 - 0.1],
                [cx + SOCKET_W_X/2 + 0.1, cy - SOCKET_LEN_Y/2 + h_cut],
                [cx + SOCKET_W_X/2 + 0.1, cy - SOCKET_LEN_Y/2 - 0.1]
            ])
            sock_cut = sock_raw.difference(tri)
            overlap = wall_poly.intersection(sock_cut)
            if overlap.area < 1e-6:
                print(f"SUCCESS: w_cut = {w_cut:.2f}mm, h_cut = {h_cut:.2f}mm -> overlap = {overlap.area:.6f} mm^2")
                break
        if overlap.area < 1e-6:
            break

if __name__ == '__main__':
    import numpy as np
    find_chamfer()
