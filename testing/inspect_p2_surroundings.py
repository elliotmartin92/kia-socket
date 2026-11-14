import trimesh
import numpy as np

m = trimesh.load('part.stl')
p2 = np.array([6.48746, -6.26706, 12.2343])
# Let's find all faces/triangles near p2
dists = np.linalg.norm(m.vertices - p2, axis=1)
close_idx = np.where(dists < 5.0)[0]
print(f"Num vertices within 5mm of p2: {len(close_idx)}")
for i in close_idx[:10]:
    print(f"Vertex {i}: {m.vertices[i]}, dist: {dists[i]:.4f}")

# Also check normal
n2 = np.array([0, -0.707107, -0.707107])
print("Note 2 normal:", n2)
