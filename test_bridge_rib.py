"""
Test extruding the bridge ribbing to the right of the right tower up to 6.77mm (outer wall height).
"""
import shapely.geometry as sg
from shapely.ops import unary_union
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    get_exact_base_polygon, create_grid_ribs_poly,
    OUTER_WALL_HEIGHT, OUTER_WALL_THICK, BASE_THICK, RIB_HEIGHT,
    build_clean_shaft_towers_mesh, extrude_shapely_geom
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
all_ribs_poly = create_grid_ribs_poly(base_poly)

# Define the bridge region to the right of the right tower:
# Right tower is at X in [13.36, 14.36], Y in [5.34, 9.99]
# Bridge box covers X from 13.36 to 25.0, Y from 4.0 to 10.0
bridge_box = sg.box(13.36, 4.0, 25.0, 9.0)
bridge_rib_poly = all_ribs_poly.intersection(bridge_box)

# Normal floor ribs (everything except the tall bridge ribs)
normal_ribs_poly = all_ribs_poly.difference(bridge_box)

print(f"Normal ribs area: {normal_ribs_poly.area:.3f}")
print(f"Bridge ribs area: {bridge_rib_poly.area:.3f}")

# Mesh bridge rib (height = OUTER_WALL_HEIGHT - BASE_THICK = 5.77mm)
mesh_bridge_rib = extrude_shapely_geom(bridge_rib_poly, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_bridge_rib.apply_translation([0, 0, BASE_THICK])

# Mesh normal ribs (height = RIB_HEIGHT = 0.5mm)
mesh_normal_ribs = extrude_shapely_geom(normal_ribs_poly, height=RIB_HEIGHT)
mesh_normal_ribs.apply_translation([0, 0, BASE_THICK])

mesh_towers = build_clean_shaft_towers_mesh()

print("Bridge rib successfully extruded to 6.77mm!")
