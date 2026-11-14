import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon, box
import build_part
from build_shaft import build_shaft_rocker_mesh

def build_contoured_trident():
    y_flat_b4 = 6.40
    z_flat_b4 = 5.60
    cos45 = np.cos(np.pi / 4)
    sin45 = np.sin(np.pi / 4)
    yp_b4_anchor = y_flat_b4 * cos45 - z_flat_b4 * sin45
    
    base_mesh, _ = build_part.build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_t = base_mesh.copy().apply_transform(R)
    z_min = m_t.bounds[0, 2]
    zp_b4_anchor = y_flat_b4 * sin45 + z_flat_b4 * cos45 - z_min
    
    zp_trunk_base = zp_b4_anchor + 0.55
    zp_fork_base = 23.60
    
    # Anchor neck at Bracket 4 top
    neck = trimesh.creation.box([1.40, 0.90, 0.80])
    neck.apply_translation([9.40, yp_b4_anchor, zp_b4_anchor + 0.15])
    
    # Trunk in Y-Z plane
    pts_trunk_yz = [
        (yp_b4_anchor - 0.40, zp_trunk_base),
        (-2.00, zp_fork_base),
        (-1.00, zp_fork_base),
        (yp_b4_anchor + 0.40, zp_trunk_base),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=2.40)
    vt = m_trunk_2d.vertices.copy()
    vt_3d = np.column_stack([vt[:, 2] + 9.40 - 1.20, vt[:, 0], vt[:, 1]])
    trunk = trimesh.Trimesh(vertices=vt_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if trunk.volume < 0:
        trunk.faces = np.fliplr(trunk.faces)
        
    # Profile in Y'-Z' plane matching the shaft curve from Y' = -2.80 to -0.90:
    # At Y' = -2.80: Z_shaft = 26.068 -> Z_top = 25.60
    # At Y' = -2.20: Z_shaft = 25.667 -> Z_top = 25.20
    # At Y' = -1.40: Z_shaft = 25.488 -> Z_top = 24.85
    # At Y' = -0.90: Z_shaft = 25.010 -> Z_top = 24.50
    pts_head_yz = [
        (-2.80, zp_fork_base),
        (-2.80, 25.60),
        (-2.20, 25.20),
        (-1.40, 24.85),
        (-0.90, 24.50),
        (-0.90, zp_fork_base),
    ]
    poly_head_yz = Polygon(pts_head_yz)
    
    # Extrude 3 separate tines across X in [8.00, 11.60]:
    # Tine 1: [8.00, 8.60] (width 0.60)
    # Tine 2: [9.50, 10.10] (width 0.60) -> supports Note 7 at X = 9.76, Y' = -2.21!
    # Tine 3: [11.00, 11.60] (width 0.60) -> supports Note 5 at X = 11.26!
    tines = []
    for x_start in [8.00, 9.50, 11.00]:
        m2d = trimesh.creation.extrude_polygon(poly_head_yz, height=0.60)
        v = m2d.vertices.copy()
        v_3d = np.column_stack([v[:, 2] + x_start, v[:, 0], v[:, 1]])
        tine_mesh = trimesh.Trimesh(vertices=v_3d, faces=m2d.faces.copy(), process=True)
        if tine_mesh.volume < 0:
            tine_mesh.faces = np.fliplr(tine_mesh.faces)
        tines.append(tine_mesh)
        
    # Cross-tie bridge connecting tines at the base (Z in [zp_fork_base, zp_fork_base + 0.60])
    bridge_box = trimesh.creation.box([3.60, 1.20, 0.60])
    bridge_box.apply_translation([9.80, -1.85, zp_fork_base + 0.30])
    
    return trimesh.util.concatenate([neck, trunk, bridge_box] + tines)

trident = build_contoured_trident()
shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, _ = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

prox = trimesh.proximity.ProximityQuery(shaft_t)
dist = prox.signed_distance(trident.vertices)
print(f"Max penetration: {dist.max():.4f} mm (must be <= 0.0)")

# Check at Note 7: [9.76224, -2.20633, 25.6702]
pt7 = np.array([9.76224, -2.20633, 25.6702])
d_pt7 = np.linalg.norm(trident.vertices - pt7, axis=1).min()
print(f"Distance from Note 7 to trident support: {d_pt7:.3f} mm")

top_t2_verts = trident.vertices[(trident.vertices[:, 0] >= 9.5) & (trident.vertices[:, 0] <= 10.1) & (trident.vertices[:, 2] > 24.5)]
gap_to_shaft = -prox.signed_distance(top_t2_verts)
print(f"Tine 2 gap to shaft: min = {gap_to_shaft.min():.4f} mm, max = {gap_to_shaft.max():.4f} mm, mean = {gap_to_shaft.mean():.4f} mm")
