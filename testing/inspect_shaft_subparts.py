"""
testing/inspect_shaft_subparts.py
Inspect the positions and elevations of each subcomponent of the shaft rocker in print coordinates.
"""

import os, sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER, HUB_DIAMETER,
    PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X, CAM_WIDTH_X, CAM_X_CENTER,
    X_TOWER_CENTER, Y_AXLE, Z_AXLE, HOLE_X_CENTER, RIB_FLANK_THICK,
    build_shaft_rocker_mesh
)
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

# Let's inspect each subcomponent separately before and after rotation
y_axle = Y_AXLE
z_axle = Z_AXLE
x_c = X_TOWER_CENTER
r_pin = PIN_DIAMETER / 2.0
r_hub = HUB_DIAMETER / 2.0
pin_len = (TOTAL_AXLE_LEN - HUB_WIDTH) / 2.0

rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])

# 1. Pins
pin_l = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
pin_l.apply_transform(rot_x)
pin_l.apply_translation([x_c - HUB_WIDTH/2.0 - pin_len/2.0, y_axle, z_axle])

pin_r = trimesh.creation.cylinder(radius=r_pin, height=pin_len + 0.10, sections=32)
pin_r.apply_transform(rot_x)
pin_r.apply_translation([x_c + HUB_WIDTH/2.0 + pin_len/2.0, y_axle, z_axle])

# 2. Hub
hub_mesh = trimesh.creation.cylinder(radius=r_hub, height=HUB_WIDTH, sections=32)
hub_mesh.apply_transform(rot_x)
hub_mesh.apply_translation([x_c, y_axle, z_axle])

# 3. Flank collar & ribs
flank_collar = Point(y_axle, z_axle).buffer(r_hub)
flank_pts = [
    (y_axle - 1.50, z_axle + 0.60),
    (y_axle + 3.20, z_axle - 1.50),
    (y_axle + 2.50, z_axle - 4.50),
    (y_axle + 0.20, z_axle - 4.20),
    (y_axle - 1.60, z_axle - 1.00)
]
poly_flank = unary_union([flank_collar, Polygon(flank_pts)])

m_rib1_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
v_r1 = m_rib1_raw.vertices.copy()
v_rib1 = np.column_stack([v_r1[:, 2] + (x_c - HUB_WIDTH/2.0 + 0.10), v_r1[:, 0], v_r1[:, 1]])
mesh_rib1 = trimesh.Trimesh(vertices=v_rib1, faces=m_rib1_raw.faces.copy(), process=True)

m_rib3_raw = trimesh.creation.extrude_polygon(poly_flank, height=RIB_FLANK_THICK)
v_r3 = m_rib3_raw.vertices.copy()
v_rib3 = np.column_stack([v_r3[:, 2] + (x_c + HUB_WIDTH/2.0 - 0.10 - RIB_FLANK_THICK), v_r3[:, 0], v_r3[:, 1]])
mesh_rib3 = trimesh.Trimesh(vertices=v_rib3, faces=m_rib3_raw.faces.copy(), process=True)

# 4. Plunger
z_tip = -PLUNGER_REACH_BELOW_Z
r_tip = 1.00
plunger_y_center = 10.479
N = 25
t = np.linspace(0, 1, N)
spine_y = (1-t)**2 * (y_axle + r_hub) + 2*(1-t)*t * (y_axle + 3.80) + t**2 * (plunger_y_center + r_tip)
spine_z = (1-t)**2 * (z_axle - 0.20) + 2*(1-t)*t * 7.50 + t**2 * 3.50
tip_angles = np.linspace(0, np.pi, 33)
tip_pts = [(plunger_y_center + r_tip * np.cos(a), z_tip + r_tip * (1 - np.sin(a))) for a in tip_angles]
belly_y = (1-t)**2 * (y_axle - r_hub) + 2*(1-t)*t * (y_axle + 1.20) + t**2 * (plunger_y_center - r_tip)
belly_z = (1-t)**2 * (z_axle - 0.50) + 2*(1-t)*t * 7.80 + t**2 * 3.50

pts_plunger = (
    list(zip(spine_y, spine_z)) +
    [(plunger_y_center + r_tip, z_tip + r_tip)] +
    tip_pts +
    [(plunger_y_center - r_tip, z_tip + r_tip)] +
    list(reversed(list(zip(belly_y, belly_z))))
)
poly_plunger = unary_union([flank_collar, Polygon(pts_plunger)])
m_plunger_raw = trimesh.creation.extrude_polygon(poly_plunger, height=PLUNGER_WIDTH_X)
v_p = m_plunger_raw.vertices.copy()
v_plunger = np.column_stack([v_p[:, 2] + (HOLE_X_CENTER - PLUNGER_WIDTH_X/2.0), v_p[:, 0], v_p[:, 1]])
mesh_plunger = trimesh.Trimesh(vertices=v_plunger, faces=m_plunger_raw.faces.copy(), process=True)

# 5. Cam
poly_pts_cam = [
    (y_axle, z_axle),
    (y_axle, z_axle + r_hub),
    (6.80, 12.20),
    (5.00, 10.00),
    (1.50, 7.40),
    (1.80, 5.10),
    (4.50, 5.30),
    (y_axle - 1.50, z_axle - 2.50)
]
poly_cam_arm = Polygon(poly_pts_cam)
poly_cam = unary_union([flank_collar, poly_cam_arm])
x_cam_start = max(x_c - HUB_WIDTH/2.0, CAM_X_CENTER - CAM_WIDTH_X/2.0)
actual_cam_w = min(CAM_WIDTH_X, (x_c + HUB_WIDTH/2.0) - x_cam_start)
m_cam_raw = trimesh.creation.extrude_polygon(poly_cam, height=actual_cam_w)
v_c = m_cam_raw.vertices.copy()
v_cam = np.column_stack([v_c[:, 2] + x_cam_start, v_c[:, 0], v_c[:, 1]])
mesh_cam = trimesh.Trimesh(vertices=v_cam, faces=m_cam_raw.faces.copy(), process=True)

# Complete assembly
full_assembly = trimesh.util.concatenate([
    pin_l, pin_r, hub_mesh, mesh_rib1, mesh_rib3, mesh_plunger, mesh_cam
])

# Print transform
rot_bed = trimesh.transformations.rotation_matrix(np.radians(198.6), [1, 0, 0])
bounds = full_assembly.copy().apply_transform(rot_bed).bounds
t_center = [
    -(bounds[0, 0] + bounds[1, 0])/2.0,
    -(bounds[0, 1] + bounds[1, 1])/2.0,
    -bounds[0, 2]
]

parts = {
    'Left Pin': pin_l,
    'Right Pin': pin_r,
    'Hub Barrel': hub_mesh,
    'Rib 1 (Left Flank)': mesh_rib1,
    'Rib 3 (Right Flank)': mesh_rib3,
    'Plunger Arm': mesh_plunger,
    'Cam Tab': mesh_cam
}

print(f"{'Component':<22} | {'X span':<16} | {'Y span':<16} | {'Z span':<16}")
print("-" * 76)

for name, mesh in parts.items():
    m = mesh.copy()
    m.apply_transform(rot_bed)
    m.apply_translation(t_center)
    b = m.bounds
    print(f"{name:<22} | [{b[0, 0]:5.2f}, {b[1, 0]:5.2f}] | [{b[0, 1]:5.2f}, {b[1, 1]:5.2f}] | [{b[0, 2]:5.2f}, {b[1, 2]:5.2f}]")
