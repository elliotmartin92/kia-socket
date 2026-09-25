import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import shapely.geometry as sg
from shapely.geometry import Point, LineString
import build_part as bp

base_poly, outer_poly, _ = bp.get_exact_base_polygon()

# Fitted center
ext_pts = np.array(outer_poly.exterior.coords)
radii_0 = np.linalg.norm(ext_pts, axis=1)
circle_mask = (radii_0 > 18.0) & (radii_0 < 19.8) & (np.abs(ext_pts[:, 1]) > 4.2) & (ext_pts[:, 1] > -16.5) & (ext_pts[:, 1] < 18.4)
c_pts = ext_pts[circle_mask]
A = np.column_stack([2 * c_pts[:, 0], 2 * c_pts[:, 1], np.ones(len(c_pts))])
b = c_pts[:, 0]**2 + c_pts[:, 1]**2
sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
xc, yc = sol[0], sol[1]
fit_center = np.array([xc, yc])

print(f"Fit Center: ({xc:.4f}, {yc:.4f}) mm")

print("\n--- CURRENT CONFIGURATION ---")
for ang in bp.CLIP_ANGLES:
    p, norm, tang = bp.find_boundary_point_and_normal(base_poly, ang)
    r_wall = np.linalg.norm(p)
    r_wall_fit = np.linalg.norm(p - fit_center)
    hook_d = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(ang, bp.CLIP_HOOK_DEPTH)
    recess = bp.CLIP_STEM_OUTER_RECESS_BY_ANGLE.get(ang, 0.0)
    
    n_dir = p / r_wall
    ps = p + n_dir * hook_d
    r_hook = np.linalg.norm(ps)
    r_hook_fit = np.linalg.norm(ps - fit_center)
    local_step = hook_d + recess
    
    print(f"Clip {ang:5.1f} deg: Wall R={r_wall:.3f} (R_fit={r_wall_fit:.3f}) | HookDepth={hook_d:.2f} Recess={recess:.2f} -> ShelfStep={local_step:.2f}mm | HookTip R={r_hook:.3f} (R_fit={r_hook_fit:.3f})")

print("\n--- TEST BOTTOM CLIP INCREMENT OPTIONS ---")
# Bottom clips are 211.3 and 327.5
# Look at top clips: HookTip R_fit is ~20.91mm (45 deg) and ~20.98mm (135 deg).
# Currently bottom clips:
# 211.3: HookTip R_fit = 20.292mm (HookDepth = 1.25mm)
# 327.5: HookTip R_fit = 20.384mm (HookDepth = 1.05mm)
for d_inc in [0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70]:
    print(f"\n+ {d_inc:.2f}mm extension on bottom clips:")
    for ang in [211.3, 327.5]:
        p, norm, tang = bp.find_boundary_point_and_normal(base_poly, ang)
        r_wall = np.linalg.norm(p)
        base_h = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(ang, bp.CLIP_HOOK_DEPTH)
        recess = bp.CLIP_STEM_OUTER_RECESS_BY_ANGLE.get(ang, 0.0)
        new_h = base_h + d_inc
        n_dir = p / r_wall
        ps = p + n_dir * new_h
        r_hook = np.linalg.norm(ps)
        r_hook_fit = np.linalg.norm(ps - fit_center)
        print(f"  Clip {ang:5.1f} deg: HookDepth={new_h:.2f}mm, ShelfStep={new_h+recess:.2f}mm -> HookTip R={r_hook:.3f} (R_fit={r_hook_fit:.3f} mm, delta to Top 20.95mm = {r_hook_fit - 20.95:+.3f}mm)")
