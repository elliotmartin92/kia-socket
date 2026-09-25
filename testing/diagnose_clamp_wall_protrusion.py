import os, sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_part import get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT
from build_clamp import build_tower_clamp_mesh, build_unified_clamp_mesh

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()

c_left = build_tower_clamp_mesh('left', in_assembly_coords=True)
c_right = build_tower_clamp_mesh('right', in_assembly_coords=True)
c_unified = build_unified_clamp_mesh(in_assembly_coords=True)

print('=== DIAGNOSING TOWER CLAMP PROTRUSION BEYOND PART WALLS ===')

for name, mesh in [('Left Clamp', c_left), ('Right Clamp', c_right), ('Unified Bridge Clamp', c_unified)]:
    print(f'\n--- {name} ---')
    print(f'Bounding box X: [{mesh.bounds[0,0]:.3f}, {mesh.bounds[1,0]:.3f}] mm')
    print(f'Bounding box Y: [{mesh.bounds[0,1]:.3f}, {mesh.bounds[1,1]:.3f}] mm')
    print(f'Bounding box Z: [{mesh.bounds[0,2]:.3f}, {mesh.bounds[1,2]:.3f}] mm')
    
    # Check vertices outside outer_body_poly
    v_xy = mesh.vertices[:, :2]
    outside_mask = [not outer_body_poly.contains(Point(x, y)) for x, y in v_xy]
    n_outside = sum(outside_mask)
    print(f'Vertices outside outer body wall (total {len(v_xy)}): {n_outside}')
    if n_outside > 0:
        v_out = v_xy[outside_mask]
        print(f'  Max X of outside vertices: {v_out[:, 0].max():.3f} mm')
        print(f'  Min X of outside vertices: {v_out[:, 0].min():.3f} mm')
        print(f'  Max Y of outside vertices: {v_out[:, 1].max():.3f} mm')
        print(f'  Min Y of outside vertices: {v_out[:, 1].min():.3f} mm')
        
        # Calculate max distance outside
        pts_out = [Point(x, y) for x, y in v_out]
        dists = [outer_body_poly.exterior.distance(p) for p in pts_out if not outer_body_poly.contains(p)]
        if dists:
            print(f'  Max protrusion distance outside wall: {max(dists):.3f} mm')

