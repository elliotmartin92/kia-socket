import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_shaft

# Test modified web
y_axle = build_shaft.Y_AXLE
z_axle = build_shaft.Z_AXLE
web_y_min = y_axle - 1.50
web_y_max = y_axle + 1.80
web_z_min = z_axle - 3.20
web_z_max = z_axle + 1.00

chamfer = 1.20
pts_web = [
    (web_y_min, web_z_max),
    (web_y_max, web_z_max),
    (web_y_max, web_z_min),
    (web_y_min + chamfer, web_z_min),
    (web_y_min, web_z_min + chamfer)
]
poly_chamfered = Polygon(pts_web)
print("Poly area:", poly_chamfered.area)

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
# Test the chamfered edge in tilted coordinates
p1_tilted = R[:3, :3] @ np.array([0, web_y_min + chamfer, web_z_min])
p2_tilted = R[:3, :3] @ np.array([0, web_y_min, web_z_min + chamfer])
print(f"Edge in tilted coords: p1 = {p1_tilted.round(3).tolist()}, p2 = {p2_tilted.round(3).tolist()}")
print(f"Delta Y' = {p2_tilted[1] - p1_tilted[1]:.4f} (must be 0.0 for vertical wall!)")
