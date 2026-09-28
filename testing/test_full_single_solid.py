import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# 1. Build part_flat and union all bodies
part_flat, base_poly = bp.build_exact_3d_model()
bodies = part_flat.split(only_watertight=False)
fixed_bodies = []
for b in bodies:
    if b.volume < 0:
        b.faces = np.fliplr(b.faces)
    fixed_bodies.append(b)

part_flat_solid = trimesh.boolean.union(fixed_bodies, engine='manifold')
print("Part flat solid watertight:", part_flat_solid.is_watertight)

# 2. Tilt 45 degrees
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_flat_solid.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

# 3. Generate support fins and union them into ONE single support solid
_, _, all_fins = bp.build_45deg_supported_part_mesh(m_tilted)
fin_bodies = all_fins.split(only_watertight=False)
fins_solid = trimesh.boolean.union(fin_bodies, engine='manifold')
print("Fins solid watertight:", fins_solid.is_watertight)

# 4. Union the part and the support fins together into ONE single print solid!
print("Unioning part and support fins...")
full_print_solid = trimesh.boolean.union([m_tilted, fins_solid], engine='manifold')
print("Full print solid watertight:", full_print_solid.is_watertight)
print("Bodies in full print solid:", len(full_print_solid.split(only_watertight=False)))
print(f"Bounds Z: [{full_print_solid.bounds[0,2]:.4f}, {full_print_solid.bounds[1,2]:.4f}]")

# Check Layer 1 slice of full_print_solid:
slice_l1 = full_print_solid.section(plane_origin=[0, 0, 0.10], plane_normal=[0, 0, 1])
print(f"Layer 1 slice area: {slice_l1.to_planar()[0].area:.2f} mm^2")
