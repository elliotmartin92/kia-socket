import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from shapely.geometry import LineString, Point
import build_part as bp

base_poly, outer_poly, _ = bp.get_exact_base_polygon()
ribs_poly = bp.create_grid_ribs_poly(base_poly, outer_poly)
brackets_poly = bp.create_all_brackets_poly()
towers_poly = bp.create_shaft_support_towers_poly()
arch_poly = bp.create_arch_wall_poly()

print("=== OUTER PERIMETER GEOMETRY ANALYSIS ===")
ext_pts = np.array(outer_poly.exterior.coords)
radii_0 = np.linalg.norm(ext_pts, axis=1)
circle_mask = (radii_0 > 18.0) & (radii_0 < 19.8) & (np.abs(ext_pts[:, 1]) > 4.2) & (ext_pts[:, 1] > -16.5) & (ext_pts[:, 1] < 18.4)
c_pts = ext_pts[circle_mask]

A = np.column_stack([2 * c_pts[:, 0], 2 * c_pts[:, 1], np.ones(len(c_pts))])
b = c_pts[:, 0]**2 + c_pts[:, 1]**2
sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
xc, yc = sol[0], sol[1]
R_fit = np.sqrt(sol[2] + xc**2 + yc**2)
print(f"Fitted Circle Center: ({xc:.4f}, {yc:.4f}) mm, Fitted Radius R = {R_fit:.4f} mm")
print(f"Left Ear outer X = -21.075 (wall -19.081), Right Ear outer X = +20.200 (wall +18.206) -> Midpoint X = {(-19.081 + 18.206)/2:.4f} mm")
print(f"Top Tab center X = 0.000 (Y = 20.008), Bottom wall Y = -18.539 -> Midpoint Y = {(20.008 - 18.539)/2:.4f} mm")

names = {
    45.0: "Top-Right (45.0 deg)",
    135.0: "Top-Left (135.0 deg) [BROKE]",
    211.3: "Bottom-Left (211.3 deg)",
    327.5: "Bottom-Right (327.5 deg) [BROKE]"
}

# Wait: The part indexes in the housing using:
# 1) Left Ear + Right Ear (centered at X_ears = (-21.075 + 20.200)/2 = -0.4375 mm, Y = 0.000 mm!)
# 2) Top Tab (centered at X = 0.000 mm, Y = +18.504..20.008 mm)
datum_ears = np.array([-0.4375, 0.0])

print("\n=== CLIP BY CLIP ANALYSIS ===")
for angle in bp.CLIP_ANGLES:
    p, norm, tang = bp.find_boundary_point_and_normal(base_poly, angle)
    r_from_origin = np.linalg.norm(p)
    r_from_true_center = np.linalg.norm(p - np.array([xc, yc]))
    r_from_ears_center = np.linalg.norm(p - datum_ears)
    
    n_dir = p / np.linalg.norm(p)
    ps = p + n_dir * bp.CLIP_HOOK_DEPTH
    hook_r_origin = np.linalg.norm(ps)
    hook_r_true_center = np.linalg.norm(ps - np.array([xc, yc]))
    hook_r_ears = np.linalg.norm(ps - datum_ears)
    
    cos_ang = np.dot(n_dir, norm)
    ang_diff = np.degrees(np.arccos(np.clip(cos_ang, -1.0, 1.0)))
    normal_protrusion = np.dot(ps - p, norm)
    
    p_inner = p - norm * bp.OUTER_WALL_THICK
    inward_line = LineString([p_inner, p_inner - norm * 6.0])
    
    # Check distance to ribs, brackets, towers
    def dist_along_ray(poly_geom):
        inter = poly_geom.intersection(inward_line)
        if inter.is_empty:
            return 99.9
        return Point(p_inner).distance(inter)
        
    d_rib = dist_along_ray(ribs_poly)
    d_brk = dist_along_ray(brackets_poly)
    d_twr = dist_along_ray(towers_poly)
    
    print(f"\n--- {names[angle]} ---")
    print(f"  Wall Outer Point p        : ({p[0]:7.3f}, {p[1]:7.3f})")
    print(f"  Radius from (0,0)         : {r_from_origin:.4f} mm")
    print(f"  Radius from Circle Fit Ctr: {r_from_true_center:.4f} mm")
    print(f"  Radius from Ear Midpoint  : {r_from_ears_center:.4f} mm")
    print(f"  Hook Tip Point ps         : ({ps[0]:7.3f}, {ps[1]:7.3f})")
    print(f"  Hook Tip R from (0,0)     : {hook_r_origin:.4f} mm")
    print(f"  Hook Tip R from Fit Ctr   : {hook_r_true_center:.4f} mm")
    print(f"  Hook Tip R from Ear Ctr   : {hook_r_ears:.4f} mm")
    print(f"  Normal Protrusion         : {normal_protrusion:.4f} mm (angle diff {ang_diff:.2f} deg)")
    print(f"  Inward distance to Floor Rib (Z=1..1.5mm): {d_rib:.3f} mm")
    print(f"  Inward distance to Brackets  (Z=1..5.6mm): {d_brk:.3f} mm")
    print(f"  Inward distance to Towers    (Z=1..14mm) : {d_twr:.3f} mm")

p45 = bp.find_boundary_point_and_normal(base_poly, 45.0)[0]
p211 = bp.find_boundary_point_and_normal(base_poly, 211.3)[0]
p135 = bp.find_boundary_point_and_normal(base_poly, 135.0)[0]
p327 = bp.find_boundary_point_and_normal(base_poly, 327.5)[0]

ps45 = p45 + (p45/np.linalg.norm(p45))*bp.CLIP_HOOK_DEPTH
ps211 = p211 + (p211/np.linalg.norm(p211))*bp.CLIP_HOOK_DEPTH
ps135 = p135 + (p135/np.linalg.norm(p135))*bp.CLIP_HOOK_DEPTH
ps327 = p327 + (p327/np.linalg.norm(p327))*bp.CLIP_HOOK_DEPTH

print("\n=== DIAGONAL & PAIRWISE SPAN COMPARISON ===")
print(f"Diagonal 1 (Top-Left 135 deg to Bottom-Right 327.5 deg [THE TWO THAT BROKE!]):")
print(f"  Wall-to-Wall Span : {np.linalg.norm(p135 - p327):.4f} mm")
print(f"  Hook-to-Hook Span : {np.linalg.norm(ps135 - ps327):.4f} mm")
print(f"Diagonal 2 (Top-Right 45 deg to Bottom-Left 211.3 deg [SURVIVED]):")
print(f"  Wall-to-Wall Span : {np.linalg.norm(p45 - p211):.4f} mm")
print(f"  Hook-to-Hook Span : {np.linalg.norm(ps45 - ps211):.4f} mm")
print(f"Top Horizontal Width (Hook 135 X to Hook 45 X): {ps45[0] - ps135[0]:.4f} mm (135 X = {ps135[0]:.3f}, 45 X = {ps45[0]:.3f})")
print(f"Bottom Horizontal Width (Hook 211.3 X to Hook 327.5 X): {ps327[0] - ps211[0]:.4f} mm (211.3 X = {ps211[0]:.3f}, 327.5 X = {ps327[0]:.3f})")
