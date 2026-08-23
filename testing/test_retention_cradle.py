"""
Visualize and test the retention shaft cradle with 1.65mm throat opening.
"""
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

y_min = 5.341
y_max = 9.991
y_shaft = (y_min + y_max) / 2.0  # 7.666 mm

z_base = 1.00
z_top = 13.59
r_shaft = 1.00  # 2.00 mm diameter shaft
z_cradle_center = 12.59

# Throat opening width = 1.65 mm
throat_w = 1.65
half_w = throat_w / 2.0  # 0.825 mm
alpha = np.arcsin(half_w / r_shaft)  # 55.59 deg from vertical, 34.41 deg above horizontal
z_throat = z_cradle_center + r_shaft * np.cos(alpha)  # 13.155 mm

# Circular arc from right throat tip (theta = +alpha) down around bottom to left throat tip (theta = -alpha)
# In standard polar angle measured from +Y axis (horizontal right):
# Right tip: angle_start = 90 - 55.59 = 34.41 deg = +0.6006 rad
# Arc goes CCW through 0 to -90 (bottom) to 180 to (180 - 34.41) = 145.59 deg
# Or measured from -Z axis (bottom = 0): angle from -124.41 deg to +124.41 deg
th = np.linspace(- (np.pi - alpha), (np.pi - alpha), 60)
# Bottom is at a = -pi/2
# Let's parameterize nicely:
# Angle phi from 0 (right tip at +alpha from top) to pi + 2*alpha
phi = np.linspace(np.pi/2 - alpha, -np.pi - (np.pi/2 - alpha), 64)
# Let's check:
# phi = pi/2 - alpha: x = r*cos(phi) = r*sin(alpha) = +half_w, y = r*sin(phi) = r*cos(alpha) = +delta_z
# phi = -pi/2: x = 0, y = -r (bottom)
# phi = -pi - (pi/2 - alpha) = -3pi/2 + alpha = +pi/2 + alpha: x = -half_w, y = +delta_z

cradle_arc_pts = []
for p in phi:
    cy = y_shaft + r_shaft * np.cos(p)
    cz = z_cradle_center + r_shaft * np.sin(p)
    cradle_arc_pts.append((cy, cz))

# Top lead-in chamfer from throat tips up to z_top
# Left throat tip is at (y_shaft - half_w, z_throat)
# Right throat tip is at (y_shaft + half_w, z_throat)
# Chamfer slopes up to (y_shaft - half_w - 0.35, z_top) and (y_shaft + half_w + 0.35, z_top)
y_left_top = y_shaft - half_w - 0.30
y_right_top = y_shaft + half_w + 0.30

profile_yz = [
    (y_min, z_base),
    (y_max, z_base),
    (y_max, z_top),
    (y_right_top, z_top),
] + cradle_arc_pts + [
    (y_left_top, z_top),
    (y_min, z_top)
]

poly_cradle = Polygon(profile_yz)

fig, ax = plt.subplots(figsize=(10, 8), dpi=160)
ax.plot(*poly_cradle.exterior.xy, 'b-', linewidth=2, label='Tower Profile in (Y, Z)')
ax.fill(*poly_cradle.exterior.xy, color='#00bcd4', alpha=0.35)

# Plot Ø2.0mm shaft inside cradle
shaft_angles = np.linspace(0, 2*np.pi, 50)
shaft_y = y_shaft + r_shaft * np.cos(shaft_angles)
shaft_z = z_cradle_center + r_shaft * np.sin(shaft_angles)
ax.plot(shaft_y, shaft_z, 'r--', linewidth=1.5, label='Ø2.00mm Retained Shaft')
ax.fill(shaft_y, shaft_z, color='#ff9800', alpha=0.3)
ax.plot(y_shaft, z_cradle_center, 'r+', markersize=10, label='Shaft Axis (Y=7.67, Z=12.59mm)')

# Annotate 1.65mm throat
ax.annotate('', xy=(y_shaft - half_w, z_throat), xytext=(y_shaft + half_w, z_throat),
            arrowprops=dict(arrowstyle='<->', color='purple', lw=1.8))
ax.text(y_shaft, z_throat + 0.15, '1.65 mm\nRetention Throat', ha='center', va='bottom', fontweight='bold', color='purple', fontsize=10)

ax.set_xlim(y_min - 0.5, y_max + 0.5)
ax.set_ylim(10.0, 14.5)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Shaft Retention Cradle Profile: Wrap-Around with 1.65mm Retention Gap', fontsize=12, fontweight='bold')
ax.set_xlabel('Y (mm)')
ax.set_ylabel('Z (mm)')
ax.legend(loc='lower left')

plt.tight_layout()
plt.savefig('retention_cradle_preview.png', dpi=160)
print("Saved retention_cradle_preview.png")
