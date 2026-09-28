import trimesh

m = trimesh.load('part.stl')
bodies = m.split(only_watertight=False)
print(f"Total bodies in part.stl: {len(bodies)}")
for i, b in enumerate(bodies):
    z_min = b.bounds[0, 2]
    if z_min > 0.05:
        print(f"  Body {i}: Z_min = {z_min:.4f}mm (FLOATING)")
    else:
        print(f"  Body {i}: Z_min = {z_min:.4f}mm (Touches bed)")
