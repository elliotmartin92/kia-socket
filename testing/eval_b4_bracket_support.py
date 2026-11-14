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

print("Shaft hub lowest point in tilted:", "Y' = -1.351, Z' = 25.483")
print("Shaft axle center in tilted:", "Y' = -1.351, Z' = 27.583")

# What part of Bracket 4 is at X around 8.0 - 9.0?
# In flat coordinates:
# Bracket 4 has top rim (Z = 5.60 mm).
# At X in [8.00, 8.90]:
# Y is between 4.950 and 7.171.
# Specifically:
# The wall at Y = 7.171 has thickness: between Y=4.95 and 7.171 is a solid block of thickness 2.22 mm!
# Wait! Let's check:
# (8.000, 7.171) to (8.000, 4.950) is the inner face of the hook!
# (8.000, 4.950) to (8.900, 4.950) is the hook front face!
# (8.900, 4.950) to (8.900, 6.400) is the step!
# (8.900, 6.400) to (9.857, 6.400) is the pocket ceiling!
# (8.000, 7.171) to (10.791, 7.171) is the top outer wall!
# So for X in [8.000, 8.900], the solid wall is between Y = 4.950 and Y = 7.171!
# In flat coords: that's a 0.90mm wide (in X) by 2.22mm deep (in Y) pillar/wall of Bracket 4, 4.6mm tall (Z from 1.0 to 5.60)!

# Now let's transform points in this region to tilted coords:
cos45 = np.cos(np.radians(45.0))
sin45 = np.sin(np.radians(45.0))
for y in [4.950, 5.500, 6.000, 6.500, 7.171]:
    yp = y * cos45 - 5.60 * sin45
    zp = y * sin45 + 5.60 * cos45 - z_min
    print(f"Flat (Y={y:.3f}, Z=5.60) -> Tilted (Y'={yp:.3f}, Z'={zp:.3f})")

# Also, what about the top wall of Bracket 4 at Y = 7.171 for X in [8.0, 10.79]?
# Flat (Y=7.171, Z=5.60) -> Tilted (Y'=1.111, Z'=22.140)
# And the shaft hub underside is at Y' = -1.351, Z' = 25.483!
