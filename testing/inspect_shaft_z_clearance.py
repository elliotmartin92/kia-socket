import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np
from build_shaft import build_shaft_rocker_mesh

shaft = build_shaft_rocker_mesh(in_assembly_coords=True)

# Check max Z of shaft at various Y ranges
# Front tie beam is at Y in [4.17, 6.37], X in [5.20, 13.30]
front_mask = (shaft.vertices[:, 1] >= 4.10) & (shaft.vertices[:, 1] <= 6.45) & (shaft.vertices[:, 0] >= 5.0) & (shaft.vertices[:, 0] <= 13.5)
if np.any(front_mask):
    max_z_front = shaft.vertices[front_mask, 2].max()
    print(f"Max Z of shaft under front tie beam (Y in [4.17, 6.37]): {max_z_front:.3f} mm")
else:
    print("Shaft does not have vertices directly under front tie beam!")

# Hub barrel
hub_mask = (shaft.vertices[:, 0] >= 5.5) & (shaft.vertices[:, 0] <= 13.0)
print(f"Overall max Z of shaft between towers (X in [5.5, 13.0]): {shaft.vertices[hub_mask, 2].max():.3f} mm")
print(f"Max Z of entire shaft: {shaft.vertices[:, 2].max():.3f} mm")
