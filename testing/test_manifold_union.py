import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

part_flat, base_poly = bp.build_exact_3d_model()
part_supported, m_tilted, all_fins = bp.build_45deg_supported_part_mesh(part_flat)

# Split all_fins into separate bodies and union them:
fin_bodies = all_fins.split(only_watertight=False)
print(f"Total fin bodies to union: {len(fin_bodies)}")
try:
    fins_solid = trimesh.boolean.union(fin_bodies, engine='manifold')
    print("Fins solid watertight:", fins_solid.is_watertight, "bounds Z:", fins_solid.bounds[:, 2])
except Exception as e:
    print("Fins union failed:", e)

# Split m_tilted into separate bodies and union them:
part_bodies = m_tilted.split(only_watertight=False)
print(f"Total part bodies to union: {len(part_bodies)}")
try:
    m_tilted_solid = trimesh.boolean.union(part_bodies, engine='manifold')
    print("m_tilted_solid watertight:", m_tilted_solid.is_watertight, "bounds Z:", m_tilted_solid.bounds[:, 2])
except Exception as e:
    print("m_tilted union failed:", e)

# Union the full thing:
try:
    full_solid = trimesh.boolean.union([fins_solid, m_tilted_solid], engine='manifold')
    print("Full solid watertight:", full_solid.is_watertight, "bounds Z:", full_solid.bounds[:, 2])
    print("Bodies in full solid:", len(full_solid.split(only_watertight=False)))
except Exception as e:
    print("Full solid union failed:", e)
