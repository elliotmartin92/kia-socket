import trimesh
import numpy as np

# Load part.stl
mesh = trimesh.load('part.stl')

notes = [
    {"id": 1, "at": [8.57168, -9.33213, 0.283819], "desc": "Note 1"},
    {"id": 2, "at": [-7.90953, -9.28153, 0.334419], "desc": "Note 2"},
    {"id": 3, "at": [7.23808, -2.78981, 18.3391], "desc": "Note 3"},
    {"id": 4, "at": [11.2643, 10.3559, 18.9869], "desc": "Note 4"},
]

print(f"Loaded part.stl: bounds = {mesh.bounds.tolist()}")

for n in notes:
    pt = np.array(n["at"])
    # Find nearest vertex or triangle
    dists = np.linalg.norm(mesh.vertices - pt, axis=1)
    min_idx = np.argmin(dists)
    min_dist = dists[min_idx]
    v_near = mesh.vertices[min_idx]
    print(f"\n--- {n['desc']} (id {n['id']}) at {pt} ---")
    print(f"Nearest vertex: {v_near} (dist: {min_dist:.3f} mm)")
    
    # Query nearby faces within 1.5mm
    face_centers = mesh.triangles_center
    face_dists = np.linalg.norm(face_centers - pt, axis=1)
    near_faces = np.where(face_dists < 1.5)[0]
    print(f"Number of faces within 1.5mm: {len(near_faces)}")
    if len(near_faces) > 0:
        normals = mesh.face_normals[near_faces]
        avg_normal = np.mean(normals, axis=0)
        avg_normal /= np.linalg.norm(avg_normal)
        print(f"Average normal of nearby faces: {avg_normal.round(3).tolist()}")
        print(f"Z range of nearby faces: min {mesh.vertices[mesh.faces[near_faces]].reshape(-1, 3)[:, 2].min():.2f}, max {mesh.vertices[mesh.faces[near_faces]].reshape(-1, 3)[:, 2].max():.2f}")
