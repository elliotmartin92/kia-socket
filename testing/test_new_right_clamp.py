import sys
sys.path.insert(0, '.')
import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
import build_clamp
from build_part import get_exact_base_polygon, OUTER_WALL_THICK

base_poly, outer_body_poly, _ = get_exact_base_polygon()
inner_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)

Z_TOP = 14.090
CLAMP_ROOF_THICK = 1.60
z_top = Z_TOP + CLAMP_ROOF_THICK
z_roof_under = Z_TOP
z_bot = 11.200

# Right clamp components
y_front_inner_top = 6.550 - 0.020
y_front_inner_bot = 6.484 - 0.010
y_rear_inner_top = 12.180 + 0.020
y_rear_inner_bot = 12.328 + 0.010

y_front_outer_top = y_front_inner_top - 1.40
y_front_outer_bot = y_front_inner_bot - 1.40
y_rear_outer_top = 12.650
y_rear_outer_bot = 12.650

saddle_right_pts_yz = [
    (y_front_outer_bot, z_bot),
    (y_front_outer_top, z_top - 0.50),
    (y_front_outer_top + 0.50, z_top),
    (y_rear_outer_top - 0.30, z_top),
    (y_rear_outer_top, z_top - 0.30),
    (y_rear_outer_bot, z_bot),
    (y_rear_inner_bot, z_bot),
    (y_rear_inner_top, z_roof_under),
    (11.20, z_roof_under),
    (build_clamp.Y_RELIEF_REAR, build_clamp.Z_PIN_RELIEF),
    (build_clamp.Y_RELIEF_FRONT, build_clamp.Z_PIN_RELIEF),
    (7.35, z_roof_under),
    (y_front_inner_top, z_roof_under),
    (y_front_inner_bot, z_bot),
]
poly_saddle_right = Polygon(saddle_right_pts_yz)

y_c = 9.279
z_c = 12.590
R = 1.85
arch_pts = []
for p in np.linspace(0, np.pi, 32):
    arch_pts.append((y_c + R * np.cos(p), z_c + R * np.sin(p)))

side_right_pts_yz = [
    (7.10, z_bot),
    (7.10, 14.09),
    (7.10, z_top),
    (11.00, z_top),
    (11.00, 14.09),
    (11.00, z_bot),
    (y_c + R, z_bot),
] + arch_pts + [
    (y_c - R, z_bot)
]
poly_side_right = Polygon(side_right_pts_yz)

m_saddle = build_clamp.extrude_yz(poly_saddle_right, height=14.60 - 13.20, x_offset=13.20)
m_cheek = build_clamp.extrude_yz(poly_side_right, height=15.05 - 14.60, x_offset=14.60)
poly_hook_right_xz = Polygon([
    (15.05, 11.75),
    (14.65, 12.15),
    (14.65, 12.35),
    (15.05, 12.35)
])
m_hf = build_clamp.extrude_xz(poly_hook_right_xz, height=8.00 - 7.10, y_offset=7.10)
c_right = build_clamp.unary_union_meshes([m_saddle, m_cheek, m_hf])

# Left clamp
c_left = build_clamp.build_tower_clamp_mesh('left', in_assembly_coords=True)

# Tie Bar
tie_pts_yz = [
    (11.85, 13.50),
    (11.85, z_top),
    (12.65, z_top),
    (12.65, 13.50)
]
poly_tie_yz = Polygon(tie_pts_yz)
m_tie = build_clamp.extrude_yz(poly_tie_yz, height=13.20 - 5.30, x_offset=5.30)

unified = build_clamp.unary_union_meshes([c_left, m_tie, c_right])
print("Unified clamp watertight:", unified.is_watertight, "volume:", unified.volume)
print("Unified bounds:", unified.bounds)

out_pts = []
for v in unified.vertices:
    p = Point(v[0], v[1])
    if not outer_body_poly.contains(p):
        out_pts.append(v)

print(f"Unified clamp vertices outside outer_body_poly: {len(out_pts)}")
dists_ext = [outer_body_poly.exterior.distance(Point(v[0], v[1])) for v in unified.vertices]
print(f"Minimum clearance to exterior wall: {min(dists_ext):.3f} mm")
