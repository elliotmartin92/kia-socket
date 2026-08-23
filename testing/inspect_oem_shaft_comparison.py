"""
testing/inspect_oem_shaft_comparison.py
Comprehensive 3D inspection and visualization script comparing the OEM 3-rib
shaft rocker with the baseplate assembly and rendering multi-angle diagnostic previews.
"""

import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.test_oem_shaft_rocker import build_oem_shaft_rocker_mesh

def plot_oem_shaft_inspection():
    print("Generating OEM shaft inspection diagrams...")
    
    shaft_assembled = build_oem_shaft_rocker_mesh(in_assembly_coords=True)
    shaft_printable = build_oem_shaft_rocker_mesh(in_assembly_coords=False)
    
    # Load baseplate if available
    part_mesh = None
    if os.path.exists("part.stl"):
        part_mesh = trimesh.load("part.stl")
    
    fig = plt.figure(figsize=(18, 12), facecolor='#1e1e1e')
    
    # Panel 1: 3D Isometric View of Rocker in Assembly
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#252526')
    ax1.set_title("1. 3D Assembly View (Towers & OEM Rocker)", color='white', fontsize=12, weight='bold', pad=10)
    
    # Plot shaft faces
    # Downsample or plot directly
    v_s = shaft_assembled.vertices
    f_s = shaft_assembled.faces
    mesh_col = Poly3DCollection(v_s[f_s], alpha=0.90, facecolor='#00d2ff', edgecolor='#007799', linewidth=0.2)
    ax1.add_collection3d(mesh_col)
    
    # Reference boxes for towers & hole
    # Left Tower: [3.90, 5.40] x [4.20, 11.20] x [1.0, 13.59]
    # Right Tower: [13.10, 14.60] x [4.20, 11.20] x [1.0, 13.59]
    # Hole: [7.61, 12.96] x [8.57, 13.08] x [0, 1.0]
    ax1.set_xlim(0, 18)
    ax1.set_ylim(0, 18)
    ax1.set_zlim(-8, 15)
    ax1.tick_params(colors='white')
    ax1.set_xlabel('X (mm)', color='white')
    ax1.set_ylabel('Y (mm)', color='white')
    ax1.set_zlabel('Z (mm)', color='white')
    ax1.view_init(elev=25, azim=-60)
    
    # Panel 2: Top-Down X-Y Clearances
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#252526')
    ax2.set_title("2. Top-Down Alignment (X-Y Plane)", color='white', fontsize=12, weight='bold', pad=10)
    
    # Slice through center of axle (Z = 12.59)
    # Draw tower bounds
    ax2.axvspan(3.90, 5.40, color='#e67e22', alpha=0.35, label='Left Tower (1.50mm)')
    ax2.axvspan(13.10, 14.60, color='#e67e22', alpha=0.35, label='Right Tower (1.50mm)')
    ax2.axvspan(7.608, 12.960, color='#9b59b6', alpha=0.25, label='Through-Hole (5.35mm)')
    
    # Axle & components
    # Pins
    ax2.barh(7.666, 1.95, left=3.50, height=1.90, color='#00d2ff', edgecolor='white', label='Pivot Pins (Ø1.90mm, L=1.95mm)')
    ax2.barh(7.666, 1.95, left=13.05, height=1.90, color='#00d2ff', edgecolor='white')
    # Hub
    ax2.barh(7.666, 7.60, left=5.45, height=3.30, color='#34495e', edgecolor='cyan', label='Central Hub Barrel (7.60mm)')
    # Cam Tab
    ax2.barh(5.50, 2.70, left=7.05 - 1.35, height=3.0, color='#2ecc71', edgecolor='white', label='Cam Tab (2.70mm @ X=7.05)')
    # Ribs
    ax2.barh(8.50, 0.90, left=5.55, height=2.0, color='#f1c40f', edgecolor='white', label='Rib 1 & 3 Flanks (0.90mm)')
    ax2.barh(8.50, 0.90, left=12.05, height=2.0, color='#f1c40f', edgecolor='white')
    ax2.barh(10.00, 2.40, left=10.284 - 1.20, height=4.0, color='#e74c3c', edgecolor='white', label='Center Plunger (2.40mm @ X=10.28)')
    
    ax2.set_xlim(2, 17)
    ax2.set_ylim(2, 14)
    ax2.set_xlabel('X (mm)', color='white')
    ax2.set_ylabel('Y (mm)', color='white')
    ax2.tick_params(colors='white')
    ax2.legend(loc='lower left', fontsize=8, facecolor='#1e1e1e', labelcolor='white')
    ax2.grid(True, color='#444444', linestyle=':')
    
    # Panel 3: Side Profile Y-Z Cross-Section & Kinematics
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#252526')
    ax3.set_title("3. Side Kinematics Profile (Y-Z Plane)", color='white', fontsize=12, weight='bold', pad=10)
    
    # Axle center
    ax3.plot([7.666], [12.590], 'o', color='cyan', markersize=8, label='Pivot Axis (Y=7.67, Z=12.59)')
    
    # Draw plunger arm profile
    # Plunger reaches Z = -6.50
    ax3.axhline(0.00, color='white', linestyle='-', lw=1.5, label='Baseplate Bottom (Z=0.00)')
    ax3.axhline(1.00, color='#888888', linestyle='--', lw=1.0, label='Baseplate Floor (Z=1.00)')
    ax3.axhline(-6.50, color='#e74c3c', linestyle=':', lw=2.0, label='PCB Switch Level (Z=-6.50)')
    
    # Plunger profile contour
    t_arr = np.linspace(0, 1, 50)
    sp_y = (1-t_arr)**2 * (7.666 + 1.65) + 2*(1-t_arr)*t_arr * (7.666 + 3.80) + t_arr**2 * (11.40 + 1.0)
    sp_z = (1-t_arr)**2 * (12.59 - 0.20) + 2*(1-t_arr)*t_arr * 7.50 + t_arr**2 * 3.50
    bl_y = (1-t_arr)**2 * (7.666 - 1.65) + 2*(1-t_arr)*t_arr * (7.666 + 1.20) + t_arr**2 * (11.40 - 1.0)
    bl_z = (1-t_arr)**2 * (12.59 - 0.50) + 2*(1-t_arr)*t_arr * 7.80 + t_arr**2 * 3.50
    
    ax3.plot(sp_y, sp_z, color='#e74c3c', lw=2)
    ax3.plot(bl_y, bl_z, color='#e74c3c', lw=2)
    ax3.plot([12.4, 12.4, 10.4, 10.4], [3.5, -5.5, -5.5, 3.5], color='#e74c3c', lw=2)
    
    # Cam Tab profile
    cam_pts = np.array([
        [7.666 + 1.2, 12.59 + 1.2],
        [3.466, 8.99],
        [3.466, 6.79],
        [6.266, 6.79],
        [7.666 + 0.2, 10.09]
    ])
    ax3.fill(cam_pts[:, 0], cam_pts[:, 1], color='#2ecc71', alpha=0.6, label='Input Cam Tab')
    
    ax3.set_xlim(0, 16)
    ax3.set_ylim(-8, 15)
    ax3.set_xlabel('Y (mm)', color='white')
    ax3.set_ylabel('Z (mm)', color='white')
    ax3.tick_params(colors='white')
    ax3.legend(loc='upper right', fontsize=8, facecolor='#1e1e1e', labelcolor='white')
    ax3.grid(True, color='#444444', linestyle=':')
    
    # Panel 4: Print-Ready Build Plate Layout (Flat at Z = 0)
    ax4 = fig.add_subplot(2, 2, 4, projection='3d', facecolor='#252526')
    ax4.set_title("4. 3D Print-Ready Bed Orientation (Z = 0.00mm)", color='white', fontsize=12, weight='bold', pad=10)
    
    v_p = shaft_printable.vertices
    f_p = shaft_printable.faces
    col_p = Poly3DCollection(v_p[f_p], alpha=0.90, facecolor='#2ecc71', edgecolor='#1b7a43', linewidth=0.2)
    ax4.add_collection3d(col_p)
    ax4.set_xlim(-12, 12)
    ax4.set_ylim(-12, 12)
    ax4.set_zlim(0, 15)
    ax4.tick_params(colors='white')
    ax4.set_xlabel('X (mm)', color='white')
    ax4.set_ylabel('Y (mm)', color='white')
    ax4.set_zlabel('Z (mm)', color='white')
    ax4.view_init(elev=35, azim=45)
    
    plt.tight_layout()
    out_path = "testing/oem_shaft_rocker_inspection.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")

if __name__ == '__main__':
    plot_oem_shaft_inspection()
