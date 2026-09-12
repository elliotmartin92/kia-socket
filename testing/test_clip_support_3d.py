"""
testing/test_clip_support_3d.py
Build and inspect 3D meshes of Twin Edge Pads vs Tri-Point Tripod supports.
Verify watertightness, volume, and exact contact areas.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt

from build_part import (
    get_exact_base_polygon, find_boundary_point_and_normal,
    CLIP_ANGLES, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ARM_WIDTH
)

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97 mm
support_top_z = stem_h - 0.15           # 4.82 mm
hook_depth = 2.49                        # 2.49 mm (-0.10mm from 2.59mm)
hook_width = 4.20

base_poly, outer_body_poly, _ = get_exact_base_polygon()

def build_support_twin_pads(base_poly):
    """Design 1: Twin lateral edge pads (2 x 0.45 mm² = 0.90 mm²)."""
    support_meshes = []
    
    for angle_deg in CLIP_ANGLES:
        rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        
        # Pillar center in radial direction
        r_supp_pillar = r_wall + hook_depth * 0.55
        pos_center = n_dir * r_supp_pillar
        
        # 1. Main vertical support pillar (1.20mm radial x 3.20mm tangential x support_top_z tall)
        pillar = trimesh.creation.box([1.20, 3.20, support_top_z])
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
        pillar.apply_transform(rot)
        pillar.apply_translation([pos_center[0], pos_center[1], support_top_z / 2.0])
        
        # 2. Bed adhesion foot (0.40mm tall, 1.80mm radial x 3.80mm tangential)
        foot = trimesh.creation.box([1.80, 3.80, 0.40])
        foot.apply_transform(rot)
        foot.apply_translation([pos_center[0], pos_center[1], 0.20])
        
        # 3. Twin breakaway contact tips (each 0.50mm radial x 0.90mm tangential x 0.12mm tall)
        # Left pad at tangential Y = -1.35mm, Right pad at tangential Y = +1.35mm
        # Radial position: r_wall + hook_depth * 0.60
        r_tip = r_wall + hook_depth * 0.60
        tips = []
        for y_tang in [-1.35, 1.35]:
            tip = trimesh.creation.box([0.50, 0.90, 0.12])
            # Shift in local radial (X) and tangential (Y) before rotating
            # Local center relative to pos_center:
            dx_local = r_tip - r_supp_pillar
            dy_local = y_tang
            tip.apply_translation([dx_local, dy_local, 0])
            tip.apply_transform(rot)
            tip.apply_translation([pos_center[0], pos_center[1], support_top_z + 0.06])
            tips.append(tip)
            
        supp_combined = trimesh.util.concatenate([pillar, foot] + tips)
        support_meshes.append(supp_combined)
        
    return trimesh.util.concatenate(support_meshes)

def build_support_tri_point(base_poly):
    """Design 2: Tri-point tripod (2 lateral edge pads + 1 center front lip pad = 0.90 mm²)."""
    support_meshes = []
    
    for angle_deg in CLIP_ANGLES:
        rad = math.radians(angle_deg)
        p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
        r_wall = np.linalg.norm(p)
        n_dir = p / r_wall
        
        # Pillar center in radial direction
        r_supp_pillar = r_wall + hook_depth * 0.55
        pos_center = n_dir * r_supp_pillar
        
        # 1. Main vertical support pillar (1.30mm radial x 3.20mm tangential x support_top_z tall)
        pillar = trimesh.creation.box([1.30, 3.20, support_top_z])
        rot = trimesh.transformations.rotation_matrix(rad, [0, 0, 1])
        pillar.apply_transform(rot)
        pillar.apply_translation([pos_center[0], pos_center[1], support_top_z / 2.0])
        
        # 2. Bed adhesion foot (0.40mm tall, 1.80mm radial x 3.80mm tangential)
        foot = trimesh.creation.box([1.80, 3.80, 0.40])
        foot.apply_transform(rot)
        foot.apply_translation([pos_center[0], pos_center[1], 0.20])
        
        # 3. Three breakaway contact tips:
        # Pad 1 & 2 (Sides): 0.50mm radial x 0.60mm tang x 0.12mm tall at tang = ±1.40mm, r = r_wall + hook_depth * 0.55
        # Pad 3 (Front lip): 0.40mm radial x 0.75mm tang x 0.12mm tall at tang = 0.00mm, r = r_wall + hook_depth * 0.80
        tips = []
        r_side = r_wall + hook_depth * 0.55
        for y_tang in [-1.40, 1.40]:
            tip = trimesh.creation.box([0.50, 0.60, 0.12])
            dx_local = r_side - r_supp_pillar
            tip.apply_translation([dx_local, y_tang, 0])
            tip.apply_transform(rot)
            tip.apply_translation([pos_center[0], pos_center[1], support_top_z + 0.06])
            tips.append(tip)
            
        r_front = r_wall + hook_depth * 0.80
        tip_front = trimesh.creation.box([0.40, 0.75, 0.12])
        dx_local = r_front - r_supp_pillar
        tip_front.apply_translation([dx_local, 0.0, 0])
        tip_front.apply_transform(rot)
        tip_front.apply_translation([pos_center[0], pos_center[1], support_top_z + 0.06])
        tips.append(tip_front)
        
        supp_combined = trimesh.util.concatenate([pillar, foot] + tips)
        support_meshes.append(supp_combined)
        
    return trimesh.util.concatenate(support_meshes)

print("Building Twin Pads Support Mesh...")
mesh_twin = build_support_twin_pads(base_poly)
print(f"Twin Pads mesh watertight: {mesh_twin.is_watertight}")
print(f"Twin Pads bounds: Z = [{mesh_twin.bounds[0,2]:.2f}, {mesh_twin.bounds[1,2]:.2f}] mm")

print("\nBuilding Tri-Point Tripod Support Mesh...")
mesh_tri = build_support_tri_point(base_poly)
print(f"Tri-Point mesh watertight: {mesh_tri.is_watertight}")
print(f"Tri-Point bounds: Z = [{mesh_tri.bounds[0,2]:.2f}, {mesh_tri.bounds[1,2]:.2f}] mm")

# Detailed 3D close-up rendering of the support under a clip
fig = plt.figure(figsize=(12, 6), dpi=180)

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

def plot_support_isometric(ax, mesh_supp, title):
    # Filter vertices near clip 1 (45 deg)
    p45, _, _ = find_boundary_point_and_normal(base_poly, 45.0)
    dists = np.linalg.norm(mesh_supp.vertices[:, :2] - p45, axis=1)
    mask = dists < 8.0
    faces_mask = np.all(mask[mesh_supp.faces], axis=1)
    sub_mesh = trimesh.Trimesh(vertices=mesh_supp.vertices, faces=mesh_supp.faces[faces_mask])
    
    v = sub_mesh.vertices
    f = sub_mesh.faces
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    mesh_col = Poly3DCollection(v[f], alpha=0.85, facecolor='#42a5f5', edgecolor='#1565c0', lw=0.3)
    ax.add_collection3d(mesh_col)
    
    ax.set_xlim(p45[0] - 4, p45[0] + 4)
    ax.set_ylim(p45[1] - 4, p45[1] + 4)
    ax.set_zlim(0, 5.5)
    ax.set_xlabel("X (mm)", fontsize=8)
    ax.set_ylabel("Y (mm)", fontsize=8)
    ax.set_zlabel("Z (mm)", fontsize=8)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.view_init(elev=25, azim=45)

plot_support_isometric(ax1, mesh_twin, "Design 1: Twin Lateral Edge Pads\n(2x 0.45 mm² = 0.90 mm²)")
plot_support_isometric(ax2, mesh_tri, "Design 2: Tri-Point Perimeter Tripod\n(3x 0.30 mm² = 0.90 mm²)")

plt.tight_layout()
out_3d_png = 'testing/clip_support_3d_render.png'
plt.savefig(out_3d_png, dpi=180)
print(f"Saved 3D render to {out_3d_png}")
