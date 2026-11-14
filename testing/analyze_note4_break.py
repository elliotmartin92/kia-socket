import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

part_mesh_flat, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_t = part_mesh_flat.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

c_feat = build_part.build_center_curved_feature_mesh()
c_feat_t = c_feat.copy().apply_transform(R)
c_feat_t.apply_translation([0, 0, -z_min])

print("Center curved feature bounds in tilted print coords:")
print(f"X: [{c_feat_t.bounds[0, 0]:.3f}, {c_feat_t.bounds[1, 0]:.3f}]")
print(f"Y': [{c_feat_t.bounds[0, 1]:.3f}, {c_feat_t.bounds[1, 1]:.3f}]")
print(f"Z': [{c_feat_t.bounds[0, 2]:.3f}, {c_feat_t.bounds[1, 2]:.3f}]")

p4 = np.array([6.40519, -3.52354, 11.5385])
p2 = np.array([6.48746, -6.26706, 12.2343])

# Untilt p4 and p2
rot_45_2d = np.array([
    [np.cos(np.radians(45.0)), -np.sin(np.radians(45.0))],
    [np.sin(np.radians(45.0)),  np.cos(np.radians(45.0))]
])

def untilt(p):
    x = p[0]
    yz_t = np.array([p[1], p[2] + z_min])
    yz = rot_45_2d.T @ yz_t
    return np.array([x, yz[0], yz[1]])

p4_orig = untilt(p4)
p2_orig = untilt(p2)

print(f"\nNote 4 in tilted print coords: {p4}")
print(f"Note 4 in untransformed coords: [X={p4_orig[0]:.3f}, Y={p4_orig[1]:.3f}, Z={p4_orig[2]:.3f}]")

print(f"\nNote 2 in tilted print coords: {p2}")
print(f"Note 2 in untransformed coords: [X={p2_orig[0]:.3f}, Y={p2_orig[1]:.3f}, Z={p2_orig[2]:.3f}]")

# Let's slice c_feat_t along the layer line at Z' = 11.54 to 12.23
slice_115 = c_feat_t.section(plane_origin=[0, 0, 11.5385], plane_normal=[0, 0, 1])
if slice_115 is not None:
    poly_2d = slice_115.to_2D()[0]
    print(f"\nAt Z' = 11.54mm (layer slice of Note 4):")
    print(f"  Area of wall cross section: {poly_2d.polygons_full[0].area:.3f} mm^2")
    print(f"  Bounds in print coords: {slice_115.bounds.tolist()}")
