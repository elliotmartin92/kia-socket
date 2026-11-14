import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

pt7 = np.array([9.76224, -2.20633, 25.6702])

# Load part.stl (which includes our latest supports and PIP shaft)
mesh = trimesh.load('part.stl')

# Find nearest vertices and faces in part.stl
dists = np.linalg.norm(mesh.vertices - pt7, axis=1)
min_idx = np.argmin(dists)
print(f"Nearest vertex in part.stl: {mesh.vertices[min_idx]} (dist: {dists[min_idx]:.3f} mm)")

# Query nearby faces within 2.0mm
face_centers = mesh.triangles_center
face_dists = np.linalg.norm(face_centers - pt7, axis=1)
near_faces = np.where(face_dists < 2.0)[0]
print(f"Faces within 2.0mm: {len(near_faces)}")
for f in near_faces:
    print(f"  Face {f}: center={face_centers[f].round(3).tolist()}, normal={mesh.face_normals[f].round(3).tolist()}")

# What is on shaft_rocker around pt7?
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, _ = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

d_shaft = np.linalg.norm(shaft_t.vertices - pt7, axis=1)
min_s_idx = np.argmin(d_shaft)
print(f"Nearest vertex on shaft: {shaft_t.vertices[min_s_idx]} (dist: {d_shaft[min_s_idx]:.3f} mm)")

# What is directly below pt7?
ray_origins = np.array([[pt7[0], pt7[1], pt7[2] - 0.1]])
ray_directions = np.array([[0, 0, -1]])
locs, _, _ = mesh.ray.intersects_location(ray_origins, ray_directions)
print("Below pt7 in part.stl:")
for loc in locs:
    print(f"  Z = {loc[2]:.3f} (dist below: {pt7[2] - loc[2]:.3f} mm)")
