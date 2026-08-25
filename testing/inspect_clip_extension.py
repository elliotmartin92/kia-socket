"""
testing/inspect_clip_extension.py
Inspect the snap clip hook geometry when extended outward by 1.00mm (from 1.59mm to 2.59mm).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt

from build_part import (
    build_exact_3d_model, get_exact_base_polygon,
    CLIP_HOOK_DEPTH, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ANGLES,
    find_boundary_point_and_normal
)

print(f"Current CLIP_HOOK_DEPTH in code: {CLIP_HOOK_DEPTH:.2f} mm")
target_hook_depth = 2.59  # 1.59mm + 1.00mm

base_poly, outer_body_poly, _ = get_exact_base_polygon()

for angle_deg in CLIP_ANGLES:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_wall = np.linalg.norm(p)
    r_old = r_wall + 1.59
    r_new = r_wall + target_hook_depth
    print(f"Clip at {angle_deg:5.1f}°: Wall R = {r_wall:.2f} mm -> Old Hook R = {r_old:.2f} mm -> New Hook R = {r_new:.2f} mm (+1.00mm extension)")

# Test generation of 3D part with updated clip depth
import build_part
build_part.CLIP_HOOK_DEPTH = 2.59

mesh_part, poly = build_part.build_exact_3d_model()
print(f"\nPart with 2.59mm clips generated successfully!")
print(f"Bounds: X: [{mesh_part.bounds[0,0]:.2f}, {mesh_part.bounds[1,0]:.2f}], Y: [{mesh_part.bounds[0,1]:.2f}, {mesh_part.bounds[1,1]:.2f}], Z: [{mesh_part.bounds[0,2]:.2f}, {mesh_part.bounds[1,2]:.2f}]")

# Plot clip comparison
fig, ax = plt.subplots(figsize=(10, 8), dpi=180)

# Plot base perimeter
x, y = outer_body_poly.exterior.xy
ax.plot(x, y, color='#1565c0', lw=2, label='Outer Perimeter Wall')

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm

for angle_deg in CLIP_ANGLES:
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_wall = np.linalg.norm(p)
    n_dir = p / r_wall
    
    p_old = p + n_dir * 1.59
    p_new = p + n_dir * 2.59
    
    ax.plot([p[0], p_new[0]], [p[1], p_new[1]], 'r-', lw=2.5)
    ax.plot(p_old[0], p_old[1], 'go', markersize=6, label='Old 1.59mm Hook' if angle_deg == 45.0 else "")
    ax.plot(p_new[0], p_new[1], 'ro', markersize=7, label='New 2.59mm Extended Hook (+1mm)' if angle_deg == 45.0 else "")
    
    ax.annotate(f"{angle_deg}° Clip\n(+1.00mm)", xy=(p_new[0], p_new[1]), xytext=(p_new[0]*1.15, p_new[1]*1.15),
                arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=1.2),
                fontsize=8.5, fontweight='bold', color='#b71c1c')

ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title("Perimeter Snap Clips: +1.00mm Radial Extension (2.59mm Hook Depth)", fontsize=12, fontweight='bold')
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.legend(loc='lower left', fontsize=9)

plt.tight_layout()
plt.savefig('testing/clip_extension_preview.png', dpi=180)
print("Saved testing/clip_extension_preview.png")
