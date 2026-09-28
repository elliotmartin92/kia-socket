"""
testing/test_cradle_slicing.py
Test horizontal cross-sections of supported rocker at each layer height.
"""

import os, sys
import numpy as np
import matplotlib.pyplot as plt
import trimesh
from shapely.geometry import box

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

def build_refined_shaft_support_frame(release_gap=0.12, bed_thickness=0.35):
    """
    Builds refined support frame with:
    - 0.20mm perimeter clearance around the hub barrel so it never welds to the hub
    - Saddles reaching Z = 0.70 - release_gap under the pins
    - Optional micro-breakaway anchor tabs linking frame to the hub end-rims
    """
    # Hub bounds: X in [-3.75, 3.75], Y in [-1.00, 3.19]
    # At Z <= 0.35, hub Y span is approx [-0.30, 2.50]
    
    # Outer frame: X in [-6.20, 6.20], Y in [-2.60, 3.80]
    outer_box = box(-6.20, -2.60, 6.20, 3.80)
    # Inner window with 0.15mm clearance from hub:
    # Hub X is [-3.75, 3.75], so window X is [-3.90, 3.90]
    # Hub Y at Z <= 0.35 is [-0.30, 2.50], so window Y is [-0.80, 2.80]
    inner_window = box(-3.85, -0.80, 3.85, 2.80)
    frame_poly = outer_box.difference(inner_window)
    
    frame_mesh = trimesh.creation.extrude_polygon(frame_poly, height=bed_thickness)
    
    # Saddles under pins
    z_saddle_top = 0.70 - release_gap
    h_saddle = z_saddle_top - bed_thickness
    
    saddle_l = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_l.apply_translation([-4.75, 1.05, bed_thickness + h_saddle / 2.0])
    
    saddle_r = trimesh.creation.box([1.70, 0.90, h_saddle])
    saddle_r.apply_translation([4.75, 1.05, bed_thickness + h_saddle / 2.0])
    
    # Micro-breakaway anchor tabs at X = +/- 3.85mm
    # A tiny bridge (0.30mm wide in X x 0.50mm in Y x 0.20mm in Z) connecting frame to hub shoulder
    tab_l = trimesh.creation.box([0.30, 0.50, 0.20])
    tab_l.apply_translation([-3.75, 1.05, 0.10])
    
    tab_r = trimesh.creation.box([0.30, 0.50, 0.20])
    tab_r.apply_translation([3.75, 1.05, 0.10])
    
    support_mesh = trimesh.util.concatenate([frame_mesh, saddle_l, saddle_r, tab_l, tab_r])
    return support_mesh

shaft_rocker = build_shaft_rocker_mesh(in_assembly_coords=False)
support_frame = build_refined_shaft_support_frame(release_gap=0.12, bed_thickness=0.35)
combined = trimesh.util.concatenate([shaft_rocker, support_frame])

print("Combined mesh watertight:", combined.is_watertight)
print("Combined mesh volume:", combined.volume)

# Plot layer slices at 0.10, 0.25, 0.45, 0.55, 0.65, 0.75, 0.85
z_slices = [0.10, 0.25, 0.45, 0.55, 0.65, 0.75, 0.85]
fig, axes = plt.subplots(1, len(z_slices), figsize=(26, 4), dpi=150)

for idx, z in enumerate(z_slices):
    ax = axes[idx]
    # Slice rocker
    s_r = shaft_rocker.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s_r is not None:
        for line in s_r.discrete:
            ax.plot(line[:, 0], line[:, 1], color='#e67e22', linewidth=2.0, label='Rocker' if idx==0 else "")
            
    # Slice support frame
    s_f = support_frame.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s_f is not None:
        for line in s_f.discrete:
            ax.plot(line[:, 0], line[:, 1], color='#00a8ff', linewidth=1.5, label='Support' if idx==0 else "")
            
    ax.set_title(f"Z = {z:.2f} mm", fontsize=11, fontweight='bold')
    ax.set_xlim(-7, 7)
    ax.set_ylim(-4, 5)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    if idx == 0:
        ax.set_ylabel('Y (mm)')
        ax.legend(loc='upper right', fontsize=8)

plt.suptitle("Layer-by-Layer Slicing of Rocker with Built-In Support Frame\nOrange = Rocker | Cyan = Sacrificial Support Frame",
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('testing/cradle_layer_slices.png', dpi=150)
print("Saved testing/cradle_layer_slices.png successfully!")
