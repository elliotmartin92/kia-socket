import trimesh
import numpy as np

m = trimesh.load('part.stl')
p2 = np.array([6.48746, -6.26706, 12.2343])
n2 = np.array([0, -0.707107, -0.707107])

# Let's find the face closest to p2 whose normal matches n2
face_normals = m.face_normals
face_centers = m.triangles.mean(axis=1)

dists = np.linalg.norm(face_centers - p2, axis=1)
dot_normals = np.dot(face_normals, n2)

# Find faces within 3mm of p2 and dot normal > 0.9
matches = np.where((dists < 4.0) & (dot_normals > 0.9))[0]
print(f"Number of matching faces near p2 with normal {n2}: {len(matches)}")
for idx in matches[:5]:
    tri = m.triangles[idx]
    norm = face_normals[idx]
    print(f"Face {idx}: center={face_centers[idx]}, normal={norm}, dist={dists[idx]:.4f}")
    print(f"  Vertices: {tri.tolist()}")

# Also check without normal filter
closest_faces = np.argsort(dists)[:5]
print("\nClosest 5 faces overall:")
for idx in closest_faces:
    print(f"Face {idx}: center={face_centers[idx]}, normal={face_normals[idx]}, dist={dists[idx]:.4f}")
