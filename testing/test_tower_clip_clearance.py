import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import Point, LineString
import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-build_part.OUTER_WALL_THICK)

towers_mesh = build_part.build_clean_shaft_towers_mesh()
p45, norm45, tang45 = build_part.find_boundary_point_and_normal(base_poly, 45.0)
center_rad = math.radians(45.0)
r_est = np.linalg.norm(p45)
d_theta = build_part.CLIP_ARM_WIDTH / r_est

# Define an inward clearance zone behind the 45 deg clip arm
# The clip arm spans theta in [center_rad - d_theta/2, center_rad + d_theta/2]
# Radial range: from (r_inner - 1.20mm) to (r_outer + 0.50mm)
# Z range: from Z = 1.00mm to Z = 7.00mm
# Any tower material in this zone blocks the clip from flexing inward!

# Let's create a cutting box/sector in this zone:
# Let's inspect the intersection of towers_mesh with this zone
clearance_box = trimesh.creation.box([build_part.CLIP_ARM_WIDTH + 1.0, 3.0, 7.0])
# Place it behind p45 along -norm45
# Angle of normal is ~45 deg
rot = trimesh.transformations.rotation_matrix(center_rad, [0, 0, 1])
clearance_box.apply_transform(rot)
# p_inner is at p45 - norm45 * OUTER_WALL_THICK
p_cut = p45 - norm45 * (build_part.OUTER_WALL_THICK + 1.0)
clearance_box.apply_translation([p_cut[0], p_cut[1], 3.5 + build_part.BASE_THICK])

inter = towers_mesh.intersection(clearance_box, engine='manifold')
print(f"Tower volume in clip flex zone: {inter.volume:.3f} mm³")
print(f"Intersection bounds: {inter.bounds}")

# Let's difference the tower with the clearance box
towers_relieved = towers_mesh.difference(clearance_box, engine='manifold')
print(f"Relieved towers watertight: {towers_relieved.is_watertight}, volume: {towers_relieved.volume:.2f} mm³")
