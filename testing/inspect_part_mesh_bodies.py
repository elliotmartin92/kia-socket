import trimesh
import numpy as np

part = trimesh.load('part.stl')

# Let's inspect the 45 degree clip at Z between 4.90 and 6.80
# At 45 degrees, angle is pi/4 -> X, Y > 10
# Find faces in the hook region: R > 19.5, Z in [4.97, 6.77]
v = part.vertices
radii = np.sqrt(v[:, 0]**2 + v[:, 1]**2)

hook_verts_idx = np.where((radii > 19.5) & (v[:, 2] >= 4.95) & (v[:, 2] <= 6.80) & (v[:, 0] > 10) & (v[:, 1] > 10))[0]
print(f"Hook region vertices: {len(hook_verts_idx)}")

# Check if part is a single connected component or multiple bodies
bodies = part.split(only_watertight=False)
print(f"Total disjoint bodies in part.stl: {len(bodies)}")
for i, b in enumerate(bodies):
    print(f"Body {i}: watertight={b.is_watertight}, volume={b.volume:.2f}, bounds={b.bounds.tolist()}")
