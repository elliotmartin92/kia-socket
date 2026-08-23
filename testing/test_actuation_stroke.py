import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from test_reinforced_shaft import build_heavy_duty_shaft_v2
from build_shaft import Y_AXLE, Z_AXLE

new_shaft = build_heavy_duty_shaft_v2()

y_ax = Y_AXLE
z_ax = Z_AXLE

hole_x_min, hole_x_max = 7.608, 12.960
hole_y_min, hole_y_max = 8.570, 13.082

print("--- Actuation Rotation Sweep (Pushing Cam in +Y -> Plunger swings in -Y) ---")
for deg in [0.0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0]:
    rad = np.radians(deg)
    rot = trimesh.transformations.rotation_matrix(rad, [1, 0, 0], point=[0, y_ax, z_ax])
    s_rot = new_shaft.copy()
    s_rot.apply_transform(rot)
    
    # Plunger arm vertices (Z <= 1.0 and X in [7.5, 13.0])
    plunger_verts = s_rot.vertices[(s_rot.vertices[:, 2] <= 1.0) & (s_rot.vertices[:, 0] > 7.0)]
    
    x_min_p = np.min(plunger_verts[:, 0])
    x_max_p = np.max(plunger_verts[:, 0])
    y_min_p = np.min(plunger_verts[:, 1])
    y_max_p = np.max(plunger_verts[:, 1])
    z_min_p = np.min(plunger_verts[:, 2])
    
    x_ok = (x_min_p >= hole_x_min) and (x_max_p <= hole_x_max)
    y_ok = (y_min_p >= hole_y_min) and (y_max_p <= hole_y_max)
    
    print(f"Rotation {deg:5.1f}°: Plunger X=[{x_min_p:.2f}, {x_max_p:.2f}] (Clearances: L={x_min_p-hole_x_min:.2f}mm, R={hole_x_max-x_max_p:.2f}mm) | Y=[{y_min_p:.2f}, {y_max_p:.2f}] (Clearances: Y_min={y_min_p-hole_y_min:.2f}mm, Y_max={hole_y_max-y_max_p:.2f}mm) | Z_tip={z_min_p:.2f} | Pass: {x_ok and y_ok}")

