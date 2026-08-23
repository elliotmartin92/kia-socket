"""
Test backside slit wall bosses.
"""
import numpy as np
import trimesh
from shapely.geometry import box
from shapely.ops import unary_union

from build_part import (
    get_exact_base_polygon, build_exact_3d_model, extrude_shapely_geom,
    SCALE, X0, Y0, bracket_1_raw_pts, bracket_4_raw_pts, to_mm_poly,
    SLIT_W_X, SLIT_LEN_Y, OUTER_WALL_THICK
)

SLIT_BOSS_HEIGHT = 2.47  # Protrudes 2.47mm on back side (-Z)
SLIT_BOSS_WALL = 0.80    # 0.8mm thick wall around slits

b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]
b1_rightmost_x = max(p[0] for p in b1_pts)  # -7.853mm
b4_leftmost_x = min(p[0] for p in b4_pts)   # +7.853mm

slit_y_bot = -18.539 + OUTER_WALL_THICK + 1.00  # -16.339mm
slit_y_top = slit_y_bot + SLIT_LEN_Y            # -13.339mm

# Left hole & outer boss
slit_left_hole = box(b1_rightmost_x - SLIT_W_X, slit_y_bot, b1_rightmost_x, slit_y_top)
slit_left_outer = box(b1_rightmost_x - SLIT_W_X - SLIT_BOSS_WALL, slit_y_bot - SLIT_BOSS_WALL,
                      b1_rightmost_x + SLIT_BOSS_WALL, slit_y_top + SLIT_BOSS_WALL)
boss_left_poly = slit_left_outer.difference(slit_left_hole)

# Right hole & outer boss
slit_right_hole = box(b4_leftmost_x, slit_y_bot, b4_leftmost_x + SLIT_W_X, slit_y_top)
slit_right_outer = box(b4_leftmost_x - SLIT_BOSS_WALL, slit_y_bot - SLIT_BOSS_WALL,
                       b4_leftmost_x + SLIT_W_X + SLIT_BOSS_WALL, slit_y_top + SLIT_BOSS_WALL)
boss_right_poly = slit_right_outer.difference(slit_right_hole)

bosses_poly = unary_union([boss_left_poly, boss_right_poly])

# Extrude downwards in -Z from Z = 0 to Z = -2.47mm
mesh_bosses = extrude_shapely_geom(bosses_poly, height=SLIT_BOSS_HEIGHT)
mesh_bosses.apply_translation([0, 0, -SLIT_BOSS_HEIGHT])

print(f"Boss mesh bounds: {mesh_bosses.bounds}")
print("Successfully generated backside slit shroud walls!")
