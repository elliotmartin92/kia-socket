import sys, os
sys.path.insert(0, os.path.abspath('.'))
from build_shaft import build_shaft_rocker_mesh
import trimesh

shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
print("Is shaft_assembled watertight?", shaft_assembled.is_watertight)
print("Shaft volume:", shaft_assembled.volume)

# Let's split shaft_assembled into bodies
bodies = shaft_assembled.split(only_watertight=False)
print(f"Number of bodies in shaft_assembled: {len(bodies)}")
for i, b in enumerate(bodies):
    print(f"  Body {i}: volume = {b.volume:.2f}, bounds = {b.bounds.tolist()}")
