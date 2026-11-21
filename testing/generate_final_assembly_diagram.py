"""
testing/generate_final_assembly_diagram.py
Generates a clean, low-detail technical illustration of the final assembled sub-housing:
  - Main Sub-Housing Baseplate (clean neutral slate)
  - Captive Safety Interlock Rocker in 360° Bridged Towers (warm amber/orange)
  - Seated OEM Brass Contacts (Neutral & Hot) in Brackets 1-4 with Terminal Blades (golden brass)
  - Key landmarks and mating features clearly called out without visual clutter.
"""
import os
import sys
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part as bp
import build_shaft as bs
from testing.generate_print_assembly_guide import build_brass_contact_mesh

def render_final_assembly_diagram():
    print("Generating Clean Final Assembly Diagram...")
    
    # 1. Base Part (flat assembly orientation)
    part_mesh, _ = bp.build_exact_3d_model()
    # 2. Shaft Rocker in assembly coordinates
    shaft_mesh = bs.build_shaft_rocker_mesh(in_assembly_coords=True, with_supports=False)
    # 3. Brass Contacts (Neutral and Hot)
    brass_hot = build_brass_contact_mesh(is_hot=True)
    brass_neutral = build_brass_contact_mesh(is_hot=False)

    fig = plt.figure(figsize=(24, 11), dpi=200, facecolor='#0f172a')
    
    def render_clean_mesh(ax, mesh, facecolor, alpha=1.0, edge_color=None, edge_lw=0.08):
        if mesh is not None and len(mesh.faces) > 0:
            # Downsample if too dense for smooth clean lines
            poly = Poly3DCollection(mesh.vertices[mesh.faces], alpha=alpha, 
                                  edgecolor=edge_color if edge_color else facecolor, 
                                  linewidths=edge_lw)
            poly.set_facecolor(facecolor)
            ax.add_collection3d(poly)

    # Subplot 1: Top-Front Isometric View (Main Seated Assembly)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#1e293b')
    ax1.set_title("FINAL SUB-HOUSING ASSEMBLY\n(Top-Front 3D View: Brass Contacts & Safety Lever)", 
                  color='#f8fafc', fontsize=15, fontweight='bold', pad=18)
    
    # Baseplate: Slate blue-grey
    render_clean_mesh(ax1, part_mesh, '#64748b', alpha=0.92, edge_color='#475569', edge_lw=0.1)
    # Safety Lever: Warm amber
    render_clean_mesh(ax1, shaft_mesh, '#f59e0b', alpha=1.0, edge_color='#d97706', edge_lw=0.15)
    # Brass Contacts: Golden brass
    render_clean_mesh(ax1, brass_hot, '#eab308', alpha=1.0, edge_color='#ca8a04', edge_lw=0.15)
    render_clean_mesh(ax1, brass_neutral, '#eab308', alpha=1.0, edge_color='#ca8a04', edge_lw=0.15)
    
    ax1.view_init(elev=42, azim=-55)
    ax1.set_xlim(-24, 24); ax1.set_ylim(-24, 24); ax1.set_zlim(-8, 22)
    ax1.set_axis_off()

    # Labels on ax1
    ax1.text2D(0.50, 0.93, "Fully Assembled Sub-Housing Ready for Housing Installation", 
               transform=ax1.transAxes, color='#ffffff', fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#0f172a', ec='#38bdf8', lw=1.2))

    ax1.text2D(0.20, 0.72, 
               "Left Brass Contact (Neutral)\nSeated in Brackets 1 & 2", 
               transform=ax1.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))

    ax1.text2D(0.80, 0.72, 
               "Right Brass Contact (Hot)\nSeated in Brackets 3 & 4", 
               transform=ax1.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))

    ax1.text2D(0.50, 0.58, 
               "Bulked Cam Tab (Centered in Throat)\nEngaged by Hot Plug Blade", 
               transform=ax1.transAxes, color='#fed7aa', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#f59e0b', lw=1.2))

    ax1.text2D(0.20, 0.20, 
               "Monolithic Rear Cross-Tie Bridge\nRigid anti-spreading truss", 
               transform=ax1.transAxes, color='#93c5fd', fontsize=10, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#3b82f6', lw=1.2))

    ax1.text2D(0.80, 0.20, 
               "4x Perimeter Snap Clips\nLatch into front housing slots", 
               transform=ax1.transAxes, color='#cbd5e1', fontsize=10, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#94a3b8', lw=1.2))

    # Subplot 2: Bottom-Angle View (Terminal Blades & Plunger Arm Output)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d', facecolor='#1e293b')
    ax2.set_title("UNDER-FLOOR MATING INTERFACE\n(Bottom View: Terminal Blades & Plunger Actuator)", 
                  color='#f8fafc', fontsize=15, fontweight='bold', pad=18)
    
    render_clean_mesh(ax2, part_mesh, '#64748b', alpha=0.90, edge_color='#475569', edge_lw=0.1)
    render_clean_mesh(ax2, shaft_mesh, '#f59e0b', alpha=1.0, edge_color='#d97706', edge_lw=0.15)
    render_clean_mesh(ax2, brass_hot, '#eab308', alpha=1.0, edge_color='#ca8a04', edge_lw=0.15)
    render_clean_mesh(ax2, brass_neutral, '#eab308', alpha=1.0, edge_color='#ca8a04', edge_lw=0.15)

    ax2.view_init(elev=-35, azim=-55) # Looking up from underneath
    ax2.set_xlim(-24, 24); ax2.set_ylim(-24, 24); ax2.set_zlim(-10, 20)
    ax2.set_axis_off()

    ax2.text2D(0.50, 0.93, "Under-Floor Interface Engaging PCB & Front Housing", 
               transform=ax2.transAxes, color='#ffffff', fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#0f172a', ec='#38bdf8', lw=1.2))

    ax2.text2D(0.20, 0.72, 
               "Neutral Terminal Blade\nPlunges into receiver socket", 
               transform=ax2.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))

    ax2.text2D(0.80, 0.72, 
               "Hot Terminal Blade\nPlunges into receiver socket", 
               transform=ax2.transAxes, color='#fef08a', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#0f172a', ec='#eab308', lw=1.2))

    ax2.text2D(0.50, 0.22, 
               "Extended Plunger Arm (Z ≤ -7.0mm)\nDepresses PCB Tactile Microswitch", 
               transform=ax2.transAxes, color='#fca5a5', fontsize=11, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.35', fc='#0f172a', ec='#ef4444', lw=1.5))

    ax2.text2D(0.50, 0.08, 
               "Integrated Slit Chimneys (Z = -2.47mm) Guide Terminal Blades with Zero Deflection", 
               transform=ax2.transAxes, color='#86efac', fontsize=10.5, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.3', fc='#052e16', ec='#22c55e', lw=1.2))

    plt.tight_layout()
    out_path = 'testing/final_assembly_diagram.png'
    fig.savefig(out_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"Successfully generated: {out_path}")

if __name__ == '__main__':
    render_final_assembly_diagram()
