import trimesh
import numpy as np
from shapely.geometry import Polygon, box
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Let's see: what if base_poly does NOT cut the detent sockets, but only cuts the 1.20 x 3.40mm slit through-holes?
# Slit through-holes:
cx_left = -7.853
cx_right = 8.453
cy = -13.589

w_slit = bp.SLIT_W_X     # 1.20 mm
len_slit = bp.SLIT_LEN_Y # 3.40 mm

slit_hole_l = box(cx_left - w_slit/2, cy - len_slit/2, cx_left + w_slit/2, cy + len_slit/2)
slit_hole_r = box(cx_right - w_slit/2, cy - len_slit/2, cx_right + w_slit/2, cy + len_slit/2)

# Shroud bodies on the back side (Z: -2.47mm to 0.00mm):
# In build_slit_insert_mesh:
# m_body = create_frustum_mesh(INSERT_BODY_W_TIP, INSERT_BODY_LEN_TIP, INSERT_BODY_W_X, INSERT_BODY_LEN_Y, z0, z1)
# with through-hole cut:
shroud_l = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
shroud_l.apply_translation([cx_left, cy, 0.0])

shroud_r = bp.create_frustum_mesh(bp.INSERT_BODY_W_TIP, bp.INSERT_BODY_LEN_TIP, bp.INSERT_BODY_W_X, bp.INSERT_BODY_LEN_Y, -bp.SLIT_BOSS_HEIGHT, 0.0)
shroud_r.apply_translation([cx_right, cy, 0.0])

# Cut the slit holes through the shrouds:
slit_cutter_l = bp.extrude_shapely_geom(slit_hole_l, height=bp.SLIT_BOSS_HEIGHT + 2.0)
slit_cutter_l.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
shroud_l_hollow = shroud_l.difference(slit_cutter_l, engine='manifold')

slit_cutter_r = bp.extrude_shapely_geom(slit_hole_r, height=bp.SLIT_BOSS_HEIGHT + 2.0)
slit_cutter_r.apply_translation([0, 0, -bp.SLIT_BOSS_HEIGHT - 1.0])
shroud_r_hollow = shroud_r.difference(slit_cutter_r, engine='manifold')

print("Left hollow shroud watertight:", shroud_l_hollow.is_watertight)
print("Right hollow shroud watertight:", shroud_r_hollow.is_watertight)
print("Left shroud bounds:\n", shroud_l_hollow.bounds)
print("Right shroud bounds:\n", shroud_r_hollow.bounds)
