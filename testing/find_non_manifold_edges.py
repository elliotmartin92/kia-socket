import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import trimesh

part_mesh, _ = build_part.build_exact_3d_model()
data = part_mesh.export(file_type='stl')
m = trimesh.load(trimesh.util.wrap_as_stream(data), file_type='stl')

non_manifold_edge_indices = trimesh.grouping.group_rows(m.edges_sorted, require_count=2)[1]
print("Number of non-manifold edges:", len(non_manifold_edge_indices))
for idx in non_manifold_edge_indices:
    edge = m.edges_sorted[idx]
    v_a = m.vertices[edge[0]]
    v_b = m.vertices[edge[1]]
    print(f"Edge {edge}: from {v_a} to {v_b}")
