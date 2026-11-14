import numpy as np
import trimesh
import os, sys
import matplotlib.pyplot as plt

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)
shaft_tilted = {}
for k, s in shaft_subparts.items():
    st = s.copy().apply_transform(R)
    st.apply_translation([0, 0, -z_min])
    shaft_tilted[k] = st

b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

print("Shaft subparts tilted bounds:")
for k, st in shaft_tilted.items():
    b = st.bounds
    print(f"  {k:10s}: X=[{b[0,0]:.2f}, {b[1,0]:.2f}], Y=[{b[0,1]:.2f}, {b[1,1]:.2f}], Z=[{b[0,2]:.2f}, {b[1,2]:.2f}]")

# Let's inspect what is above the top surface of Bracket 4:
# Bracket 4 top face: Z_flat = 5.60 mm.
# In flat coordinates:
# Points on Bracket 4 top face:
# From X = 8.000 to X = 10.791, Y is up to 7.171.
# What is above Bracket 4 at X = 8.0 to 10.8?
# Let's check:
# 1. At X in [8.00, 8.484]: Hub barrel!
#    Hub barrel cylinder is at Y_flat = 9.279, Z_flat = 11.190, radius 2.10 mm.
# 2. At X in [8.484, 10.791]: Plunger blade is at Y_flat in [7.18, 12.25]!
#    Wait! The plunger blade passes directly down into the through-hole!
#    Through-hole in flat coords: X in [7.608, 12.960], Y in [8.570, 13.750].
#    Where is the plunger blade in flat coords?
#    Plunger belly is at Y in [7.18, 12.25].
#    Bracket 4 top wall is at Y = 7.171!
#    The plunger blade belly is just 0.01 mm behind Bracket 4 top wall in flat coords!
#    In tilted coords, the plunger blade slopes down towards the bed pad!
#    And the plunger already has a dedicated support rising from the bed pad!

# Now, why did the user say:
# "It looks like it might be too small to print"
# Let's check the size of the strut we just generated:
# Width in X: 0.50 mm!
# Tine width: 0.18 mm!
# Notch opening: 0.13 mm!
# Neck: 0.50 x 0.50 mm!
# Trunk width in X: 0.48 mm!
