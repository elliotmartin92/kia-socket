import trimesh
import numpy as np

p4 = np.array([6.40519, -3.52354, 11.5385])
p5 = np.array([6.60662, -5.26423, 11.2315])

z_min = -13.1091
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
p5_orig = untilt(p5)

print(f"Note 4 ('Back of break'):")
print(f"  Tilted:  {p4}")
print(f"  Original: [X={p4_orig[0]:.3f}, Y={p4_orig[1]:.3f}, Z={p4_orig[2]:.3f}]")

print(f"\nNote 5 ('Front of break'):")
print(f"  Tilted:  {p5}")
print(f"  Original: [X={p5_orig[0]:.3f}, Y={p5_orig[1]:.3f}, Z={p5_orig[2]:.3f}]")

# Layer height in print coords:
print(f"\nPrint Z' height: Note 5 Z' = {p5[2]:.3f} mm, Note 4 Z' = {p4[2]:.3f} mm")
print(f"Delta Z' between front and back of break: {abs(p4[2] - p5[2]):.3f} mm (~{abs(p4[2] - p5[2])/0.20:.1f} layers of 0.20mm)")
