import trimesh
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
from build_shaft import build_shaft_rocker_mesh

# 1. Main Part Single Solid
part_flat, base_poly = bp.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_flat.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

# Fins with y_tine_stations = np.arange(y_start + 1.5, y_end - 0.8, 3.1)
fin_components = []
pad_mesh = trimesh.creation.box([48.0, 33.0, 0.60])
pad_mesh.apply_translation([0.0, -2.50, 0.30])
cx_left, cx_right = -7.853, 8.453
relief_l = trimesh.creation.box([4.5, 6.0, 1.0])
relief_l.apply_translation([cx_left, -9.5, 0.30])
relief_r = trimesh.creation.box([4.5, 6.0, 1.0])
relief_r.apply_translation([cx_right, -9.5, 0.30])
pad_mesh = pad_mesh.difference(trimesh.util.concatenate([relief_l, relief_r]), engine='manifold')
fin_components.append(pad_mesh)

fin_thick_x = 0.80
standoff = 0.20
z_bed = 0.60
y_start = -5.80
y_end = 12.30
z_start = y_start - z_min - standoff
z_end = y_end - z_min - standoff
from shapely.geometry import Polygon

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
    
    y_tine_stations = np.arange(y_start + 1.5, y_end - 0.8, 3.1)
    for yt in y_tine_stations:
        zt_underside = yt - z_min
        tine = trimesh.creation.box([fin_thick_x, 0.60, standoff + 0.35])
        tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.10])
        fin_components.append(tine)

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
fin_bodies = [b for b in all_fins.split(only_watertight=False) if abs(b.volume) > 0.001]
fins_solid = trimesh.boolean.union(fin_bodies, engine='manifold')

part_solid_raw = trimesh.boolean.union([m_tilted, fins_solid], engine='manifold')
bodies = part_solid_raw.split(only_watertight=False)
main_bodies = [b for b in bodies if abs(b.volume) > 5.0]
part_solid = trimesh.boolean.union(main_bodies, engine='manifold')

print(f"part_solid: watertight={part_solid.is_watertight}, bodies={len(part_solid.split(only_watertight=False))}, Z_min={part_solid.bounds[0,2]:.4f}")

# 2. Shaft Rocker Single Solid
shaft_raw = build_shaft_rocker_mesh(in_assembly_coords=False, with_supports=True)
shaft_bodies = [b for b in shaft_raw.split(only_watertight=False) if abs(b.volume) > 5.0]
shaft_solid = trimesh.boolean.union(shaft_bodies, engine='manifold')
print(f"shaft_solid: watertight={shaft_solid.is_watertight}, bodies={len(shaft_solid.split(only_watertight=False))}, Z_min={shaft_solid.bounds[0,2]:.4f}")

# 3. Cooling Tower
cool_tower = bp.build_cooling_tower_mesh(radius=2.0, height=20.50)

# Position in assembly
shaft_positioned = shaft_solid.copy().apply_translation([27.50, 6.00, 0.00])
tower_positioned = cool_tower.copy().apply_translation([27.50, -18.00, 0.00])

clean_assembly = trimesh.util.concatenate([part_solid, shaft_positioned, tower_positioned])
assembly_bodies = clean_assembly.split(only_watertight=False)
print(f"\nClean Assembly Total Objects: {len(assembly_bodies)}")
for i, b in enumerate(assembly_bodies):
    print(f"  Object {i}: Z_min = {b.bounds[0,2]:.4f}mm, Z_max = {b.bounds[1,2]:.4f}mm, volume = {abs(b.volume):.2f}mm^3, watertight = {b.is_watertight}")
