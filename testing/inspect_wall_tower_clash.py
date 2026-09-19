import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString
import build_part

base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(inner_wall_poly)
towers_poly = build_part.create_shaft_support_towers_poly()

print(f"Inner wall intersects tower? {inner_wall_poly.intersects(towers_poly)}")
print(f"Wall 2D intersects tower? {wall_2d.intersects(towers_poly)}")
inter = wall_2d.intersection(towers_poly)
if not inter.is_empty:
    print(f"Intersection area: {inter.area:.4f} mm^2, bounds: {inter.bounds}")
    print(f"Intersection geom type: {inter.geom_type}")
