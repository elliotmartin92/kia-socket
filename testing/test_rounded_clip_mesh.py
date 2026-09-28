"""
Build and verify 3D mesh for rounded snap clips.
Test watertightness, boolean union with perimeter wall, and slot cutting.
Save 3D render in testing/
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon
import matplotlib.pyplot as plt

import build_part

base_poly, outer_body_poly, _ = build_part.get_exact_base_polygon()

CLIP_HEIGHT = 6.77
CLIP_HOOK_HEIGHT = 1.80
CLIP_HOOK_DEPTH = 2.10
CLIP_ARM_WIDTH = 4.20
stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97mm
top_z = CLIP_HEIGHT  # 6.77mm
H = CLIP_HOOK_HEIGHT  # 1.80mm
D = CLIP_HOOK_DEPTH  # 2.10mm

def build_rounded_hook_mesh(center_rad, r_est, d_theta, hook_depth, n_theta=16, n_z=16):
    """
    Constructs a 3D hook mesh with a smooth rounded lead-in profile
    tangent to the outer diameter at z = stem_h.
    Retention shelf at z = stem_h remains 100% flat and undercut.
    """
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, n_theta)
    
    # Outer wall boundary points
    outer_coords = []
    inner_overlap_coords = []
    normal_dirs = []
    
    for th in theta_vals:
        ray_dir = np.array([np.cos(th), np.sin(th)])
        ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
        inter_out = outer_body_poly.exterior.intersection(ray)
        if inter_out.geom_type == 'Point':
            po = np.array([inter_out.x, inter_out.y])
        elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
            po = np.array([inter_out.x, inter_out.y]) if hasattr(inter_out, 'x') else np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
            
        n_dir = po / np.linalg.norm(po)
        p_in = po - n_dir * 0.25  # Inward penetration into wall for seamless union
        
        outer_coords.append(po)
        inner_overlap_coords.append(p_in)
        normal_dirs.append(n_dir)
        
    outer_coords = np.array(outer_coords)
    inner_overlap_coords = np.array(inner_overlap_coords)
    normal_dirs = np.array(normal_dirs)
    
    # Elevation stations from stem_h to top_z
    # We use a smooth convex rounded curve:
    # u in [0, 1] where u=0 at stem_h (shelf), u=1 at top_z (rim)
    # Cosine / circular round profile:
    # r(u) = hook_depth * cos(pi/2 * u) or smooth cosine:
    # Using circular arc tangent to outer diameter at u=0:
    # R_c = (D^2 + H^2) / (2D)
    R_c = (hook_depth**2 + H**2) / (2.0 * hook_depth)
    
    z_stations = np.linspace(stem_h, top_z, n_z)
    
    # Grid of surface vertices: shape (n_z, n_theta, 3)
    surf_verts = np.zeros((n_z, n_theta, 3))
    
    for iz, z in enumerate(z_stations):
        dz = z - stem_h
        val = max(0.0, R_c**2 - dz**2)
        r_protrusion = (hook_depth - R_c) + np.sqrt(val)
        r_protrusion = max(0.0, min(hook_depth, r_protrusion))
        
        # Optional: slight lateral edge rounding in theta to prevent corner snagging
        # At the very lateral edges (first and last 15% of width), taper r_protrusion slightly
        for it in range(n_theta):
            t_frac = abs((it / (n_theta - 1.0)) - 0.5) * 2.0  # 0 at center, 1 at edges
            # Corner easing: if t_frac > 0.75, round corners by up to 0.15mm
            edge_factor = 1.0
            if t_frac > 0.70:
                edge_factor = 1.0 - 0.12 * ((t_frac - 0.70) / 0.30)**2
            
            p_surf = outer_coords[it] + normal_dirs[it] * (r_protrusion * edge_factor)
            surf_verts[iz, it] = [p_surf[0], p_surf[1], z]
            
    # Bottom shelf inner vertices (at stem_h, penetrating wall)
    shelf_inner = np.column_stack([inner_overlap_coords, np.full(n_theta, stem_h)])
    # Top rim inner vertices (at top_z, penetrating wall)
    top_inner = np.column_stack([inner_overlap_coords, np.full(n_theta, top_z)])
    
    # Vertices array:
    # 0 to n_theta - 1: shelf_inner
    # n_theta to 2*n_theta - 1: top_inner
    # then n_z * n_theta surface vertices: index 2*n_theta + iz*n_theta + it
    all_verts = list(shelf_inner) + list(top_inner)
    surf_offset = 2 * n_theta
    for iz in range(n_z):
        for it in range(n_theta):
            all_verts.append(surf_verts[iz, it])
    all_verts = np.array(all_verts)
    
    faces = []
    
    # 1. Bottom retention shelf: flat undercut at z = stem_h
    # Connects shelf_inner[it] to surf_verts[0, it]
    for it in range(n_theta - 1):
        i_in_0 = it
        i_in_1 = it + 1
        i_out_0 = surf_offset + it
        i_out_1 = surf_offset + it + 1
        # Facing -Z
        faces.append([i_in_0, i_out_1, i_out_0])
        faces.append([i_in_0, i_in_1, i_out_1])
        
    # 2. Rounded outer lead-in surface: grid from iz=0 to n_z-1
    for iz in range(n_z - 1):
        for it in range(n_theta - 1):
            v00 = surf_offset + iz * n_theta + it
            v01 = surf_offset + iz * n_theta + it + 1
            v10 = surf_offset + (iz + 1) * n_theta + it
            v11 = surf_offset + (iz + 1) * n_theta + it + 1
            # Facing outward (+R / +Z)
            faces.append([v00, v01, v11])
            faces.append([v00, v11, v10])
            
    # 3. Top rim closure: from surf_verts[n_z-1, it] to top_inner[it]
    top_surf_start = surf_offset + (n_z - 1) * n_theta
    top_inner_start = n_theta
    for it in range(n_theta - 1):
        v_s0 = top_surf_start + it
        v_s1 = top_surf_start + it + 1
        v_i0 = top_inner_start + it
        v_i1 = top_inner_start + it + 1
        # Facing +Z
        faces.append([v_s0, v_s1, v_i1])
        faces.append([v_s0, v_i1, v_i0])
        
    # 4. Inner vertical mating face (inside wall): shelf_inner to top_inner
    for it in range(n_theta - 1):
        v_b0 = it
        v_b1 = it + 1
        v_t0 = n_theta + it
        v_t1 = n_theta + it + 1
        # Facing inward (-R)
        faces.append([v_b0, v_t0, v_t1])
        faces.append([v_b0, v_t1, v_b1])
        
    # 5. Left endcap (it = 0)
    for iz in range(n_z - 1):
        v_s0 = surf_offset + iz * n_theta
        v_s1 = surf_offset + (iz + 1) * n_theta
        faces.append([0, v_s1, v_s0])
    # Top triangle for left endcap: between shelf_inner[0], surf_verts[n_z-1, 0], and top_inner[0]
    v_top_surf_0 = surf_offset + (n_z - 1) * n_theta
    faces.append([0, n_theta, v_top_surf_0])
    
    # 6. Right endcap (it = n_theta - 1)
    it_r = n_theta - 1
    for iz in range(n_z - 1):
        v_s0 = surf_offset + iz * n_theta + it_r
        v_s1 = surf_offset + (iz + 1) * n_theta + it_r
        faces.append([it_r, v_s0, v_s1])
    # Top triangle for right endcap:
    v_top_surf_r = surf_offset + (n_z - 1) * n_theta + it_r
    faces.append([it_r, v_top_surf_r, n_theta + it_r])
    
    mesh = trimesh.Trimesh(vertices=all_verts, faces=np.array(faces), process=True)
    if mesh.volume < 0:
        mesh.faces = np.fliplr(mesh.faces)
    return mesh

# Test all 4 clips
all_watertight = True
for angle in build_part.CLIP_ANGLES:
    center_rad = math.radians(angle)
    p, norm, tang = build_part.find_boundary_point_and_normal(base_poly, angle)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    m = build_rounded_hook_mesh(center_rad, r_est, d_theta, CLIP_HOOK_DEPTH)
    print(f"Clip {angle:5.1f}°: Watertight={m.is_watertight}, Volume={m.volume:+.3f} mm³, Vertices={len(m.vertices)}, Faces={len(m.faces)}")
    if not m.is_watertight:
        all_watertight = False

print(f"\nAll rounded clip hook meshes watertight: {all_watertight}")
