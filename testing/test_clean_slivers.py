import trimesh

m = trimesh.load('part.stl')
bodies = m.split(only_watertight=False)
valid_bodies = [b for b in bodies if len(b.faces) > 4 and abs(b.volume) > 0.001]
print(f"Original bodies: {len(bodies)}, Valid watertight bodies: {len(valid_bodies)}")

clean_part = trimesh.util.concatenate(valid_bodies)
print(f"Clean part is_watertight: {clean_part.is_watertight}")
