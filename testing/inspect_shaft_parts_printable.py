"""
testing/inspect_shaft_parts_printable.py
Inspect subcomponents and their overhangs in printable orientation.
"""

import sys, os
import trimesh
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)

print("=" * 90)
print(f"{'PART NAME':<12} | {'X SPAN':<18} | {'Y SPAN':<18} | {'Z SPAN':<18} | {'OH FACES (>45°)':<15}")
print("=" * 90)

for name, m in parts.items():
    b = m.bounds
    x_str = f"[{b[0,0]:.2f}, {b[1,0]:.2f}]"
    y_str = f"[{b[0,1]:.2f}, {b[1,1]:.2f}]"
    z_str = f"[{b[0,2]:.2f}, {b[1,2]:.2f}]"
    
    c = m.triangles_center
    n = m.face_normals
    a = m.area_faces
    
    # Overhangs > 45° from vertical: n_z < -0.707
    mask_oh45 = (n[:, 2] < -0.707)
    # Steep downward: n_z < -0.5 (overhang angle > 30° from vertical, i.e. 60° overhang)
    mask_oh60 = (n[:, 2] < -0.5)
    
    oh45_cnt = np.sum(mask_oh45)
    oh45_area = np.sum(a[mask_oh45])
    
    print(f"{name:<12} | {x_str:<18} | {y_str:<18} | {z_str:<18} | {oh45_cnt:<4} ({oh45_area:.2f} mm²)")
    
    # For any part with faces having Z > 1.0 and n_z < -0.2:
    mask_high_oh = (c[:, 2] > 1.0) & (n[:, 2] < -0.3)
    if np.any(mask_high_oh):
        c_h = c[mask_high_oh]
        n_h = n[mask_high_oh]
        a_h = a[mask_high_oh]
        print(f"    -> High downward faces (Z > 1.0mm, n_z < -0.3): count={np.sum(mask_high_oh)}, area={np.sum(a_h):.2f} mm²")
        print(f"       Z span of faces: [{c_h[:,2].min():.2f}, {c_h[:,2].max():.2f}] mm")
        print(f"       Y span of faces: [{c_h[:,1].min():.2f}, {c_h[:,1].max():.2f}] mm")
        print(f"       X span of faces: [{c_h[:,0].min():.2f}, {c_h[:,0].max():.2f}] mm")
        print(f"       Min n_z: {n_h[:,2].min():.3f} (most horizontal downward)")

print("=" * 90)
