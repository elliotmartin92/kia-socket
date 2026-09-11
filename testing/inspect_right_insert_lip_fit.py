import os, sys
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK,
    INSERT_KEY_W_X, INSERT_KEY_LEN_Y, INSERT_KEY_HEIGHT,
    SOCKET_W_X, SOCKET_LEN_Y, INSERT_CLEARANCE,
    INSERT_BODY_W_X, INSERT_BODY_LEN_Y, INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP,
    SLIT_W_X, SLIT_LEN_Y
)

def inspect_fit():
    print("=== INSPECTING RIGHT INSERT LIP FIT ===")
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    inner_wall = outer_body_poly.buffer(-OUTER_WALL_THICK)
    wall_poly = outer_body_poly.difference(inner_wall)
    
    cx = 8.453
    cy = -13.589
    
    print(f"Right Detent Center: ({cx}, {cy})")
    print(f"INSERT_KEY: {INSERT_KEY_W_X} x {INSERT_KEY_LEN_Y}")
    print(f"SOCKET: {SOCKET_W_X} x {SOCKET_LEN_Y}")
    print(f"INSERT_BODY: base={INSERT_BODY_W_X} x {INSERT_BODY_LEN_Y}, tip={INSERT_BODY_W_TIP} x {INSERT_BODY_LEN_TIP}")
    
    # 1. Baseplate socket in the floor
    x_r_max = cx + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    chamfer_right_tri = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                                 [x_r_max + 0.05, y_r_bot + 0.75],
                                 [x_r_max + 0.05, y_r_bot - 0.05]])
    detent_right = box(cx - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_right_tri)
    
    print(f"\nSocket bounds: {detent_right.bounds}")
    print(f"Does socket intersect wall_poly? {detent_right.intersects(wall_poly)}")
    if detent_right.intersects(wall_poly):
        overlap = detent_right.intersection(wall_poly)
        print(f"Socket overlap with wall_poly area: {overlap.area:.4f} mm^2")
        print(f"Socket overlap with wall_poly bounds: {overlap.bounds}")
        
    # 2. Key geometry (relative to cx, cy)
    key_poly_raw = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2)
    p1 = [INSERT_KEY_W_X/2 - 0.60, -INSERT_KEY_LEN_Y/2]
    p2 = [INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.60]
    chamfer_tri = Polygon([[p1[0], p1[1] - 0.02],
                           [p2[0] + 0.02, p2[1]],
                           [p2[0] + 0.02, p1[1] - 0.02]])
    key_poly = key_poly_raw.difference(chamfer_tri)
    key_in_plate = translate(key_poly, xoff=cx, yoff=cy)
    
    print(f"\nKey bounds in plate coords: {key_in_plate.bounds}")
    print(f"Does detent_right contain key_in_plate? {detent_right.contains(key_in_plate)}")
    print(f"Does key_in_plate intersect wall_poly? {key_in_plate.intersects(wall_poly)}")
    if key_in_plate.intersects(wall_poly):
        k_overlap = key_in_plate.intersection(wall_poly)
        print(f"Key overlap with wall_poly area: {k_overlap.area:.4f} mm^2")
        print(f"Key overlap with wall_poly bounds: {k_overlap.bounds}")
        
    print(f"Does key_in_plate intersect or exceed outer_body_poly? {not outer_body_poly.contains(key_in_plate)}")
    if not outer_body_poly.contains(key_in_plate):
        outside = key_in_plate.difference(outer_body_poly)
        print(f"Key sticking outside outer perimeter area: {outside.area:.4f} mm^2")
        
    # 3. Body geometry (relative to cx, cy)
    body_raw = box(-INSERT_BODY_W_X/2, -INSERT_BODY_LEN_Y/2, INSERT_BODY_W_X/2, INSERT_BODY_LEN_Y/2)
    body_in_plate = translate(body_raw, xoff=cx, yoff=cy)
    print(f"\nBody bounds in plate coords: {body_in_plate.bounds}")
    print(f"Does body_in_plate intersect or exceed outer_body_poly? {not outer_body_poly.contains(body_in_plate)}")
    if not outer_body_poly.contains(body_in_plate):
        b_outside = body_in_plate.difference(outer_body_poly)
        print(f"Body sticking outside outer perimeter area: {b_outside.area:.4f} mm^2")
        print(f"Body sticking outside bounds: {b_outside.bounds}")
    else:
        print(f"Clearance from body_in_plate to outer_body_poly edge: {outer_body_poly.exterior.distance(body_in_plate):.4f} mm")

if __name__ == '__main__':
    inspect_fit()
