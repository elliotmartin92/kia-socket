# Automotive 120V AC Outlet Sub-Housing — Architecture & Engineering Quick Reference

> High-density architectural reference for developers and autonomous agents.

---

## 1. System Function & Kinematic Summary
- **Intermediate Sub-Housing Baseplate**: Retains OEM stamped brass conductive contacts and mounts the safety interlock rocker.
- **Interlock Mechanism**: Right plug blade engages the angled belly cam ($105^\circ$ bellcrank) rotating the shaft axle ($Y = 9.279\text{ mm}, Z = 12.590\text{ mm}$) to drive the extended plunger downwards ($Z \le -6.50\text{ mm}$) through the baseplate floor through-hole ($Y \in [8.57, 13.75]\text{ mm}$), actuating a PCB momentary tactile switch at $Y = 12.40\text{ mm}$.
- **Print Optimization**: Main part is tilted 45° with baked-in support fins; shaft rocker has built-in sacrificial breakaway frame ($Z \in [0.00, 0.58]\text{ mm}$, release gap $0.12\text{ mm}$) for 1-click support-free printing.

---

## 2. Global Coordinates & Critical Datums
- **Scale Factor**: Calibrated from SVG pixel coordinates:
  $$\text{SCALE} = 0.349787\text{ mm/pixel}, \quad X_0 = 128.65\text{ px}, \quad Y_0 = 128.65\text{ px}$$
- **Axle Datum**: $Y_{\text{axle}} = 9.279\text{ mm}, \quad Z_{\text{axle}} = 12.590\text{ mm}$
- **Shaft Sockets**: $\varnothing 3.00\text{ mm}$ cradle, $2.60\text{ mm}$ throat ($240^\circ$ wrap), fits $\varnothing 2.80\text{ mm}$ shaft pin.
- **Towers**: Left: $X \in [3.90, 5.40]\text{ mm}$, Right: $X \in [13.10, 14.60]\text{ mm}$ ($7.70\text{ mm}$ clear gap).
- **Z-Elevation Datum (Main Baseplate)**:
  - $Z = 0.00\text{ mm}$: Flat build datum.
  - $Z \in [0.00, 1.00]\text{ mm}$: Floor plate ($1.00\text{ mm}$).
  - $Z \in [1.00, 1.50]\text{ mm}$: Stiffener grid ribs ($0.50\text{ mm}$).
  - $Z \in [1.00, 2.15]\text{ mm}$: Brass seating ribs ($1.15\text{ mm}$ elevation).
  - $Z \in [1.00, 5.60]\text{ mm}$: Guide brackets ($4.60\text{ mm}$ tall).
  - $Z \in [1.00, 6.77]\text{ mm}$: Outer perimeter wall & snap clips ($6.77\text{ mm}$ tall).
  - $Z \in [1.00, 10.50]\text{ mm}$: Center curved D-wall ($10.50\text{ mm}$ tall).
  - $Z \in [1.00, 14.09]\text{ mm}$: Support towers ($14.09\text{ mm}$ tall).
- **Perimeter Clips (4x)**: $45^\circ, 135^\circ, 211.3^\circ, 327.5^\circ$. Hook shelf at $Z = 4.97\text{ mm}$, $1.85\text{ mm}$ center depth with $0.20\text{ mm}$ crown ease, $0.53\text{ mm}$ blunt land, $2.07\text{ mm}$ solid hoop ring.
- **Slit Inserts**: Channels $1.20 \times 3.40\text{ mm}$, indexing key $1.80 \times 4.00\text{ mm}$ with $45^\circ$ chamfer.

---

## 3. Directory Layout & Organization

```
kind-bardeen/
├── build_part.py                   # Master baseplate CAD generator
├── build_shaft.py                  # Parametric shaft/rocker CAD generator
├── generate_labeled_preview.py     # 3-panel annotated blueprint generator
├── part.svg                        # Master 2D source geometry (SVG vector paths)
├── part.stl / .obj / .scad         # Production baseplate deliverables (45° supported)
├── shaft_rocker.stl / .obj / .scad # Production shaft/rocker (print-ready with breakaway frame)
├── shaft_rocker_assembled.stl/.obj # Shaft seated in assembly coordinates
├── shaft_rocker_clean.stl / .obj   # Bare shaft without breakaway frame
├── slit_insert.stl / .obj          # Separate slit insert deliverable
├── slit_inserts_pair.stl           # Pre-arranged pair of slit inserts
├── cooling_tower.stl / .obj        # Sacrificial cooling column for tower tips
├── complete_assembly.stl / .obj    # Complete 1-click build plate layout
├── part_preview.png                # 3-view primary render preview
├── labeled_part_preview.png        # Production blueprint diagram
├── build_clamp.py                  # Forwarding shim for accessories/tower_clamp
├── accessories/
│   └── tower_clamp/                # Optional anti-spreading tower clamp accessory
├── slicer/                         # 3MF print project files
├── testing/                        # Unit tests, geometric verifications & diagnostic plots
│   └── README.md                   # Complete test catalog & execution guide
├── README.md                       # Comprehensive engineering documentation
├── ARCHITECTURE.md                 # This architecture reference
├── AGENTS.md                       # AI assistant operational rules
└── .gitignore                      # Git exclusion rules
```

---

## 4. Pipeline Execution Commands

```bash
# Generate all main baseplate models & assemblies
py -3 build_part.py

# Generate shaft/rocker mechanism (with support frame & bare variant)
py -3 build_shaft.py

# Generate optional tower clamp accessories
py -3 accessories/tower_clamp/build_clamp.py

# Generate high-resolution dimensioned feature blueprints
py -3 generate_labeled_preview.py

# Run primary production verification suite
py -3 testing/verify_exported_deliverables.py
py -3 testing/verify_shaft_supports_production.py
py -3 testing/verify_slit_alignment.py
```
