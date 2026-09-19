import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
towers_poly = build_part.create_shaft_support_towers_poly()
brackets_poly = build_part.create_all_brackets_poly()

all_internal = towers_poly.union(brackets_poly)

for angle_deg in build_part.CLIP_ANGLES:
    center_rad = np.radians(angle_deg)
    p, n, t = build_part.find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = build_part.CLIP_ARM_WIDTH / r_est
    thetas = np.linspace(center_rad - d_theta/2, center_rad + d_theta/2, 10)
    
    min_dist_to_internal = 999.0
    for th in thetas:
        ray = LineString([(0, 0), np.array([np.cos(th), np.sin(th)]) * 50])
        p_in = inner_wall_poly.exterior.intersection(ray)
        if hasattr(p_in, 'geoms'): p_in = p_in.geoms[-1]
        pt = Point(p_in.x, p_in.y)
        d = pt.distance(all_internal)
        if all_internal.contains(pt):
            d = -all_internal.exterior.distance(pt) if hasattr(all_internal, 'exterior') else -0.1
        min_dist_to_internal = min(min_dist_to_internal, d)
        
    print(f"Clip at {angle_deg:5.1f}°: min distance from inner wall to internal features = {min_dist_to_internal:.3f} mm")
