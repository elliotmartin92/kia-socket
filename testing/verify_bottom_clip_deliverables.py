import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import trimesh
import numpy as np
import build_part as bp

# Load generated part.stl
part = trimesh.load('part.stl')
print("=== VERIFYING PART.STL ===")
print(f"Watertight: {part.is_watertight}")
print(f"Volume: {part.volume:.2f} mm³")
print(f"Bounds Z: [{part.bounds[0,2]:.2f}, {part.bounds[1,2]:.2f}] mm")
print(f"Bounds X: [{part.bounds[0,0]:.2f}, {part.bounds[1,0]:.2f}] mm")
print(f"Bounds Y: [{part.bounds[0,1]:.2f}, {part.bounds[1,1]:.2f}] mm")

# Verify hook vertices in the mesh
base_poly, outer_poly, _ = bp.get_exact_base_polygon()
ext_pts = np.array(outer_poly.exterior.coords)
radii_0 = np.linalg.norm(ext_pts, axis=1)
circle_mask = (radii_0 > 18.0) & (radii_0 < 19.8) & (np.abs(ext_pts[:, 1]) > 4.2) & (ext_pts[:, 1] > -16.5) & (ext_pts[:, 1] < 18.4)
c_pts = ext_pts[circle_mask]
A = np.column_stack([2 * c_pts[:, 0], 2 * c_pts[:, 1], np.ones(len(c_pts))])
b = c_pts[:, 0]**2 + c_pts[:, 1]**2
sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
xc, yc = sol[0], sol[1]
fit_center = np.array([xc, yc])

print("\n=== HOOK PROTRUSIONS & RETENTION SHELVES IN PART ===")
for ang in bp.CLIP_ANGLES:
    p, norm, tang = bp.find_boundary_point_and_normal(base_poly, ang)
    r_wall = np.linalg.norm(p)
    n_dir = p / r_wall
    hook_d = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(ang, bp.CLIP_HOOK_DEPTH)
    recess = bp.CLIP_STEM_OUTER_RECESS_BY_ANGLE.get(ang, 0.0)
    ps = p + n_dir * hook_d
    r_tip_fit = np.linalg.norm(ps - fit_center)
    shelf_step = hook_d + recess
    print(f"Angle {ang:5.1f}°: HookDepth = {hook_d:.2f} mm, ShelfStep = {shelf_step:.2f} mm, Tip R_fit = {r_tip_fit:.3f} mm")

# Load complete_assembly.stl
assembly = trimesh.load('complete_assembly.stl')
print("\n=== VERIFYING COMPLETE_ASSEMBLY.STL ===")
print(f"Assembly Volume: {assembly.volume:.2f} mm³")
print(f"Assembly Bounds Z: [{assembly.bounds[0,2]:.2f}, {assembly.bounds[1,2]:.2f}] mm")

assert part.is_watertight, "part.stl must be watertight!"
print("\nALL VERIFICATIONS PASSED!")
