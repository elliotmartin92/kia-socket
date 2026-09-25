import trimesh
import numpy as np
from build_part import get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT, BASE_THICK
import build_part

base_poly, outer_body_poly, _ = get_exact_base_polygon()

# Let's inspect the hooks and wall union
part = trimesh.load('part.stl')

# Let's see if we can do a proper boolean union of the wall and hooks
# In build_part.py, line 852: hook_mesh is created with an inner mating face.
# If hook_mesh is unioned with mesh_wall (or if hook overlaps into mesh_wall by 0.2mm and is unioned with engine='manifold'):
# Then the internal wall disappears completely and the hook becomes a monolithic feature of the stem!

print("Current part is_watertight:", part.is_watertight)
