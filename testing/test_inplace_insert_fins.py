import trimesh
import numpy as np
from shapely.geometry import Polygon, box
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp

# Build part with in-place inserts
part_flat, base_poly = bp.build_exact_3d_model()
ins_r = bp.build_slit_insert_mesh(is_right=True)
ins_l = bp.build_slit_insert_mesh(is_right=False)

cx_left = -7.853
cx_right = 8.453
cy = -13.589
z_insert = -bp.SLIT_BOSS_HEIGHT

ins_r_placed = ins_r.copy().apply_translation([cx_right, cy, z_insert])
ins_l_placed = ins_l.copy().apply_translation([cx_left, cy, z_insert])

# Unified part with in-place inserts
part_with_inserts = trimesh.util.concatenate([part_flat, ins_r_placed, ins_l_placed])

# Tilt 45 deg
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_with_inserts.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

# Construct updated support fins that clear the in-place inserts:
fin_components = []

# 1. Bed pad with relief windows under the in-place insert tips
pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
pad_mesh.apply_translation([0.0, -2.50, 0.30])

# Cut relief pockets under left and right insert tips (Z in [0, 0.60])
relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
relief_l.apply_translation([cx_left, -9.5, 0.30])

relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
relief_r.apply_translation([cx_right, -9.5, 0.30])

pad_mesh = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
fin_components.append(pad_mesh)

# 2. Main Twin Support Fins from Y = -5.8mm up to Y = +12.30mm (clearing the inserts completely)
fin_thick_x = 0.80
standoff = 0.20
z_bed = 0.60
y_start = -5.80
y_end = 12.30
z_start = y_start - z_min - standoff
z_end = y_end - z_min - standoff

for x_pos in [-8.0, 8.0]:
    pts_yz = [
        (y_start, z_bed),
        (y_start, z_start),
        (y_end, z_end),
        (y_end, z_bed)
    ]
    poly_yz = Polygon(pts_yz)
    m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
    v = m_fin_raw.vertices.copy()
    v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
    m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
    fin_components.append(m_fin)
    
    y_tine_stations = np.arange(y_start + 1.5, y_end, 3.1)
    for yt in y_tine_stations:
        zt_underside = yt - z_min
        tine = trimesh.creation.box([fin_thick_x, 0.60, standoff + 0.35])
        tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.10])
        fin_components.append(tine)

# 3. Sway Braces
sway_l = trimesh.creation.box([1.00, 8.0, 17.40])
sway_l.apply_translation([-22.20, -1.0, 9.30])
fin_components.append(sway_l)
for z_t in [10.0, 14.0, 17.5]:
    tine_l = trimesh.creation.box([2.00, 1.00, 0.40])
    tine_l.apply_translation([-21.70, -1.0, z_t])
    fin_components.append(tine_l)

sway_r = trimesh.creation.box([1.00, 8.0, 17.40])
sway_r.apply_translation([21.32, -1.0, 9.30])
fin_components.append(sway_r)
for z_t in [10.0, 14.0, 17.5]:
    tine_r = trimesh.creation.box([2.00, 1.00, 0.40])
    tine_r.apply_translation([20.82, -1.0, z_t])
    fin_components.append(tine_r)

all_fins = trimesh.util.concatenate(fin_components)

print("Checking collision between updated fins and tilted part...")
try:
    inter = all_fins.intersection(m_tilted, engine='manifold')
    print("Intersection volume (tines penetration only):", inter.volume)
except Exception as e:
    print("Intersection check error:", e)

comb = trimesh.util.concatenate([m_tilted, all_fins])
print("Combined bounds:", comb.bounds)
print("Combined watertight:", comb.is_watertight)
