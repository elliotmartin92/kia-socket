import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString, Polygon
import build_part
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()
clamp_r = build_tower_clamp_mesh(tower_side='right', in_assembly_coords=True)
u_clamp = build_unified_clamp_mesh(in_assembly_coords=True)

print(f"Clamp R bounds: X={clamp_r.bounds[:,0]}, Y={clamp_r.bounds[:,1]}, Z={clamp_r.bounds[:,2]}")

# Check which vertices of clamp_r are OUTSIDE outer_body_poly
pts_outside = []
for v in clamp_r.vertices:
    pt = Point(v[0], v[1])
    if not outer_body_poly.contains(pt):
        pts_outside.append(v)

print(f"Right clamp vertices outside baseplate perimeter: {len(pts_outside)} / {len(clamp_r.vertices)}")
if len(pts_outside) > 0:
    pts_outside = np.array(pts_outside)
    print(f"Outside pts X: [{np.min(pts_outside[:,0]):.2f}, {np.max(pts_outside[:,0]):.2f}], Y: [{np.min(pts_outside[:,1]):.2f}, {np.max(pts_outside[:,1]):.2f}], Z: [{np.min(pts_outside[:,2]):.2f}, {np.max(pts_outside[:,2]):.2f}]")
    dists = [outer_body_poly.exterior.distance(Point(p[0], p[1])) for p in pts_outside]
    print(f"Max distance protruding outside baseplate: {max(dists):.3f} mm")
