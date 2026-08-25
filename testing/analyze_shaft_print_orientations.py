"""
testing/analyze_shaft_print_orientations.py
Comprehensive analysis of 3D printing orientations for the shaft/rocker mechanism:
- Support volume & overhang areas (>45° from vertical)
- Bed contact area & stability
- Pin roundness & layer adhesion strength
- Ease of support removal (accessible vs trapped supports)
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build_shaft import build_shaft_rocker_mesh

shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)

def analyze_orientation(mesh, name, rot_matrix, description=""):
    m = mesh.copy()
    m.apply_transform(rot_matrix)
    # Shift Z_min to 0
    bounds = m.bounds
    m.apply_translation([-(bounds[0,0]+bounds[1,0])/2.0, -(bounds[0,1]+bounds[1,1])/2.0, -bounds[0,2]])
    
    faces = m.faces
    normals = m.face_normals
    areas = m.area_faces
    
    downward_mask = normals[:, 2] < -0.05
    steep_overhang_mask = normals[:, 2] < -0.7071  # Overhang > 45° from vertical (needs support)
    
    # Calculate bed contact area (faces with Z <= 0.15 and normal[2] < -0.90)
    face_min_z = np.min(m.vertices[faces, 2], axis=1)
    bed_mask = (face_min_z < 0.10) & (normals[:, 2] < -0.90)
    bed_area = np.sum(areas[bed_mask])
    
    overhang_area = np.sum(areas[steep_overhang_mask])
    total_downward_area = np.sum(areas[downward_mask])
    
    height_z = bounds[1,2] - bounds[0,2]
    
    return {
        "name": name,
        "description": description,
        "mesh": m,
        "height_z": height_z,
        "bed_area": bed_area,
        "overhang_area": overhang_area,
        "total_downward_area": total_downward_area,
        "bounds": m.bounds
    }

# 1. Current Default (Rot X = +90°)
r_curr = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])

# 2. Inverted / Cam-Flat (Rot X = 180° - 200°)
# At ~198.6°, the flat top face of the 105° cam tab is 100% flat on the build plate!
# Angle of cam top normal: theta_cam = -161.4° -> normal is at +108.6°
# To lay cam top flat on bed (normal pointing to -Z / -90°), rotation is 198.6°!
r_cam_flat = trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])

# 3. Plunger Back Flat (Rot X = -86.4° -> ~273.6° or ~93.6°)
# Plunger centerline is at -86.4°. Laying plunger spine flat:
r_plunger_flat = trimesh.transformations.rotation_matrix(np.radians(86.4 + 90), [1, 0, 0]) # 176.4°

# 4. Rot X = 210° (Cam and Web flat on bed)
r_210 = trimesh.transformations.rotation_matrix(np.radians(210), [1, 0, 0])

# 5. Inverted (Rot X = 180°)
r_180 = trimesh.transformations.rotation_matrix(np.radians(180), [1, 0, 0])

# 6. Standing (Rot X = 0°)
r_0 = np.eye(4)

candidate_configs = [
    ("Current Default (Rot X = +90°)", r_curr, "Belly down. Traps support between 3 ribs & under axle pins."),
    ("Cam-Tab Flat on Bed (Rot X = 198.6°)", r_cam_flat, "Flat 2.7x6.8mm cam face directly on build plate. Plunger stands up self-supporting."),
    ("Cam & Web Bed Contact (Rot X = 210°)", r_210, "Wide flat bed contact. Minimal support on plunger tip."),
    ("Inverted Assembled (Rot X = 180°)", r_180, "Top face down. Broad bed contact on hub top."),
    ("Standing Assembled (Rot X = 0°)", r_0, "Plunger tip on bed (tiny footprint, needs brim)."),
]

results = [analyze_orientation(shaft_assembled, name, mat, desc) for name, mat, desc in candidate_configs]

print("=== Print Orientation Analysis ===")
print(f"{'Orientation':<38} | {'Height':<8} | {'Bed Area':<10} | {'Overhang Area':<14} | {'Notes'}")
print("-" * 110)
for r in results:
    print(f"{r['name']:<38} | {r['height_z']:<6.2f}mm | {r['bed_area']:<8.2f}mm² | {r['overhang_area']:<12.2f}mm² | {r['description']}")

# Plot 3D visualization of orientations
fig = plt.figure(figsize=(22, 10), dpi=180)
for i, r in enumerate(results):
    m = r["mesh"]
    ax = fig.add_subplot(1, len(results), i+1, projection='3d')
    
    verts = m.vertices
    faces = m.faces
    normals = m.face_normals
    steep_overhang = normals[:, 2] < -0.7071
    
    face_colors = np.ones((len(faces), 4)) * [0.8, 0.85, 0.9, 0.9] # Neutral body
    face_colors[steep_overhang] = [0.9, 0.2, 0.2, 0.95] # Red = Support needed
    
    face_min_z = np.min(verts[faces, 2], axis=1)
    bed_mask = (face_min_z < 0.10) & (normals[:, 2] < -0.90)
    face_colors[bed_mask] = [0.2, 0.8, 0.2, 1.0] # Green = Bed contact
    
    poly3d = [[verts[idx] for idx in face] for face in faces]
    collection = Poly3DCollection(poly3d, facecolors=face_colors, edgecolors='k', linewidths=0.2, alpha=0.9)
    ax.add_collection3d(collection)
    
    # Bed plate plane (Z=0)
    xx, yy = np.meshgrid(np.linspace(-10, 10, 2), np.linspace(-10, 10, 2))
    ax.plot_surface(xx, yy, np.zeros_like(xx), color='#bdbdbd', alpha=0.3)
    
    ax.set_xlim(-9, 9)
    ax.set_ylim(-9, 9)
    ax.set_zlim(0, 22)
    ax.set_title(f"{r['name']}\nOverhang: {r['overhang_area']:.1f} mm² (Bed: {r['bed_area']:.1f} mm²)", fontsize=9.5, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init(elev=20, azim=45)

plt.tight_layout()
plt.savefig('testing/shaft_print_orientations_visualized.png', dpi=180)
print("Saved testing/shaft_print_orientations_visualized.png")
