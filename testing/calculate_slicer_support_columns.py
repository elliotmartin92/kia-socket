"""
testing/calculate_slicer_support_columns.py
Simulate slicer support generation: find every downward surface with angle > 45°
(or > 35°), project it down to the bed (or lower surface), and identify where
slicers place support columns / sticks.
"""

import trimesh
import numpy as np

mesh = trimesh.load('shaft_rocker_clean.stl')

normals = mesh.face_normals
centers = mesh.triangles_center
areas = mesh.area_faces

# Let's check overhang thresholds:
# Angle from horizontal theta: sin(theta) = -normal_z
# If normal_z < -0.5: angle < 60° from horizontal (steep overhang)
# If normal_z < -0.707: angle < 45° from horizontal (very steep)

print("=" * 80)
print("ANALYSIS OF OVERHANG REGIONS NEEDING SUPPORTS")
print("=" * 80)

# Group into Z regions:
# Region 1: Low Z (Z < 2.0 mm) - Axle pins & hub (already supported by our cradle!)
# Region 2: Mid Z (Z between 2.0 and 12.0 mm)
# Region 3: High Z (Z > 12.0 mm)

for thresh_name, thresh_val in [('Steep (n_z < -0.5, >40° from vertical)', -0.5), ('Moderate (n_z < -0.3, >20° from vertical)', -0.3)]:
    print(f"\n--- Overhang Threshold: {thresh_name} ---")
    mask = (normals[:, 2] < thresh_val)
    
    # Low Z
    m_low = mask & (centers[:, 2] <= 2.0)
    print(f"Low Z (Z <= 2.0 mm): {np.sum(m_low)} faces, Area = {np.sum(areas[m_low]):.2f} mm² (Covered by v9.4 cradle)")
    
    # Mid Z
    m_mid = mask & (centers[:, 2] > 2.0) & (centers[:, 2] <= 12.0)
    print(f"Mid Z (2.0 < Z <= 12.0 mm): {np.sum(m_mid)} faces, Area = {np.sum(areas[m_mid]):.2f} mm²")
    if np.any(m_mid):
        c_m = centers[m_mid]
        print(f"    Bounds: X: [{c_m[:,0].min():.2f}, {c_m[:,0].max():.2f}], Y: [{c_m[:,1].min():.2f}, {c_m[:,1].max():.2f}], Z: [{c_m[:,2].min():.2f}, {c_m[:,2].max():.2f}]")
        # Split by X (Cam vs Plunger vs Web)
        cam_mask = m_mid & (centers[:, 0] < -1.0)
        plunger_mask = m_mid & (centers[:, 0] >= -1.0)
        if np.any(cam_mask):
            c_cam = centers[cam_mask]
            print(f"    -> CAM TAB Overhang: {np.sum(cam_mask)} faces, Area = {np.sum(areas[cam_mask]):.2f} mm²")
            print(f"       X: [{c_cam[:,0].min():.2f}, {c_cam[:,0].max():.2f}], Y: [{c_cam[:,1].min():.2f}, {c_cam[:,1].max():.2f}], Z: [{c_cam[:,2].min():.2f}, {c_cam[:,2].max():.2f}]")
        if np.any(plunger_mask):
            c_plung = centers[plunger_mask]
            print(f"    -> PLUNGER/WEB Overhang: {np.sum(plunger_mask)} faces, Area = {np.sum(areas[plunger_mask]):.2f} mm²")
            print(f"       X: [{c_plung[:,0].min():.2f}, {c_plung[:,0].max():.2f}], Y: [{c_plung[:,1].min():.2f}, {c_plung[:,1].max():.2f}], Z: [{c_plung[:,2].min():.2f}, {c_plung[:,2].max():.2f}]")
            
    # High Z
    m_high = mask & (centers[:, 2] > 12.0)
    print(f"High Z (Z > 12.0 mm): {np.sum(m_high)} faces, Area = {np.sum(areas[m_high]):.2f} mm²")
    if np.any(m_high):
        c_h = centers[m_high]
        print(f"    Bounds: X: [{c_h[:,0].min():.2f}, {c_h[:,0].max():.2f}], Y: [{c_h[:,1].min():.2f}, {c_h[:,1].max():.2f}], Z: [{c_h[:,2].min():.2f}, {c_h[:,2].max():.2f}]")

