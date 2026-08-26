"""
testing/find_closest_contact_points.py
Finds the exact (Y, Z) coordinates of the closest point between the cam and the rear arm.
"""

import os
import sys
import numpy as np
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import nearest_points

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import Y_AXLE, Z_AXLE
from testing.model_exact_brass_part import get_brass_contact_2d_profile, SHEET_THICK
from testing.optimize_gooseneck_clearance import get_optimized_gooseneck

def run():
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    cam_poly = get_optimized_gooseneck()
    
    t_half = SHEET_THICK / 2.0
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    rear_poly = Polygon(r_poly_pts)
    
    print("Closest points at each angle:")
    for ang in [0, 2, 4, 6, 8, 10]:
        rad = np.radians(ang)
        c_a, s_a = np.cos(rad), np.sin(rad)
        vecs = cam_poly - np.array([Y_AXLE, Z_AXLE])
        p_rot = np.zeros_like(cam_poly)
        p_rot[:, 0] = Y_AXLE + c_a * vecs[:, 0] - s_a * vecs[:, 1]
        p_rot[:, 1] = Z_AXLE + s_a * vecs[:, 0] + c_a * vecs[:, 1]
        
        pg = Polygon(p_rot)
        p_cam, p_rear = nearest_points(pg, rear_poly)
        dist = pg.distance(rear_poly)
        print(f"  theta = {ang:2d} deg: Dist = {dist:.3f} mm | Cam Pt = ({p_cam.x:.2f}, {p_cam.y:.2f}) | Rear Pt = ({p_rear.x:.2f}, {p_rear.y:.2f})")

if __name__ == '__main__':
    run()
