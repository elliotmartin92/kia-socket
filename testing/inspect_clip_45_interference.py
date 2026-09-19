import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import build_part
from build_shaft import X_LEFT_TOWER_OUTER, X_LEFT_TOWER_INNER, X_RIGHT_TOWER_INNER, X_RIGHT_TOWER_OUTER

# Let's inspect the part mesh and components around the 45 degree clip
base_poly, outer_body_poly, hole_info = build_part.get_exact_base_polygon()
towers = build_part.build_clean_shaft_towers_mesh()
p45, norm45, _ = build_part.find_boundary_point_and_normal(base_poly, 45.0)

print(f"p45: {p45}, norm45: {norm45}")
print(f"Right tower bounds: X=[{X_RIGHT_TOWER_INNER}, {X_RIGHT_TOWER_OUTER}], Y=[6.25, 12.85], Z=[1.0, 14.09]")

# Check distances between right tower vertices and p45
t_verts = towers.vertices
t_right = t_verts[t_verts[:, 0] >= X_RIGHT_TOWER_INNER - 0.1]
dists = np.linalg.norm(t_right[:, :2] - p45, axis=1)
print(f"Min 2D distance from right tower to p45: {np.min(dists):.3f} mm")

# Find where the 45 hook is
hook_apex = p45 + norm45 * build_part.CLIP_HOOK_DEPTH
print(f"45 Hook apex: {hook_apex}")

# Let's inspect all vertices of the full part near (14, 14)
part_mesh, _ = build_part.build_exact_3d_model()
pts_near_45 = part_mesh.vertices[np.linalg.norm(part_mesh.vertices[:, :2] - p45, axis=1) < 8.0]
print(f"Points near 45 clip: Z min={np.min(pts_near_45[:, 2]):.2f}, Z max={np.max(pts_near_45[:, 2]):.2f}")
