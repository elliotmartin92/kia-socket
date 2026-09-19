import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

y_vals = np.linspace(5.0, 14.0, 19)
for y in y_vals:
    line = LineString([(0, y), (25, y)])
    inter = outer_body_poly.exterior.intersection(line)
    if inter.geom_type == 'Point':
        x_max = inter.x
    elif hasattr(inter, 'geoms') and len(inter.geoms) > 0:
        x_max = max(g.x for g in inter.geoms)
    else:
        x_max = None
    print(f"Y = {y:5.2f} mm -> Outer X max = {x_max:.3f} mm")
