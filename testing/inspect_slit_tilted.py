import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

# Inspect right slit insert: X in [7.0, 10.0], Y in [-12.0, -8.0], Z in [0, 4.0]
# Find vertices
v = m_t.vertices
mask = (v[:, 0] >= 7.0) & (v[:, 0] <= 10.0) & (v[:, 1] >= -12.0) & (v[:, 1] <= -7.0) & (v[:, 2] <= 4.0)
v_slit = v[mask]
print(f"Slit insert tilted bounds: X [{v_slit[:, 0].min():.3f}, {v_slit[:, 0].max():.3f}], Y [{v_slit[:, 1].min():.3f}, {v_slit[:, 1].max():.3f}], Z [{v_slit[:, 2].min():.3f}, {v_slit[:, 2].max():.3f}]")

# Check downward faces on right slit insert
down_faces = []
for i, tri in enumerate(m_t.triangles):
    c = np.mean(tri, axis=0)
    if (7.0 <= c[0] <= 10.0) and (-12.0 <= c[1] <= -7.0) and (c[2] <= 4.0):
        if m_t.face_normals[i, 2] < -0.2:
            down_faces.append(i)

print(f"Downward faces on right slit: {len(down_faces)}")
for df in down_faces:
    print(f"  Face {df}: center={m_t.triangles_center[df].round(3).tolist()}, normal={m_t.face_normals[df].round(3).tolist()}")
