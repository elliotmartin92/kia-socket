import trimesh

assembly = trimesh.load('complete_assembly.stl')
bodies = assembly.split(only_watertight=False)
print("Before filtering:", len(bodies))

real_objects = []
for i, b in enumerate(bodies):
    vol = abs(b.volume)
    print(f"Body {i}: volume = {vol:.6f}, bounds Z: [{b.bounds[0,2]:.4f}, {b.bounds[1,2]:.4f}]")
    if vol > 0.05:  # Only keep real 3D solid volumes
        real_objects.append(b)

print(f"\nAfter filtering: {len(real_objects)} real objects!")
for i, b in enumerate(real_objects):
    print(f"Real Object {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, volume = {abs(b.volume):.2f}mm^3")
