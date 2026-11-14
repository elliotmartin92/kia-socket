import os, sys
import numpy as np
import trimesh

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

# Let's inspect where Bracket 4 is in X:
# Bracket 4 flat bounds: X in [8.000, 10.791]
# What is the shaft geometry at various X positions across Bracket 4?
# Specifically at X = 8.0, 8.5, 9.0, 9.5, 10.0, 10.5:
# Let's slice the shaft at these X stations!
full_shaft = trimesh.util.concatenate(list(shaft_tilted.values()))
for x in np.arange(7.5, 11.5, 0.5):
    # Slice perpendicular to X
    sl = full_shaft.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sl is not None:
        pts = sl.vertices
        print(f"X={x:4.1f}: Y' in [{np.min(pts[:, 0]):.2f}, {np.max(pts[:, 0]):.2f}], Z' in [{np.min(pts[:, 1]):.2f}, {np.max(pts[:, 1]):.2f}], lowest Z'={np.min(pts[:, 1]):.2f}")
    else:
        print(f"X={x:4.1f}: None")

# Also let's inspect Bracket 4 slices at those X stations:
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

print("\nBracket 4 tilted slices:")
for x in np.arange(7.5, 11.5, 0.5):
    sl = b4_tilted.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sl is not None:
        pts = sl.vertices
        print(f"X={x:4.1f}: Y' in [{np.min(pts[:, 0]):.2f}, {np.max(pts[:, 0]):.2f}], Z' in [{np.min(pts[:, 1]):.2f}, {np.max(pts[:, 1]):.2f}], highest Z'={np.max(pts[:, 1]):.2f}")
    else:
        print(f"X={x:4.1f}: None")
