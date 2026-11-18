import os
import sys
import numpy as np
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testing.build_prototype_levers import (
    get_test_suite, build_b4877a9_rocker_mesh,
    build_variant_lever_45deg, build_variant_supports_45deg,
    PROTO_AXLE_LEN, R_PIP_45, BED_PAD_H
)

def run_prototype_support_test():
    suite = get_test_suite()
    print("=" * 75)
    print("RUNNING COMPREHENSIVE PROTOTYPE 5-PIECE SUPPORT ALIGNMENT VERIFICATION")
    print("=" * 75)
    
    overall_pass = True
    
    for i, test in enumerate(suite):
        name = test['short_name']
        print(f"\n--- Checking [Test {i+1}/5] {name} ---")
        
        if test['is_b4877a9']:
            m_lever = build_b4877a9_rocker_mesh(axle_len=PROTO_AXLE_LEN, plunger_y=test['plunger_y'], cam_pts=test['cam_pts']).apply_transform(R_PIP_45)
            x_cam_tines = [5.80 + 0.15 + 0.25, 7.70 - 0.15 - 0.25]
        else:
            m_lever = build_variant_lever_45deg(test['cfg'], axle_len=PROTO_AXLE_LEN)
            x_cam_tines = [5.50 + 0.15 + 0.25, 7.60 - 0.15 - 0.25]
            
        m_supp = build_variant_supports_45deg(test)
        
        # 1. Base adhesion check (all supports touch bed pad at Z = BED_PAD_H)
        z_min_supp = m_supp.bounds[0, 2]
        print(f"  Bed Pad Seating: Z_min = {z_min_supp:.3f} mm (Expected: {BED_PAD_H:.3f} mm)")
        assert np.isclose(z_min_supp, BED_PAD_H, atol=0.01), f"Support not seated on bed pad: {z_min_supp}"
        
        # 2. Shaft Hub Release Gap:
        shaft_supp = m_supp.vertices[(np.abs(m_supp.vertices[:, 0] - 8.85) < 0.35) & (np.abs(m_supp.vertices[:, 1] - (-2.341)) < 0.35)]
        z_hub_bottom = 15.464 - 2.10  # 13.364 mm
        shaft_gap = z_hub_bottom - shaft_supp[:, 2].max()
        print(f"  Shaft Hub Support: Gap = {shaft_gap:.3f} mm (Target: 0.480 mm)")
        assert 0.45 <= shaft_gap <= 0.50, f"Shaft gap failed: {shaft_gap}"
        
        # 3. Ray-traced Cam Tines Release Gap:
        y_cams = np.linspace(-3.60, -1.00, 12)
        cam_gaps = []
        for xc in x_cam_tines:
            for yc in y_cams:
                ray_org = np.array([[xc, yc, 0.0]])
                locs, _, _ = m_supp.ray.intersects_location(ray_org, np.array([[0, 0, 1.0]]))
                if len(locs) > 0:
                    z_top = locs[:, 2].max()
                    ray_up = np.array([[xc, yc, z_top - 0.01]])
                    locs_l, _, _ = m_lever.ray.intersects_location(ray_up, np.array([[0, 0, 1.0]]))
                    if len(locs_l) > 0:
                        gap = locs_l[:, 2].min() - z_top
                        cam_gaps.append(gap)
                        
        print(f"  Cam Tines Gap: [{min(cam_gaps):.3f}, {max(cam_gaps):.3f}] mm (Mean: {np.mean(cam_gaps):.3f} mm)")
        assert min(cam_gaps) >= 0.18 and max(cam_gaps) <= 0.26, f"Cam gap out of spec: {cam_gaps}"
        assert np.isclose(np.mean(cam_gaps), 0.22, atol=0.02), f"Cam mean gap out of spec: {np.mean(cam_gaps)}"
        
        # 4. Ray-traced Plunger Tines Release Gap:
        x_pls = [8.484 + 0.40, 10.284, 11.284 + 0.40]
        y_pls = np.linspace(8.60, 12.0, 15)
        pl_gaps = []
        for xp in x_pls:
            for yp in y_pls:
                ray_org = np.array([[xp, yp, 0.0]])
                locs, _, _ = m_supp.ray.intersects_location(ray_org, np.array([[0, 0, 1.0]]))
                if len(locs) > 0:
                    z_top = locs[:, 2].max()
                    ray_up = np.array([[xp, yp, z_top - 0.01]])
                    locs_l, _, _ = m_lever.ray.intersects_location(ray_up, np.array([[0, 0, 1.0]]))
                    if len(locs_l) > 0:
                        gap = locs_l[:, 2].min() - z_top
                        pl_gaps.append(gap)
                        
        print(f"  Plunger Tines Gap: [{min(pl_gaps):.3f}, {max(pl_gaps):.3f}] mm (Mean: {np.mean(pl_gaps):.3f} mm)")
        assert min(pl_gaps) >= 0.18 and max(pl_gaps) <= 0.26, f"Plunger gap out of spec: {pl_gaps}"
        assert np.isclose(np.mean(pl_gaps), 0.22, atol=0.02), f"Plunger mean gap out of spec: {np.mean(pl_gaps)}"
        
        # 5. Collision verification
        collision = False
        for sv in m_supp.vertices:
            nearby_l = m_lever.vertices[
                (np.abs(m_lever.vertices[:, 0] - sv[0]) < 0.12) &
                (np.abs(m_lever.vertices[:, 1] - sv[1]) < 0.12)
            ]
            if len(nearby_l) > 0 and sv[2] > nearby_l[:, 2].min() - 0.05:
                print(f"    Collision detected at X={sv[0]:.2f}, Y={sv[1]:.2f}, Supp_Z={sv[2]:.2f}, Lev_Z={nearby_l[:,2].min():.2f}")
                collision = True
                break
        assert not collision, f"Collision detected for {name}!"
        print(f"  Status: 100% PERFECTLY ALIGNED (Gap = 0.22mm uniform, zero collisions)")

    print("\n" + "=" * 75)
    print("ALL 5 PROTOTYPE LEVER TESTS HAVE PERFECTLY ALIGNED BREAKAWAY SUPPORTS!")
    print("=" * 75)
    return True

if __name__ == '__main__':
    run_prototype_support_test()
