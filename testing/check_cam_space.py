import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import build_part

part_mesh_flat, base_poly = build_part.build_exact_3d_model()
y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

# Let's test various cam profiles with thicker necks:
# Specifically, let's see how much space we have above the cam arm at Y in [5.0, 9.279]
# We can do this by checking distance to part_mesh_flat!
print("Testing clearance to baseplate mesh...")

# In assembly coords, baseplate floor is at Z=1.0.
# Guide brackets: Z up to 5.60.
# Towers: Z up to 14.19. Left tower at X in [3.90, 5.40], Right tower at X in [13.10, 14.60].
# Rear cross-tie bridge: X in [3.90, 14.60], Y in [11.75, 12.85], Z in [11.19, 13.36].
# Cam is at X in [5.80, 7.70], Y in [1.5, 9.279].
# Notice: Cam is at Y <= 9.279, while rear cross-tie bridge is at Y >= 11.75!
# So cam is completely in front of the cross-tie bridge!

# What about the plug blade?
# Blade enters vertically at X = 6.28, Y from ~ 1.5 to 5.5, Z from 20 down to ~ 3.0.
# The blade pushes down on the cam ramp!
