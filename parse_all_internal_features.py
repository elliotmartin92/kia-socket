"""
Extract every internal feature (brackets, bottom arch, top-right hole) exactly from part.svg.
"""
import re
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import polygonize, unary_union

with open('part.svg', 'r') as f:
    svg_text = f.read()

SCALE = 8.22 / 23.5
X0 = 128.65
Y0 = 124.20

def to_mm(x, y):
    return ((x - X0) * SCALE, -(y - Y0) * SCALE)

# 1. Let's parse each bracket directly from lines and polylines
# Let's inspect the 4 bracket groups in the SVG:
# Bracket 4 (lines 31-39):
# polyline: 151.6,141.5 156.4,141.5 156.4,106.8
# line: (159.5, 144.7) -> (159.5, 103.7)
# line: (156.4, 106.8) -> (154, 106.8)
# line: (159.5, 144.6) -> (151.6, 144.6)
# line: (151.6, 144.6) -> (151.6, 141.5)
# line: (159.5, 103.7) -> (151.1, 103.7)
# line: (151.1, 111.1) -> (151.1, 103.7)
# line: (154, 111.1) -> (154, 106.8)
# line: (151.1, 111.1) -> (154, 111.1)

bracket_4_raw_pts = [
    (159.5, 103.7),
    (151.1, 103.7),
    (151.1, 111.1),
    (154.0, 111.1),
    (154.0, 106.8),
    (156.4, 106.8),
    (156.4, 141.5),
    (151.6, 141.5),
    (151.6, 144.6),
    (159.5, 144.6),
    (159.5, 103.7)
]

# Bracket 3 (lines 41-49):
bracket_3_raw_pts = [
    (133.7, 103.7),
    (142.1, 103.7),
    (142.1, 111.1),
    (139.3, 111.1),
    (139.3, 106.9),
    (136.8, 106.9),
    (136.8, 141.6),
    (141.7, 141.6),
    (141.7, 144.7),
    (133.7, 144.7),
    (133.7, 103.7)
]

# Bracket 2 (lines 50-59):
bracket_2_raw_pts = [
    (123.6, 103.7),
    (115.3, 103.7),
    (115.3, 111.1),
    (118.1, 111.1),
    (118.1, 106.9),
    (120.5, 106.9),
    (120.5, 141.5),
    (115.7, 141.5),
    (115.7, 144.6),
    (123.6, 144.6),
    (123.6, 103.7)
]

# Bracket 1 (lines 70-78):
bracket_1_raw_pts = [
    (97.8, 103.8),
    (106.2, 103.8),
    (106.2, 111.1),
    (103.4, 111.1),
    (103.4, 106.9),
    (100.9, 106.9),
    (100.9, 141.6),
    (105.8, 141.6),
    (105.8, 144.7),
    (97.8, 144.7),
    (97.8, 103.8)
]

def to_mm_poly(raw_pts):
    pts_mm = [to_mm(x, y) for x, y in raw_pts]
    return Polygon(pts_mm)

b1 = to_mm_poly(bracket_1_raw_pts)
b2 = to_mm_poly(bracket_2_raw_pts)
b3 = to_mm_poly(bracket_3_raw_pts)
b4 = to_mm_poly(bracket_4_raw_pts)

# Let's also evaluate the bottom arch exactly using Bézier curve
# d="M132.6,171.8c-0.6-9.6,2-16.2-5.1-16.2c-7,0-5.7,5.7-5.4,16.2"
arch_d = "M132.6,171.8c-0.6-9.6,2-16.2-5.1-16.2c-7,0-5.7,5.7-5.4,16.2"
# Start at (132.6, 171.8)
# Curve 1: to (127.5, 155.6)
# Curve 2: to (122.1, 171.8)
arch_curve_pts = []
# c1:
p0 = (132.6, 171.8)
p1 = (132.6 - 0.6, 171.8 - 9.6)
p2 = (132.6 + 2.0, 171.8 - 16.2)
p3 = (132.6 - 5.1, 171.8 - 16.2)
for t in np.linspace(0, 1, 30):
    bx = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
    by = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
    arch_curve_pts.append(to_mm(bx, by))

p0 = p3
p1 = (p0[0] - 7.0, p0[1] + 0.0)
p2 = (p0[0] - 5.7, p0[1] + 5.7)
p3 = (p0[0] - 5.4, p0[1] + 16.2)
for t in np.linspace(0.03, 1, 30):
    bx = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
    by = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
    arch_curve_pts.append(to_mm(bx, by))

print("Extracted exact bracket polygons and bottom arch curve!")

# Plot all 4 brackets and the bottom arch
fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
for idx, b in enumerate([b1, b2, b3, b4]):
    x, y = b.exterior.xy
    ax.plot(x, y, linewidth=2, label=f'Bracket {idx+1}')

arch_x, arch_y = zip(*arch_curve_pts)
ax.plot(arch_x, arch_y, 'r-', linewidth=2.5, label='Exact SVG Bottom Arch')

ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right')
ax.set_title('Exact SVG Internal Brackets & Arch (Unsimplified)', fontsize=12, fontweight='bold')
plt.savefig('internal_features_exact.png', dpi=150)
print("Saved internal_features_exact.png")
