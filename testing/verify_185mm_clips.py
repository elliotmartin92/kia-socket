"""
Verify 1.85mm clip hook dimensions on the flat un-tilted part geometry and exports.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh

import build_part

part_flat, base_poly = build_part.build_exact_3d_model()
print(f"Flat Part Volume: {part_flat.volume:.2f} mm³")

# Slices at stem level (Z = 3.50mm) and hook level (Z = 5.20mm)
sec_stem = part_flat.section(plane_origin=[0, 0, 3.50], plane_normal=[0, 0, 1])
sec_hook = part_flat.section(plane_origin=[0, 0, 5.20], plane_normal=[0, 0, 1])

stem_pts = sec_stem.vertices[:, :2]
hook_pts = sec_hook.vertices[:, :2]

for ang in build_part.CLIP_ANGLES:
    rad = np.radians(ang)
    ray = np.array([np.cos(rad), np.sin(rad)])
    
    # Perp distance in 2D
    perp_stem = np.abs(ray[0] * stem_pts[:, 1] - ray[1] * stem_pts[:, 0])
    r_stem = np.max(np.dot(stem_pts[perp_stem < 0.3], ray))
    
    perp_hook = np.abs(ray[0] * hook_pts[:, 1] - ray[1] * hook_pts[:, 0])
    r_hook_center = np.max(np.dot(hook_pts[perp_hook < 0.3], ray))
    
    # Near edge (tangential offset ~1.8mm)
    edge_mask = (perp_hook > 1.6) & (perp_hook < 2.0)
    r_hook_edge = np.max(np.dot(hook_pts[edge_mask], ray)) if np.any(edge_mask) else 0
    
    overhang_center = r_hook_center - r_stem
    overhang_edge = r_hook_edge - r_stem if r_hook_edge > 0 else 0
    
    print(f"Clip {ang:5.1f}°:")
    print(f"  Center Overhang: {overhang_center:.2f} mm (Target: 1.85 mm)")
    print(f"  Edge Overhang:   {overhang_edge:.2f} mm (Target: ~1.65 mm)")
    print(f"  Crown Relief:    {overhang_center - overhang_edge:.2f} mm (Target: 0.20 mm)")

print("\nVerification complete!")
