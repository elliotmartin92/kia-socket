"""
testing/test_twin_prong_support.py
Build and verify the Twin-Prong Fork support with a central prying arch.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ARM_WIDTH
)

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97 mm
support_top_z = stem_h - 0.15           # 4.82 mm
hook_depth = 2.49                        # 2.49 mm (-0.10mm from 2.59mm)
hook_width = 4.20

base_poly, outer_body_poly, _ = get_exact_base_polygon()

def build_clip_supports_twin_prong(base_poly, hook_depth=2.49):
    """
    Twin-prong fork breakaway support:
    - Shared solid trunk from Z=0 to Z=3.20mm on a wide bed adhesion foot.
    - Central prying arch/relief cutout from Z=3.20mm to Z=4.82mm (1.80mm wide).
    - Twin vertical support prongs at lateral edges (Y = +/- 1.40mm).
    - Twin chisel breakaway tips (0.50mm radial x 0.90mm tangential x 0.12mm tall, Z in [4.82, 4.94]mm).
    - Total contact area = 2 * (0.50 * 0.90) = 0.90 mm² (identically matches previous 0.90 mm² area).
    """
    support_meshes = []
    
    # Prongs Y center
    y_prongs = [-1.40, 1.40]
    prong_w_tang = 0.90
    prong_t_rad = 1.10
    
    # Radial position: 60% of hook depth
    r_supp_radial = hook_depth * 0.60
    
    for angle_deg in CLIP_ANGLES:
        rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        
        pos_center = n_dir * (r_wall + r_supp_radial)
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
        
        # 1. Wide bed adhesion foot (Z in [0, 0.40]mm, 1.80mm radial x 3.80mm tangential)
        foot = trimesh.creation.box([1.80, 3.80, 0.40])
        foot.apply_transform(rot)
        foot.apply_translation([pos_center[0], pos_center[1], 0.20])
        
        # 2. Lower solid shared trunk (Z in [0.40, 3.20]mm -> height 2.80mm)
        z_trunk_h = 2.80
        trunk = trimesh.creation.box([1.20, 3.40, z_trunk_h])
        trunk.apply_transform(rot)
        trunk.apply_translation([pos_center[0], pos_center[1], 0.40 + z_trunk_h / 2.0])
        
        # 3. Twin vertical prongs (Z in [3.20, 4.82]mm -> height 1.62mm)
        # Left prong at Y = -1.40, Right prong at Y = +1.40
        z_prong_h = support_top_z - 3.20  # 1.62mm
        prong_parts = []
        for yp in y_prongs:
            prong = trimesh.creation.box([prong_t_rad, prong_w_tang, z_prong_h])
            prong.apply_translation([0, yp, 0])
            prong.apply_transform(rot)
            prong.apply_translation([pos_center[0], pos_center[1], 3.20 + z_prong_h / 2.0])
            prong_parts.append(prong)
            
        # 4. Twin breakaway chisel contact tips (Z in [4.82, 4.94]mm -> height 0.12mm)
        # Each tip is 0.50mm radial x 0.90mm tangential x 0.12mm tall
        tip_parts = []
        for yp in y_prongs:
            tip = trimesh.creation.box([0.50, prong_w_tang, 0.12])
            tip.apply_translation([0, yp, 0])
            tip.apply_transform(rot)
            tip.apply_translation([pos_center[0], pos_center[1], support_top_z + 0.06])
            tip_parts.append(tip)
            
        supp_combined = trimesh.util.concatenate([foot, trunk] + prong_parts + tip_parts)
        support_meshes.append(supp_combined)
        
    return trimesh.util.concatenate(support_meshes)

supp_mesh = build_clip_supports_twin_prong(base_poly, hook_depth=2.49)
print(f"Twin-Prong Support mesh watertight: {supp_mesh.is_watertight}")
print(f"Twin-Prong Support volume: {supp_mesh.volume:.2f} mm³")
print(f"Twin-Prong Support bounds: Z = [{supp_mesh.bounds[0,2]:.2f}, {supp_mesh.bounds[1,2]:.2f}] mm")

# Plot 3D view of the support together with the clip hook
fig = plt.figure(figsize=(10, 8), dpi=180)
ax = fig.add_subplot(1, 1, 1, projection='3d')

p45, _, _ = find_boundary_point_and_normal(base_poly, 45.0)
dists = np.linalg.norm(supp_mesh.vertices[:, :2] - p45, axis=1)
mask = dists < 6.0
faces_mask = np.all(mask[supp_mesh.faces], axis=1)
sub_supp = trimesh.Trimesh(vertices=supp_mesh.vertices, faces=supp_mesh.faces[faces_mask])

# Draw support in green/teal
v = sub_supp.vertices
f = sub_supp.faces
col = Poly3DCollection(v[f], alpha=0.9, facecolor='#26a69a', edgecolor='#004d40', lw=0.4)
ax.add_collection3d(col)

ax.set_xlim(p45[0] - 3.5, p45[0] + 3.5)
ax.set_ylim(p45[1] - 3.5, p45[1] + 3.5)
ax.set_zlim(0, 5.5)
ax.set_xlabel("X (mm)", fontsize=9, fontweight='bold')
ax.set_ylabel("Y (mm)", fontsize=9, fontweight='bold')
ax.set_zlabel("Z (mm)", fontsize=9, fontweight='bold')
ax.set_title("Twin-Prong Breakaway Fork Support with Central Prying Arch\n(Total Contact Area = 2 x 0.45 = 0.90 mm²)", fontsize=11, fontweight='bold')
ax.view_init(elev=20, azim=40)

plt.tight_layout()
out_png = 'testing/twin_prong_support_3d.png'
plt.savefig(out_png, dpi=180)
print(f"Saved {out_png}")
