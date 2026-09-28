import trimesh
import numpy as np
import shapely.geometry
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model

part_flat, base_poly = build_exact_3d_model()
print(f"Flat part bounds:\n  X: {part_flat.bounds[0, 0]:.2f} to {part_flat.bounds[1, 0]:.2f}\n  Y: {part_flat.bounds[0, 1]:.2f} to {part_flat.bounds[1, 1]:.2f}\n  Z: {part_flat.bounds[0, 2]:.2f} to {part_flat.bounds[1, 2]:.2f}")

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
part_tilted = part_flat.copy().apply_transform(R)
z_min = part_tilted.bounds[0, 2]
part_tilted.apply_translation([0, 0, -z_min])

print(f"Tilted part bounds (Z >= 0):\n  X: {part_tilted.bounds[0, 0]:.2f} to {part_tilted.bounds[1, 0]:.2f}\n  Y: {part_tilted.bounds[0, 1]:.2f} to {part_tilted.bounds[1, 1]:.2f}\n  Z: {part_tilted.bounds[0, 2]:.2f} to {part_tilted.bounds[1, 2]:.2f}")

# Check base_poly min/max Y at X = -8.0 and X = +8.0
# In flat coordinates, base plate underside is Z = 0.
# For any point (x, y, 0) on the underside of the base plate:
# Tilted coordinates:
# y_tilt = y * cos(45) - 0 * sin(45) = y * cos(45)
# z_tilt_raw = y * sin(45) + 0 * cos(45) = y * sin(45)
# z_tilt = z_tilt_raw - z_min = y * sin(45) - z_min
# Notice that since sin(45) == cos(45), z_tilt = y_tilt - z_min !
line_l = shapely.geometry.LineString([(-8.0, -50.0), (-8.0, 50.0)])
line_r = shapely.geometry.LineString([(8.0, -50.0), (8.0, 50.0)])
inter_l = base_poly.intersection(line_l)
inter_r = base_poly.intersection(line_r)

print(f"Base poly at X=-8.0: Y from {inter_l.bounds[1]:.2f} to {inter_l.bounds[3]:.2f}")
print(f"Base poly at X=+8.0: Y from {inter_r.bounds[1]:.2f} to {inter_r.bounds[3]:.2f}")

c45 = np.cos(np.radians(45))
print(f"Tilted underside at X=-8.0: Y_tilt from {inter_l.bounds[1]*c45:.2f} to {inter_l.bounds[3]*c45:.2f}, Z_tilt from {inter_l.bounds[1]*c45 - z_min:.2f} to {inter_l.bounds[3]*c45 - z_min:.2f}")
print(f"Tilted underside at X=+8.0: Y_tilt from {inter_r.bounds[1]*c45:.2f} to {inter_r.bounds[3]*c45:.2f}, Z_tilt from {inter_r.bounds[1]*c45 - z_min:.2f} to {inter_r.bounds[3]*c45 - z_min:.2f}")

# Overall base_poly Y min/max:
print(f"Base poly overall Y: {base_poly.bounds[1]:.2f} to {base_poly.bounds[3]:.2f}")
print(f"Tilted overall underside Y: {base_poly.bounds[1]*c45:.2f} to {base_poly.bounds[3]*c45:.2f}, Z: {base_poly.bounds[1]*c45 - z_min:.2f} to {base_poly.bounds[3]*c45 - z_min:.2f}")
