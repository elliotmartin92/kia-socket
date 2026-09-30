# Testing, Verification & Diagnostic Suite

This directory contains the verification tests, dimensional checks, geometric simulations, and diagnostic visualization scripts developed over the project lifecycle.

---

## 1. Primary Production Verification Suite
Run these canonical tests to validate deliverables before release or after modifying CAD code:

| Verification Script | Description |
| :--- | :--- |
| `py -3 testing/verify_exported_deliverables.py` | Validates all exported STL deliverables (`part.stl`, `shaft_rocker.stl`, `cooling_tower.stl`, `complete_assembly.stl`) for manifold integrity, body counts, and Z-bounds. |
| `py -3 testing/verify_shaft_support_stick.py` | Verifies dedicated breakaway stick support with Y-fork head under floating lever shaft cylinder (X in [7.90, 11.10], 0.28mm release gap). |
| `py -3 testing/verify_shaft_supports_production.py` | Verifies shaft rocker print support frame: bed contact ($Z = 0.00\text{ mm}$), pin release micro-gap ($0.12\text{ mm}$), and stick geometry. |
| `py -3 testing/verify_slit_alignment.py` | Verifies slit detent key alignment ($X = -7.853, +8.453\text{ mm}$) and fit clearances. |
| `py -3 testing/verify_185mm_clips.py` | Validates the 4 snap clips for $1.85\text{ mm}$ hook depth, $0.20\text{ mm}$ top-down crown arc ease, and $0.53\text{ mm}$ blunt land. |
| `py -3 testing/verify_all_new_fixes.py` | Comprehensive regression suite checking all critical geometric updates against baseline specifications. |

---

## 2. Functional Domains & Script Prefixes

To keep the suite organized, scripts adhere to the following prefix conventions:

| Prefix | Count | Role & Purpose |
| :--- | :---: | :--- |
| **`verify_*.py`** | ~35 | **Production Verifications**: Formal pass/fail assertion checks against geometric and kinematic specs. |
| **`analyze_*.py`** | ~35 | **Kinematic & Mechanical Analyses**: Physics/kinematics calculations (blade travel, rocker moment, insertion force). |
| **`inspect_*.py`** | ~100 | **Geometric Inspections**: Dimension extractions, slice profile checks, clearance gap inspections. |
| **`simulate_*.py`**| ~15 | **Slicer & Interaction Simulations**: Layer slicing simulations, blade insertion kinematics, tolerance stackups. |
| **`render_*.py`**  | ~20 | **3D Diagnostic Renders**: Matplotlib/trimesh isometric and multi-view diagnostic renderings. |
| **`plot_*.py`**    | ~25 | **2D Technical Plots**: Cross-sections, deflection curves, contact profiles. |
| **`check_*.py`**   | ~25 | **Targeted Collision & Clearance Checks**: Checking clearances to OEM brass contacts and housing walls. |
| **`test_*.py`**    | ~150 | **Feature Development & Prototypes**: Iterative exploratory prototypes for specific features. |

---

## 3. Key Technical Datums in Tests
- **Scale**: `SCALE = 0.349787 mm/px`
- **Axle Center**: $Y = 9.279\text{ mm}, Z = 12.590\text{ mm}$
- **Plunger Travel**: $Z \le -6.50\text{ mm}$, $Y \in [8.57, 13.75]\text{ mm}$
- **Switch Trip Point**: $Y = 12.40\text{ mm}$
- **Brass Seating Elevation**: $Z = 2.15\text{ mm}$ ($1.15\text{ mm}$ above floor)

---

## 4. Temporary Artifacts & Cleanliness
- Diagnostic preview images (`*.png`) and test meshes (`*_test.stl`) produced by scripts in this directory are git-ignored or cataloged as temporary inspection outputs.
- Test scripts import from root using `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`.
