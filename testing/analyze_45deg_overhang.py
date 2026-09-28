"""
analyze_45deg_overhang.py
Overhang analysis for 45-degree print orientation with baked-in support fins.

Based on the Support Fins spec (https://github.com/gittrahan/support-fins):
- Fins stand beside near-vertical faces, 0.2mm standoff
- Horizontal tines (one layer line) fuse into the part every few layers
- Only TRUE overhangs need fins: faces whose normal points >45deg below horizontal
  AND that have no mesh geometry directly below them to bridge/print onto
- A tilted flat face at exactly 45deg is AT the printability limit (not an overhang)
- Vertical walls, upward faces, and the 45deg incline itself are all self-supporting

This script:
1. Rotates the flat model 45 degrees (matching build_45deg_supported_part_mesh)
2. Identifies genuinely unsupported overhangs via downward ray-casting
3. Clusters them into regions and maps to named features
4. Evaluates which are already covered by the existing fin system
5. Reports gaps requiring additional fins or geometry fixes
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==============================================================================
# CONFIGURATION (per FIN-SPEC.md)
# ==============================================================================
OVERHANG_ANGLE_DEG = 45.0       # Faces needing support: normal > this angle below horizontal
LAYER_HEIGHT = 0.20             # mm - typical FDM layer height
FIN_STANDOFF = 0.20             # mm - gap between fin wall and part (FIN-SPEC)
TINE_HEIGHT = LAYER_HEIGHT      # one layer line (FIN-SPEC)
TINE_WIDTH = 0.60               # mm (FIN-SPEC: 0.4-0.8mm)
BED_PAD_Z = 0.60                # mm - bed adhesion pad height from build code
MIN_OVERHANG_AREA_MM2 = 0.5     # Ignore overhang clusters smaller than this

# Existing fin system geometry (from build_45deg_supported_part_mesh)
EXISTING_FIN_X = [-8.0, 8.0]
EXISTING_FIN_THICK = 0.80
EXISTING_FIN_Y_RANGE = (-5.80, 12.30)
EXISTING_SWAY_X = [-22.20, 21.32]
EXISTING_SWAY_Y_RANGE = (-5.0, 3.0)
EXISTING_SWAY_Z_RANGE = (0.60, 18.0)
EXISTING_TINE_Y_STATIONS_START = -5.80 + 1.5
EXISTING_TINE_SPACING = 3.1


def classify_face_overhang(normal_z):
    """Classify a face by its Z-normal component in the tilted frame.
    
    Per the fins spec, only faces whose normal points substantially downward
    are true overhangs. The 45deg tilt itself makes the original baseplate 
    surface sit right at the self-support boundary.
    
    Returns: 'safe', 'marginal', or 'overhang'
    """
    # normal_z > 0: upward-facing (safe)
    # normal_z ~ 0: vertical wall (safe, fins can attach here)
    # normal_z < 0: downward-facing
    # The critical angle: acos(-normal_z) measured from -Z
    # overhang if angle from horizontal < OVERHANG_ANGLE_DEG
    # i.e., normal_z < -sin(OVERHANG_ANGLE_DEG)
    
    threshold = -np.sin(np.radians(OVERHANG_ANGLE_DEG))  # -0.707 for 45deg
    marginal_threshold = -np.sin(np.radians(OVERHANG_ANGLE_DEG - 10))  # -0.574 for 35deg
    
    if normal_z < threshold:
        return 'overhang'
    elif normal_z < marginal_threshold:
        return 'marginal'
    return 'safe'


def find_unsupported_overhangs(mesh_tilted):
    """Find faces that are genuine overhangs with nothing below them.
    
    A face is a true unsupported overhang if:
    1. Its normal points >45deg below horizontal (downward-facing)
    2. Casting a ray straight down (-Z) from its centroid does NOT hit 
       another part of the mesh within a reasonable distance
       
    Faces where a downward ray hits nearby mesh are "bridgeable" - the 
    slicer can bridge across them or they'll print on previously-deposited 
    material.
    """
    normals = mesh_tilted.face_normals
    centroids = mesh_tilted.triangles_center
    
    threshold_z = -np.sin(np.radians(OVERHANG_ANGLE_DEG))
    
    # Step 1: Find all downward-facing faces
    overhang_mask = normals[:, 2] < threshold_z
    
    # Exclude faces at or below the bed pad (they sit on the pad)
    above_bed = centroids[:, 2] > BED_PAD_Z + 0.5
    overhang_mask = overhang_mask & above_bed
    
    overhang_indices = np.where(overhang_mask)[0]
    
    if len(overhang_indices) == 0:
        return [], []
    
    # Step 2: For each overhang face, cast a ray downward to check if 
    # there's mesh below it (self-supporting bridgeable gap)
    ray_origins = centroids[overhang_indices].copy()
    # Offset slightly below the face so we don't hit the face itself
    ray_origins[:, 2] -= 0.05
    ray_directions = np.tile([0, 0, -1], (len(overhang_indices), 1)).astype(float)
    
    # Use trimesh ray casting
    try:
        hit_faces, ray_ids, hit_locs = mesh_tilted.ray.intersects_id(
            ray_origins, ray_directions, 
            return_locations=True, multiple_hits=False
        )
        
        # Build set of overhang faces that have mesh below them
        supported_set = set()
        for i, ray_id in enumerate(ray_ids):
            orig_idx = overhang_indices[ray_id]
            dist_below = ray_origins[ray_id, 2] - hit_locs[i, 2]
            # If there's mesh within 3mm below, it can bridge/self-support
            if 0.05 < dist_below < 3.0:
                supported_set.add(orig_idx)
    except Exception:
        supported_set = set()
    
    truly_unsupported = [i for i in overhang_indices if i not in supported_set]
    bridgeable = [i for i in overhang_indices if i in supported_set]
    
    return truly_unsupported, bridgeable


def check_existing_fin_coverage(centroid):
    """Check if a point in the tilted frame is within range of existing fin supports."""
    x, y, z = centroid
    
    # Main fin walls at X = +/-8.0
    for fx in EXISTING_FIN_X:
        if abs(x - fx) < EXISTING_FIN_THICK / 2 + 2.0:  # fin wall + tine reach
            if EXISTING_FIN_Y_RANGE[0] <= y <= EXISTING_FIN_Y_RANGE[1]:
                return True, 'Main Fin'
    
    # Sway braces
    for sx in EXISTING_SWAY_X:
        if abs(x - sx) < 2.0:
            if EXISTING_SWAY_Y_RANGE[0] <= y <= EXISTING_SWAY_Y_RANGE[1]:
                if EXISTING_SWAY_Z_RANGE[0] <= z <= EXISTING_SWAY_Z_RANGE[1]:
                    return True, 'Sway Brace'
    
    # Bed pad
    if z < BED_PAD_Z + 0.3:
        return True, 'Bed Pad'
    
    return False, None


def cluster_overhangs(centroids, max_gap=3.0):
    """Cluster nearby overhang centroids into spatial groups."""
    if len(centroids) == 0:
        return []
    
    from scipy.spatial import KDTree
    tree = KDTree(centroids)
    
    visited = set()
    clusters = []
    
    for i in range(len(centroids)):
        if i in visited:
            continue
        # BFS flood fill
        cluster = []
        queue = [i]
        while queue:
            idx = queue.pop(0)
            if idx in visited:
                continue
            visited.add(idx)
            cluster.append(idx)
            neighbors = tree.query_ball_point(centroids[idx], max_gap)
            for n in neighbors:
                if n not in visited:
                    queue.append(n)
        clusters.append(cluster)
    
    return clusters


def identify_pretilt_feature(centroid_pretilt):
    """Map a pre-tilt coordinate to a named part feature."""
    x, y, z = centroid_pretilt
    
    # Check Z first - backside slit shrouds are below Z=0
    if z < 0:
        if x < 0:
            return 'Left Slit Shroud (backside)'
        return 'Right Slit Shroud (backside)'
    
    # Shaft towers (tallest features)
    if 3.5 <= x <= 5.8 and 6.0 <= y <= 13.5 and z > 5:
        return 'Left Shaft Tower'
    if 12.8 <= x <= 15.0 and 6.0 <= y <= 13.5 and z > 5:
        return 'Right Shaft Tower'
    if 1.5 <= x <= 4.5 and 6.0 <= y <= 13.5 and z > 3:
        return 'Tower Struts'
    
    # Snap clips (small, protruding)
    if z > 4.5:
        r = np.sqrt(x**2 + y**2)
        if r > 16:
            angle = np.degrees(np.arctan2(y, x))
            if angle < 0:
                angle += 360
            if 30 <= angle <= 60:
                return 'Clip 45 deg hook'
            if 120 <= angle <= 150:
                return 'Clip 135 deg hook'
            if 195 <= angle <= 230:
                return 'Clip 211 deg hook'
            if 310 <= angle <= 345:
                return 'Clip 328 deg hook'
    
    # Brackets
    if -11 <= x <= -1.5 and -8 <= y <= 8:
        return 'Left Brackets (B1-B2)'
    if 1.5 <= x <= 11 and -8 <= y <= 8:
        return 'Right Brackets (B3-B4)'
    
    # Half moon
    if 4.0 <= x <= 8.5 and -5.5 <= y <= -3.0:
        return 'Half Moon'
    
    # Ears
    if x > 18:
        return 'Right Ear'
    if x < -18:
        return 'Left Ear'
    
    # Top tab
    if y > 18:
        return 'Top Tab'
    
    # Bottom arch
    if -4.0 <= x <= 4.0 and y < -14:
        return 'Bottom Arch'
    
    # Outer wall
    if z > 0.8:
        return 'Outer Perimeter Wall'
    
    return 'Baseplate Floor'


def render_results(mesh_tilted, unsupported_indices, bridgeable_indices, output_path):
    """Render the tilted model with unsupported overhangs highlighted."""
    fig = plt.figure(figsize=(22, 8), dpi=150)
    
    verts = mesh_tilted.vertices
    faces = mesh_tilted.faces
    tris = verts[faces]
    normals = mesh_tilted.face_normals
    
    # Build face color array
    n_faces = len(faces)
    face_colors = np.full((n_faces, 4), [0.75, 0.85, 0.95, 0.15])  # light blue, very transparent
    
    # Color vertical walls (fin-attachable surfaces) in light green
    vertical_mask = np.abs(normals[:, 2]) < 0.3
    face_colors[vertical_mask] = [0.6, 0.9, 0.6, 0.12]
    
    # Color bridgeable overhangs in yellow
    for i in bridgeable_indices:
        face_colors[i] = [1.0, 1.0, 0.3, 0.5]
    
    # Color truly unsupported overhangs
    unsup_set = set(unsupported_indices)
    for i in unsupported_indices:
        ct = mesh_tilted.triangles_center[i]
        covered, _ = check_existing_fin_coverage(ct)
        if covered:
            face_colors[i] = [0.3, 0.8, 1.0, 0.7]  # Cyan = covered by existing fin
        else:
            face_colors[i] = [1.0, 0.15, 0.15, 0.9]  # RED = truly unsupported
    
    views = [
        (30, 225, 'Front-Top Isometric'),
        (-35, 225, 'Front-Bottom (overhangs visible)'),
        (-35, 45, 'Rear-Bottom'),
        (0, 180, 'Front Elevation'),
    ]
    
    for vi, (elev, azim, title) in enumerate(views):
        ax = fig.add_subplot(1, 4, vi + 1, projection='3d')
        pc = Poly3DCollection(tris, facecolors=face_colors, edgecolors='none', linewidths=0)
        ax.add_collection3d(pc)
        
        bounds = mesh_tilted.bounds
        pad = 2
        ax.set_xlim(bounds[0, 0] - pad, bounds[1, 0] + pad)
        ax.set_ylim(bounds[0, 1] - pad, bounds[1, 1] + pad)
        ax.set_zlim(bounds[0, 2] - 1, bounds[1, 2] + 1)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.set_xlabel('X', fontsize=7)
        ax.set_ylabel('Y', fontsize=7)
        ax.set_zlabel('Z', fontsize=7)
    
    plt.suptitle(
        'Support Fins Overhang Analysis -- 45 deg Orientation\n'
        'RED = unsupported overhang (needs fin)  |  CYAN = covered by existing fin  |  '
        'YELLOW = bridgeable (self-supporting)',
        fontsize=10, fontweight='bold'
    )
    plt.tight_layout(rect=[0, 0, 1.0, 0.90])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  Saved: {output_path}")
    plt.close()


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testing_dir = os.path.join(project_root, 'testing')
    
    print("=" * 72)
    print("  SUPPORT FINS OVERHANG ANALYSIS -- 45 deg PRINT ORIENTATION")
    print("  Methodology: github.com/gittrahan/support-fins (FIN-SPEC.md)")
    print("=" * 72)
    
    # Build the model
    print("\n[1/5] Building flat 3D model...")
    from build_part import build_exact_3d_model, build_45deg_supported_part_mesh
    part_flat, base_poly = build_exact_3d_model()
    
    print("[2/5] Applying 45 deg rotation (with existing fins)...")
    part_45, m_tilted_only, fins_only = build_45deg_supported_part_mesh(part_flat)
    
    # Apply 45deg rotation to flat model (without fins) for analysis
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_analysis = part_flat.copy().apply_transform(R)
    z_min = m_analysis.bounds[0, 2]
    m_analysis.apply_translation([0, 0, -z_min])
    
    print(f"\n  Model stats:")
    print(f"    Flat:   {len(part_flat.faces):,} faces | "
          f"bbox: {part_flat.bounds[1] - part_flat.bounds[0]}")
    print(f"    Tilted: {len(m_analysis.faces):,} faces | "
          f"bbox: [{m_analysis.bounds[0][0]:.1f},{m_analysis.bounds[0][1]:.1f},{m_analysis.bounds[0][2]:.1f}] "
          f"-> [{m_analysis.bounds[1][0]:.1f},{m_analysis.bounds[1][1]:.1f},{m_analysis.bounds[1][2]:.1f}]")
    print(f"    Max Z (tilted): {m_analysis.bounds[1][2]:.1f} mm")
    
    # Analyze overhangs
    print("\n[3/5] Analyzing overhangs (ray-casting for true unsupported faces)...")
    unsupported, bridgeable = find_unsupported_overhangs(m_analysis)
    
    normals = m_analysis.face_normals
    centroids = m_analysis.triangles_center
    threshold_z = -np.sin(np.radians(OVERHANG_ANGLE_DEG))
    total_overhang = np.sum((normals[:, 2] < threshold_z) & (centroids[:, 2] > BED_PAD_Z + 0.5))
    
    print(f"\n  Overhang summary:")
    print(f"    Total downward faces (>{OVERHANG_ANGLE_DEG} deg): {total_overhang:,}")
    print(f"    Bridgeable (mesh below, self-supporting):     {len(bridgeable):,}")
    print(f"    Truly unsupported (nothing below):            {len(unsupported):,}")
    
    # Check existing fin coverage
    print("\n[4/5] Evaluating existing fin coverage...")
    covered_count = 0
    uncovered_count = 0
    uncovered_indices = []
    covered_indices = []
    
    for i in unsupported:
        ct = centroids[i]
        covered, cover_type = check_existing_fin_coverage(ct)
        if covered:
            covered_count += 1
            covered_indices.append(i)
        else:
            uncovered_count += 1
            uncovered_indices.append(i)
    
    print(f"    Covered by existing fins/braces/pad: {covered_count:,}")
    print(f"    NOT covered (gaps in support):       {uncovered_count:,}")
    
    # Cluster and identify uncovered regions
    if uncovered_indices:
        uncov_centroids = centroids[uncovered_indices]
        clusters = cluster_overhangs(uncov_centroids, max_gap=3.0)
        
        # Map back to pre-tilt coords for feature identification
        R_inv = trimesh.transformations.rotation_matrix(np.radians(-45.0), [1, 0, 0])[:3, :3]
        
        print(f"\n{'='*72}")
        print(f"  UNSUPPORTED OVERHANG REGIONS ({len(clusters)} clusters)")
        print(f"{'='*72}")
        
        significant_regions = []
        
        for ci, cluster in enumerate(sorted(clusters, key=len, reverse=True)):
            cluster_centroids = uncov_centroids[cluster]
            
            # Compute total area
            total_area = 0
            for idx in cluster:
                orig_idx = uncovered_indices[idx]
                tri = m_analysis.triangles[orig_idx]
                total_area += 0.5 * np.linalg.norm(np.cross(tri[1]-tri[0], tri[2]-tri[0]))
            
            if total_area < MIN_OVERHANG_AREA_MM2:
                continue
            
            # Feature identification via pre-tilt coordinates
            center = cluster_centroids.mean(axis=0)
            center_shifted = center.copy()
            center_shifted[2] += z_min  # undo Z shift
            center_pretilt = R_inv @ center_shifted
            feature = identify_pretilt_feature(center_pretilt)
            
            # Max overhang angle in cluster
            max_nz = min(normals[uncovered_indices[idx], 2] for idx in cluster)
            max_angle = np.degrees(np.arccos(np.clip(-max_nz, -1, 1)))
            
            significant_regions.append({
                'feature': feature,
                'n_faces': len(cluster),
                'area_mm2': total_area,
                'max_angle': max_angle,
                'center_tilted': center,
                'center_pretilt': center_pretilt,
                'bbox_min': cluster_centroids.min(axis=0),
                'bbox_max': cluster_centroids.max(axis=0),
                'z_range': (cluster_centroids[:, 2].min(), cluster_centroids[:, 2].max()),
            })
        
        for ri, reg in enumerate(significant_regions):
            status = "[!] " if reg['area_mm2'] > 5 else "[i] "
            if reg['area_mm2'] > 20:
                status = "[X]"
            
            print(f"\n  {status} Region {ri+1}: {reg['feature']}")
            print(f"      Faces: {reg['n_faces']:,}  |  Area: {reg['area_mm2']:.1f} mm^2  |  "
                  f"Max overhang: {reg['max_angle']:.0f} deg")
            print(f"      Tilted position (center): X={reg['center_tilted'][0]:.1f}, "
                  f"Y={reg['center_tilted'][1]:.1f}, Z={reg['center_tilted'][2]:.1f}")
            print(f"      Z range: {reg['z_range'][0]:.1f} -> {reg['z_range'][1]:.1f} mm")
            
            # Recommendation
            if reg['area_mm2'] > 20:
                print(f"      -> RECOMMENDATION: Add fin wall here. Best anchor: nearby vertical face.")
            elif reg['area_mm2'] > 5:
                print(f"      -> RECOMMENDATION: Consider additional fin or extend existing fin Y-range.")
            else:
                print(f"      -> Small area, likely printable with short bridges. Monitor during print.")
    else:
        significant_regions = []
        print(f"\n  [OK] All overhangs are covered by existing fins!")
    
    # Generate visualization
    print(f"\n[5/5] Generating diagnostic renders...")
    render_path = os.path.join(testing_dir, 'overhang_analysis_45deg.png')
    render_results(m_analysis, unsupported, bridgeable, render_path)
    
    # Final verdict
    total_uncovered_area = sum(r['area_mm2'] for r in significant_regions)
    critical_regions = [r for r in significant_regions if r['area_mm2'] > 5]
    
    print(f"\n{'='*72}")
    print(f"  VERDICT")
    print(f"{'='*72}")
    print(f"  Total uncovered overhang area: {total_uncovered_area:.1f} mm^2")
    print(f"  Significant gap regions (>5 mm^2): {len(critical_regions)}")
    
    if total_uncovered_area < 3:
        print(f"\n  [OK] PASS -- Existing fin system provides adequate support.")
        print(f"  The 45 deg orientation with current fins is ready to print.")
    elif total_uncovered_area < 15:
        print(f"\n  [!]  MARGINAL -- Small gaps exist but may bridge successfully.")
        print(f"  Recommended: extend fin coverage or add spot fins for reliability.")
    else:
        print(f"\n  [X] GAPS FOUND -- Additional fins needed before printing.")
        print(f"  {len(critical_regions)} region(s) require fin walls or geometry changes.")
    
    return significant_regions, m_analysis, part_flat


if __name__ == '__main__':
    regions, m_tilted, m_flat = main()
