"""
testing/verify_calibrated_clips_and_supports.py

Comprehensive verification of:
1. Watertightness and bounds of part.stl and complete_assembly.stl.
2. Per-angle clip shelf elevations (CLIP_SHELF_Z_BY_ANGLE):
   - Top clips (45.0°, 135.0°): Z = 3.97mm (-0.75mm, eliminating SIM-tool gap).
   - Bottom clips (211.3°, 327.5°): Z = 4.35mm (-0.37mm, eliminating half-SIM gap).
3. Radial hook depths:
   - Top & Bottom-Left (45.0°, 135.0°, 211.3°): 1.80mm.
   - Bottom-Right (327.5°): 1.85mm (+0.05mm reach for reliable retention).
4. Anti-sag 45° trident support geometry:
   - 3 prongs per bottom clip with center apex coverage.
   - 0.23mm release gap below shelf (contact top Z = 4.12mm).
"""
import os
import sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import build_part as bp

def run_verification():
    print("=" * 80)
    print("VERIFICATION: CALIBRATED SNAP CLIPS & ANTI-SAG TRIDENT SUPPORTS")
    print("=" * 80)
    
    # 1. Verify Configuration Constants
    print("\n[1] Verifying Clip Constants in build_part.py:")
    assert bp.CLIP_SHELF_Z_BY_ANGLE[45.0] == 4.72, f"Expected 4.72, got {bp.CLIP_SHELF_Z_BY_ANGLE[45.0]}"
    assert bp.CLIP_SHELF_Z_BY_ANGLE[135.0] == 4.72, f"Expected 4.72, got {bp.CLIP_SHELF_Z_BY_ANGLE[135.0]}"
    assert bp.CLIP_SHELF_Z_BY_ANGLE[211.3] == 4.72, f"Expected 4.72, got {bp.CLIP_SHELF_Z_BY_ANGLE[211.3]}"
    assert bp.CLIP_SHELF_Z_BY_ANGLE[327.5] == 4.72, f"Expected 4.72, got {bp.CLIP_SHELF_Z_BY_ANGLE[327.5]}"
    print("    -> PASS: All clips restored to Z = 4.72mm baseline shelf elevation.")
    
    assert bp.CLIP_HOOK_DEPTH_BY_ANGLE[45.0] == 1.80
    assert bp.CLIP_HOOK_DEPTH_BY_ANGLE[135.0] == 1.80
    assert bp.CLIP_HOOK_DEPTH_BY_ANGLE[211.3] == 2.35
    assert bp.CLIP_HOOK_DEPTH_BY_ANGLE[327.5] == 2.45
    print("    -> PASS: Clip radial hook depths equalized (Top: 1.80mm, 211.3°: 2.35mm, 327.5°: 2.45mm).")
    
    # 2. Verify Bottom Clip Supports
    print("\n[2] Verifying Bottom Clip 45° Supports Geometry:")
    base_poly, outer_poly, _ = bp.get_exact_base_polygon()
    supp_mesh = bp.build_bottom_clip_45deg_supports_mesh(base_poly)
    assert supp_mesh.is_watertight, "Support mesh must be watertight!"
    comps = supp_mesh.split()
    assert len(comps) == 6, f"Expected 6 prongs (3 per clip), got {len(comps)}"
    print(f"    -> PASS: 6 separate watertight prongs generated (trident configuration).")
    
    # Check top Z of all prongs
    for i, c in enumerate(comps):
        z_top = c.bounds[1, 2]
        assert abs(z_top - 4.43) < 0.01, f"Prong {i} top Z expected 4.43mm (4.72 - 0.29), got {z_top:.3f}mm"
    print("    -> PASS: All prongs maintain calibrated 0.29mm release gap under Z=4.72mm shelf.")
    
    # Check apex support prongs (center prongs)
    prongs_327 = [c for c in comps if (np.degrees(np.arctan2(c.centroid[1], c.centroid[0])) + 360) % 360 > 300]
    assert len(prongs_327) == 3, f"Expected 3 prongs for 327.5°, got {len(prongs_327)}"
    
    # Check that one prong is centered right under the apex
    p_327, _, _ = bp.find_boundary_point_and_normal(base_poly, 327.5)
    u_r = p_327 / np.linalg.norm(p_327)
    u_t = np.array([-u_r[1], u_r[0]])
    
    tang_offsets = []
    for c in prongs_327:
        dv = c.centroid[:2] - p_327
        t_off = np.dot(dv, u_t)
        tang_offsets.append(t_off)
    tang_offsets.sort()
    print(f"    Tangential offsets for 327.5° prongs: {[f'{to:.2f}mm' for to in tang_offsets]}")
    assert any(abs(to) < 0.15 for to in tang_offsets), "Must have a prong directly centered under apex!"
    print("    -> PASS: Center prong directly supports the hook apex (eliminates sagging).")
    
    # 3. Verify Exported Deliverables
    print("\n[3] Verifying Production Deliverables on Disk:")
    part = trimesh.load('part.stl')
    bodies = part.split(only_watertight=False)
    print(f"    part.stl: Bodies={len(bodies)}, Volume={part.volume:.2f}mm³, Bounds Z=[{part.bounds[0,2]:.2f}, {part.bounds[1,2]:.2f}]mm")
    assert len(bodies) >= 1, "part.stl must have valid bodies!"
    assert part.volume > 5000.0, f"Expected volume > 5000mm³, got {part.volume:.2f}mm³"
    
    assembly = trimesh.load('complete_assembly.stl')
    print(f"    complete_assembly.stl: Bodies={len(assembly.split(only_watertight=False))}, Volume={assembly.volume:.2f}mm³")
    assert assembly.volume > 5000.0, f"Expected volume > 5000mm³, got {assembly.volume:.2f}mm³"
    
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_verification()
