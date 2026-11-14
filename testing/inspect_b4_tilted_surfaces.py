import numpy as np
import trimesh
import os, sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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

# Let's inspect the bounding box of each subpart in tilted space:
for k, st in shaft_tilted.items():
    b = st.bounds
    print(f"{k:10s}: X=[{b[0,0]:.2f}, {b[1,0]:.2f}], Y=[{b[0,1]:.2f}, {b[1,1]:.2f}], Z=[{b[0,2]:.2f}, {b[1,2]:.2f}]")

# Let's isolate Bracket 4 from base_mesh
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])
b_b4 = b4_tilted.bounds
print(f"Bracket 4 : X=[{b_b4[0,0]:.2f}, {b_b4[1,0]:.2f}], Y=[{b_b4[0,1]:.2f}, {b_b4[1,1]:.2f}], Z=[{b_b4[0,2]:.2f}, {b_b4[1,2]:.2f}]")

# Now let's see: Where can a support rise from Bracket 4 in tilted coordinates?
# In 3D printing (45 deg tilt), the build direction is +Z' (vertical).
# A support can rise vertically in +Z' from a surface of Bracket 4!
# Let's check what surfaces of Bracket 4 are facing up in +Z' direction:
# Let's inspect the normal vectors of Bracket 4 faces in tilted coords.
fn = b4_tilted.face_normals
fc = b4_tilted.triangles.mean(axis=1)

print("\nUpward facing surfaces of Bracket 4 (tilted):")
for i in range(len(fn)):
    if fn[i, 2] > 0.5: # upward normal in Z'
        # print some info about high points
        pass

# Specifically:
# In flat coordinates, Bracket 4 has:
# - Top face at Z = 5.60 mm (flat normal is [0, 0, 1]).
#   In tilted coordinates, flat [0, 0, 1] becomes [0, -sin(45), cos(45)] = [0, -0.707, +0.707]!
#   This tilted face faces upward-and-backward (+Z', -Y')!
# - Side walls:
#   * Front wall at Y = 7.171 mm (flat normal [0, 1, 0]).
#     In tilted coordinates, flat [0, 1, 0] becomes [0, cos(45), sin(45)] = [0, +0.707, +0.707]!
#     This face also faces upward-and-forward (+Z', +Y')!
#   * Inner wall at X = 8.000 mm (flat normal [-1, 0, 0]). In tilted: [-1, 0, 0].
#   * Outer wall at X = 10.791 mm (flat normal [+1, 0, 0]). In tilted: [+1, 0, 0].
#   * Pocket wall at Y = 6.400 mm, etc.

# Now look at the top edge of Bracket 4:
# In flat coords: Y = 7.171, Z = 5.60.
# In tilted coords: Y' = 7.171*cos(45) - 5.60*sin(45) = 1.111 mm.
# Z' = 7.171*sin(45) + 5.60*cos(45) - z_min = 22.140 mm!
# And what is right above Bracket 4 at X in [8.0, 10.8]?
# Look at the shaft in tilted coords:
# Shaft hub underside: Y' = -1.351 mm, Z' = 25.483 mm.
# Plunger: X in [8.48, 12.08] mm, Y' in [-3.40, 12.30] mm, Z' in [15.63, 29.63] mm.
# Wait! Plunger passes through the baseplate through-hole!
# Where is the through-hole?
# Through hole in flat coords: X in [7.608, 12.960], Y in [8.570, 13.750].
# Where is Bracket 4? Bracket 4 top wall is at Y = 7.171 mm!
# So Bracket 4 is at Y <= 7.171 mm!
# Through hole begins at Y = 8.570 mm!
# There is a gap of 8.570 - 7.171 = 1.40 mm in flat coords between Bracket 4 top wall and the through hole!
