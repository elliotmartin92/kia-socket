import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part
import trimesh

part_mesh, _ = build_part.build_exact_3d_model()
print("Direct part_mesh:", part_mesh.is_watertight)

# Let's check trimesh.repair
trimesh.repair.fix_inversion(part_mesh)
trimesh.repair.fix_normals(part_mesh)
trimesh.repair.fix_winding(part_mesh)

data = part_mesh.export(file_type='stl')
m = trimesh.load(trimesh.util.wrap_as_stream(data), file_type='stl')
print("Reloaded after repair:", m.is_watertight)

# If we don't include supports in part_mesh, is it watertight?
mesh_no_supp = trimesh.util.concatenate([
    m for m in [part_mesh] # let's check
])
