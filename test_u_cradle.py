"""
Verify clean U-cradle polygon profile.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import trimesh
import matplotlib.pyplot as plt

y_min = 5.341
y_max = 9.991
y_shaft = (y_min + y_max) / 2.0  # 7.666mm

z_base = 1.00
z_top = 13.59
r_shaft = 1.00
z_cradle_center = z_top - r_shaft  # 12.59mm

# Angle from 0 to pi:
# At a = 0: cos(0)=1 -> y = y_shaft + r_shaft, sin(0)=0 -> z = z_cradle_center
# At a = pi/2: cos(pi/2)=0 -> y = y_shaft, sin(pi/2)=1 -> z = z_cradle_center - r_shaft (bottom of U)
# At a = pi: cos(pi)=-1 -> y = y_shaft - r_shaft, sin(pi)=0 -> z = z_cradle_center
angles = np.linspace(0, np.pi, 32)
arc_pts = [(y_shaft + r_shaft * np.cos(a), z_cradle_center - r_shaft * np.sin(a)) for a in angles]

profile_yz = [
    (y_min, z_base),
    (y_max, z_base),
    (y_max, z_top),
    (y_shaft + r_shaft, z_top),
    (y_shaft + r_shaft, z_cradle_center),
] + arc_pts + [
    (y_shaft - r_shaft, z_cradle_center),
    (y_shaft - r_shaft, z_top),
    (y_min, z_top)
]

poly = Polygon(profile_yz)
print("Is valid polygon:", poly.is_valid)

# Plot polygon
fig, ax = plt.subplots(figsize=(6, 8), dpi=160)
py, pz = poly.exterior.xy
ax.plot(py, pz, 'b-o', markersize=3)
ax.set_title(f'U-Cradle Profile (Valid: {poly.is_valid})')
ax.set_xlabel('Y (mm)')
ax.set_ylabel('Z (mm)')
ax.set_aspect('equal')
ax.grid(True)
plt.savefig('u_cradle_profile_test.png', dpi=160)
print("Saved u_cradle_profile_test.png")

# Test 3D extrusion
m_raw = trimesh.creation.extrude_polygon(poly, height=1.25)
print("Mesh is watertight:", m_raw.is_watertight)
print("Mesh is volume:", m_raw.volume)
