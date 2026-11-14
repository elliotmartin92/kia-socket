"""
testing/measure_tilted_supports.py
Measures tilted coordinates of shaft rocker components and baseplate features
to compute exact parameters for the 3 breakaway support struts in build_part.py.
"""

import os
import sys
import numpy as np
import trimesh

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_part import build_exact_3d_model
from build_shaft import build_shaft_rocker_mesh, Y_AXLE, Z_AXLE

def main():
    print("Loading base geometry...")
    base_mesh, base_poly = build_exact_3d_model()
    
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    
    print(f"z_min = {z_min:.4f}")
    print(f"m_tilted bounds: X=[{m_tilted.bounds[0,0]:.2f}, {m_tilted.bounds[1,0]:.2f}], "
          f"Y=[{m_tilted.bounds[0,1]:.2f}, {m_tilted.bounds[1,1]:.2f}], "
          f"Z=[{m_tilted.bounds[0,2]:.2f}, {m_tilted.bounds[1,2]:.2f}]")
          
    shaft_mesh = build_shaft_rocker_mesh(hub_w=6.90, in_assembly_coords=True, with_supports=False)
    shaft_tilted = shaft_mesh.copy().apply_transform(R)
    shaft_tilted.apply_translation([0, 0, -z_min])
    
    print(f"shaft_tilted bounds: X=[{shaft_tilted.bounds[0,0]:.2f}, {shaft_tilted.bounds[1,0]:.2f}], "
          f"Y=[{shaft_tilted.bounds[0,1]:.2f}, {shaft_tilted.bounds[1,1]:.2f}], "
          f"Z=[{shaft_tilted.bounds[0,2]:.2f}, {shaft_tilted.bounds[1,2]:.2f}]")

    print("\n--- 1. PLUNGER SUPPORT ---")
    # Plunger blade: X in [8.484, 12.084]
    p_mask = (shaft_tilted.vertices[:, 0] >= 8.484) & (shaft_tilted.vertices[:, 0] <= 12.084)
    p_verts = shaft_tilted.vertices[p_mask]
    
    # We want the lowest point of plunger blade in Z' near Y' ~ 11.30
    p_lowest_idx = np.argmin(p_verts[:, 2])
    p_lowest = p_verts[p_lowest_idx]
    print(f"Plunger lowest vertex in tilt coords: X={p_lowest[0]:.3f}, Y'={p_lowest[1]:.3f}, Z'={p_lowest[2]:.3f}")
    
    # Check vertices around the belly
    # Filter vertices near Y' = 11.30 +/- 1.50
    belly_mask = (p_verts[:, 1] >= 9.8) & (p_verts[:, 1] <= 12.8)
    belly_verts = p_verts[belly_mask]
    min_belly_z = np.min(belly_verts[:, 2])
    print(f"Plunger belly min Z' (around Y' in [9.8, 12.8]): {min_belly_z:.3f} mm")
    
    # In old code:
    # z_plunger_lowest = 2.52 - z_min  # ~15.63mm
    # Let's check what 2.52 - z_min was or what assembly coords point corresponds to it:
    # A point in assembly coords (x, y, z) transformed by R (45 deg about X):
    # y' = y*cos(45) - z*sin(45) = (y - z) / sqrt(2)
    # z' = y*sin(45) + z*cos(45) = (y + z) / sqrt(2)
    # in tilted coords: z' - z_min
    
    print("\n--- 2. CAM TAB SUPPORT ---")
    # Cam tab: X in [5.60, 7.60]
    cam_mask = (shaft_tilted.vertices[:, 0] >= 5.60) & (shaft_tilted.vertices[:, 0] <= 7.60)
    cam_verts = shaft_tilted.vertices[cam_mask]
    cam_lowest_idx = np.argmin(cam_verts[:, 2])
    cam_lowest = cam_verts[cam_lowest_idx]
    print(f"Cam lowest vertex in tilt coords: X={cam_lowest[0]:.3f}, Y'={cam_lowest[1]:.3f}, Z'={cam_lowest[2]:.3f}")
    # Let's inspect lowest points along the cam tab ramp/underside
    low_cam_pts = cam_verts[cam_verts[:, 2] <= cam_lowest[2] + 0.5]
    print(f"Cam low points Y' range: [{np.min(low_cam_pts[:, 1]):.3f}, {np.max(low_cam_pts[:, 1]):.3f}], Z' range: [{np.min(low_cam_pts[:, 2]):.3f}, {np.max(low_cam_pts[:, 2]):.3f}]")

    # Check baseplate floor below cam tab:
    # cam_c_x = 6.600, cam_c_y = -2.333 (or whatever new Y' is)
    # In m_tilted, what is max Z' around (X=6.60, Y'=cam_c_y)?
    floor_cam_mask = (np.abs(m_tilted.vertices[:, 0] - cam_lowest[0]) <= 1.0) & \
                     (np.abs(m_tilted.vertices[:, 1] - cam_lowest[1]) <= 1.0)
    floor_cam_z = np.max(m_tilted.vertices[floor_cam_mask, 2])
    print(f"Baseplate floor Z' near cam lowest point: {floor_cam_z:.3f} mm")

    print("\n--- 3. HUB BARREL SUPPORT ---")
    hub_mask = (shaft_tilted.vertices[:, 0] >= 7.80) & (shaft_tilted.vertices[:, 0] <= 8.50)
    print(f"Number of hub barrel vertices with X in [7.80, 8.50]: {np.sum(hub_mask)}")
    if np.sum(hub_mask) > 0:
        for v in shaft_tilted.vertices[hub_mask][:15]:
            print(f"  v: X={v[0]:.3f}, Y'={v[1]:.3f}, Z'={v[2]:.3f}")
        
        # Check floor / seating rib below hub support at new Y' = -1.351
        floor_hub_mask = (np.abs(m_tilted.vertices[:, 0] - 8.16) <= 0.6) & \
                         (np.abs(m_tilted.vertices[:, 1] - hub_lowest[1]) <= 0.6)
        floor_hub_z = np.max(m_tilted.vertices[floor_hub_mask, 2])
        print(f"Baseplate floor / seating rib Z' near hub lowest point: {floor_hub_z:.3f} mm")
    else:
        print("Still no vertices found")

if __name__ == '__main__':
    main()
