import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import get_exact_base_polygon, CLIP_ARM_WIDTH, find_boundary_point_and_normal, OUTER_WALL_THICK
import numpy as np
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt

base_poly, outer_poly, _ = get_exact_base_polygon()
coords = np.array(outer_poly.exterior.coords)

r_curve = LineString(coords[4:55])
l_curve = LineString(list(reversed(coords[61:112])))

fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=160)

# 1. Right Side Bottom Quadrant
ax = axes[0]
ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2, label='Outer Body')
ax.plot(*outer_poly.buffer(-OUTER_WALL_THICK).exterior.xy, 'r--', linewidth=1, label='Inner Wall (1.2mm)')

# Ear bottom corner (18.206, -4.100)
ax.plot(18.206, -4.100, 'go', markersize=8, label='Right Ear Bottom Corner')
# Bottom tab corner (9.812, -15.950)
ax.plot(9.812, -15.950, 'mo', markersize=8, label='Bottom Tab Top Corner')

# Old position (325.5°)
pt_old, _, _ = find_boundary_point_and_normal(outer_poly, 325.5)
ax.plot(pt_old[0], pt_old[1], 'k^', markersize=9, label='Old Centered (325.5°): 7.2mm / 8.0mm')

# Option A: 4.42mm from Ear edge to clip near edge (clip center = 4.42 + 2.1 = 6.52mm) -> ~328.5°
pt_opt_a = r_curve.interpolate(6.52)
ang_a = np.degrees(np.arctan2(pt_opt_a.y, pt_opt_a.x)) % 360
ax.plot(pt_opt_a.x, pt_opt_a.y, 'rs', markersize=9, label=f'Edge-to-Edge Spacing ({ang_a:.1f}°): Gap to Ear=4.42mm')

# Option B: 4.42mm from Ear to Clip Center -> ~333.9°
pt_opt_b = r_curve.interpolate(4.42)
ang_b = np.degrees(np.arctan2(pt_opt_b.y, pt_opt_b.x)) % 360
ax.plot(pt_opt_b.x, pt_opt_b.y, 'cd', markersize=9, label=f'Center-to-Ear 4.42mm ({ang_b:.1f}°)')

# Option C: 8.47mm from Tab to Clip Center -> ~326.9°
pt_opt_c = r_curve.interpolate(r_curve.length - 8.47)
ang_c = np.degrees(np.arctan2(pt_opt_c.y, pt_opt_c.x)) % 360
ax.plot(pt_opt_c.x, pt_opt_c.y, 'y*', markersize=11, label=f'Center-to-Tab 8.47mm ({ang_c:.1f}°)')

# Option D: Proportional Ratio (4.42 / 12.89) -> ~331.5°
pt_opt_d = r_curve.interpolate(r_curve.length * (4.42 / 12.89))
ang_d = np.degrees(np.arctan2(pt_opt_d.y, pt_opt_d.x)) % 360
ax.plot(pt_opt_d.x, pt_opt_d.y, 'gX', markersize=9, label=f'Proportional ({ang_d:.1f}°): 5.2mm / 10.0mm')

ax.set_xlim(5, 23)
ax.set_ylim(-19, -2)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Right Bottom Clip Positioning Options', fontsize=12, fontweight='bold')
ax.legend(loc='lower left', fontsize=9)

# 2. Left Side Bottom Quadrant
ax = axes[1]
ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2, label='Outer Body')
ax.plot(*outer_poly.buffer(-OUTER_WALL_THICK).exterior.xy, 'r--', linewidth=1, label='Inner Wall (1.2mm)')

# Ear bottom corner (-19.081, -4.100)
ax.plot(-19.081, -4.100, 'go', markersize=8, label='Left Ear Bottom Corner')
# Bottom tab corner (-10.686, -15.950)
ax.plot(-10.686, -15.950, 'mo', markersize=8, label='Bottom Tab Top Corner')

# Old position (214.5°)
pt_old_l, _, _ = find_boundary_point_and_normal(outer_poly, 214.5)
ax.plot(pt_old_l[0], pt_old_l[1], 'k^', markersize=9, label='Old Centered (214.5°): 7.2mm / 7.6mm')

# Option A Left: Edge-to-Edge Spacing (clip center = 4.42 + 2.1 = 6.52mm from ear)
pt_opt_a_l = l_curve.interpolate(6.52)
ang_a_l = np.degrees(np.arctan2(pt_opt_a_l.y, pt_opt_a_l.x)) % 360
ax.plot(pt_opt_a_l.x, pt_opt_a_l.y, 'rs', markersize=9, label=f'Edge-to-Edge Spacing ({ang_a_l:.1f}°): Gap to Ear=4.42mm')

# Option B Left: 4.42mm from Ear to Clip Center
pt_opt_b_l = l_curve.interpolate(4.42)
ang_b_l = np.degrees(np.arctan2(pt_opt_b_l.y, pt_opt_b_l.x)) % 360
ax.plot(pt_opt_b_l.x, pt_opt_b_l.y, 'cd', markersize=9, label=f'Center-to-Ear 4.42mm ({ang_b_l:.1f}°)')

# Option C Left: 8.47mm from Tab to Clip Center
pt_opt_c_l = l_curve.interpolate(l_curve.length - 8.47)
ang_c_l = np.degrees(np.arctan2(pt_opt_c_l.y, pt_opt_c_l.x)) % 360
ax.plot(pt_opt_c_l.x, pt_opt_c_l.y, 'y*', markersize=11, label=f'Center-to-Tab 8.47mm ({ang_c_l:.1f}°)')

# Option D Left: Proportional Ratio
pt_opt_d_l = l_curve.interpolate(l_curve.length * (4.42 / 12.89))
ang_d_l = np.degrees(np.arctan2(pt_opt_d_l.y, pt_opt_d_l.x)) % 360
ax.plot(pt_opt_d_l.x, pt_opt_d_l.y, 'gX', markersize=9, label=f'Proportional ({ang_d_l:.1f}°)')

ax.set_xlim(-23, -5)
ax.set_ylim(-19, -2)
ax.set_aspect('equal')
ax.grid(True)
ax.set_title('Left Bottom Clip Positioning Options', fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig('testing/bottom_clip_options_plot.png', dpi=160)
print("Saved testing/bottom_clip_options_plot.png")
