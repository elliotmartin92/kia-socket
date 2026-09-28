"""
testing/inspect_full_height_fins.py
Inspects the full geometry of the tilted part:
1. Exact span of backplate underside in build coordinates (Y_build and Z_build)
2. Height of the towers and top tab
3. Removing legacy clip supports
4. Designing full-height support fins that run all the way up to the top of the part
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh

import build_part as bp

# Build part without clip supports
base_poly, outer_body_poly, hole_info = bp.get_exact_base_polygon()
mesh_base = bp.extrude_shapely_geom(base_poly, height=bp.BASE_THICK)
mesh_wall = bp.extrude_shapely_geom(outer_body_poly.difference(outer_body_poly.buffer(-bp.OUTER_WALL_THICK)).union(bp.create_arch_wall_poly()), height=bp.OUTER_WALL_HEIGHT - bp.BASE_THICK)
mesh_wall.apply_translation([0, 0, bp.BASE_THICK])
mesh_ribs = bp.extrude_shapely_geom(bp.create_grid_ribs_poly(base_poly, outer_body_poly), height=bp.RIB_HEIGHT)
mesh_ribs.apply_translation([0, 0, bp.BASE_THICK])
mesh_brackets = bp.extrude_shapely_geom(bp.create_all_brackets_poly(), height=bp.BRACKET_HEIGHT)
mesh_brackets.apply_translation([0, 0, bp.BASE_THICK])
mesh_seating_ribs = bp.build_chamfered_seating_ribs_mesh()
mesh_towers = bp.build_clean_shaft_towers_mesh()
mesh_curved_feat = bp.build_center_curved_feature_mesh()

# Hooks without clip supports
unmerged_hooks = []
for angle_deg in bp.CLIP_ANGLES:
    wedge = bp.build_hook_wedge_mesh(base_poly, angle_deg)
    unmerged_hooks.append(wedge)

# Combine part WITHOUT clip supports
part_clean = trimesh.util.concatenate([mesh_base, mesh_wall, mesh_ribs, mesh_brackets, mesh_seating_ribs, mesh_towers, mesh_curved_feat] + unmerged_hooks)

print("Part without clip supports:")
print(f"Vertices: {len(part_clean.vertices)}, Faces: {len(part_clean.faces)}")
print(f"X bounds: [{part_clean.bounds[0,0]:.2f}, {part_clean.bounds[1,0]:.2f}]")
print(f"Y bounds: [{part_clean.bounds[0,1]:.2f}, {part_clean.bounds[1,1]:.2f}]")
print(f"Z bounds: [{part_clean.bounds[0,2]:.2f}, {part_clean.bounds[1,2]:.2f}]")

# Now rotate 45° about X:
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = part_clean.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

print("\n45° Tilted Part Bounds:")
print(f"X: [{m_tilted.bounds[0,0]:.2f}, {m_tilted.bounds[1,0]:.2f}]")
print(f"Y: [{m_tilted.bounds[0,1]:.2f}, {m_tilted.bounds[1,1]:.2f}]")
print(f"Z: [{m_tilted.bounds[0,2]:.2f}, {m_tilted.bounds[1,2]:.2f}]")

# Let's inspect the backplate underside in tilted coordinates:
# Original backplate bottom face was at Z_orig = 0, with Y_orig in [-18.539, +20.008].
# In tilted coordinates:
# y_build = y_orig * cos(45°) = y_orig * 0.707107
# z_build = y_orig * sin(45°) - z_min = y_orig * 0.707107 - z_min
print("\nBackplate Underside Path along Y:")
y_top_tab_orig = 20.008
y_bot_tab_orig = -18.539

y_bot_build = y_bot_tab_orig * np.cos(np.radians(45))
z_bot_build = y_bot_tab_orig * np.sin(np.radians(45)) - z_min
print(f"Bottom edge (contact with bed): Y_build = {y_bot_build:.2f} mm, Z_build = {z_bot_build:.2f} mm")

y_top_build = y_top_tab_orig * np.cos(np.radians(45))
z_top_build = y_top_tab_orig * np.sin(np.radians(45)) - z_min
print(f"Top edge (top tab underside):   Y_build = {y_top_build:.2f} mm, Z_build = {z_top_build:.2f} mm")

# Notice: Top tab underside reaches Y_build = +14.15 mm, Z_build = 27.26 mm!
# Currently our fins stopped at y_end = +8.0 mm (Z_build = 21.11 mm)!
# There was an unsupported span from Y_build = 8.0 to 14.15 mm (6.15mm along Y, 6.15mm along Z -> 8.7mm along the slope)!
# If we extend the fins all the way up to Y_build = +13.5 mm (Z_build = 26.6 mm),
# the entire backplate is supported directly under the towers and top tab!
