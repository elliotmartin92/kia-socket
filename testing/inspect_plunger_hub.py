import numpy as np
import trimesh
import os, sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import build_part
import build_shaft

base_mesh, base_poly = build_part.build_exact_3d_model()
R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
m_tilted = base_mesh.copy().apply_transform(R)
z_min = m_tilted.bounds[0, 2]
m_tilted.apply_translation([0, 0, -z_min])

shaft_subparts = build_shaft.build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, return_subparts=True, with_supports=False)

# Let's inspect the plunger in flat coords:
p_flat = shaft_subparts['plunger']
hub_flat = shaft_subparts['hub']
cam_flat = shaft_subparts['cam']

print("Flat coords:")
print(f"Hub bounds:     X={hub_flat.bounds[:,0]}, Y={hub_flat.bounds[:,1]}, Z={hub_flat.bounds[:,2]}")
print(f"Plunger bounds: X={p_flat.bounds[:,0]}, Y={p_flat.bounds[:,1]}, Z={p_flat.bounds[:,2]}")
print(f"Cam bounds:     X={cam_flat.bounds[:,0]}, Y={cam_flat.bounds[:,1]}, Z={cam_flat.bounds[:,2]}")

# What is the plunger cross-section in YZ?
# In flat coords:
# Axle is at Y = 9.279, Z = 11.190.
# Hub cylinder is from Y = 9.279 - 2.10 = 7.179 to 9.279 + 2.10 = 11.379.
# Z is from 11.190 - 2.10 = 9.090 to 11.190 + 2.10 = 13.290.
# Look at Y of hub: [7.179, 11.379].
# What is Y of plunger at Z = 9.09 to 13.29?
# Plunger connects to hub collar!
# Plunger arm swings down towards Z = -6.50!
# At Z = 0 (baseplate floor), where is plunger?
# Plunger is at Y in [8.57, 12.0]!

# Now let's look in TILTED coords:
p_tilted = p_flat.copy().apply_transform(R)
p_tilted.apply_translation([0, 0, -z_min])
hub_tilted = hub_flat.copy().apply_transform(R)
hub_tilted.apply_translation([0, 0, -z_min])

print("\nTilted coords:")
print(f"Hub bounds:     X={hub_tilted.bounds[:,0]}, Y={hub_tilted.bounds[:,1]}, Z={hub_tilted.bounds[:,2]}")
print(f"Plunger bounds: X={p_tilted.bounds[:,0]}, Y={p_tilted.bounds[:,1]}, Z={p_tilted.bounds[:,2]}")

# Where is the lowest point of the hub cylinder in tilted coords?
# Y' = -1.351, Z' = 25.483.
# Does the plunger blade intersect Y' = -1.351, Z' = 25.483?
# Let's check!
# Slicing the plunger at Y' = -1.351:
sl_y = p_tilted.section(plane_origin=[0, -1.351, 0], plane_normal=[0, 1, 0])
if sl_y is not None:
    print(f"Plunger at Y'=-1.351 has Z' in [{np.min(sl_y.vertices[:, 2]):.3f}, {np.max(sl_y.vertices[:, 2]):.3f}]")
else:
    print("Plunger at Y'=-1.351: None")
