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
for k, s in shaft_subparts.items():
    s_t = s.copy().apply_transform(R)
    s_t.apply_translation([0, 0, -z_min])
    b = s_t.bounds
    print(f"Shaft {k:15s} (tilted): X=[{b[0,0]:.2f}, {b[1,0]:.2f}], Y=[{b[0,1]:.2f}, {b[1,1]:.2f}], Z=[{b[0,2]:.2f}, {b[1,2]:.2f}]")
    bf = s.bounds
    print(f"      {k:15s} (flat):   X=[{bf[0,0]:.2f}, {bf[1,0]:.2f}], Y=[{bf[0,1]:.2f}, {bf[1,1]:.2f}], Z=[{bf[0,2]:.2f}, {bf[1,2]:.2f}]")

b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
print("Bracket 4 2D bounds (flat):", b4_poly.bounds)
# Extrude Bracket 4 in flat coords
b4_mesh = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_mesh.apply_translation([0, 0, build_part.BASE_THICK])
bf4 = b4_mesh.bounds
print(f"Bracket 4 3D bounds (flat): X=[{bf4[0,0]:.2f}, {bf4[1,0]:.2f}], Y=[{bf4[0,1]:.2f}, {bf4[1,1]:.2f}], Z=[{bf4[0,2]:.2f}, {bf4[1,2]:.2f}]")

b4_tilted = b4_mesh.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])
bt4 = b4_tilted.bounds
print(f"Bracket 4 3D bounds (tilted): X=[{bt4[0,0]:.2f}, {bt4[1,0]:.2f}], Y=[{bt4[0,1]:.2f}, {bt4[1,1]:.2f}], Z=[{bt4[0,2]:.2f}, {bt4[1,2]:.2f}]")

# Let's inspect the shaft hub and pins
# Axle datum: Y=9.279, Z=11.190 in flat coords
# Shaft hub barrel: X in [5.40+0.40, 13.10-0.40] = [5.80, 12.70], radius 2.10 (diam 4.20)
# But wait! Where is the plunger and cam tab attached to the hub?
