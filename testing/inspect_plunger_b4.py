import numpy as np
import trimesh
import os, sys

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

# Let's inspect the tilted coordinates of the shaft hub across its X span:
# Hub has radius 2.10.
# Axle in flat is Y=9.279, Z=11.190.
# In tilted: Y' = -1.351, Z' = 27.583.
# Lowest point of hub barrel (underside in Z'):
# Y' = -1.351, Z' = 25.483.
# This lowest ridge of the hub cylinder runs along X from X = 5.80 to 12.70!
# Along this line:
# For X in [5.80, 7.70]: Cam tab merges into the hub.
# For X in [5.90, 6.90]: Left flank rib merges into the hub.
# For X in [8.484, 12.084]: Plunger blade merges into the hub.
# For X in [11.60, 12.60]: Right flank rib merges into the hub.
# What about between Cam and Plunger?
# Between X = 7.70 (right edge of cam tab) and X = 8.484 (left edge of plunger blade):
# That is an open span of hub barrel:
# X in [7.70, 8.484] -> 0.784 mm wide clear hub barrel!
# That's where the old stick was trying to hit (at X = 8.16, width 0.48, in [7.92, 8.40])!
# BUT WAIT!
# What about the hub barrel to the right of the plunger blade? Or in front of / behind the plunger?
# Wait! Where does the plunger go in Y' and Z'?
# Let's check where the plunger is located in Y' and Z'!
print("Plunger bounds in tilted:")
pb = shaft_tilted['plunger'].bounds
print(f"X in [{pb[0,0]:.3f}, {pb[1,0]:.3f}]")
print(f"Y in [{pb[0,1]:.3f}, {pb[1,1]:.3f}]")
print(f"Z in [{pb[0,2]:.3f}, {pb[1,2]:.3f}]")

# Let's check plunger cross section at X = 9.0, 9.5, 10.0, etc.
# In flat coords:
# Plunger belly in Y is at Y in [7.18, 12.25], Z in [-6.50, 13.24].
# When tilted 45 degrees:
# Flat +Y is up and right, flat +Z is up and left.
# Tilted Z' = Y*sin(45) + Z*cos(45) - z_min.
# Tilted Y' = Y*cos(45) - Z*sin(45).
# The plunger blade extends DOWN into the through-hole (towards negative flat Z)!
# At Z = -6.50 (the tip), in flat coords, Y = 10.48.
# Tilted:
# Y' = 10.48*cos(45) - (-6.50)*sin(45) = 7.41 + 4.60 = 12.01 mm!
# Z' = 10.48*sin(45) + (-6.50)*cos(45) - z_min = 7.41 - 4.60 - (-12.82) = 15.63 mm!
# Notice: the plunger tip is at Y' = +12.01 mm, Z' = 15.63 mm!
# And the plunger support strut comes from the bed pad at Y' = +11.30 mm, rising up to Z' = 15.35 mm!

# Now look at where Bracket 4 is:
# Bracket 4 is at flat Y in [-7.136, 7.171]!
# Flat Y is NEGATIVE or SMALL POSITIVE (up to 7.171).
# Tilted Y' for Bracket 4:
# At flat Y = 7.171, Z = 5.60:
# Y' = 7.171*cos(45) - 5.60*sin(45) = +1.111 mm!
# Z' = 7.171*sin(45) + 5.60*cos(45) - z_min = 22.140 mm!
# Notice that at Bracket 4's top: Y' = +1.111 mm!
# And where is the shaft hub?
# Shaft hub underside: Y' = -1.351 mm, Z' = 25.483 mm!
# Look at the distance from Bracket 4 top (Y' = 1.111, Z' = 22.140) to shaft hub underside (Y' = -1.351, Z' = 25.483):
# Delta Y' = -1.351 - 1.111 = -2.462 mm!
# Delta Z' = 25.483 - 22.140 = +3.343 mm!
