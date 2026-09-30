import sys, os
import numpy as np
import trimesh
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import build_shaft

def inspect_all():
    part_mesh_flat, base_poly = build_part.build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = part_mesh_flat.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    
    # Lever subparts
    shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, return_subparts=True, with_supports=False)
    lever_all = []
    for name, part in shaft_subparts.items():
        part.apply_transform(R)
        part.apply_translation([0, 0, -z_min])
        lever_all.append(part)
    full_lever = trimesh.util.concatenate(lever_all)
    tree_lever = cKDTree(full_lever.vertices)

    # Let's inspect fin_components directly from build_45deg_supported_part_mesh
    # We can inspect what build_45deg_supported_part_mesh produces
    _, _, all_fins = build_part.build_45deg_supported_part_mesh(part_mesh_flat, base_poly, include_pip_shaft=False)
    
    bodies = all_fins.split(only_watertight=False)
    print(f"Total split bodies in all_fins: {len(bodies)}")
    for i, b in enumerate(bodies):
        dists, _ = tree_lever.query(b.vertices)
        min_d = np.min(dists)
        if min_d < 3.0:
            print(f"Body #{i}: bounds X=[{b.bounds[0,0]:.2f}, {b.bounds[1,0]:.2f}], Y=[{b.bounds[0,1]:.2f}, {b.bounds[1,1]:.2f}], Z=[{b.bounds[0,2]:.2f}, {b.bounds[1,2]:.2f}] -> min dist to lever = {min_d:.3f} mm")
            for name, sub in shaft_subparts.items():
                tree_s = cKDTree(sub.vertices)
                ds, _ = tree_s.query(b.vertices)
                if np.min(ds) < 3.0:
                    print(f"    vs {name}: {np.min(ds):.3f} mm")

if __name__ == '__main__':
    inspect_all()
