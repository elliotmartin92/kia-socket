"""
testing/render_3d_plug_insertion.py
3D Isometric and perspective rendering of US NEMA AC plug insertion into the outlet assembly:
- Main Baseplate sub-housing (part.stl)
- Shaft & Rocker Mechanism seated in retention towers (rotated dynamically on insertion)
- Standard US 3-Prong NEMA 5-15 Plug (Hot blade, Neutral blade, Ground pin, molded body)
- Generates 3D multi-angle inspection blueprint saved to testing/3d_plug_insertion_view.png
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER, build_shaft_rocker_mesh
)
from build_part import build_exact_3d_model

def create_nema_plug_mesh(z_tip=13.5, y_center=2.50, plug_body_height=28.0):
    """
    Creates a detailed 3D mesh of a standard US 3-prong NEMA 5-15 plug:
    - Right / Hot Blade (narrow): 1.52mm x 6.35mm x 16.5mm @ X = +6.28mm
    - Left / Neutral Blade (wide): 1.52mm x 7.92mm x 16.5mm @ X = -6.28mm
    - Ground Pin (U-round): Ø4.75mm x 19.0mm @ X = 0.0mm, Y = -11.0mm
    - Molded Plug Body: 34.0mm x 28.0mm x 28.0mm textured shell
    """
    meshes = []
    
    # 1. Hot Blade (X = +6.28mm, Y in [y_center - 3.175, y_center + 3.175])
    w_hot = 6.35
    t_hot = 1.52
    l_hot = 16.50
    m_hot = trimesh.creation.box([t_hot, w_hot, l_hot])
    m_hot.apply_translation([6.28, y_center, z_tip + l_hot/2.0])
    meshes.append(m_hot)
    
    # 2. Neutral Blade (X = -6.28mm, Y in [y_center - 3.96, y_center + 3.96])
    w_neut = 7.92
    t_neut = 1.52
    l_neut = 16.50
    m_neut = trimesh.creation.box([t_neut, w_neut, l_neut])
    m_neut.apply_translation([-6.28, y_center, z_tip + l_neut/2.0])
    meshes.append(m_neut)
    
    # 3. Round Ground Pin (X = 0.0mm, Y = -11.0mm)
    r_gnd = 2.38 # Ø4.75mm
    l_gnd = 18.50
    m_gnd = trimesh.creation.cylinder(radius=r_gnd, height=l_gnd, sections=24)
    m_gnd.apply_translation([0.0, -11.0, (z_tip - 2.0) + l_gnd/2.0])
    meshes.append(m_gnd)
    
    # 4. Molded Plug Grip Body (Z starting at z_tip + 16.5mm)
    z_face = z_tip + l_hot
    m_body = trimesh.creation.box([34.0, 30.0, plug_body_height])
    m_body.apply_translation([0.0, -2.5, z_face + plug_body_height/2.0])
    
    # Plug cord strain relief cylinder
    m_cord = trimesh.creation.cylinder(radius=4.5, height=18.0, sections=24)
    m_cord.apply_translation([0.0, -2.5, z_face + plug_body_height + 9.0])
    
    # Combine
    plug_blades = trimesh.util.concatenate([m_hot, m_neut, m_gnd])
    plug_body = trimesh.util.concatenate([m_body, m_cord])
    
    return plug_blades, plug_body

def render_3d_plug_insertion():
    print("Generating 3D isometric plug insertion visualization...")
    
    # Baseplate mesh
    part_mesh, _ = build_exact_3d_model()
    
    # Shaft rocker mesh rotated 5.0 deg CCW (engaged position)
    shaft_mesh = build_shaft_rocker_mesh(in_assembly_coords=True)
    rot_ccw = trimesh.transformations.rotation_matrix(np.radians(-5.0), [1, 0, 0], point=[0, Y_AXLE, Z_AXLE])
    shaft_engaged = shaft_mesh.copy()
    shaft_engaged.apply_transform(rot_ccw)
    
    # Plug mesh at Z_tip = 13.5mm
    plug_blades, plug_body = create_nema_plug_mesh(z_tip=13.5, y_center=2.50)
    
    fig = plt.figure(figsize=(24, 11), dpi=180, facecolor='#1e1e1e')
    
    # Panel 1: Overall 3D Assembly Perspective View
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#252526')
    ax1.set_title("1. 3D Overview: US NEMA 5-15 Plug Descending into Sub-Housing", color='white', fontsize=12, weight='bold', pad=12)
    
    # Baseplate
    v_b = part_mesh.vertices
    f_b = part_mesh.faces
    col_b = Poly3DCollection(v_b[f_b], alpha=0.35, facecolor='#42a5f5', edgecolor='#1565c0', linewidths=0.05)
    ax1.add_collection3d(col_b)
    
    # Shaft Rocker (Orange/Gold)
    v_s = shaft_engaged.vertices
    f_s = shaft_engaged.faces
    col_s = Poly3DCollection(v_s[f_s], alpha=0.95, facecolor='#ff9800', edgecolor='#b71c1c', linewidths=0.2)
    ax1.add_collection3d(col_s)
    
    # Plug Blades (Shiny Brass / Yellow)
    v_bl = plug_blades.vertices
    f_bl = plug_blades.faces
    col_bl = Poly3DCollection(v_bl[f_bl], alpha=0.95, facecolor='#ffeb3b', edgecolor='#f57f17', linewidths=0.25)
    ax1.add_collection3d(col_bl)
    
    # Plug Body (Dark Rubber Grip)
    v_bd = plug_body.vertices
    f_bd = plug_body.faces
    col_bd = Poly3DCollection(v_bd[f_bd], alpha=0.85, facecolor='#37474f', edgecolor='#212121', linewidths=0.3)
    ax1.add_collection3d(col_bd)
    
    ax1.set_xlim(-28, 28)
    ax1.set_ylim(-28, 28)
    ax1.set_zlim(-10, 50)
    ax1.view_init(elev=28, azim=-55)
    ax1.tick_params(colors='white')
    ax1.set_xlabel('X (mm)', color='white', fontweight='bold')
    ax1.set_ylabel('Y (mm)', color='white', fontweight='bold')
    ax1.set_zlabel('Z (mm)', color='white', fontweight='bold')
    
    # Panel 2: 3D Closeup of Right Blade Engaging Rocker Cam
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#252526')
    ax2.set_title("2. 3D Kinematic Interface: Right Hot Blade Striking Crowned Cam Tab", color='white', fontsize=12, weight='bold', pad=12)
    
    ax2.add_collection3d(Poly3DCollection(v_b[f_b], alpha=0.40, facecolor='#42a5f5', edgecolor='#1565c0', linewidths=0.08))
    ax2.add_collection3d(Poly3DCollection(v_s[f_s], alpha=0.95, facecolor='#ff9800', edgecolor='#b71c1c', linewidths=0.3))
    ax2.add_collection3d(Poly3DCollection(v_bl[f_bl], alpha=0.95, facecolor='#ffeb3b', edgecolor='#f57f17', linewidths=0.35))
    ax2.add_collection3d(Poly3DCollection(v_bd[f_bd], alpha=0.45, facecolor='#37474f', edgecolor='#212121', linewidths=0.2))
    
    # Focus bounds on the right tower / cam junction: X in [2, 16], Y in [0, 16], Z in [-8, 26]
    ax2.set_xlim(2, 16)
    ax2.set_ylim(0, 15)
    ax2.set_zlim(-8, 25)
    ax2.view_init(elev=20, azim=-35)
    ax2.tick_params(colors='white')
    ax2.set_xlabel('X (mm)', color='white', fontweight='bold')
    ax2.set_ylabel('Y (mm)', color='white', fontweight='bold')
    ax2.set_zlabel('Z (mm)', color='white', fontweight='bold')
    
    plt.tight_layout()
    out_3d_path = "testing/3d_plug_insertion_view.png"
    plt.savefig(out_3d_path, dpi=200)
    print(f"Saved 3D plug insertion diagram to {out_3d_path} successfully!")

if __name__ == '__main__':
    render_3d_plug_insertion()
