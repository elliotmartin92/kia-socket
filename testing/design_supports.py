import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon, box
import build_part
from build_shaft import build_shaft_rocker_mesh

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
shaft_tilted = shaft_mesh.copy().apply_transform(R)
shaft_tilted.apply_translation([0, 0, -z_min])

print("Testing support designs...")
# Let's test:
# 1. Slit insert supports and relief cutouts
# 2. Plunger support cradle
# 3. Cam tab support head
# 4. Shaft web support wing

print("z_min =", z_min)
