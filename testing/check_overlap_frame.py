"""
testing/check_overlap_frame.py
Check exact intersection between shaft_rocker and support_frame.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from testing.model_shaft_support_frame import build_shaft_support_frame_mesh
from build_shaft import build_shaft_rocker_mesh

shaft_rocker = build_shaft_rocker_mesh(in_assembly_coords=False)
support_frame = build_shaft_support_frame_mesh()

# Check boolean intersection between rocker and support frame
try:
    inter = shaft_rocker.intersection(support_frame, engine='manifold')
    print("Intersection volume:", inter.volume)
    if inter.volume > 0.001:
        print("Overlap bounds:")
        print("  X:", inter.bounds[0, 0], inter.bounds[1, 0])
        print("  Y:", inter.bounds[0, 1], inter.bounds[1, 1])
        print("  Z:", inter.bounds[0, 2], inter.bounds[1, 2])
    else:
        print("ZERO OVERLAP! 100% separate bodies with air gap everywhere!")
except Exception as e:
    print("Intersection check error:", e)
