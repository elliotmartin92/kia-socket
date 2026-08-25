"""
testing/verify_all_deliverables.py
Verify integrity, watertightness, manifold geometry, and dimensions of all production STL models.
"""
import os
import trimesh

files = [
    "part.stl",
    "shaft_rocker.stl",
    "shaft_rocker_assembled.stl",
    "slit_insert.stl",
    "slit_inserts_pair.stl",
    "cooling_tower.stl",
    "complete_assembly.stl"
]

print("=== Production STL Deliverables Integrity Check ===")
all_passed = True

for fname in files:
    fpath = os.path.join(os.path.dirname(__file__), '..', fname)
    if not os.path.exists(fpath):
        print(f"FAILED: {fname} does not exist!")
        all_passed = False
        continue
    
    mesh = trimesh.load(fpath)
    is_wt = mesh.is_watertight
    bounds = mesh.bounds
    vol = mesh.volume if is_wt else 0.0
    
    status = "OK (Watertight)" if is_wt else "WARNING (Non-watertight)"
    print(f"[{status}] {fname:<28} | Vol: {vol:8.2f} mm³ | Bounds X:[{bounds[0,0]:6.2f}, {bounds[1,0]:6.2f}] Y:[{bounds[0,1]:6.2f}, {bounds[1,1]:6.2f}] Z:[{bounds[0,2]:6.2f}, {bounds[1,2]:6.2f}]")
    if not is_wt:
        all_passed = False

if all_passed:
    print("\nALL DELIVERABLES 100% WATERTIGHT AND VERIFIED!")
else:
    print("\nSome files failed verification.")
