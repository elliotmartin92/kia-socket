"""
testing/model_45deg_support_fins.py
Constructs the 45-degree tilted main part with baked-in breakaway Support Fins,
adhering to the Slant3D / Support Fins specification (https://github.com/gittrahan/support-fins):
- 45° rotation about X-axis (tilts baseplate so layer lines cross half moon at 45°)
- Solid 1.0mm bed adhesion pad on build plate
- Dual vertical fin walls beneath the sloped backplate with 0.20mm release gap
- Periodic horizontal breakaway tines (0.24mm H x 0.60mm W) connecting fins to part
- Lateral sway brace fins stabilizing side ears
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import trimesh
from shapely.geometry import Polygon, box

import build_part as bp

def create_45deg_tilted_part(base_mesh):
    """Rotates the main part 45° about X and sets lowest Z to 0.00mm."""
    R = trimesh.transformations.rotation_matrix(np.radians(45.0), [1, 0, 0])
    m_tilted = base_mesh.copy().apply_transform(R)
    z_min = m_tilted.bounds[0, 2]
    m_tilted.apply_translation([0, 0, -z_min])
    return m_tilted, z_min

def build_support_fins(tilted_mesh, z_shift):
    """Builds baked-in breakaway support fins according to FIN-SPEC.md:
    1. Bed Adhesion Pad: 1.0mm thick disc/plate on Z = [0, 0.60]mm.
    2. Vertical Fin Walls: Thin vertical ribs (0.80mm thick) parallel to Y_build.
    3. Horizontal Breakaway Tines: 0.24mm x 0.60mm horizontal bridges fusing into the part.
    4. 0.20mm Standoff Clearance between fin bodies and part surface.
    """
    fin_components = []
    
    # 1. Bed Adhesion Pad (44mm wide x 34mm long x 0.60mm thick on bed Z in [0, 0.60]mm)
    pad_mesh = trimesh.creation.box([44.0, 36.0, 0.60])
    pad_mesh.apply_translation([0, -5.0, 0.30])
    fin_components.append(pad_mesh)
    
    # 2. Main Support Fins under the 45° inclined backplate
    # The original backplate bottom face was at Z_orig = 0.
    # In tilted coordinates: Z_build = Y_build - (lowest Y_build of backplate)
    # Since rotation was +45° around X:
    # y_build = y_orig * cos(45°) - z_orig * sin(45°) = y_orig * sqrt(2)/2
    # z_build_raw = y_orig * sin(45°) + z_orig * cos(45°) = y_orig * sqrt(2)/2
    # So for z_orig = 0: z_build_raw = y_build!
    # And after subtracting z_min:
    # Z_underside(Y_build) = Y_build - z_min!
    
    fin_thick_x = 0.80 # 2 nozzle perimeters
    standoff = 0.20    # 0.20mm gap as per Slant3D spec
    z_bed = 0.60
    
    for x_pos in [-8.0, 8.0]:
        y_start = -11.0
        y_end = +8.0
        
        # At y_start:
        z_start = y_start - z_shift - standoff
        # At y_end:
        z_end = y_end - z_shift - standoff
        
        # Build 2D polygon of fin wall in YZ
        pts_yz = [
            (y_start, z_bed),
            (y_start, z_start),
            (y_end, z_end),
            (y_end, z_bed)
        ]
        poly_yz = Polygon(pts_yz)
        if poly_yz.is_valid and poly_yz.area > 0.1:
            m_fin_raw = trimesh.creation.extrude_polygon(poly_yz, height=fin_thick_x)
            v = m_fin_raw.vertices.copy()
            v_reorient = np.column_stack([v[:, 2] + x_pos - fin_thick_x/2.0, v[:, 0], v[:, 1]])
            m_fin = trimesh.Trimesh(vertices=v_reorient, faces=m_fin_raw.faces.copy(), process=True)
            fin_components.append(m_fin)
            
            # 3. Horizontal Breakaway Tines connecting fin to part underside
            # Spaced every ~3.5mm along Y
            y_tine_stations = np.arange(y_start + 2.0, y_end, 3.5)
            for yt in y_tine_stations:
                zt_underside = yt - z_shift
                # Tine bridges the standoff gap (0.20mm) and penetrates 0.30mm into part
                tine = trimesh.creation.box([fin_thick_x, 0.60, standoff + 0.35])
                tine.apply_translation([x_pos, yt, zt_underside - standoff/2.0 + 0.10])
                fin_components.append(tine)
                
    # 4. Sway Braces for Lateral Stability (at X = -18.5 and X = +18.5)
    for x_side in [-19.0, 19.0]:
        sway_wall = trimesh.creation.box([1.00, 18.0, 10.0])
        sway_wall.apply_translation([x_side, -4.0, 5.0])
        fin_components.append(sway_wall)
        
        # Tines tying sway brace to perimeter rim
        for z_tine in [5.0, 8.5]:
            tine_side = trimesh.creation.box([1.20, 0.80, 0.30])
            tine_side.apply_translation([x_side, -4.0, z_tine])
            fin_components.append(tine_side)

    all_fins = trimesh.util.concatenate(fin_components)
    return all_fins

def run_test():
    print("Building base part...")
    base_part, _ = bp.build_exact_3d_model()
    
    print("Rotating 45° about X...")
    part_45, z_shift = create_45deg_tilted_part(base_part)
    print(f"45° Part Bounds: X [{part_45.bounds[0,0]:.2f}, {part_45.bounds[1,0]:.2f}], Y [{part_45.bounds[0,1]:.2f}, {part_45.bounds[1,1]:.2f}], Z [{part_45.bounds[0,2]:.2f}, {part_45.bounds[1,2]:.2f}]")
    
    print("Generating baked-in Support Fins according to FIN-SPEC.md...")
    fins_mesh = build_support_fins(part_45, z_shift)
    print(f"Fins Mesh Bounds: X [{fins_mesh.bounds[0,0]:.2f}, {fins_mesh.bounds[1,0]:.2f}], Y [{fins_mesh.bounds[0,1]:.2f}, {fins_mesh.bounds[1,1]:.2f}], Z [{fins_mesh.bounds[0,2]:.2f}, {fins_mesh.bounds[1,2]:.2f}]")
    
    print("Combining into single support-free printable mesh...")
    combined = trimesh.util.concatenate([part_45, fins_mesh])
    print(f"Combined Mesh Watertight: {combined.is_watertight}")
    print(f"Combined Total Volume: {combined.volume:.2f} mm3")
    
    out_stl = "testing/part_45deg_supported_test.stl"
    combined.export(out_stl)
    print(f"Exported test mesh to {out_stl}")

if __name__ == '__main__':
    run_test()
