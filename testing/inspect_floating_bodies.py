import trimesh
import numpy as np

# Load complete_assembly.stl
assembly = trimesh.load('complete_assembly.stl')
bodies = assembly.split(only_watertight=False)

print(f"Total bodies in complete_assembly.stl: {len(bodies)}")
print(f"Overall assembly bounds: Z in [{assembly.bounds[0,2]:.4f}, {assembly.bounds[1,2]:.4f}]")

floating_bodies = []
for i, b in enumerate(bodies):
    z_min = b.bounds[0, 2]
    z_max = b.bounds[1, 2]
    if z_min > 0.05:  # First layer is typically 0.20mm. If z_min > 0.05, it doesn't touch the bed!
        floating_bodies.append((i, z_min, z_max, b.bounds))
        print(f"Body {i:2d}: Z_min = {z_min:.4f}mm (FLOATING! Bounds: X=[{b.bounds[0,0]:.2f}, {b.bounds[1,0]:.2f}], Y=[{b.bounds[0,1]:.2f}, {b.bounds[1,1]:.2f}], Z=[{z_min:.2f}, {z_max:.2f}])")
    else:
        print(f"Body {i:2d}: Z_min = {z_min:.4f}mm (Touches bed)")

print(f"\nTotal floating bodies in complete_assembly.stl: {len(floating_bodies)}")
