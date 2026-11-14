import sys, os
sys.path.insert(0, os.path.abspath('.'))
from build_shaft import build_shaft_rocker_mesh

subparts = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False, return_subparts=True)
for k, v in subparts.items():
    print(f"{k}: bounds X = [{v.bounds[0, 0]:.3f}, {v.bounds[1, 0]:.3f}], Y = [{v.bounds[0, 1]:.3f}, {v.bounds[1, 1]:.3f}], Z = [{v.bounds[0, 2]:.3f}, {v.bounds[1, 2]:.3f}], vol = {v.volume:.2f}")
