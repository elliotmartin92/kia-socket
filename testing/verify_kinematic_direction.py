"""
testing/verify_kinematic_direction.py
Verify the rigid-body kinematic rotation direction and plunger displacement
when a plug blade pushes down (-Z) on the rocker cam.
"""

import numpy as np

# Coordinates
Y_AXLE = 9.279
Z_AXLE = 12.590

Y_CAM = 5.000     # Cam contact point
Z_CAM = 13.500

Y_PLUNGER = 10.479 # Plunger tip
Z_PLUNGER = -6.500

print("=== RIGID BODY KINEMATICS VERIFICATION ===")
print(f"Pivot Axis:        (Y = {Y_AXLE:.3f}, Z = {Z_AXLE:.3f})")
print(f"Cam Contact Point: (Y = {Y_CAM:.3f}, Z = {Z_CAM:.3f}) -> Vector from pivot: (dY = {Y_CAM - Y_AXLE:.3f}, dZ = {Z_CAM - Z_AXLE:.3f})")
print(f"Plunger Tip:       (Y = {Y_PLUNGER:.3f}, Z = {Z_PLUNGER:.3f}) -> Vector from pivot: (dY = {Y_PLUNGER - Y_AXLE:.3f}, dZ = {Z_PLUNGER - Z_AXLE:.3f})")

# Let's apply a CCW rotation theta > 0
for deg in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
    rad = np.radians(deg) # CCW
    # CCW rotation matrix: [[cos, -sin], [sin, cos]]
    rot_ccw = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])
    
    # Cam motion
    v_cam = np.array([Y_CAM - Y_AXLE, Z_CAM - Z_AXLE])
    v_cam_rot = rot_ccw @ v_cam
    p_cam_new = np.array([Y_AXLE, Z_AXLE]) + v_cam_rot
    dZ_cam = p_cam_new[1] - Z_CAM
    
    # Plunger motion
    v_plunger = np.array([Y_PLUNGER - Y_AXLE, Z_PLUNGER - Z_AXLE])
    v_plunger_rot = rot_ccw @ v_plunger
    p_plunger_new = np.array([Y_AXLE, Z_AXLE]) + v_plunger_rot
    dY_plunger = p_plunger_new[0] - Y_PLUNGER
    dZ_plunger = p_plunger_new[1] - Z_PLUNGER
    
    print(f"Rotation {deg:4.1f}° CCW: Cam dZ = {dZ_cam:+6.3f} mm (Z={p_cam_new[1]:.2f}) | Plunger dY = {dY_plunger:+6.3f} mm (Y={p_plunger_new[0]:.2f}), dZ = {dZ_plunger:+6.3f} mm")

print("\n--- HOLE CLEARANCES ---")
HOLE_Y_MIN = 8.570
HOLE_Y_MAX = 13.082
print(f"Through-hole Y bounds: [{HOLE_Y_MIN:.3f}, {HOLE_Y_MAX:.3f}] mm (Total opening: {HOLE_Y_MAX - HOLE_Y_MIN:.3f} mm)")
print(f"At rest (Y = {Y_PLUNGER:.3f}): Clearance to -Y wall = {Y_PLUNGER - HOLE_Y_MIN:.3f} mm, Clearance to +Y wall = {HOLE_Y_MAX - Y_PLUNGER:.3f} mm")
print(f"At 7.0° CCW (Y = 12.79 mm): Clearance to +Y wall = {HOLE_Y_MAX - 12.79:.3f} mm (Passes inside hole!)")
