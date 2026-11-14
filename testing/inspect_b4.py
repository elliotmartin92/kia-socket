import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

# Inspect Bracket 4
brackets = build_part.create_all_brackets_poly()
# Let's find which polygon is Bracket 4
for i, geom in enumerate(brackets.geoms):
    print(f"Bracket {i} bounds: {geom.bounds}, center: {geom.centroid.coords[0]}")
