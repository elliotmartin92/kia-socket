import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import build_shaft

# Temporarily mock build_shaft_rocker_mesh with reinforced cam
subparts = build_shaft.build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False, return_subparts=True)

y_axle = build_shaft.Y_AXLE
z_axle = build_shaft.Z_AXLE
r_hub = build_shaft.HUB_DIAMETER / 2.0

poly_pts_cam_reinf = [
    (y_axle, z_axle),                          # Center of hub (9.279, 11.190)
    (y_axle, z_axle + r_hub),                  # (9.279, 13.290) - Flush tangent at hub top
    (8.20, z_axle + r_hub - 0.20),             # (8.20, 13.090) - Tangential crown extending off hub apex
    (6.80, 11.60),                             # (6.80, 11.600) - Heavy-duty reinforced root neck blend
    (5.00, 9.20),                              # Exact operational ramp knee
    (1.50, 7.40),                              # Active contact tip inside belly cavity
    (1.80, 5.10),                              # Rounded nose bottom inside belly
    (4.50, 5.30),                              # Beam underside
    (7.50, 8.40),                              # Deep underside return into belly
    (y_axle, z_axle - r_hub)                   # (9.279, 9.090) - Solid tangential return to bottom of hub
]
flank_collar = Point(y_axle, z_axle).buffer(r_hub)
poly_cam = unary_union([flank_collar, Polygon(poly_pts_cam_reinf)])

x_c = build_shaft.X_TOWER_CENTER
hub_w = build_shaft.HUB_WIDTH
cam_x_c = build_shaft.CAM_X_CENTER
cam_w_x = build_shaft.CAM_WIDTH_X

x_cam_start = max(x_c - hub_w/2.0, cam_x_c - cam_w_x/2.0)
actual_cam_w = min(cam_w_x, (x_c + hub_w/2.0) - x_cam_start)
m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=actual_cam_w)
v_c = m_cam_raw.vertices.copy()
v_cam = np.column_stack([v_c[:, 2] + x_cam_start, v_c[:, 0], v_c[:, 1]])
mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)

subparts['cam'] = mesh_cam

shaft_solid = trimesh.boolean.union(list(subparts.values()), engine='manifold')
print("Is shaft_solid watertight?", shaft_solid.is_watertight)
print("Volume:", shaft_solid.volume)
bodies = shaft_solid.split(only_watertight=False)
print("Bodies count:", len(bodies))
