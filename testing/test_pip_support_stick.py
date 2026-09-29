"""
testing/test_pip_support_stick.py
Tests the generation of the dedicated breakaway support strut for the Print-in-Place plunger arm.
"""

import os
import sys
import numpy as np
import trimesh

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_shaft import build_shaft_rocker_mesh
from testing.explore_pip_closed_towers import build_pip_closed_towers_mesh
from build_part import build_exact_3d_model

def test_pip_support():
    print("Building baseplate and PIP shaft...")
    part_flat, _ = build_exact_3d_model()
    shaft = build_shaft_rocker_mesh(hub_w=7.20, in_assembly_coords=True, with_supports=False)
    
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    part_t = part_flat.copy().apply_transform(R)
    shaft_t = shaft.copy().apply_transform(R)
    
    z_min = part_t.bounds[0, 2]
    part_t.apply_translation([0, 0, -z_min])
    shaft_t.apply_translation([0, 0, -z_min])
    
    print(f"Part bounds Z: {part_t.bounds[:, 2]}")
    print(f"Shaft bounds Z: {shaft_t.bounds[:, 2]}")
    
    # Plunger lowest point in tilted coords
    plunger_v = shaft_t.vertices[shaft_t.vertices[:, 0] > 8.0] # Plunger is at X in [8.48, 12.08]
    idx_min = np.argmin(plunger_v[:, 2])
    p_lowest = plunger_v[idx_min]
    print(f"Plunger lowest point: X={p_lowest[0]:.3f}, Y={p_lowest[1]:.3f}, Z={p_lowest[2]:.3f}")
    
    # Design breakaway stick
    z_bed = 0.60 # Bed pad surface
    standoff = 0.20 # 0.20mm release gap
    z_stick_top = p_lowest[2] - standoff
    stick_h = z_stick_top - z_bed
    print(f"Stick height: {stick_h:.3f} mm (Z from {z_bed:.2f} to {z_stick_top:.2f} mm)")
    
    # Main trunk: 1.20mm in X x 1.60mm in Y
    trunk_h = max(1.0, stick_h - 1.20)
    trunk = trimesh.creation.box([1.40, 1.80, trunk_h])
    trunk.apply_translation([p_lowest[0], p_lowest[1], z_bed + trunk_h/2.0])
    
    # Chisel tip: 0.60mm in X x 1.00mm in Y x 1.20mm in Z
    tip = trimesh.creation.box([0.70, 1.00, 1.20])
    tip.apply_translation([p_lowest[0], p_lowest[1], z_stick_top - 0.60])
    
    stick = trimesh.util.concatenate([trunk, tip])
    print(f"Stick volume: {stick.volume:.2f} mm3, watertight: {stick.is_watertight}")
    
    # Check gap between stick and shaft
    from scipy.spatial import cKDTree
    tree_shaft = cKDTree(shaft_t.vertices)
    dists, _ = tree_shaft.query(stick.vertices)
    print(f"Min gap from stick to shaft: {np.min(dists):.3f} mm (target >= {standoff:.2f} mm)")
    assert np.min(dists) >= standoff - 0.05, f"Gap too small: {np.min(dists)}"
    print("SUCCESS: Breakaway support strut test passed!")

if __name__ == '__main__':
    test_pip_support()
