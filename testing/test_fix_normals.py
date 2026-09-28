import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

part_flat, base_poly = bp.build_exact_3d_model()
bodies = part_flat.split(only_watertight=False)

fixed_bodies = []
for i, b in enumerate(bodies):
    if b.volume < 0:
        b.faces = np.fliplr(b.faces)
        print(f"Fixed inverted normals on Body {i}, new volume: {b.volume:.4f}")
    fixed_bodies.append(b)

# Now union all bodies of part_flat into ONE single monolithic mesh!
print("Unioning fixed part_flat bodies...")
part_flat_solid = trimesh.boolean.union(fixed_bodies, engine='manifold')
print(f"part_flat_solid watertight: {part_flat_solid.is_watertight}, volume: {part_flat_solid.volume:.4f}")
print("Number of bodies in part_flat_solid:", len(part_flat_solid.split(only_watertight=False)))
