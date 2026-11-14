import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

base_mesh, base_poly = build_part.build_exact_3d_model()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

# Note 5 location
pt5 = np.array([11.2648, -0.686527, 24.7967])

# Check what is directly below pt5 in Z' (downward ray from pt5)
ray_origins = np.array([[pt5[0], pt5[1], pt5[2] - 0.1]])
ray_directions = np.array([[0, 0, -1]])

locations, index_ray, index_tri = m_t.ray.intersects_location(
    ray_origins=ray_origins,
    ray_directions=ray_directions
)

print(f"Directly below Note 5 in tilted orientation on base part:")
if len(locations) > 0:
    for loc in locations:
        print(f"  Hit at Z' = {loc[2]:.2f} mm (distance below: {pt5[2] - loc[2]:.2f} mm)")
else:
    print("  No base part geometry directly below (hits bed pad at Z=0.60mm)")

# Check in flat coordinates what is directly below
# Flat Note 5: [11.265, 7.779, 8.75]
print("\nIn flat coordinates:")
print("Note 5 is at X=11.265, Y=7.779, Z=8.75")
# What is Bracket 4?
# Bracket 4 in flat coordinates:
# Let's check brackets poly bounds
brackets_poly = build_part.create_all_brackets_poly()
print(f"All brackets bounds: {brackets_poly.bounds}")
