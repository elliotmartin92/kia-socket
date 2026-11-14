import numpy as np
import trimesh
import os, sys
from shapely.geometry import Polygon, Point, box

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

# Bracket 4 flat geometry:
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
print("Bracket 4 polygon vertices (flat):")
for pt in build_part.bracket_4_raw_pts:
    print(f"  ({pt[0]:.3f}, {pt[1]:.3f})")

# In flat coords: Bracket 4 has top face at Z = 5.60 mm.
# What are the vertices of Bracket 4 top face in tilted coords?
# Tilted formula: Y' = Y*cos(45) - Z*sin(45), Z' = Y*sin(45) + Z*cos(45) - z_min
cos45 = np.cos(np.radians(45.0))
sin45 = np.sin(np.radians(45.0))

print("\nBracket 4 top face (Z=5.60) in tilted coords:")
for x, y in build_part.bracket_4_raw_pts[:-1]:
    yp = y * cos45 - 5.60 * sin45
    zp = y * sin45 + 5.60 * cos45 - z_min
    print(f"  X={x:6.3f}: flat Y={y:6.3f} -> tilted Y'={yp:6.3f}, Z'={zp:6.3f}")

# Shaft hub underside in tilted coords:
# Shaft axle in flat coords: Y_axle = 9.279, Z_axle = 11.190
yp_axle = 9.279 * cos45 - 11.190 * sin45
zp_axle = 9.279 * sin45 + 11.190 * cos45 - z_min
print(f"\nShaft Axle Datum: flat (Y=9.279, Z=11.190) -> tilted (Y'={yp_axle:.3f}, Z'={zp_axle:.3f})")
# Hub radius = 2.10 mm.
# In tilted coords, lowest point of cylindrical hub (at angle -90 deg from tilted Z, i.e. Z' direction):
# A cylinder oriented along X has cross section in Y'Z' that is a circle of radius R=2.10!
# So lowest point in Z' is at Y' = yp_axle = -1.351 mm, Z' = zp_axle - 2.10 = 27.583 - 2.10 = 25.483 mm!
print(f"Lowest point of hub cylinder: Y'={yp_axle:.3f}, Z'={zp_axle - 2.10:.3f}")

# Where is Bracket 4 in X?
# Bracket 4 has outer spine wall at X in [9.857, 10.791], Y in [-7.136, 7.171]
# Top transverse hook/pocket wall at Y in [4.95, 7.171], X in [8.000, 10.791]
# Specifically:
# (8.000, 7.171) to (10.791, 7.171) is the top outer wall (Y=7.171)
# (8.000, 4.950) to (8.900, 4.950) is the hook face (Y=4.950)
# (8.900, 4.950) to (8.900, 6.400) is the step
# (8.900, 6.400) to (9.857, 6.400) is the pocket ceiling (Y=6.400)
# (9.857, 6.400) to (9.857, -6.200) is the outer spine channel inner face (X=9.857)
# (10.791, -7.136) to (10.791, 7.171) is the outer wall (X=10.791)
