"""
Test clean grid ribs connecting directly to the outer walls.
"""
import shapely.geometry as sg
from shapely.ops import unary_union
import numpy as np
import matplotlib.pyplot as plt

from build_part import (
    get_exact_base_polygon, bracket_1_raw_pts, bracket_2_raw_pts,
    bracket_3_raw_pts, bracket_4_raw_pts, X0, Y0, SCALE,
    RIB_GRID_X, RIB_GRID_Y, RIB_THICK, OUTER_WALL_THICK
)

base_poly, outer_body_poly, hole_info = get_exact_base_polygon()
inner_wall_poly = outer_body_poly.buffer(-OUTER_WALL_THICK)
hole_x, hole_y, hole_w, hole_h = hole_info

hole_box = sg.box(hole_x - hole_w/2, hole_y - hole_h/2, hole_x + hole_w/2, hole_y + hole_h/2)

b1_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_1_raw_pts]
b2_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_2_raw_pts]
b3_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_3_raw_pts]
b4_pts = [((x - X0)*SCALE, -(y - Y0)*SCALE) for x, y in bracket_4_raw_pts]

# Bracket envelopes
left_pair_bbox = sg.box(
    min(p[0] for p in b1_pts) - 0.05,
    min(p[1] for p in b1_pts) - 0.05,
    max(p[0] for p in b2_pts) + 0.05,
    max(p[1] for p in b2_pts) + 0.05
)

right_pair_bbox = sg.box(
    min(p[0] for p in b3_pts) - 0.05,
    min(p[1] for p in b3_pts) - 0.05,
    max(p[0] for p in b4_pts) + 0.05,
    max(p[1] for p in b4_pts) + 0.05
)

bracket_exclusions = unary_union([left_pair_bbox, right_pair_bbox])
below_brackets_box = sg.box(-30.0, -30.0, 30.0, -7.17)

# Generate thin rib strips (0.60mm thick)
bounds = outer_body_poly.bounds
rib_strips = []

# X lines (vertical ribs)
x_vals = np.concatenate([
    np.arange(0, bounds[2] + 2, RIB_GRID_X),
    np.arange(-RIB_GRID_X, bounds[0] - 2, -RIB_GRID_X)
])
for x in x_vals:
    rib_strips.append(sg.box(x - RIB_THICK/2, bounds[1] - 2, x + RIB_THICK/2, bounds[3] + 2))

# Y lines (horizontal ribs)
y_vals = np.concatenate([
    np.arange(0, bounds[3] + 2, RIB_GRID_Y),
    np.arange(-RIB_GRID_Y, bounds[1] - 2, -RIB_GRID_Y)
])
for y in y_vals:
    rib_strips.append(sg.box(bounds[0] - 2, y - RIB_THICK/2, bounds[2] + 2, y + RIB_THICK/2))

raw_grid = unary_union(rib_strips)

# Ribs extend up to the outer body polygon (connecting firmly to the inner wall face / outer wall)
connected_ribs = raw_grid.intersection(outer_body_poly).difference(bracket_exclusions).difference(below_brackets_box).difference(hole_box)

# Plot
fig, ax = plt.subplots(figsize=(12, 12), dpi=160)

x, y = outer_body_poly.exterior.xy
ax.plot(x, y, color='#1f77b4', linewidth=2.5, label='Perimeter Wall')

ix, iy = inner_wall_poly.exterior.xy
ax.plot(ix, iy, color='#1f77b4', linestyle='--', linewidth=1.2, label='Inner Wall Face')

for g in (connected_ribs.geoms if hasattr(connected_ribs, 'geoms') else [connected_ribs]):
    gx, gy = g.exterior.xy
    ax.fill(gx, gy, color='#ff7f0e', alpha=0.8, edgecolor='#d95f02', linewidth=0.5)

ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_title('Floor Ribs (0.6mm wide, 5.2x3.2mm grid) Connected to Outer Walls', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('connected_ribs_clean.png', dpi=160)
print("Saved connected_ribs_clean.png")
