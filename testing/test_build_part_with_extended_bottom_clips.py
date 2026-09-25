import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
import trimesh

# Temporarily update clip hook depths for test
bp.CLIP_HOOK_DEPTH_BY_ANGLE[211.3] = 1.70
bp.CLIP_HOOK_DEPTH_BY_ANGLE[327.5] = 1.50

print("Building exact 3D model with updated bottom clip hook depths...")
mesh, base_poly = bp.build_exact_3d_model()

print(f"Mesh volume: {mesh.volume:.2f} mm³")
print(f"Mesh is watertight: {mesh.is_watertight}")
print(f"Mesh vertex count: {len(mesh.vertices)}, face count: {len(mesh.faces)}")

bodies = mesh.split(only_watertight=False)
print(f"Total split bodies in mesh: {len(bodies)}")
for i, b in enumerate(bodies):
    print(f"  Body {i}: volume = {b.volume:.2f} mm³, bounds Z = [{b.bounds[0,2]:.2f}, {b.bounds[1,2]:.2f}], bounds R_xy = [{b.bounds[0,0]:.2f}..{b.bounds[1,0]:.2f}, {b.bounds[0,1]:.2f}..{b.bounds[1,1]:.2f}]")

# Check that hooks are 100% fused to the wall
detached_hooks = [b for b in bodies if 4.90 <= b.bounds[0, 2] and b.bounds[1, 2] <= 6.80 and 4.0 <= b.volume <= 30.0]
print(f"Detached hook bodies count: {len(detached_hooks)} (expected 0 - 100% fused!)")
assert len(detached_hooks) == 0, "Error: hooks are detached!"
print("Test completed successfully!")
