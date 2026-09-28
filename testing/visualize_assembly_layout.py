import os, sys
import trimesh
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from build_part import build_exact_3d_model, build_slit_insert_mesh, build_cooling_tower_mesh
from build_shaft import build_shaft_rocker_mesh

def plot_layout(positions_to_test):
    part_mesh, base_poly = build_exact_3d_model()
    ins_left = build_slit_insert_mesh(is_right=False)
    ins_left.apply_translation([27.50, -5.00, 0.00])

    ins_right = build_slit_insert_mesh(is_right=True)
    ins_right.apply_translation([27.50, 5.00, 0.00])

    shaft_printable = build_shaft_rocker_mesh(in_assembly_coords=False)
    shaft_plate = shaft_printable.copy()
    shaft_plate.apply_translation([27.50, 16.00, 0.00])

    fig, axes = plt.subplots(1, len(positions_to_test), figsize=(7 * len(positions_to_test), 7), dpi=150)
    if len(positions_to_test) == 1:
        axes = [axes]

    for ax, (title, (r, x, y)) in zip(axes, positions_to_test.items()):
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Plot Main Part footprint (slice or projection)
        poly = part_mesh.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
        if poly is not None:
            for p in poly.discrete:
                ax.plot(p[:, 0], p[:, 1], 'b-', linewidth=1.5, label='Main Part' if 'Main Part' not in ax.get_legend_handles_labels()[1] else "")
                ax.fill(p[:, 0], p[:, 1], 'lightblue', alpha=0.3)
                
        # Slit left
        poly_sl = ins_left.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
        if poly_sl is not None:
            for p in poly_sl.discrete:
                ax.plot(p[:, 0], p[:, 1], 'g-', linewidth=1.5, label='Slits' if 'Slits' not in ax.get_legend_handles_labels()[1] else "")
                ax.fill(p[:, 0], p[:, 1], 'lightgreen', alpha=0.4)
                
        # Slit right
        poly_sr = ins_right.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
        if poly_sr is not None:
            for p in poly_sr.discrete:
                ax.plot(p[:, 0], p[:, 1], 'g-', linewidth=1.5)
                ax.fill(p[:, 0], p[:, 1], 'lightgreen', alpha=0.4)
                
        # Shaft Rocker
        poly_sh = shaft_plate.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
        if poly_sh is not None:
            for p in poly_sh.discrete:
                ax.plot(p[:, 0], p[:, 1], 'm-', linewidth=1.5, label='Shaft Rocker' if 'Shaft Rocker' not in ax.get_legend_handles_labels()[1] else "")
                ax.fill(p[:, 0], p[:, 1], 'plum', alpha=0.4)
                
        # Tower
        circle = plt.Circle((x, y), r, color='crimson', fill=True, alpha=0.6, label=f'Cooling Tower (r={r:.1f}mm)')
        ax.add_patch(circle)
        ax.plot(x, y, 'rx')
        
        # Annotations
        ax.annotate(f"Tower\n(X={x:.1f}, Y={y:.1f}\nØ={r*2:.1f}mm)", xy=(x, y), xytext=(x + 4, y - 4),
                    arrowprops=dict(arrowstyle="->", color='red'))
                    
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.legend(loc='upper left', fontsize=9)
        
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), 'preview_layout_comparison.png')
    plt.savefig(out_path)
    print(f"Saved layout preview to {out_path}")

if __name__ == '__main__':
    positions = {
        "Current (r=4.0mm, [27.5, -16.0])": (4.0, 27.50, -16.00),
        "Option 1: r=2.0mm, [30.0, -25.0]": (2.0, 30.00, -25.00),
        "Option 2: r=2.0mm, [35.0, -25.0]": (2.0, 35.00, -25.00),
    }
    plot_layout(positions)
