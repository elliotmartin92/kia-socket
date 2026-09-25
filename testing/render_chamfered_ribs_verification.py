"""
testing/render_chamfered_ribs_verification.py
Renders a closeup 3D view of the new chamfered seating ribs and continuous Rib 4 bridge.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import build_part as bp

full_part, _ = bp.build_exact_3d_model()

# Crop tightly around bracket 3 & 4 seating ribs: X in [1.5, 11.0], Y in [-7.5, 7.5], Z in [0.5, 6.0]
crop_box = trimesh.creation.box([10.0, 15.0, 5.5])
crop_box.apply_translation([6.25, 0.0, 3.25])

cropped = full_part.intersection(crop_box, engine='manifold')

fig = plt.figure(figsize=(10, 8), dpi=180)
ax = fig.add_subplot(1, 1, 1, projection='3d')
ax.plot_trisurf(cropped.vertices[:, 0], cropped.vertices[:, 1], cropped.vertices[:, 2],
                triangles=cropped.faces, color='#42a5f5', alpha=0.9, edgecolor='none')
ax.view_init(elev=45, azim=-55)
ax.set_title("3D Closeup: 45° Chamfered Seating Ribs & Continuous Rib 4 Foundation", fontsize=11, fontweight='bold')
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_zlabel("Z (mm)")

plt.tight_layout()
plt.savefig('testing/chamfered_ribs_closeup.png')
print("Saved testing/chamfered_ribs_closeup.png")
