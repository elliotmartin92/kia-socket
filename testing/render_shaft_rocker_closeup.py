"""
testing/render_shaft_rocker_closeup.py
Generates high-resolution close-up renders of the OEM 3-prong shaft rocker from multiple angles.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Add parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_shaft import build_shaft_rocker_mesh

def render_shaft_closeup():
    print("Rendering close-up views of OEM shaft rocker...")
    shaft_assembled = build_shaft_rocker_mesh(in_assembly_coords=True)
    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
    
    fig = plt.figure(figsize=(16, 12), facecolor='#1e1e1e')
    
    # Panel 1: Top-Down 3D View (Matching Photo 1)
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#252526')
    ax1.set_title("1. Top View: Axle Pins, 3 Prongs & Open Gaps\n(Matches Photo 1)", color='white', fontsize=12, weight='bold', pad=10)
    v1 = shaft_assembled.vertices
    f1 = shaft_assembled.faces
    col1 = Poly3DCollection(v1[f1], alpha=0.95, facecolor='#00d2ff', edgecolor='#005577', linewidth=0.2)
    ax1.add_collection3d(col1)
    ax1.set_xlim(2, 16)
    ax1.set_ylim(2, 14)
    ax1.set_zlim(-7, 15)
    ax1.view_init(elev=75, azim=-90)
    ax1.tick_params(colors='white')
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    
    # Panel 2: Side Profile (Matching Photo 2)
    ax2 = fig.add_subplot(2, 2, 2, projection='3d', facecolor='#252526')
    ax2.set_title("2. Side Profile: Bellcrank Angle & Plunger\n(Matches Photo 2)", color='white', fontsize=12, weight='bold', pad=10)
    col2 = Poly3DCollection(v1[f1], alpha=0.95, facecolor='#2ecc71', edgecolor='#155724', linewidth=0.2)
    ax2.add_collection3d(col2)
    ax2.set_xlim(2, 16)
    ax2.set_ylim(2, 14)
    ax2.set_zlim(-7, 15)
    ax2.view_init(elev=5, azim=0)
    ax2.tick_params(colors='white')
    ax2.set_ylabel('Y (mm)', color='white')
    ax2.set_zlabel('Z (mm)', color='white')
    
    # Panel 3: Underside 3D View (Matching Photo 3)
    ax3 = fig.add_subplot(2, 2, 3, projection='3d', facecolor='#252526')
    ax3.set_title("3. Underside 3D View: Hub Barrel & Coring\n(Matches Photo 3)", color='white', fontsize=12, weight='bold', pad=10)
    col3 = Poly3DCollection(v1[f1], alpha=0.95, facecolor='#f39c12', edgecolor='#b9770e', linewidth=0.2)
    ax3.add_collection3d(col3)
    ax3.set_xlim(2, 16)
    ax3.set_ylim(2, 14)
    ax3.set_zlim(-7, 15)
    ax3.view_init(elev=-45, azim=-60)
    ax3.tick_params(colors='white')
    ax3.set_xlabel('X (mm)', color='white')
    ax3.set_ylabel('Y (mm)', color='white')
    ax3.set_zlabel('Z (mm)', color='white')
    
    # Panel 4: 3D Isometric View (Matching Photo 4)
    ax4 = fig.add_subplot(2, 2, 4, projection='3d', facecolor='#252526')
    ax4.set_title("4. 3D Isometric View: Complete 3-Prong Structure\n(Matches Photo 4)", color='white', fontsize=12, weight='bold', pad=10)
    col4 = Poly3DCollection(v1[f1], alpha=0.95, facecolor='#e74c3c', edgecolor='#78281f', linewidth=0.2)
    ax4.add_collection3d(col4)
    ax4.set_xlim(2, 16)
    ax4.set_ylim(2, 14)
    ax4.set_zlim(-7, 15)
    ax4.view_init(elev=30, azim=-45)
    ax4.tick_params(colors='white')
    ax4.set_xlabel('X (mm)', color='white')
    ax4.set_ylabel('Y (mm)', color='white')
    ax4.set_zlabel('Z (mm)', color='white')
    
    plt.tight_layout()
    out_path = "testing/shaft_rocker_closeup.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")

if __name__ == '__main__':
    render_shaft_closeup()
