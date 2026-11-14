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

# Plunger downward faces (X in [8.0, 13.0], Y in [5.0, 13.0])
p_faces = []
for i, norm in enumerate(shaft_t.face_normals):
    c = shaft_t.triangles_center[i]
    if 8.0 <= c[0] <= 13.0 and 5.0 <= c[1] <= 13.0:
        if norm[2] < -0.1:
            p_faces.append(i)

print(f"Plunger downward faces: {len(p_faces)}")
p_centers = shaft_t.triangles_center[p_faces]
sorted_idx = np.argsort(p_centers[:, 1])
for idx in sorted_idx:
    fi = p_faces[idx]
    c = shaft_t.triangles_center[fi]
    n = shaft_t.face_normals[fi]
    print(f"  Y={c[1]:.2f}, Z={c[2]:.2f}, X={c[0]:.2f}, normal={n.round(3).tolist()}")
