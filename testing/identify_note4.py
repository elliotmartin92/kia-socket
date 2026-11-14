import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np

# Load base mesh, tilted mesh, shaft mesh, etc.
import build_part
base_mesh, base_poly = build_part.build_exact_3d_model()
part_mesh, tilted, fins = build_part.build_45deg_supported_part_mesh(base_mesh, base_poly=base_poly)

pt4 = np.array([11.2643, 10.3559, 18.9869])

# Check distance to tilted main part vs shaft vs fins
d_tilted = np.min(np.linalg.norm(tilted.vertices - pt4, axis=1))
d_fins = np.min(np.linalg.norm(fins.vertices - pt4, axis=1))

from build_shaft import build_shaft_rocker_mesh
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
z_min = tilted.bounds[0, 2] # wait, z_min was used in build_45deg_supported_part_mesh
# in build_45deg:
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
shaft_tilted = shaft_mesh.copy().apply_transform(R)
shaft_tilted.apply_translation([0, 0, -z_min])

d_shaft = np.min(np.linalg.norm(shaft_tilted.vertices - pt4, axis=1))

print(f"Distances to Note 4 {pt4}:")
print(f"  To tilted base part: {d_tilted:.3f} mm")
print(f"  To support fins/struts: {d_fins:.3f} mm")
print(f"  To tilted PIP shaft: {d_shaft:.3f} mm")

# Also print bounds of shaft_tilted
print(f"Shaft bounds: {shaft_tilted.bounds.tolist()}")
