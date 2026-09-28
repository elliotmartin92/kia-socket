"""
testing/inspect_bed_profile.py
Inspect the 2D profiles of the shaft rocker at Z = 0.00, 0.20, 0.40, 0.60, 0.70, 0.80, 1.00 mm.
"""

import os, sys
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import build_shaft_rocker_mesh

shaft_print = build_shaft_rocker_mesh(in_assembly_coords=False)

z_levels = [0.05, 0.20, 0.40, 0.60, 0.70, 0.80, 1.00]

fig, axes = plt.subplots(1, len(z_levels), figsize=(24, 4), dpi=150)

for idx, z in enumerate(z_levels):
    ax = axes[idx]
    # Slice mesh at plane z
    slice_2d = shaft_print.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if slice_2d is not None:
        for line in slice_2d.discrete:
            ax.plot(line[:, 0], line[:, 1], color='#2980b9', linewidth=1.5)
    ax.set_title(f"Z = {z:.2f} mm", fontsize=10, fontweight='bold')
    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel('X (mm)')
    if idx == 0:
        ax.set_ylabel('Y (mm)')

plt.suptitle("Shaft Rocker Horizontal Slices at Low Z Heights (Print Orientation)", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('testing/shaft_slices_low_z.png', dpi=150)
print("Saved testing/shaft_slices_low_z.png successfully!")
