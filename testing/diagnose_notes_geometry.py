import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from build_shaft import build_shaft_rocker_mesh
import build_part

part_mesh_flat, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = part_mesh_flat.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

# Subparts in assembly coords
subparts = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False, return_subparts=True)

p1 = np.array([6.94966, -2.83171, 25.4984])
p2 = np.array([6.48746, -6.26706, 12.2343])

# Inverse transform p1 and p2 back to assembly coords (un-tilt)
# In tilted: x' = x, [y', z'] = rot_45 @ [y, z] + [0, -z_min]
# So [y', z' + z_min] = rot_45 @ [y, z]
# [y, z] = rot_45.T @ [y', z' + z_min]
rot_45_2d = np.array([
    [np.cos(np.radians(45.0)), -np.sin(np.radians(45.0))],
    [np.sin(np.radians(45.0)),  np.cos(np.radians(45.0))]
])

def untilt(p):
    x = p[0]
    yz_t = np.array([p[1], p[2] + z_min])
    yz = rot_45_2d.T @ yz_t
    return np.array([x, yz[0], yz[1]])

p1_orig = untilt(p1)
p2_orig = untilt(p2)

print(f"z_min = {z_min:.4f}")
print(f"p1 in tilted coords: {p1}")
print(f"p1 in assembly coords: {p1_orig}")
print(f"p2 in tilted coords: {p2}")
print(f"p2 in assembly coords: {p2_orig}")

for name, mesh in subparts.items():
    d1 = np.linalg.norm(mesh.vertices - p1_orig, axis=1).min()
    d2 = np.linalg.norm(mesh.vertices - p2_orig, axis=1).min()
    print(f"Subpart {name}: min dist to p1 = {d1:.4f}, min dist to p2 = {d2:.4f}")
