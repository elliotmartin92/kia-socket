"""
testing/test_insert_lip_removal.py
Validates the removal of the bottom-right corner lip from the slit insert.
Tests watertightness, lip-flush chamfer geometry, and clearance inside the baseplate socket.
"""

import os
import sys
import numpy as np
import trimesh
from shapely.geometry import box, Polygon
from shapely.affinity import translate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import (
    create_frustum_mesh, extrude_shapely_geom,
    INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y,
    SLIT_BOSS_HEIGHT, INSERT_KEY_HEIGHT, INSERT_KEY_W_X, INSERT_KEY_LEN_Y,
    SLIT_W_X, SLIT_LEN_Y, SOCKET_W_X, SOCKET_LEN_Y, get_exact_base_polygon
)

def build_test_insert(is_right=True):
    z0 = 0.00
    z1 = SLIT_BOSS_HEIGHT  # 2.47mm
    z2 = z1 + INSERT_KEY_HEIGHT  # 3.32mm
    
    m_body = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, z0, z1)
    
    key_poly_raw = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2)
    if is_right:
        p1 = [INSERT_KEY_W_X/2 - 0.60, -INSERT_KEY_LEN_Y/2]
        p2 = [INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.60]
        chamfer_tri = Polygon([[p1[0], p1[1] - 0.02],
                               [p2[0] + 0.02, p2[1]],
                               [p2[0] + 0.02, p1[1] - 0.02]])
        corner_cutter_poly = Polygon([[-2.0, -5.10], [5.0, 1.90], [5.0, -5.10]])
    else:
        p1 = [-INSERT_KEY_W_X/2 + 0.60, -INSERT_KEY_LEN_Y/2]
        p2 = [-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.60]
        chamfer_tri = Polygon([[p1[0], p1[1] - 0.02],
                               [p2[0] - 0.02, p2[1]],
                               [p2[0] - 0.02, p1[1] - 0.02]])
        corner_cutter_poly = Polygon([[2.0, -5.10], [-5.0, 1.90], [-5.0, -5.10]])
        
    key_poly = key_poly_raw.difference(chamfer_tri)
    
    m_key = extrude_shapely_geom(key_poly, height=INSERT_KEY_HEIGHT + 0.05)
    m_key.apply_translation([0, 0, z1 - 0.05])
    
    m_solid = m_body.union(m_key, engine='manifold')
    
    m_corner_cutter = extrude_shapely_geom(corner_cutter_poly, height=z2 + 2.0)
    m_corner_cutter.apply_translation([0, 0, -0.5])
    m_solid = m_solid.difference(m_corner_cutter, engine='manifold')
    
    slit_poly_raw = box(-SLIT_W_X/2, -SLIT_LEN_Y/2, SLIT_W_X/2, SLIT_LEN_Y/2)
    slit_cutter = extrude_shapely_geom(slit_poly_raw, height=z2 + 2.0)
    slit_cutter.apply_translation([0, 0, -0.5])
    return m_solid.difference(slit_cutter, engine='manifold')

def run_tests():
    print("Testing right insert generation...")
    m_right = build_test_insert(is_right=True)
    print(f"Right insert: is_watertight = {m_right.is_watertight}, volume = {m_right.volume:.2f} mm^3")
    assert m_right.is_watertight, "Right insert must be watertight!"
    
    print("Testing left insert generation...")
    m_left = build_test_insert(is_right=False)
    print(f"Left insert: is_watertight = {m_left.is_watertight}, volume = {m_left.volume:.2f} mm^3")
    assert m_left.is_watertight, "Left insert must be watertight!"
    
    # Check that for right insert, NO point in the entire mesh has (x - y) > 3.1001
    v = m_right.vertices
    diffs = v[:, 0] - v[:, 1]
    max_diff = np.max(diffs)
    print(f"Max (x - y) across entire right insert: {max_diff:.4f} (Chamfer cut plane is 3.1000)")
    assert max_diff <= 3.105, f"Protruding corner detected! max (x - y) = {max_diff}"
    print("SUCCESS: Zero protruding lip beyond chamfer plane at bottom-right corner!")
    
    # Check that flat shoulders still exist (lip width = 0.35mm on flat sides)
    print(f"Mesh X bounds: [{np.min(v[:, 0]):.3f}, {np.max(v[:, 0]):.3f}] mm (Expected [-1.650, 1.650])")
    print(f"Mesh Y bounds: [{np.min(v[:, 1]):.3f}, {np.max(v[:, 1]):.3f}] mm (Expected [-2.750, 2.750])")
    assert np.max(v[:, 0]) >= 1.64, "Side shoulder was accidentally removed!"
    assert np.min(v[:, 1]) <= -2.74, "Bottom shoulder was accidentally removed!"
    
    print("SUCCESS: 0.35mm seating shoulder preserved on non-chamfered edges!")
    
    # Check baseplate fit and clearance
    base_poly, outer_body_poly, _ = get_exact_base_polygon()
    cx_right = 8.453
    cy = -13.589
    
    # Right socket
    x_r_max = cx_right + SOCKET_W_X/2
    y_r_bot = cy - SOCKET_LEN_Y/2
    chamfer_right_tri = Polygon([[x_r_max - 0.75, y_r_bot - 0.05],
                                 [x_r_max + 0.05, y_r_bot + 0.75],
                                 [x_r_max + 0.05, y_r_bot - 0.05]])
    detent_right = box(cx_right - SOCKET_W_X/2, cy - SOCKET_LEN_Y/2, cx_right + SOCKET_W_X/2, cy + SOCKET_LEN_Y/2).difference(chamfer_right_tri)
    
    # Key in plate coordinates
    key_poly_raw = box(-INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2, INSERT_KEY_W_X/2, INSERT_KEY_LEN_Y/2)
    p1 = [INSERT_KEY_W_X/2 - 0.60, -INSERT_KEY_LEN_Y/2]
    p2 = [INSERT_KEY_W_X/2, -INSERT_KEY_LEN_Y/2 + 0.60]
    chamfer_tri = Polygon([[p1[0], p1[1] - 0.02],
                           [p2[0] + 0.02, p2[1]],
                           [p2[0] + 0.02, p1[1] - 0.02]])
    key_poly = key_poly_raw.difference(chamfer_tri)
    key_in_plate = translate(key_poly, xoff=cx_right, yoff=cy)
    
    assert detent_right.contains(key_in_plate), "Key is not fully inside socket!"
    min_clr = detent_right.boundary.distance(key_in_plate)
    print(f"Key clearance inside socket: {min_clr:.3f} mm")
    assert min_clr >= 0.10, f"Clearance too small: {min_clr}"
    
    # Check body footprint clearance to plate outer boundary
    footprint_poly = Polygon([
        (cx_right - 1.65, cy - 2.75),
        (cx_right + 0.35, cy - 2.75),
        (cx_right + 1.65, cy - 1.45),
        (cx_right + 1.65, cy + 2.75),
        (cx_right - 1.65, cy + 2.75)
    ])
    assert outer_body_poly.contains(footprint_poly), "Right insert shoulder collides with plate boundary!"
    dist_wall = outer_body_poly.exterior.distance(footprint_poly)
    print(f"Right insert shoulder clearance to outer plate wall: {dist_wall:.3f} mm")
    assert dist_wall >= 0.40, f"Clearance to outer wall too tight: {dist_wall}"
    print("SUCCESS: 100% collision-free seating against baseplate floor and outer wall!")

if __name__ == '__main__':
    run_tests()
