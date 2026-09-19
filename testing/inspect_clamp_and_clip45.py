import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import build_part
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
p45, norm45, _ = build_part.find_boundary_point_and_normal(base_poly, 45.0)

clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)
u_clamp = build_unified_clamp_mesh(in_assembly_coords=True)

print("Right Clamp bounds:", clamp_r.bounds)
print("Unified Clamp bounds:", u_clamp.bounds)

dists_clamp_r = np.linalg.norm(clamp_r.vertices[:, :2] - p45, axis=1)
print(f"Min 2D distance from right clamp to p45: {np.min(dists_clamp_r):.3f} mm")

# Distance to the 45 degree clip wedge
full_part, _ = build_part.build_exact_3d_model()
# isolate 45 degree clip
clip45_pts = full_part.vertices[np.linalg.norm(full_part.vertices[:, :2] - p45, axis=1) < 3.5]
dists_3d = []
for cp in clip45_pts:
    d = np.min(np.linalg.norm(clamp_r.vertices - cp, axis=1))
    dists_3d.append(d)
print(f"Min 3D distance between 45 clip and right clamp: {np.min(dists_3d):.3f} mm")
