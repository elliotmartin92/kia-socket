"""
testing/render_45deg_support_fins.py
Renders multi-angle 3D views of the 45-degree tilted part with baked-in Support Fins:
- Shows the tilted part, support fins, breakaway tines, and bed adhesion pad
- Demonstrates how layer lines cut across the half moon at 45°
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import build_part as bp

def render_preview():
    base_part, _ = bp.build_exact_3d_model()
    part_supported, part_45, fins_mesh = bp.build_45deg_supported_part_mesh(base_part)
    
    fig = plt.figure(figsize=(18, 7.5), dpi=160, facecolor='#1e1e1e')
    
    # 1. Perspective View
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#252525')
    ax1.tick_params(colors='white')
    
    # Render Part (Blue)
    col_part = Poly3DCollection(part_45.vertices[part_45.faces], alpha=0.85, edgecolor='#222222', linewidths=0.1)
    col_part.set_facecolor('#3498db')
    ax1.add_collection3d(col_part)
    
    # Render Support Fins (Orange)
    col_fins = Poly3DCollection(fins_mesh.vertices[fins_mesh.faces], alpha=0.90, edgecolor='#d35400', linewidths=0.15)
    col_fins.set_facecolor('#e67e22')
    ax1.add_collection3d(col_fins)
    
    ax1.set_xlim(-26, 26)
    ax1.set_ylim(-22, 22)
    ax1.set_zlim(0, 35)
    ax1.view_init(elev=20, azim=215)
    ax1.set_title("3D Isometric: 45° Tilted Part + In-Place Printed Slit Shrouds\n(Zero Assembly; Full-Height Fins to Z ≈ 25.2mm Under Towers)", color='white', fontsize=11, weight='bold')
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    ax1.set_zlabel('Z (mm)', color='white')

    # 2. Side View (YZ plane) showing 45° Layer Angle vs Half Moon
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#252525')
    ax2.tick_params(colors='white')
    
    col_part2 = Poly3DCollection(part_45.vertices[part_45.faces], alpha=0.85, edgecolor='#222222', linewidths=0.1)
    col_part2.set_facecolor('#3498db')
    ax2.add_collection3d(col_part2)
    
    col_fins2 = Poly3DCollection(fins_mesh.vertices[fins_mesh.faces], alpha=0.90, edgecolor='#d35400', linewidths=0.15)
    col_fins2.set_facecolor('#e67e22')
    ax2.add_collection3d(col_fins2)
    
    ax2.set_xlim(-26, 26)
    ax2.set_ylim(-22, 22)
    ax2.set_zlim(0, 35)
    ax2.view_init(elev=0, azim=180) # Side view looking down X axis
    ax2.set_title("Side View (Y-Z Plane): In-Place Slits Self-Supporting at 45°\n(Snap Clip Supports Removed; Clean Monolithic One-Piece Part)", color='white', fontsize=11, weight='bold')
    ax2.set_xlabel('X (mm)', color='white')
    ax2.set_ylabel('Y (mm)', color='white')
    ax2.set_zlabel('Z (mm)', color='white')

    plt.tight_layout()
    out_path = 'testing/part_45deg_supported_preview.png'
    plt.savefig(out_path, dpi=180)
    print(f"Saved 3D render preview to {out_path}")

if __name__ == '__main__':
    render_preview()
