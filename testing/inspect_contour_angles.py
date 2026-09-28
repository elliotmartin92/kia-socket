"""
testing/inspect_contour_angles.py
Analyze the 2D boundary contour of the plunger and cam in printable orientation.
Find every segment whose angle with the horizontal build plate is < 45° (overhang > 45°),
and where cantilevered sections start in mid-air.
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

parts = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=False, return_subparts=True)
plunger = parts['plunger']
cam = parts['cam']
web = parts['web']

# Let's inspect the mesh slices along Y-Z for plunger
# The plunger has X span around [-1.17, 3.23].
# In printable coords, let's take a slice at X = (plunger.bounds[0,0] + plunger.bounds[1,0])/2
x_mid = (plunger.bounds[0,0] + plunger.bounds[1,0])/2

# Find vertices and edges in Y-Z
fig, ax = plt.subplots(figsize=(10, 10))

for name, p, color in [('hub', parts['hub'], 'gray'), ('cam', cam, 'orange'), ('plunger', plunger, 'blue'), ('web', web, 'green')]:
    c = p.triangles_center
    n = p.face_normals
    # Project all vertices on Y-Z
    ax.scatter(p.vertices[:, 1], p.vertices[:, 2], s=2, c=color, label=name, alpha=0.5)
    
    # Highlight faces with n_z < -0.5 (overhangs > 45° from vertical)
    steep = (n[:, 2] < -0.5)
    if np.any(steep):
        ax.scatter(c[steep, 1], c[steep, 2], s=20, c='red', marker='x')

ax.set_xlabel('Y (mm)')
ax.set_ylabel('Z (mm)')
ax.set_title('Shaft Rocker in Printable Orientation (Red = Downward overhangs > 45°)')
ax.grid(True)
ax.axis('equal')
ax.legend()
plt.savefig('testing/shaft_printable_slices_colored.png', dpi=150)
print("Saved testing/shaft_printable_slices_colored.png")
