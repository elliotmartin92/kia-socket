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

# Check intersection volume between cam and hub:
intersection = trimesh.boolean.intersection([subparts['hub'], subparts['cam']], engine='manifold')
print(f"Intersection volume in assembly coords: {intersection.volume:.3f} mm^3")
print(f"Intersection bounds in assembly coords: {intersection.bounds.tolist()}")

union_hc = trimesh.boolean.union([subparts['hub'], subparts['cam']], engine='manifold')
union_tilted = union_hc.copy().apply_transform(R)
union_tilted.apply_translation([0, 0, -z_min])

# Let's slice union_tilted and cam separately at Z' from 25.0 to 27.0
for z in np.arange(25.0, 27.5, 0.2):
    s_union = union_tilted.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    s_cam = cam.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    s_hub = hub.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    
    # Check 2D paths
    poly_cam = s_cam.to_2D()[0] if s_cam is not None else None
    poly_hub = s_hub.to_2D()[0] if s_hub is not None else None
    poly_u = s_union.to_2D()[0] if s_union is not None else None
    
    area_c = poly_cam.polygons_full[0].area if poly_cam and len(poly_cam.polygons_full) > 0 else 0
    area_h = poly_hub.polygons_full[0].area if poly_hub and len(poly_hub.polygons_full) > 0 else 0
    area_u = poly_u.polygons_full[0].area if poly_u and len(poly_u.polygons_full) > 0 else 0
    
    num_u = len(poly_u.polygons_full) if poly_u else 0
    
    print(f"Z'={z:.2f}: Cam area={area_c:.2f}, Hub area={area_h:.2f}, Union area={area_u:.2f}, Num union islands={num_u}")
