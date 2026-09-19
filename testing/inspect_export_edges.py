import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import trimesh

part_mesh, _ = build_part.build_exact_3d_model()
print("part_mesh is_watertight:", part_mesh.is_watertight)
print("Euler number:", part_mesh.euler_number)
print("Is volume positive?", part_mesh.volume > 0)

# Export to bytes as stl
data = part_mesh.export(file_type='stl')
reloaded = trimesh.load(trimesh.util.wrap_as_stream(data), file_type='stl')
print("Reloaded from bytes is_watertight:", reloaded.is_watertight)
print("Edges non-manifold:", len(trimesh.grouping.group_rows(reloaded.edges_sorted, require_count=2)[1]))
