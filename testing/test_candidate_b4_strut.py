import numpy as np
import trimesh
import os, sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

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

full_lever = trimesh.util.concatenate(list(shaft_subparts.values()))
full_lever_tilted = full_lever.copy().apply_transform(R)
full_lever_tilted.apply_translation([0, 0, -z_min])

# Isolate Bracket 4
b4_poly = build_part.to_mm_poly(build_part.bracket_4_raw_pts)
b4_flat = build_part.extrude_shapely_geom(b4_poly, height=build_part.BRACKET_HEIGHT)
b4_flat.apply_translation([0, 0, build_part.BASE_THICK])
b4_tilted = b4_flat.copy().apply_transform(R)
b4_tilted.apply_translation([0, 0, -z_min])

# Towers
towers_flat = build_part.build_clean_shaft_towers_mesh()
towers_tilted = towers_flat.copy().apply_transform(R)
towers_tilted.apply_translation([0, 0, -z_min])

# Let's test Candidate 1:
# Anchor on Bracket 4 top face.
# In flat coords: Bracket 4 top face is at Z = 5.60.
# At X = 8.20 (centered between 8.00 and 8.40):
# Bracket 4 top face spans Y in [4.950, 7.171].
# In tilted coords:
# Center of this top face at Y_flat = 6.00, Z_flat = 5.60:
# Y' = 6.00*cos(45) - 5.60*sin(45) = 0.283 mm
# Z' = 6.00*sin(45) + 5.60*cos(45) - z_min = 21.311 mm.
# Target shaft hub contact:
# Underside of hub cylinder: Y' = -1.351 mm, Z' = 25.483 mm.
# Gap: 0.48 mm -> Z'_top = 25.003 mm.
# Target contact center: X = 8.16 mm, Y' = -1.351 mm, Z' = 25.003 mm.

# Let's build a candidate strut coming off Bracket 4:
# Trunk: starts on Bracket 4 top surface, angled or straight, rising to Z'_fork = 23.50 mm.
# Then Y-fork head from Z' = 23.50 to 25.00 mm supporting the shaft barrel!

# Let's test trunk and Y-fork in tilted coordinates directly:
# Option 1A: Angled trunk from (Y'=0.283, Z'=21.31) to (Y'=-1.351, Z'=23.50).
# Length is sqrt((0.283 - (-1.351))^2 + (23.50 - 21.31)^2) = sqrt(1.634^2 + 2.19^2) = 2.73 mm!
# Angle from vertical: arctan(1.634 / 2.19) = 36.7 degrees! (Completely printable without supports, since <= 45 deg!)

# Option 1B: What if the anchor on Bracket 4 is at Y_flat = 4.95 (hook face)?
# Y' = -0.460 mm, Z' = 20.569 mm!
# Then to (Y'=-1.351, Z'=23.50):
# Delta Y' = -1.351 - (-0.460) = -0.891 mm.
# Delta Z' = 23.50 - 20.569 = 2.931 mm.
# Angle from vertical: arctan(0.891 / 2.931) = 16.9 degrees! (Super steep, almost vertical, very rigid!)

# Option 1C: What if the anchor on Bracket 4 is on the front wall (Y_flat = 7.171)?
# Y' = 1.111, Z' = 22.140.

# Let's build both and render them!
def build_strut_option_b(anchor_y_flat=4.95, x_c=8.16, w_x=0.55):
    # Anchor point on Bracket 4
    cos45 = np.cos(np.pi/4)
    sin45 = np.sin(np.pi/4)
    yp_anchor = anchor_y_flat * cos45 - 5.60 * sin45
    zp_anchor = anchor_y_flat * sin45 + 5.60 * cos45 - z_min
    
    # Target hub contact
    yp_target = -1.351
    zp_target = 25.483 - 0.48 # 25.003
    
    # Let's create an easy-snap neck at the anchor
    # Neck: 0.50 x 0.50 mm block sitting on Bracket 4
    neck = trimesh.creation.box([0.50, 0.50, 0.60])
    neck.apply_translation([x_c, yp_anchor, zp_anchor + 0.30])
    
    # Trunk: loft/box from neck top to fork base
    zp_fork_base = 23.50
    # Center of trunk in Y' interpolates between yp_anchor and yp_target
    # Fork base at zp_fork_base:
    frac = (zp_fork_base - (zp_anchor + 0.60)) / (zp_target - (zp_anchor + 0.60))
    yp_fork_base = yp_anchor + frac * (yp_target - yp_anchor)
    
    # We can model trunk as a swept polygon in Y'Z' extruded in X
    pts_trunk_yz = [
        (yp_anchor - 0.25, zp_anchor + 0.60),
        (yp_fork_base - 0.30, zp_fork_base),
        (yp_fork_base + 0.30, zp_fork_base),
        (yp_anchor + 0.25, zp_anchor + 0.60),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=w_x)
    v_t = m_trunk_2d.vertices.copy()
    # extrude is in Z of 2D polygon: X_3d = Z_2d + x_c - w_x/2, Y_3d = X_2d, Z_3d = Y_2d
    v_t_3d = np.column_stack([v_t[:, 2] + x_c - w_x/2.0, v_t[:, 0], v_t[:, 1]])
    m_trunk = trimesh.Trimesh(vertices=v_t_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if m_trunk.volume < 0:
        m_trunk.faces = np.fliplr(m_trunk.faces)
        
    # Y-fork head at the top:
    # Fork spans in X from 7.92 to 8.40 (or 7.85 to 8.45), width 0.50 in Y'
    # Twin prongs with central V-notch
    z_notch = zp_target - 0.80
    pts_fork_xz = [
        (7.90, zp_fork_base),
        (7.90, zp_target),
        (8.08, zp_target),
        (x_c,  z_notch),
        (8.24, zp_target),
        (8.42, zp_target),
        (8.42, zp_fork_base),
    ]
    poly_fork_xz = Polygon(pts_fork_xz)
    m_fork_2d = trimesh.creation.extrude_polygon(poly_fork_xz, height=0.60)
    v_f = m_fork_2d.vertices.copy()
    v_f_3d = np.column_stack([v_f[:, 0], v_f[:, 2] - 0.30 + yp_target, v_f[:, 1]])
    m_fork = trimesh.Trimesh(vertices=v_f_3d, faces=m_fork_2d.faces.copy(), process=True)
    if m_fork.volume < 0:
        m_fork.faces = np.fliplr(m_fork.faces)
        
    return trimesh.util.concatenate([neck, m_trunk, m_fork])

strut_b = build_strut_option_b()
print("Built candidate strut from Bracket 4! Bounds:")
print(strut_b.bounds)
