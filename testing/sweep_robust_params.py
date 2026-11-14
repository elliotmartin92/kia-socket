import numpy as np
import trimesh
import os, sys
from scipy.spatial import cKDTree
from test_robust_b4_strut import build_robust_strut, shaft_tilted, m_tilted

tree_cam = cKDTree(shaft_tilted['cam'].vertices)
tree_p = cKDTree(shaft_tilted['plunger'].vertices)
tree_b4 = cKDTree(m_tilted.vertices)

for x_c in [8.70, 8.80, 8.90, 9.00]:
    for fork_w in [1.60, 1.80, 2.00]:
        strut = build_robust_strut(x_c=x_c, fork_w=fork_w, tine_w=0.55)
        d_cam, _ = tree_cam.query(strut.vertices)
        d_p, _ = tree_p.query(strut.vertices)
        d_b4, _ = tree_b4.query(strut.vertices)
        print(f"X_c={x_c:.2f}, W={fork_w:.2f} (X in [{x_c-fork_w/2:.2f}, {x_c+fork_w/2:.2f}]): Cam={np.min(d_cam):.3f}mm, Plunger={np.min(d_p):.3f}mm, B4_dist={np.min(d_b4):.3f}mm")
