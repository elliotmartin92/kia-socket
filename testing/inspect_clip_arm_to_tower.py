import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString, Polygon
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
towers_poly = build_part.create_shaft_support_towers_poly()

# 45 deg clip span
center_rad = np.radians(45.0)
p45, n45, t45 = build_part.find_boundary_point_and_normal(base_poly, 45.0)
r_est = np.linalg.norm(p45)
d_theta = build_part.CLIP_ARM_WIDTH / r_est

# Ray from inner wall of clip inward
thetas = np.linspace(center_rad - d_theta/2, center_rad + d_theta/2, 20)
print(f"45 degree clip angle range: [{np.degrees(thetas[0]):.2f}, {np.degrees(thetas[-1]):.2f}]")

for th in thetas:
    ray_dir = np.array([np.cos(th), np.sin(th)])
    ray = LineString([(0, 0), ray_dir * 50])
    p_outer = outer_body_poly.exterior.intersection(ray)
    p_inner = inner_wall_poly.exterior.intersection(ray)
    if hasattr(p_outer, 'geoms'): p_outer = p_outer.geoms[-1]
    if hasattr(p_inner, 'geoms'): p_inner = p_inner.geoms[-1]
    
    pt_inner = Point(p_inner.x, p_inner.y)
    dist_to_tower = pt_inner.distance(towers_poly)
    # Check if pt_inner is inside towers_poly
    inside_tower = towers_poly.contains(pt_inner)
    print(f"th={np.degrees(th):.1f}°: p_inner=({p_inner.x:.2f}, {p_inner.y:.2f}), dist_to_tower={dist_to_tower:.3f}, inside={inside_tower}")
