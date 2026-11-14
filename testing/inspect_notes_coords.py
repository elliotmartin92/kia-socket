import trimesh
import numpy as np

m = trimesh.load('part.stl')
p1 = np.array([6.94966, -2.83171, 25.4984])
p2 = np.array([6.48746, -6.26706, 12.2343])

d1 = np.linalg.norm(m.vertices - p1, axis=1)
idx1 = np.argmin(d1)
print(f"Closest vertex to p1: {m.vertices[idx1]} at dist {d1[idx1]:.4f}")

d2 = np.linalg.norm(m.vertices - p2, axis=1)
idx2 = np.argmin(d2)
print(f"Closest vertex to p2: {m.vertices[idx2]} at dist {d2[idx2]:.4f}")
