import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import build_part

m = trimesh.load('part.stl')
print(f"part.stl loaded: watertight={m.is_watertight}, volume={m.volume if m.is_watertight else 0}")

# Let's inspect each component of build_exact_3d_model
part_mesh, base_poly = build_part.build_exact_3d_model()
print(f"Direct build_exact_3d_model watertight: {part_mesh.is_watertight}")
