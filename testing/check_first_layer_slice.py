import trimesh
import numpy as np

# Load part.stl
m = trimesh.load('part.stl')

# Let's inspect slicing at Layer 1: Z = 0.10mm, Layer 2: Z = 0.30mm, etc.
for z in [0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70]:
    slice_2d = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if slice_2d is None:
        print(f"Slice at Z = {z:.2f}mm is NONE!")
    else:
        print(f"Slice at Z = {z:.2f}mm has {len(slice_2d.entities)} entities, total perimeter: {slice_2d.length:.2f}mm")
