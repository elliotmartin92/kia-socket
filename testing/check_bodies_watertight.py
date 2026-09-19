import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh

m = trimesh.load('part.stl')
bodies = m.split(only_watertight=False)
print(f"Total separate bodies in part.stl: {len(bodies)}")
for i, b in enumerate(bodies):
    print(f"  Body {i}: Watertight={b.is_watertight}, Vol={b.volume if b.is_watertight else 0:.2f} mm³, Vertices={len(b.vertices)}, Faces={len(b.faces)}")
