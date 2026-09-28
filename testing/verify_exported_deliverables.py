import trimesh

print("=" * 60)
print("VERIFYING EXPORTED STL FILES ON DISK")
print("=" * 60)

# 1. part.stl
part = trimesh.load('part.stl')
part_bodies = part.split(only_watertight=False)
print(f"\n[1] part.stl:")
print(f"    Total bodies: {len(part_bodies)}")
print(f"    Watertight: {part.is_watertight}")
print(f"    Overall bounds Z: [{part.bounds[0,2]:.4f}, {part.bounds[1,2]:.4f}]")
for i, b in enumerate(part_bodies):
    print(f"    Body {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, watertight = {b.is_watertight}")

# 2. shaft_rocker.stl
shaft = trimesh.load('shaft_rocker.stl')
shaft_bodies = shaft.split(only_watertight=False)
print(f"\n[2] shaft_rocker.stl:")
print(f"    Total bodies: {len(shaft_bodies)}")
print(f"    Watertight: {shaft.is_watertight}")
print(f"    Overall bounds Z: [{shaft.bounds[0,2]:.4f}, {shaft.bounds[1,2]:.4f}]")
for i, b in enumerate(shaft_bodies):
    print(f"    Body {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, watertight = {b.is_watertight}")

# 3. cooling_tower.stl
tower = trimesh.load('cooling_tower.stl')
print(f"\n[3] cooling_tower.stl:")
print(f"    Watertight: {tower.is_watertight}")
print(f"    Overall bounds Z: [{tower.bounds[0,2]:.4f}, {tower.bounds[1,2]:.4f}]")

# 4. complete_assembly.stl
assembly = trimesh.load('complete_assembly.stl')
assembly_bodies = assembly.split(only_watertight=False)
print(f"\n[4] complete_assembly.stl:")
print(f"    Total bodies: {len(assembly_bodies)}")
print(f"    Overall bounds Z: [{assembly.bounds[0,2]:.4f}, {assembly.bounds[1,2]:.4f}]")
for i, b in enumerate(assembly_bodies):
    print(f"    Object {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, watertight = {b.is_watertight}")
