import sys, os
sys.path.insert(0, os.path.abspath('.'))
import trimesh
import numpy as np
import build_part

# Hole 2 in base_poly is the through hole:
# bounds in flat coords: X in [7.608, 12.960], Y in [8.570, 13.750], Z in [0, 1.0]
# Let's transform these corners to tilted coords:
cos45 = np.cos(np.pi/4)
sin45 = np.sin(np.pi/4)

R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
base_mesh, base_poly = build_part.build_exact_3d_model()
m_t = base_mesh.copy().apply_transform(R)
z_min = m_t.bounds[0, 2]

def to_tilted(y, z):
    yp = y * cos45 - z * sin45
    zp = y * sin45 + z * cos45 - z_min
    return yp, zp

print("Hole 2 corners in tilted coords:")
for y in [8.570, 13.750]:
    for z in [0.0, 1.0]:
        yp, zp = to_tilted(y, z)
        print(f"  flat Y={y:.2f}, Z={z:.2f} -> tilted Y={yp:.3f}, Z={zp:.3f}")
