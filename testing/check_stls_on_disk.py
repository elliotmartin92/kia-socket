import trimesh
import numpy as np

for fname in ['tower_clamp.stl', 'tower_clamp_bridge.stl', 'tower_clamp_right.stl', 'tower_clamp_left.stl']:
    m = trimesh.load(fname)
    print(f"{fname}: bounds={m.bounds.tolist()}, volume={m.volume:.2f}, watertight={m.is_watertight}")
