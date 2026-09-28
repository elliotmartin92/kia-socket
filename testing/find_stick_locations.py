"""
testing/find_stick_locations.py
Vectorized triangle intersection without rtree to find the exact Z height of the
underside of the Cam tab and Plunger arm for any (X, Y) coordinate.
"""

import trimesh
import numpy as np

mesh = trimesh.load('shaft_rocker_clean.stl')

triangles = mesh.vertices[mesh.faces] # (N, 3, 3)

def get_z_at_xy(x_pt, y_pt):
    """Find all Z intersections of vertical line at (x_pt, y_pt) with triangles."""
    # 2D projection on XY plane
    p0 = triangles[:, 0, :2]
    p1 = triangles[:, 1, :2]
    p2 = triangles[:, 2, :2]
    
    # Vectors
    v0 = p2 - p0
    v1 = p1 - p0
    v2 = np.array([x_pt, y_pt]) - p0
    
    # Dot products
    dot00 = np.sum(v0 * v0, axis=1)
    dot01 = np.sum(v0 * v1, axis=1)
    dot02 = np.sum(v0 * v2, axis=1)
    dot11 = np.sum(v1 * v1, axis=1)
    dot12 = np.sum(v1 * v2, axis=1)
    
    # Barycentric coordinates
    inv_denom = 1.0 / (dot00 * dot11 - dot01 * dot01 + 1e-12)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    
    # Check if point is inside triangle
    inside = (u >= -1e-5) & (v >= -1e-5) & (u + v <= 1.00001)
    
    if not np.any(inside):
        return []
    
    # Calculate Z for matching triangles
    # z = z0 + u * (z2 - z0) + v * (z1 - z0)
    z0 = triangles[inside, 0, 2]
    z1 = triangles[inside, 1, 2]
    z2 = triangles[inside, 2, 2]
    u_m = u[inside]
    v_m = v[inside]
    z_vals = z0 + u_m * (z2 - z0) + v_m * (z1 - z0)
    return sorted(z_vals)

print("=" * 80)
print("EXACT Z HEIGHT PROFILES FOR STICK SUPPORTS")
print("=" * 80)

print("\n--- 1. CAM TAB UNDERSIDE PROFILES (X in [-3.75, -1.05], Center X ~ -2.40 mm) ---")
for y in np.arange(3.5, 6.9, 0.3):
    z_hits = get_z_at_xy(-2.40, y)
    if z_hits:
        print(f"Y = {y:4.1f} mm | Bottom Z = {z_hits[0]:5.2f} mm | Top Z = {z_hits[-1]:5.2f} mm | Thickness = {z_hits[-1]-z_hits[0]:4.2f} mm")
    else:
        print(f"Y = {y:4.1f} mm | NO HIT")

print("\n--- 2. PLUNGER ARM UNDERSIDE PROFILES (X in [-1.17, 3.23], Center X ~ 1.03 mm) ---")
for y in np.arange(-6.8, -2.5, 0.4):
    z_hits = get_z_at_xy(1.03, y)
    if z_hits:
        print(f"Y = {y:5.1f} mm | Bottom Z = {z_hits[0]:5.2f} mm | Top Z = {z_hits[-1]:5.2f} mm | Thickness = {z_hits[-1]-z_hits[0]:4.2f} mm")
    else:
        print(f"Y = {y:5.1f} mm | NO HIT")

