"""
Inspect STL clip outer wall geometry and slot cutouts in detail.
"""
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

from build_part import (
    build_exact_3d_model, find_boundary_point_and_normal,
    get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT,
    CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ARM_WIDTH, CLIP_HOOK_DEPTH
)

# Load the exported part.stl
stl_mesh = trimesh.load('part.stl')
print("STL mesh watertight:", stl_mesh.is_watertight)
print("Number of vertices:", len(stl_mesh.vertices), "faces:", len(stl_mesh.faces))

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()

for angle_deg in [45, 135, 225, 315]:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    
    # Crop mesh around this clip
    dists = np.linalg.norm(stl_mesh.vertices[:, :2] - p[:2], axis=1)
    mask = np.all(dists[stl_mesh.faces] < 5.0, axis=1)
    faces = stl_mesh.faces[mask]
    
    fig = plt.figure(figsize=(16, 8), dpi=160)
    
    # 1. Perspective view from outside looking towards center
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    col1 = Poly3DCollection(stl_mesh.vertices[faces], alpha=0.9, edgecolor='#222222', linewidths=0.25)
    col1.set_facecolor('#00acc1')
    ax1.add_collection3d(col1)
    
    ax1.set_xlim(p[0] - 3.5, p[0] + 3.5)
    ax1.set_ylim(p[1] - 3.5, p[1] + 3.5)
    ax1.set_zlim(0, 8)
    # Azimuth pointing towards center
    azim = np.rad2deg(np.arctan2(p[1], p[0])) + 180
    ax1.view_init(elev=20, azim=azim)
    ax1.set_title(f"Clip at {angle_deg}° (Outer View, azim={azim:.0f}°)", fontsize=11, fontweight='bold')
    
    # 2. Side view looking along tangent
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    col2 = Poly3DCollection(stl_mesh.vertices[faces], alpha=0.9, edgecolor='#222222', linewidths=0.25)
    col2.set_facecolor('#00acc1')
    ax2.add_collection3d(col2)
    
    ax2.set_xlim(p[0] - 3.5, p[0] + 3.5)
    ax2.set_ylim(p[1] - 3.5, p[1] + 3.5)
    ax2.set_zlim(0, 8)
    azim_side = azim - 90
    ax2.view_init(elev=0, azim=azim_side)
    ax2.set_title(f"Clip at {angle_deg}° (Side Tangent View)", fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'clip_{angle_deg}_detailed_stl.png', dpi=160)
    print(f"Saved clip_{angle_deg}_detailed_stl.png")
