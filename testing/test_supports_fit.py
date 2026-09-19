import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import build_part

base_poly, _, _ = build_part.get_exact_base_polygon()
build_part.CLIP_HOOK_DEPTH = 2.39
supp_mesh = build_part.build_clip_supports_mesh(base_poly)
print(f"Supports watertight: {supp_mesh.is_watertight}")
print(f"Supports volume: {supp_mesh.volume:.2f} mm³")
print(f"Supports bounds: {supp_mesh.bounds}")
assert supp_mesh.is_watertight
print("Supports verification passed!")
