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

# Let's check what parts of Bracket 4 exist:
print("Bracket 4 polygon coordinates:")
for p in build_part.bracket_4_raw_pts:
    print(p)

# Let's check where the right side of the shaft is relative to Bracket 4:
# Bracket 4 outer wall is at X = 10.791 mm.
# Where is the right shaft tower?
# Right tower inner wall is at X = 13.100 mm!
# Where is the right flank rib of the shaft (Rib 3)?
# Rib 3 is at X in [11.60, 12.60]!
# Where does the plunger blade end?
# Plunger blade is at X in [8.484, 12.084]!
# So the plunger blade spans X from 8.484 to 12.084.
# And between Rib 3 (X=11.60) and Plunger (X=12.084), Rib 3 and Plunger overlap on the hub.
# Between Plunger (left edge X = 8.484) and Cam (right edge X = 7.700):
# That is X in [7.700, 8.484] -> 0.784 mm gap.
# What about between Cam (left edge X = 5.80) and Left Tower (inner wall X = 5.40)?
# That is X in [5.40, 5.80] -> 0.40 mm gap.
# What about between Rib 3 (right edge X = 12.60) and Right Tower (inner wall X = 13.10)?
# That is X in [12.60, 13.10] -> 0.50 mm gap.

# So the ONLY open sections of the hub barrel along X are:
# 1. Left end of hub: X in [5.40, 5.80] (0.40 mm)
# 2. Between Cam and Plunger: X in [7.70, 8.484] (0.784 mm)
# 3. Right end of hub: X in [12.60, 13.10] (0.50 mm)
