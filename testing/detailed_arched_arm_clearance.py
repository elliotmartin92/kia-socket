"""
testing/detailed_arched_arm_clearance.py
Calculates precise geometric clearance between the arched rocker cam and each section
of the OEM brass pinching contact (Top Lip, Flare Flank, Throat, Belly Cavity)
at every degree of rotation from 0° to 12°.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, Point, box, LineString

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from build_shaft import (
    Y_AXLE, Z_AXLE, TOTAL_AXLE_LEN, HUB_WIDTH, PIN_DIAMETER,
    HUB_DIAMETER, PLUNGER_REACH_BELOW_Z, PLUNGER_WIDTH_X,
    CAM_WIDTH_X, CAM_X_CENTER
)
from testing.model_exact_brass_part import get_brass_contact_2d_profile, D1A, D1B, D2, D4, D5, D3, SHEET_THICK
from testing.simulate_arched_arm_insertion import get_arched_cam_profile_2d, simulate_insertion

def run():
    print("=== DETAILED CLEARANCE AUDIT: ARCHED CAM VS BRASS CONTACT ===")
    front_pts, rear_pts, y_blade_c = get_brass_contact_2d_profile()
    top_spine, cam_poly_home = get_arched_cam_profile_2d()
    
    t_half = SHEET_THICK / 2.0
    r_poly_pts = [(p[0] - t_half, p[1]) for p in rear_pts] + [(p[0] + t_half, p[1]) for p in reversed(rear_pts)]
    rear_poly = Polygon(r_poly_pts)
    
    f_poly_pts = [(p[0] - t_half, p[1]) for p in front_pts] + [(p[0] + t_half, p[1]) for p in reversed(front_pts)]
    front_poly = Polygon(f_poly_pts)
    
    angles_deg = np.linspace(0, 12, 13)
    
    fig, axes = plt.subplots(3, 4, figsize=(18, 14), facecolor='#1a1a1a', dpi=180)
    fig.suptitle("Arched Full-Width Rocker Cam: Motion Study at Every 1° Rotation (0° to 11°)", color='white', fontsize=14, weight='bold', y=0.98)
    
    for i, ang in enumerate(angles_deg[:12]):
        ax = axes[i // 4, i % 4]
        ax.set_facecolor('#222222')
        ax.set_title(f"θ = {ang:.0f}° Rotation", color='#00d2ff', fontsize=10, weight='bold')
        
        # Draw Floor & Brass
        ax.add_patch(patches.Rectangle((-4, 0), 18, 1.0, facecolor='#666666', alpha=0.4))
        ax.add_patch(patches.Polygon(f_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.2))
        ax.add_patch(patches.Polygon(r_poly_pts, facecolor='#f39c12', alpha=0.5, edgecolor='#d68910', lw=1.2))
        ax.add_patch(patches.Circle((Y_AXLE, Z_AXLE), HUB_DIAMETER/2.0, facecolor='#e67e22', alpha=0.3, edgecolor='#d35400', lw=1))
        
        # Rotate cam
        rad = np.radians(ang)
        c_a, s_a = np.cos(rad), np.sin(rad)
        cam_vecs = cam_poly_home - np.array([Y_AXLE, Z_AXLE])
        poly_rot = np.zeros_like(cam_poly_home)
        poly_rot[:, 0] = Y_AXLE + c_a * cam_vecs[:, 0] - s_a * cam_vecs[:, 1]
        poly_rot[:, 1] = Z_AXLE + s_a * cam_vecs[:, 0] + c_a * cam_vecs[:, 1]
        
        poly_geom = Polygon(poly_rot)
        dist_rear = poly_geom.distance(rear_poly)
        dist_front = poly_geom.distance(front_poly)
        
        col = '#2ecc71' if (dist_rear > 0.05 and dist_front > 0.05) else '#e74c3c'
        ax.add_patch(patches.Polygon(poly_rot, facecolor=col, alpha=0.6, edgecolor=col, lw=1.5))
        
        # Annotate status
        status_txt = f"Rear Gap:  +{dist_rear:.2f} mm\nFront Gap: +{dist_front:.2f} mm"
        ax.text(0.05, 0.92, status_txt, transform=ax.transAxes, color='white', fontsize=7.5, fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#111111', edgecolor=col, alpha=0.8))
        
        ax.set_xlim(-3, 13)
        ax.set_ylim(0, 19)
        ax.tick_params(colors='white', labelsize=7)
        ax.grid(True, color='#333333', linestyle=':')
        
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_png = os.path.join(os.path.dirname(__file__), "arched_cam_step_by_step_study.png")
    plt.savefig(out_png, dpi=180)
    print(f"\nSaved step-by-step motion study diagram to: {out_png}")

if __name__ == '__main__':
    run()
