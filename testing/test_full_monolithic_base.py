import trimesh
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Test building full part with monolithic in-place slit shrouds:
base_poly_raw, outer_body_poly, hole_info = bp.get_exact_base_polygon()

# Instead of detent sockets, cut only the 1.20 x 3.40mm slit holes:
cx_left = -7.853
cx_right = 8.453
cy = -13.589
w_slit = bp.SLIT_W_X     # 1.20 mm
len_slit = bp.SLIT_LEN_Y # 3.40 mm

hole_box = box(hole_info[0] - hole_info[2]/2, hole_info[1] - hole_info[3]/2,
               hole_info[0] + hole_info[2]/2, hole_info[1] + hole_info[3]/2)
slit_hole_l = box(cx_left - w_slit/2, cy - len_slit/2, cx_left + w_slit/2, cy + len_slit/2)
slit_hole_r = box(cx_right - w_slit/2, cy - len_slit/2, cx_right + w_slit/2, cy + len_slit/2)

base_poly = outer_body_poly.difference(unary_union([hole_box, slit_hole_l, slit_hole_r]))
mesh_base = bp.extrude_shapely_geom(base_poly, height=bp.BASE_THICK)

# Build in-place shrouds on backside (Z: -2.47mm to 0.00mm)
shroud_l = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
shroud_l.apply_translation([cx_left, cy, 0.0])
shroud_r = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
shroud_r.apply_translation([cx_right, cy, 0.0])

slit_cutter_l = bp.extrude_shapely_geom(slit_hole_l, height=bp.SLIT_BOSS_HEIGHT + 2.0)
slit_cutter_l.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
shroud_l_hollow = shroud_l.difference(slit_cutter_l, engine='manifold')

slit_cutter_r = bp.extrude_shapely_geom(slit_hole_r, height=bp.SLIT_BOSS_HEIGHT + 2.0)
slit_cutter_r.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
shroud_r_hollow = shroud_r.difference(slit_cutter_r, engine='manifold')

mesh_shrouds = trimesh.util.concatenate([shroud_l_hollow, shroud_r_hollow])
mesh_base_complete = trimesh.util.concatenate([mesh_base, mesh_shrouds])

print("mesh_base_complete watertight:", mesh_base_complete.is_watertight)
print("mesh_base_complete bounds:\n", mesh_base_complete.bounds)
