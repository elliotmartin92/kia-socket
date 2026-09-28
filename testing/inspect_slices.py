import trimesh
import numpy as np
import shapely.geometry
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model

part_flat, base_poly = build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_flat.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

for x in [-19.0, -18.0, -15.0, 0.0, 15.0, 18.0, 19.0]:
    line = shapely.geometry.LineString([(x, -50.0), (x, 50.0)])
    inter = base_poly.intersection(line)
    if not inter.is_empty:
        c45 = np.cos(np.radians(45))
        y_min_t = inter.bounds[1] * c45
        y_max_t = inter.bounds[3] * c45
        z_min_t = y_min_t - z_min
        z_max_t = y_max_t - z_min
        print(f"X = {x:5.1f} | Y_tilt: [{y_min_t:6.2f}, {y_max_t:6.2f}] | Z_underside: [{z_min_t:5.2f}, {z_max_t:5.2f}]")
