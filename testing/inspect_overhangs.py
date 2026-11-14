import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part
from build_shaft import build_shaft_rocker_mesh

# Let's inspect:
# 1. Slit insert backside geometry and supports
# 2. Cam tab geometry and supports
# 3. Plunger arm geometry and supports
# in the 45-degree tilted orientation.

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
base_mesh, base_poly = build_part.build_exact_3d_model()
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
shaft_tilted = shaft_mesh.copy().apply_transform(R)
shaft_tilted.apply_translation([0, 0, -z_min])

print("=== PIP SHAFT OVERHANG ANALYSIS (tilted 45°) ===")
# Find faces of shaft_tilted that are downward-facing (normal Z < -0.1)
down_faces = np.where(shaft_tilted.face_normals[:, 2] < -0.3)[0]
print(f"Downward-facing faces in shaft: {len(down_faces)} of {len(shaft_tilted.faces)}")

# Check overhangs specifically in Plunger (X in [8.0, 13.0], Y > 8.0)
plunger_faces = []
for fi in down_faces:
    c = shaft_tilted.triangles_center[fi]
    if 8.0 <= c[0] <= 13.0 and c[1] >= 5.0:
        plunger_faces.append(fi)
print(f"Plunger downward faces: {len(plunger_faces)}")
if plunger_faces:
    p_centers = shaft_tilted.triangles_center[plunger_faces]
    print(f"Plunger downward face Z range: {p_centers[:, 2].min():.2f} to {p_centers[:, 2].max():.2f}")
    print(f"Plunger downward face Y range: {p_centers[:, 1].min():.2f} to {p_centers[:, 1].max():.2f}")

# Check overhangs in Cam Tab (X in [5.0, 8.0], Y < 2.0)
cam_faces = []
for fi in down_faces:
    c = shaft_tilted.triangles_center[fi]
    if 5.0 <= c[0] <= 8.0 and c[1] <= 2.0:
        cam_faces.append(fi)
print(f"Cam Tab downward faces: {len(cam_faces)}")
if cam_faces:
    c_centers = shaft_tilted.triangles_center[cam_faces]
    print(f"Cam Tab downward face Z range: {c_centers[:, 2].min():.2f} to {c_centers[:, 2].max():.2f}")
    print(f"Cam Tab downward face Y range: {c_centers[:, 1].min():.2f} to {c_centers[:, 1].max():.2f}")

print("\n=== SLIT INSERTS OVERHANG ANALYSIS ===")
# Base mesh slit insert tips around X = +/- 8.0, Y = -9.5, Z in [0, 2]
slit_faces = []
down_base_faces = np.where(m_tilted.face_normals[:, 2] < -0.3)[0]
for fi in down_base_faces:
    c = m_tilted.triangles_center[fi]
    if abs(abs(c[0]) - 8.1) < 2.0 and -12.0 <= c[1] <= -7.0 and c[2] <= 4.0:
        slit_faces.append(fi)
print(f"Slit insert downward faces: {len(slit_faces)}")
if slit_faces:
    s_centers = m_tilted.triangles_center[slit_faces]
    print(f"Slit insert downward face Z range: {s_centers[:, 2].min():.2f} to {s_centers[:, 2].max():.2f}")
    print(f"Slit insert downward face Y range: {s_centers[:, 1].min():.2f} to {s_centers[:, 1].max():.2f}")
