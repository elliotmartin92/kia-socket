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

b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

print("Bracket 4 flat bounds:", b4_flat.bounds)
print("Bracket 4 tilted bounds:", b4_tilted.bounds)

# Let's inspect the entire Bracket 4:
# In flat coords:
# Bracket 4 spans X from 8.000 to 10.791!
# Bracket 4 has:
# 1) Top wall at Y = 7.171: X from 8.000 to 10.791! (2.791 mm wide in X!)
# 2) Hook front at Y = 4.950: X from 8.000 to 8.900! (0.900 mm wide in X!)
# 3) Step at X = 8.900: Y from 4.950 to 6.400!
# 4) Pocket ceiling at Y = 6.400: X from 8.900 to 9.857! (0.957 mm wide in X!)
# 5) Outer spine wall at X = 9.857 to 10.791: Y from -7.136 to +7.171! (0.934 mm wide in X, 14.3 mm long in Y!)

# Now look at the shaft:
# Shaft Axle: Y_axle = 9.279, Z_axle = 11.190 (flat).
# Tilted: Y' = -1.351, Z' = 27.583.
# Where is Bracket 4 relative to the shaft axle?
# In flat coords:
# Shaft axle is at Y = 9.279.
# Bracket 4 top wall is at Y = 7.171.
# The distance from Bracket 4 top wall (Y=7.171) to shaft axle (Y=9.279) is only 2.108 mm in Y!
# In tilted coords:
# Bracket 4 top wall (Y=7.171, Z=5.60) is at Y' = 1.111, Z' = 22.140.
# Shaft axle is at Y' = -1.351, Z' = 27.583.
# Shaft hub cylinder has radius R = 2.10.
# Underside of hub cylinder:
# At Y' = -1.351, Z' = 25.483.
# What about the FRONT of the hub cylinder (towards Bracket 4)?
# In tilted coords:
# The circle in Y'Z' is (Y' - (-1.351))^2 + (Z' - 27.583)^2 = 2.10^2!
# At Y' = 0.0: (Z' - 27.583)^2 = 2.10^2 - 1.351^2 = 4.41 - 1.825 = 2.585 => Z' = 27.583 - 1.608 = 25.975!
# At Y' = +0.5: (Z' - 27.583)^2 = 4.41 - 1.851^2 = 4.41 - 3.426 = 0.984 => Z' = 27.583 - 0.992 = 26.591!
# At Y' = +0.749: Z' = 27.583 (the rightmost edge of the hub cylinder in Y'!).
