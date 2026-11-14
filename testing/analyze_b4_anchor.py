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
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

print("Bracket 4 flat bounds:", b4_flat.bounds)
print("Bracket 4 tilted bounds:", b4_tilted.bounds)

# Let's inspect the shaft hub barrel:
# The hub barrel is a cylinder from X = 5.80 to X = 12.70.
# Between X = 7.70 (cam tab right edge) and X = 8.484 (plunger blade left edge), the hub barrel has NO attached ribs or blades.
# That is a clean cylindrical hub section: X in [7.70, 8.484].
# Center of this section is X = (7.70 + 8.484) / 2 = 8.092 mm.
# Or if we support slightly wider, say X in [7.90, 8.35] (centered at 8.125 or 8.16).
# Bracket 4 is at X in [8.000, 10.791].
# So Bracket 4 directly underlies X in [8.000, 8.484]!
# But wait! Does Bracket 4 also underlie the plunger blade?
# Plunger blade is at X in [8.484, 12.084]!
# And Bracket 4 extends up to X = 10.791!
# Wait, can a support off Bracket 4 support the hub barrel, or the plunger, or both?
# The user specifically said:
# "add one coming off of bracket 4 ending in a Y to better support the shaft"
# "better support the shaft" means supporting the SHAFT (the hub barrel of the lever shaft)!
# Just like the one we had before ("a stick support between the base and the lever shaft... delete it and add one coming off of bracket 4 ending in a Y to better support the shaft").

# Now let's examine:
# Where on Bracket 4 can this support be rooted?
# Look at Bracket 4 top surfaces:
# At X in [8.00, 8.50]:
# In flat coordinates:
# Top face of Bracket 4 is at Z = 5.60 mm.
# Y is from 4.950 to 7.171 mm!
# Let's see what happens if the support roots on Bracket 4's top face:
# In flat coords: Z = 5.60 mm.
# In tilted coords:
# For Y in [4.950, 7.171]:
# Y' is in [-0.460, 1.111] mm.
# Z' is in [20.569, 22.140] mm.
# And the shaft hub barrel underside is at:
# Y' = -1.351 mm, Z' = 25.483 mm.
# Release gap: 0.48 mm (or 0.28 to 0.48 mm). Top of support at Z' = 25.003 mm.
