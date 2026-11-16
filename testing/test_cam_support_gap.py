import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from build_shaft import build_shaft_rocker_mesh
import build_part

# Build flat part and get z_min after 45 deg tilt
part_flat, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_flat.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]

# Build PIP shaft in tilted print orientation
shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
shaft_tilted = shaft_mesh.copy().apply_transform(R)
shaft_tilted.apply_translation([0, 0, -z_min])

# Build cam support tines exactly as in build_part.py
z_cam_fork_base = 16.00
pts_cam_tine_yz = [
    (-3.60, z_cam_fork_base),
    (-3.60, 20.123),        # 0.28mm release gap under nose curve (Z'_cam = 20.403)
    (-3.20, 19.952),        # 0.28mm release gap under lower blend (Z'_cam = 20.232)
    (-2.40, 19.895),        # 0.28mm release gap under underside saddle (Z'_cam = 20.175)
    (-1.60, 20.069),        # 0.28mm release gap under mid beam (Z'_cam = 20.349)
    (-1.00, 20.232),        # 0.28mm release gap under rear transition (Z'_cam = 20.512)
    (-1.00, z_cam_fork_base),
]
poly_cam_head_yz = Polygon(pts_cam_tine_yz)
cam_tine_w = 0.55

m_cl = trimesh.creation.extrude_polygon(poly_cam_head_yz, height=cam_tine_w)
v_cl = m_cl.vertices.copy()
v_cl_3d = np.column_stack([v_cl[:, 2] + 5.65, v_cl[:, 0], v_cl[:, 1]])
cam_tine_l = trimesh.Trimesh(vertices=v_cl_3d, faces=m_cl.faces.copy(), process=True)

m_cr = trimesh.creation.extrude_polygon(poly_cam_head_yz, height=cam_tine_w)
v_cr = m_cr.vertices.copy()
v_cr_3d = np.column_stack([v_cr[:, 2] + 7.00, v_cr[:, 0], v_cr[:, 1]])
cam_tine_r = trimesh.Trimesh(vertices=v_cr_3d, faces=m_cr.faces.copy(), process=True)

cam_support = trimesh.util.concatenate([cam_tine_l, cam_tine_r])

# 1. Overall minimum 3D Euclidean distance from cam support tines to the shaft rocker
tree = cKDTree(shaft_tilted.vertices)
dists, indices = tree.query(cam_support.vertices)
min_3d_dist = np.min(dists)
min_idx = np.argmin(dists)
closest_tine_pt = cam_support.vertices[min_idx]
closest_shaft_pt = shaft_tilted.vertices[indices[min_idx]]

print(f"Overall Minimum 3D Euclidean Distance: {min_3d_dist:.4f} mm")
print(f"  At Tine Vertex: {closest_tine_pt}")
print(f"  To Shaft Vertex: {closest_shaft_pt}")
print(f"  Delta (dX, dY, dZ): {closest_shaft_pt - closest_tine_pt}")

# 2. Check vertical Z' release gap directly above each tine station
print("\nVertical Release Gap by Y' Station (Print Frame):")
y_stations = [-3.60, -3.20, -2.40, -1.60, -1.00]
for ys in y_stations:
    # Shaft vertices right above tine (X in [5.65, 7.55], Y near ys)
    s_mask = (
        (np.abs(shaft_tilted.vertices[:, 1] - ys) < 0.15) &
        (shaft_tilted.vertices[:, 0] >= 5.60) &
        (shaft_tilted.vertices[:, 0] <= 7.60) &
        (shaft_tilted.vertices[:, 2] >= 19.5) &
        (shaft_tilted.vertices[:, 2] <= 21.5)
    )
    # Tine head top vertices
    t_mask = (
        (np.abs(cam_support.vertices[:, 1] - ys) < 0.05) &
        (cam_support.vertices[:, 2] > 18.0)
    )
    if np.any(s_mask) and np.any(t_mask):
        cam_z_min = np.min(shaft_tilted.vertices[s_mask, 2])
        tine_z_max = np.max(cam_support.vertices[t_mask, 2])
        z_gap = cam_z_min - tine_z_max
        print(f"  Station Y' = {ys:5.2f} mm | Tine Top Z' = {tine_z_max:6.3f} mm | Cam Underside Z' = {cam_z_min:6.3f} mm | Gap = {z_gap:6.3f} mm")

# 3. Check lateral clearance (in X) between the Cam Arm and the adjacent Shaft Barrel Support Stick
cam_x_max = np.max(shaft_tilted.vertices[
    (shaft_tilted.vertices[:, 1] >= -4.0) & (shaft_tilted.vertices[:, 1] <= 0.0) &
    (shaft_tilted.vertices[:, 2] >= 19.0) & (shaft_tilted.vertices[:, 2] <= 22.0),
    0
])
# Shaft barrel support stick is at X_c = 8.85, width = 0.70 (X in [8.50, 9.20])
stick_x_min = 8.85 - 0.70 / 2.0
stick_gap_x = stick_x_min - cam_x_max
print(f"\nLateral Clearance to Shaft Support Stick (X direction):")
print(f"  Cam Arm max X: {cam_x_max:.3f} mm")
print(f"  Shaft Support Stick min X: {stick_x_min:.3f} mm")
print(f"  Clear lateral air gap: {stick_gap_x:.3f} mm")
