import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np

mesh = trimesh.load('part.stl')
pt5 = np.array([11.2648, -0.686527, 24.7967])

dists = np.linalg.norm(mesh.vertices - pt5, axis=1)
min_idx = np.argmin(dists)
print(f"Nearest vertex to Note 5: {mesh.vertices[min_idx]} (dist: {dists[min_idx]:.3f} mm)")

face_centers = mesh.triangles_center
face_dists = np.linalg.norm(face_centers - pt5, axis=1)
near_faces = np.where(face_dists < 1.5)[0]
print(f"Faces within 1.5mm: {len(near_faces)}")
if len(near_faces) > 0:
    for f in near_faces:
        print(f"  Face {f}: normal={mesh.face_normals[f].round(3).tolist()}, center={face_centers[f].round(3).tolist()}")

# Untilt pt5 to flat coordinate system
# Tilted: R_45(X) * p_flat + [0, 0, -z_min] = pt5
# So R_45 * p_flat = pt5 - [0, 0, -z_min]
# p_flat = R_45^T * (pt5 - [0, 0, -z_min])
z_min = -19.0 * np.sin(np.pi/4) # let's get exact z_min
# or let's use the actual transform from build_part
import build_part
base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

p_tilted_no_trans = pt5 + np.array([0, 0, z_min])
p_flat = np.linalg.inv(R[:3, :3]) @ p_tilted_no_trans
print(f"Flat coordinates of Note 5: {p_flat.round(3).tolist()}")
