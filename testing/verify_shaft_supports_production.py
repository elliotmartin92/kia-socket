"""
testing/verify_shaft_supports_production.py
Verify all production files exported with the new built-in shaft supports.
"""

import os, sys
import trimesh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

files_to_check = [
    ('shaft_rocker.stl', True),
    ('shaft_rocker.obj', True),
    ('shaft_rocker_clean.stl', True),
    ('shaft_rocker_assembled.stl', True),
    ('complete_assembly.stl', False),
    ('part.stl', False)
]

print("=" * 70)
print("PRODUCTION ASSETS VERIFICATION")
print("=" * 70)

all_passed = True
for fname, require_wt in files_to_check:
    if not os.path.exists(fname):
        print(f"FAIL: {fname} does not exist!")
        all_passed = False
        continue
    mesh = trimesh.load(fname)
    is_wt = mesh.is_watertight
    vol = mesh.volume if is_wt else 0.0
    b = mesh.bounds
    z_span = [b[0, 2], b[1, 2]]
    passed = is_wt if require_wt else (mesh.is_empty == False)
    status = "PASS" if passed else "FAIL"
    print(f"{fname:<26} | WT: {str(is_wt):<5} | Vol: {vol:8.2f} mm³ | Z: [{z_span[0]:.2f}, {z_span[1]:.2f}] | {status}")
    if not passed:
        all_passed = False

print("=" * 70)
if all_passed:
    print("ALL PRODUCTION ASSETS VERIFIED AND READY FOR PRINTING!")
else:
    print("SOME CHECKS FAILED!")
