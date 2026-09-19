import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString
import build_part
from build_shaft import X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
p45, norm45, tang45 = build_part.find_boundary_point_and_normal(base_poly, 45.0)

# Check ray from p45 inward (-norm45)
print(f"p45: {p45}")
print(f"Inward direction: {-norm45}")

# Check what features exist inside near 45 deg
# Right tower:
# X: [13.10, 14.60], Y: [6.25, 12.85]
towers_poly = build_part.create_shaft_support_towers_poly()
brackets_poly = build_part.create_all_brackets_poly()

inward_ray = LineString([p45, p45 - norm45 * 5.0])
print(f"Inward ray intersects tower? {inward_ray.intersects(towers_poly)}")
print(f"Distance from inward ray to tower: {inward_ray.distance(towers_poly):.3f} mm")
print(f"Distance from p45 to tower poly: {Point(p45).distance(towers_poly):.3f} mm")

# Check distance from clip arm area to tower poly
center_rad = np.radians(45.0)
r_est = np.linalg.norm(p45)
d_theta = build_part.CLIP_ARM_WIDTH / r_est
clip_angles = np.linspace(center_rad - d_theta/2, center_rad + d_theta/2, 10)
for ca in clip_angles:
    p_wall = np.array([np.cos(ca), np.sin(ca)]) * r_est
    d_tow = Point(p_wall).distance(towers_poly)
    print(f"Angle {np.degrees(ca):.2f}°: pos={p_wall}, dist to tower={d_tow:.3f} mm")
