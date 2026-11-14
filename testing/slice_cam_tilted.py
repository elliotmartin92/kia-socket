import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from build_shaft import build_shaft_rocker_mesh
import build_part

part_mesh_flat, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = part_mesh_flat.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

subparts = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False, return_subparts=True)

cam = subparts['cam'].copy().apply_transform(R)
cam.apply_translation([0, 0, -z_min])

hub = subparts['hub'].copy().apply_transform(R)
hub.apply_translation([0, 0, -z_min])

# Let's inspect the bounding box of cam and hub in Z' (print height)
print("Hub Z' bounds:", hub.bounds[:, 2])
print("Cam Z' bounds:", cam.bounds[:, 2])

# In assembly coords, what is the union of hub and cam?
union_hc = trimesh.boolean.union([subparts['hub'], subparts['cam']], engine='manifold')
union_tilted = union_hc.copy().apply_transform(R)
union_tilted.apply_translation([0, 0, -z_min])

# Let's slice union_tilted at various Z' levels where cam connects to hub
z_levels = np.linspace(cam.bounds[0, 2] + 0.2, cam.bounds[1, 2] - 0.2, 25)
for z in z_levels:
    slice_2d = union_tilted.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if slice_2d is not None:
        poly_2d = slice_2d.to_planar()[0]
        # Let's check how many polygons there are in this layer slice:
        # If there are 2 separate polygons, it means in this layer, the cam is NOT CONNECTED to the hub!
        area = slice_2d.area
        bounds = slice_2d.bounds
        print(f"Z' = {z:.2f} mm: area = {area:.2f} mm^2, X span = [{bounds[0, 0]:.2f}, {bounds[1, 0]:.2f}]")
