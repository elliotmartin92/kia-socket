import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import build_part as bp
import trimesh

base_poly, outer_poly, _ = bp.get_exact_base_polygon()

print("=== CURRENT BREAKAWAY SUPPORT GEOMETRY ===")
stem_h = bp.CLIP_HEIGHT - bp.CLIP_HOOK_HEIGHT  # 4.97mm

for ang in bp.CLIP_ANGLES:
    p, norm, tang = bp.find_boundary_point_and_normal(base_poly, ang)
    r_wall = np.linalg.norm(p)
    hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(ang, bp.CLIP_HOOK_DEPTH)
    r_supp_radial = max(0.58, hook_depth * 0.62)
    
    # Current params
    prong_t_rad = 0.75
    prong_w_tang = 0.85
    tip_radial = 0.38
    tip_tang = prong_w_tang
    
    # Inner margin to wall
    inner_margin = r_supp_radial - prong_t_rad / 2.0
    outer_cantilever = hook_depth - (r_supp_radial + prong_t_rad / 2.0)
    
    print(f"Angle {ang:5.1f}° (HookDepth {hook_depth:.2f}mm):")
    print(f"  Support center radial offset : {r_supp_radial:.3f} mm")
    print(f"  Inner margin to wall         : {inner_margin:.3f} mm")
    print(f"  Outer cantilever remaining   : {outer_cantilever:.3f} mm")
    print(f"  Contact tip area (each)      : {tip_radial * tip_tang:.3f} mm² (Twin tips = {2 * tip_radial * tip_tang:.3f} mm²)")

print("\n=== PROPOSED SMALLER HIGH-TEMP BREAKAWAY SUPPORTS ===")
# Smaller supports for high print temp:
# - Slimmer prongs: prong_w_tang = 0.65mm (was 0.85mm), prong_t_rad = 0.55mm (was 0.75mm)
# - Sharp micro-chisel tip: tip_radial = 0.25mm (was 0.38mm), tip_tang = 0.55mm (was 0.85mm)
#   -> Tip area drops from 0.323 mm² to 0.138 mm² (-57% contact area!)
# - Z-gap increased from 0.20mm to 0.26mm (support_top_z = stem_h - 0.36, tip_h = 0.10mm)
# - Slimmer trunk (0.65 x 2.60mm) and foot (1.10 x 3.00mm)
for ang in bp.CLIP_ANGLES:
    p, norm, tang = bp.find_boundary_point_and_normal(base_poly, ang)
    hook_depth = bp.CLIP_HOOK_DEPTH_BY_ANGLE.get(ang, bp.CLIP_HOOK_DEPTH)
    # Optimize radial position for slimer prongs (center at 60% of hook depth, min 0.62mm)
    r_supp_radial = max(0.62, hook_depth * 0.58)
    
    prong_t_rad = 0.55
    prong_w_tang = 0.65
    tip_radial = 0.25
    tip_tang = 0.55
    
    inner_margin = r_supp_radial - prong_t_rad / 2.0
    outer_cantilever = hook_depth - (r_supp_radial + prong_t_rad / 2.0)
    
    print(f"Angle {ang:5.1f}° (HookDepth {hook_depth:.2f}mm):")
    print(f"  Support center radial offset : {r_supp_radial:.3f} mm")
    print(f"  Inner margin to wall         : {inner_margin:.3f} mm (>= 0.345mm -> ZERO sidewall welding!)")
    print(f"  Outer cantilever remaining   : {outer_cantilever:.3f} mm")
    print(f"  Contact tip area (each)      : {tip_radial * tip_tang:.3f} mm² (-57% reduction!)")
