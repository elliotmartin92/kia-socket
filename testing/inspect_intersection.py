import sys
sys.path.insert(0, '.')
import trimesh
import numpy as np
from shapely.geometry import Point, Polygon
from build_part import get_exact_base_polygon
import build_clamp

_, outer_body_poly, _ = get_exact_base_polygon()
clamp = build_clamp.build_tower_clamp_mesh('right', in_assembly_coords=True)

print("Clamp vertices count:", len(clamp.vertices))
print("Clamp X max:", clamp.vertices[:, 0].max())
print("Clamp Y max:", clamp.vertices[:, 1].max())

# Let's see vertices where X > 16.0
high_x_verts = clamp.vertices[clamp.vertices[:, 0] > 16.0]
print(f"Vertices with X > 16.0: {len(high_x_verts)}")
for v in high_x_verts:
    p = Point(v[0], v[1])
    dist = outer_body_poly.exterior.distance(p)
    inside = outer_body_poly.contains(p)
    print(f"X={v[0]:.2f}, Y={v[1]:.2f}, Z={v[2]:.2f} -> inside={inside}, dist={dist:.3f}")

# What is the actual WALL of the baseplate?
# The outer wall in build_part.py is created by:
# inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
# wall_poly = outer_body_poly.difference(inner_poly)
# But wait! Where is the cylindrical wall? What is the shape of outer_body_poly?
