"""
Test curved snap clip generation following the curved perimeter wall.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union
import trimesh
import matplotlib.pyplot as plt

from build_part import (
    SCALE, X0, Y0, outer_pts, OUTER_WALL_THICK, OUTER_WALL_HEIGHT, BASE_THICK,
    CLIP_HEIGHT, CLIP_GAP_DEPTH, CLIP_ARM_WIDTH, CLIP_SLOT_CLEARANCE,
    CLIP_HOOK_DEPTH, CLIP_HOOK_HEIGHT, find_boundary_point_and_normal,
    get_exact_base_polygon
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

def build_curved_clip_mesh(angle_deg):
    """
    Build a single snap clip that follows the exact curve of the wall.
    - Inner face: follows inner_wall_poly.exterior arc over angular span
    - Outer face: follows outer_body_poly.exterior arc over angular span
    - Hook: extends outward by CLIP_HOOK_DEPTH (1.59mm) and tapers back to inner wall curve at apex.
    """
    # Angular span for width CLIP_ARM_WIDTH (~3.0mm)
    # At R ~ 19.25mm, d_theta = 3.0 / 19.25 rad ~ 0.1558 rad ~ 8.93 deg
    center_rad = math.radians(angle_deg)
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    
    num_pts = 16
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, num_pts)
    
    # Trace inner and outer boundary points along the exact polygons
    inner_coords = []
    outer_coords = []
    for th in theta_vals:
        ray_dir = np.array([np.cos(th), np.sin(th)])
        ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
        
        # Outer intersection
        inter_out = outer_body_poly.exterior.intersection(ray)
        if inter_out.geom_type == 'Point':
            po = np.array([inter_out.x, inter_out.y])
        elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
            po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
            
        # Inner intersection
        inter_in = inner_wall_poly.exterior.intersection(ray)
        if inter_in.geom_type == 'Point':
            pi = np.array([inter_in.x, inter_in.y])
        elif hasattr(inter_in, 'geoms') and len(inter_in.geoms) > 0:
            pi = np.array([inter_in.geoms[-1].x, inter_in.geoms[-1].y])
        else:
            pi = po - (po / np.linalg.norm(po)) * OUTER_WALL_THICK
            
        inner_coords.append(pi)
        outer_coords.append(po)
        
    inner_coords = np.array(inner_coords)
    outer_coords = np.array(outer_coords)
    
    # 2D cross-section of the curved stem (closed polygon)
    stem_2d_pts = list(outer_coords) + list(reversed(inner_coords))
    stem_2d_poly = Polygon(stem_2d_pts)
    
    stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
    stem_mesh = trimesh.creation.extrude_polygon(stem_2d_poly, height=stem_h)
    
    # Hook mesh: 3D loft / mesh from stem_h to CLIP_HEIGHT
    # Outer coordinates at shelf (z = stem_h): outer_coords + normal * CLIP_HOOK_DEPTH
    hook_outer_shelf = []
    for po in outer_coords:
        n_dir = po / np.linalg.norm(po)
        hook_outer_shelf.append(po + n_dir * CLIP_HOOK_DEPTH)
    hook_outer_shelf = np.array(hook_outer_shelf)
    
    # Build vertices for the hook:
    # 0..N-1: inner bottom (z = stem_h) -> inner_coords
    # N..2N-1: outer bottom shelf (z = stem_h) -> hook_outer_shelf
    # 2N..3N-1: outer wall bottom (z = stem_h) -> outer_coords
    # 3N..4N-1: inner top apex (z = CLIP_HEIGHT) -> inner_coords
    N = num_pts
    v_in_bot = np.column_stack([inner_coords, np.full(N, stem_h)])
    v_out_shelf = np.column_stack([hook_outer_shelf, np.full(N, stem_h)])
    v_out_wall = np.column_stack([outer_coords, np.full(N, stem_h)])
    v_in_top = np.column_stack([inner_coords, np.full(N, CLIP_HEIGHT)])
    
    verts = np.vstack([v_in_bot, v_out_shelf, v_out_wall, v_in_top])
    
    # Build faces for hook:
    # 1. Undercut shelf face (between v_out_wall and v_out_shelf at z = stem_h): pointing -Z
    # 2. Slanted outer face (between v_out_shelf at stem_h and v_in_top at CLIP_HEIGHT)
    # 3. Inner vertical face (between v_in_bot at stem_h and v_in_top at CLIP_HEIGHT)
    # 4. Left side end cap (at index 0)
    # 5. Right side end cap (at index N-1)
    faces = []
    for i in range(N - 1):
        # 1. Undercut shelf face: indices (2N+i, 2N+i+1, N+i+1, N+i)
        faces.append([2*N + i, N + i, N + i + 1])
        faces.append([2*N + i, N + i + 1, 2*N + i + 1])
        
        # 2. Slanted outer bevel: indices (N+i, N+i+1, 3N+i+1, 3N+i)
        faces.append([N + i, N + i + 1, 3*N + i + 1])
        faces.append([N + i, 3*N + i + 1, 3*N + i])
        
        # 3. Inner vertical curved face: indices (i, 3N+i, 3N+i+1, i+1)
        faces.append([i, 3*N + i + 1, 3*N + i])
        faces.append([i, i + 1, 3*N + i + 1])
        
    # Side endcaps:
    # Left endcap (i = 0): triangle (v_in_bot[0], v_out_shelf[0], v_in_top[0]) and (v_in_bot[0], v_out_wall[0], v_out_shelf[0])
    faces.append([0, 3*N, N])
    faces.append([0, N, 2*N])
    # Right endcap (i = N-1):
    faces.append([N - 1, N + N - 1, 3*N + N - 1])
    faces.append([N - 1, 2*N + N - 1, N + N - 1])
    
    hook_mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    full_clip = trimesh.util.concatenate([stem_mesh, hook_mesh])
    return full_clip, stem_2d_poly

import math
clip_mesh, poly2d = build_curved_clip_mesh(45)
print("Curved clip mesh generated successfully! Is watertight:", clip_mesh.is_watertight)

fig = plt.figure(figsize=(10, 8), dpi=160)
ax = fig.add_subplot(1, 1, 1, projection='3d')
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
col = Poly3DCollection(clip_mesh.vertices[clip_mesh.faces], alpha=0.85, edgecolor='#222222', linewidths=0.2)
col.set_facecolor('#17becf')
ax.add_collection3d(col)
ax.set_xlim(10, 20)
ax.set_ylim(10, 20)
ax.set_zlim(0, 8)
ax.set_title('Curved Snap Clip (45 deg) - Follows Curved Wall', fontsize=12, fontweight='bold')
plt.savefig('curved_clip_test.png', dpi=160)
print("Saved curved_clip_test.png")
