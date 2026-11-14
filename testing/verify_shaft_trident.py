import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
from shapely.geometry import Polygon
import build_part
from build_shaft import build_shaft_rocker_mesh

def build_test_shaft_trident():
    shaft_s_x_c = 9.80  # center between 8.00 and 11.60
    cos45 = np.cos(np.pi / 4)
    sin45 = np.sin(np.pi / 4)
    y_flat_b4 = 6.40
    z_flat_b4 = 5.60
    yp_b4_anchor = y_flat_b4 * cos45 - z_flat_b4 * sin45
    
    # We need z_min
    base_mesh, _ = build_part.build_exact_3d_model()
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_t = base_mesh.copy().apply_transform(R)
    z_min = m_t.bounds[0, 2]
    zp_b4_anchor = y_flat_b4 * sin45 + z_flat_b4 * cos45 - z_min
    
    yp_hub_target = -1.450
    z_shaft_stick_top = 24.850  # calibrated release gap
    zp_trunk_base = zp_b4_anchor + 0.55
    zp_fork_base = 23.60
    
    # Bracket 4 anchor neck: 0.90 x 0.90 at Bracket 4 center X = 9.40
    neck = trimesh.creation.box([1.40, 0.90, 0.80])
    neck.apply_translation([9.40, yp_b4_anchor, zp_b4_anchor + 0.15])
    
    # Trunk in Y-Z plane
    pts_trunk_yz = [
        (yp_b4_anchor - 0.40, zp_trunk_base),
        (yp_hub_target - 0.35, zp_fork_base),
        (yp_hub_target + 0.35, zp_fork_base),
        (yp_b4_anchor + 0.40, zp_trunk_base),
    ]
    poly_trunk_yz = Polygon(pts_trunk_yz)
    m_trunk_2d = trimesh.creation.extrude_polygon(poly_trunk_yz, height=2.40)
    vt = m_trunk_2d.vertices.copy()
    vt_3d = np.column_stack([vt[:, 2] + 9.40 - 1.20, vt[:, 0], vt[:, 1]])
    trunk = trimesh.Trimesh(vertices=vt_3d, faces=m_trunk_2d.faces.copy(), process=True)
    if trunk.volume < 0:
        trunk.faces = np.fliplr(trunk.faces)
        
    # Trident head in X-Z plane:
    # Spans X in [8.00, 11.60] (width 3.60mm)
    # Tine 1: [8.00, 8.55]
    # Notch 1: [8.55, 9.50] (notch apex at Z = 24.05)
    # Tine 2: [9.50, 10.10]
    # Notch 2: [10.10, 11.05] (notch apex at Z = 24.05)
    # Tine 3: [11.05, 11.60]
    z_notch = z_shaft_stick_top - 0.80  # 24.05
    pts_head_xz = [
        (8.00, zp_fork_base),
        (8.00, z_shaft_stick_top),
        (8.55, z_shaft_stick_top),
        (9.025, z_notch),
        (9.50, z_shaft_stick_top),
        (10.10, z_shaft_stick_top),
        (10.575, z_notch),
        (11.05, z_shaft_stick_top),
        (11.60, z_shaft_stick_top),
        (11.60, zp_fork_base),
    ]
    poly_head_xz = Polygon(pts_head_xz)
    m_head_2d = trimesh.creation.extrude_polygon(poly_head_xz, height=0.70)
    vh = m_head_2d.vertices.copy()
    vh_3d = np.column_stack([vh[:, 0], vh[:, 2] - 0.35 + yp_hub_target, vh[:, 1]])
    head = trimesh.Trimesh(vertices=vh_3d, faces=m_head_2d.faces.copy(), process=True)
    if head.volume < 0:
        head.faces = np.fliplr(head.faces)
        
    return trimesh.util.concatenate([neck, trunk, head])

shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]
m_t.apply_translation([0, 0, -z_min])

shaft_t = shaft_mesh.copy().apply_transform(R)
shaft_t.apply_translation([0, 0, -z_min])

trident = build_test_shaft_trident()
print(f"Trident bounds: {trident.bounds.tolist()}, volume: {trident.volume:.2f} mm^3")

prox_shaft = trimesh.proximity.ProximityQuery(shaft_t)
dist_shaft = prox_shaft.signed_distance(trident.vertices)
print(f"Max penetration into shaft: {dist_shaft.max():.4f} mm (must be <= 0.0)")

top_verts = trident.vertices[trident.vertices[:, 2] > 24.8]
gap_to_shaft = -prox_shaft.signed_distance(top_verts)
print(f"Min gap to shaft at trident lands: {gap_to_shaft.min():.4f} mm")
print(f"Max gap to shaft at trident lands: {gap_to_shaft.max():.4f} mm")
print(f"Mean gap to shaft at trident lands: {gap_to_shaft.mean():.4f} mm")

prox_base = trimesh.proximity.ProximityQuery(m_t)
dist_base = prox_base.signed_distance(trident.vertices)
print(f"Max penetration into base part (outside anchor neck): {dist_base.max():.4f} mm")
