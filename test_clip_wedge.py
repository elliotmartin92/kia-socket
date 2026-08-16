"""
Test modeling snap clips by adding hook wedges directly to the slotted wall.
"""
import numpy as np
import trimesh
import shapely.geometry as sg
from shapely.geometry import Polygon, box, LineString
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math

from build_part import (
    get_exact_base_polygon, OUTER_WALL_THICK, OUTER_WALL_HEIGHT,
    BASE_THICK, CLIP_HEIGHT, CLIP_HOOK_HEIGHT, CLIP_ARM_WIDTH,
    CLIP_HOOK_DEPTH, CLIP_GAP_DEPTH, find_boundary_point_and_normal
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
wall_2d = outer_body_poly.difference(inner_wall_poly)

# Base mesh
mesh_base = trimesh.creation.extrude_polygon(base_poly, height=BASE_THICK)

# Full continuous wall mesh
mesh_wall = trimesh.creation.extrude_polygon(wall_2d, height=OUTER_WALL_HEIGHT - BASE_THICK)
mesh_wall.apply_translation([0, 0, BASE_THICK])

# Cut two vertical flex slots for each clip
slot_cuts = []
hook_meshes = []

stem_h = CLIP_HEIGHT - CLIP_HOOK_HEIGHT  # 4.97 mm
slot_z_bot = OUTER_WALL_HEIGHT - CLIP_GAP_DEPTH  # 3.07 mm
slot_t = 0.60  # Slot clearance width (0.60mm)

for angle_deg in [45, 135, 225, 315]:
    center_rad = math.radians(angle_deg)
    p, norm, tang = find_boundary_point_and_normal(base_poly, angle_deg)
    r_est = np.linalg.norm(p)
    d_theta = CLIP_ARM_WIDTH / r_est
    slot_d_theta = slot_t / r_est
    
    # Left slot angle range: [center_rad - d_theta/2 - slot_d_theta, center_rad - d_theta/2]
    # Right slot angle range: [center_rad + d_theta/2, center_rad + d_theta/2 + slot_d_theta]
    for th_slot_center in [center_rad - d_theta/2 - slot_d_theta/2, center_rad + d_theta/2 + slot_d_theta/2]:
        slot_p = np.array([np.cos(th_slot_center), np.sin(th_slot_center)]) * r_est
        slot_norm_angle = th_slot_center
        rot_mat = trimesh.transformations.rotation_matrix(slot_norm_angle, [0, 0, 1])
        s_box = trimesh.creation.box([OUTER_WALL_THICK * 4.0, slot_t, CLIP_GAP_DEPTH + 1.0])
        s_box.apply_transform(rot_mat)
        s_box.apply_translation([slot_p[0], slot_p[1], slot_z_bot + (CLIP_GAP_DEPTH + 1.0)/2])
        slot_cuts.append(s_box)
        
    # Hook Wedge: Triangular wedge sitting on the outer face of the beam (Z: 4.97 to 6.77mm)
    N = 16
    theta_vals = np.linspace(center_rad - d_theta/2.0, center_rad + d_theta/2.0, N)
    
    outer_coords = []
    shelf_coords = []
    
    for th in theta_vals:
        ray_dir = np.array([np.cos(th), np.sin(th)])
        ray = LineString([(0, 0), (ray_dir[0] * 50, ray_dir[1] * 50)])
        inter_out = outer_body_poly.exterior.intersection(ray)
        if inter_out.geom_type == 'Point':
            po = np.array([inter_out.x, inter_out.y])
        elif hasattr(inter_out, 'geoms') and len(inter_out.geoms) > 0:
            po = np.array([inter_out.geoms[-1].x, inter_out.geoms[-1].y])
        else:
            po = ray_dir * r_est
            
        n_dir = po / np.linalg.norm(po)
        ps = po + n_dir * CLIP_HOOK_DEPTH
        outer_coords.append(po)
        shelf_coords.append(ps)
        
    outer_coords = np.array(outer_coords)
    shelf_coords = np.array(shelf_coords)
    
    # 3D vertices for the hook wedge:
    # 0..N-1:    V0 = (outer_coords, stem_h)    -> bottom-inner of hook (on outer wall at Z = 4.97)
    # N..2N-1:   V1 = (shelf_coords, stem_h)    -> bottom-outer shelf tip (at Z = 4.97)
    # 2N..3N-1:  V2 = (outer_coords, CLIP_HEIGHT) -> top apex (on outer wall at Z = 6.77)
    v0 = np.column_stack([outer_coords, np.full(N, stem_h)])
    v1 = np.column_stack([shelf_coords, np.full(N, stem_h)])
    v2 = np.column_stack([outer_coords, np.full(N, CLIP_HEIGHT)])
    hook_verts = np.vstack([v0, v1, v2])
    
    hook_faces = []
    for i in range(N - 1):
        # 1. Undercut shelf face (at stem_h, pointing -Z): V0 -> V1
        hook_faces.append([i, N + i, N + i + 1])
        hook_faces.append([i, N + i + 1, i + 1])
        
        # 2. Slanted outer bevel (pointing +radial/+Z): V1 -> V2
        hook_faces.append([N + i, 2*N + i + 1, N + i + 1])
        hook_faces.append([N + i, 2*N + i, 2*N + i + 1])
        
        # 3. Inner mating face (at outer wall, pointing -radial): V2 -> V0
        hook_faces.append([2*N + i, i, i + 1])
        hook_faces.append([2*N + i, i + 1, 2*N + i + 1])
        
    # Side endcaps (Triangles at i=0 and i=N-1)
    # Left endcap (pointing -tangent): (v0[0], v2[0], v1[0])
    hook_faces.append([0, 2*N, N])
    # Right endcap (pointing +tangent): (v0[N-1], v1[N-1], v2[N-1])
    hook_faces.append([N - 1, 2*N - 1, 3*N - 1])
    
    hook_mesh = trimesh.Trimesh(vertices=hook_verts, faces=np.array(hook_faces), process=True)
    hook_meshes.append(hook_mesh)

all_slot_cuts = trimesh.util.concatenate(slot_cuts)
mesh_wall_slotted = mesh_wall.difference(all_slot_cuts, engine='manifold')
all_hooks = trimesh.util.concatenate(hook_meshes)

complete_wall = trimesh.util.concatenate([mesh_wall_slotted, all_hooks])
print("Slotted wall watertight:", mesh_wall_slotted.is_watertight)
print("Complete wall with hooks watertight:", complete_wall.is_watertight)

# Plot detailed views
fig = plt.figure(figsize=(16, 8), dpi=160)
p45, _, _ = find_boundary_point_and_normal(base_poly, 45)
dists = np.linalg.norm(complete_wall.vertices[:, :2] - p45[:2], axis=1)
mask = np.all(dists[complete_wall.faces] < 5.0, axis=1)
faces = complete_wall.faces[mask]

ax1 = fig.add_subplot(1, 2, 1, projection='3d')
col1 = Poly3DCollection(complete_wall.vertices[faces], alpha=0.9, edgecolor='#222222', linewidths=0.25)
col1.set_facecolor('#00acc1')
ax1.add_collection3d(col1)
ax1.set_xlim(p45[0] - 3.5, p45[0] + 3.5)
ax1.set_ylim(p45[1] - 3.5, p45[1] + 3.5)
ax1.set_zlim(0, 8)
ax1.view_init(elev=20, azim=225)
ax1.set_title("New Slotted Wall + Direct Hook Wedge (Outer View)", fontsize=11, fontweight='bold')

ax2 = fig.add_subplot(1, 2, 2, projection='3d')
col2 = Poly3DCollection(complete_wall.vertices[faces], alpha=0.9, edgecolor='#222222', linewidths=0.25)
col2.set_facecolor('#00acc1')
ax2.add_collection3d(col2)
ax2.set_xlim(p45[0] - 3.5, p45[0] + 3.5)
ax2.set_ylim(p45[1] - 3.5, p45[1] + 3.5)
ax2.set_zlim(0, 8)
ax2.view_init(elev=0, azim=135)
ax2.set_title("New Slotted Wall + Direct Hook Wedge (Side Tangent View)", fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('new_clip_wedge_views.png', dpi=160)
print("Saved new_clip_wedge_views.png")
