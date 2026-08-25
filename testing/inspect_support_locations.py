"""
testing/inspect_support_locations.py
Inspect the exact geometric overhang locations, rib slot clearance, and support accessibility
for the Inverted / Cam-Flat orientation vs the old belly-down orientation.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from build_shaft import build_shaft_rocker_mesh

shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)

# Compare 3 orientations:
configs = [
    ("Old Default (Rot X = +90°)", trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])),
    ("Optimal: Cam-Face Down (Rot X = 198.6°)", trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])),
    ("Optimal: Flat Inverted (Rot X = 180°)", trimesh.transformations.rotation_matrix(np.radians(180), [1, 0, 0]))
]

fig, axes = plt.subplots(1, 3, figsize=(20, 7), dpi=180)

for ax, (title, rot) in zip(axes, configs):
    m = shaft_assembled.copy()
    m.apply_transform(rot)
    bounds = m.bounds
    m.apply_translation([-(bounds[0,0]+bounds[1,0])/2.0, -(bounds[0,1]+bounds[1,1])/2.0, -bounds[0,2]])
    
    # 2D projection in Y-Z
    # Find edges / cross section
    # Let's plot 3D wireframe or 2D silhouette
    verts = m.vertices
    faces = m.faces
    normals = m.face_normals
    steep_overhang = normals[:, 2] < -0.7071
    
    # Project all faces to Y-Z plane
    for f_idx, face in enumerate(faces):
        fv = verts[face]
        # Y is fv[:, 1], Z is fv[:, 2]
        if steep_overhang[f_idx]:
            ax.fill(fv[:, 1], fv[:, 2], color='#e53935', alpha=0.6, ec='#b71c1c', lw=0.5)
        else:
            ax.fill(fv[:, 1], fv[:, 2], color='#90caf9', alpha=0.3, ec='#1565c0', lw=0.3)
            
    # Draw bed line
    ax.axhline(0, color='#37474f', lw=2.5, linestyle='-', label='Print Bed (Z=0)')
    
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xlabel('Y (mm)')
    ax.set_ylabel('Height Z (mm)')
    ax.set_xlim(-12, 12)
    ax.set_ylim(-1, 23)

plt.tight_layout()
plt.savefig('testing/support_comparison_yz_profile.png', dpi=180)
print("Saved testing/support_comparison_yz_profile.png")
