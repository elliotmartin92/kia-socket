import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
from build_shaft import build_shaft_rocker_mesh

# 1. Main Part Single Solid
part_flat, base_poly = bp.build_exact_3d_model()
bodies = part_flat.split(only_watertight=False)
fixed_bodies = []
for b in bodies:
    if b.volume < 0:
        b.faces = np.fliplr(b.faces)
    fixed_bodies.append(b)

part_flat_solid = trimesh.boolean.union(fixed_bodies, engine='manifold')
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_flat_solid.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

_, _, all_fins = bp.build_45deg_supported_part_mesh(m_tilted)
fin_bodies = all_fins.split(only_watertight=False)
fixed_fins = []
for b in fin_bodies:
    if b.volume < 0:
        b.faces = np.fliplr(b.faces)
    fixed_fins.append(b)
fins_solid = trimesh.boolean.union(fixed_fins, engine='manifold')

part_45_solid = trimesh.boolean.union([m_tilted, fins_solid], engine='manifold')
print(f"part_45_solid: watertight={part_45_solid.is_watertight}, bodies={len(part_45_solid.split(only_watertight=False))}, Z_min={part_45_solid.bounds[0,2]:.4f}")

# 2. Shaft Rocker Single Solid
shaft_raw = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=True)
shaft_bodies = shaft_raw.split(only_watertight=False)
fixed_shaft = []
for b in shaft_bodies:
    if b.volume < 0:
        b.faces = np.fliplr(b.faces)
    fixed_shaft.append(b)
shaft_solid = trimesh.boolean.union(fixed_shaft, engine='manifold')
print(f"shaft_solid: watertight={shaft_solid.is_watertight}, bodies={len(shaft_solid.split(only_watertight=False))}, Z_min={shaft_solid.bounds[0,2]:.4f}")

# 3. Cooling Tower Single Solid
cool_tower = bp.build_cooling_tower_mesh(radius=2.0, height=20.50)
print(f"cool_tower: watertight={cool_tower.is_watertight}, bodies={len(cool_tower.split(only_watertight=False))}, Z_min={cool_tower.bounds[0,2]:.4f}")

# 4. Position and check complete assembly
shaft_positioned = shaft_solid.copy().apply_translation([27.50, 6.00, 0.00])
tower_positioned = cool_tower.copy().apply_translation([27.50, -18.00, 0.00])

assembly = trimesh.util.concatenate([part_45_solid, shaft_positioned, tower_positioned])
assembly_bodies = assembly.split(only_watertight=False)
print(f"\nAssembly total bodies: {len(assembly_bodies)}")
for i, b in enumerate(assembly_bodies):
    print(f"  Object {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, watertight = {b.is_watertight}")
