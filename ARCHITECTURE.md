# Automotive 120V AC Outlet Sub-Housing — Architecture & Engineering Quick Reference

> High-density architectural reference for developers and autonomous agents.

---

## 1. System Function & Kinematic Summary
- **Intermediate Sub-Housing Baseplate**: Retains OEM stamped brass conductive contacts and mounts the safety interlock rocker.
- **Interlock Mechanism**: Right plug blade engages the angled belly cam ($105^\circ$ bellcrank) rotating the shaft axle ($Y = 9.279\text{ mm}, Z = 12.590\text{ mm}$) to drive the extended plunger downwards ($Z \le -6.50\text{ mm}$) through the baseplate floor through-hole ($Y \in [8.57, 13.75]\text{ mm}$), actuating a PCB momentary tactile switch at $Y = 12.40\text{ mm}$.
- **Print Optimization**: Main part is tilted 45° with baked-in breakaway support fins (0.24mm release gap, 4.5mm pitch; inner fin pair with left fin at $X = -8.00\text{ mm}$ and right fin shifted to $X = +6.80\text{ mm}$ to ensure $+1.28\text{ mm}$ clearance from the PIP lever plunger blade), monolithic $0.60\text{ mm}$ bed pad with an expanded $26.0 \times 8.5\text{ mm}$ relief window completely clearing the insert shroud tips and bottom baseplate corner ($0.00\text{ mm}^3$ pad fusion, clean separation), hardcoded 45° stem-anchored breakaway twin struts supporting the bottom clips (0.28mm release gap under shelf, enlarged 1.10mm width, 0.60mm root neck), twin breakaway support struts under the back side of each integrated slit insert (0.28mm parallel release gap, enlarged 0.90mm width), dedicated breakaway plunger support strut protruding from base pad with twin-tine fork (0.28mm release gap), dedicated breakaway cantilever (cam tab) support strut (0.28mm release gap, 0.70x0.70mm easy-snap floor neck), and a dedicated breakaway lever shaft (hub barrel) support strut with a Y-fork head at the end (0.28mm release gap, 0.70x0.70mm floor neck) supporting the captive Print-in-Place (PIP) safety lever inside the enclosed bridged towers.
 
 ---
 
 ## 2. Global Coordinates & Critical Datums
 - **Scale Factor**: Calibrated from SVG pixel coordinates:
   $$\text{SCALE} = 0.349787\text{ mm/pixel}, \quad X_0 = 128.65\text{ px}, \quad Y_0 = 128.65\text{ px}$$
 - **Axle Datum**: $Y_{\text{axle}} = 9.279\text{ mm}, \quad Z_{\text{axle}} = 12.590\text{ mm}$
 - **Shaft Sockets**: Fully enclosed $360^\circ$ teardrop journal ($\varnothing 3.50\text{ mm}$), $0.35\text{ mm}$ radial clearance around $\varnothing 2.80\text{ mm}$ shaft pin for smooth Print-in-Place pivot.
 - **Towers & Rear Bridge**: Left: $X \in [3.90, 5.40]\text{ mm}$, Right: $X \in [13.10, 14.60]\text{ mm}$ ($7.70\text{ mm}$ clear gap, $0.40\text{ mm}$ lateral clearance per side to $6.90\text{ mm}$ wide $\varnothing 4.20\text{ mm}$ hub barrel). Features a thick rounded arch crown ($R_y = 2.85\text{ mm}, R_z = 3.00\text{ mm}$, apex at $Z = 15.59\text{ mm}$, providing $1.25\text{ mm}$ solid plastic roof over the teardrop bore). Towers are united across the rear by a monolithic cross-tie bridge ($X \in [5.40, 13.10]\text{ mm}$, $Y \in [11.75, 12.85]\text{ mm}$, $Z \in [12.60, 15.00]\text{ mm}$, $2.40\text{ mm}$ tall, $0.37\text{ mm}$ clearance behind hub) permanently preventing tower spreading.
 - **Z-Elevation Datum (Main Baseplate)**:
   - $Z = 0.00\text{ mm}$: Flat build datum.
   - $Z \in [0.00, 1.00]\text{ mm}$: Floor plate ($1.00\text{ mm}$).
   - $Z \in [1.00, 1.50]\text{ mm}$: Stiffener grid ribs ($0.50\text{ mm}$).
   - $Z \in [1.00, 2.15]\text{ mm}$: Brass seating ribs ($1.15\text{ mm}$ elevation).
   - $Z \in [1.00, 5.60]\text{ mm}$: Guide brackets ($4.60\text{ mm}$ tall).
   - $Z \in [1.00, 6.77]\text{ mm}$: Outer perimeter wall & snap clips ($6.77\text{ mm}$ tall).
   - $Z \in [1.00, 10.50]\text{ mm}$: Center curved D-wall ($9.50\text{ mm}$ tall above floor, base extended to $Y = -5.05\text{ mm}$ as brass insert backstop).
   - $Z \in [1.00, 15.59]\text{ mm}$: Support towers & monolithic cross-tie bridge ($14.59\text{ mm}$ tall above floor, apex at $Z = 15.59\text{ mm}$, solid rounded arch crown).
 - **Perimeter Clips (4x)**: $45^\circ, 135^\circ, 211.3^\circ, 327.5^\circ$. Hook shelf at $Z = 4.72\text{ mm}$ ($+0.25\text{ mm}$ under shelf for positive switch engagement), $1.75\text{ mm}$ center depth ($-0.10\text{ mm}$ trimmed face for lower insertion force) with $0.20\text{ mm}$ crown ease, $0.53\text{ mm}$ blunt land, $2.07\text{ mm}$ solid hoop ring. Bottom clips ($211.3^\circ, 327.5^\circ$) equipped with hardcoded 45° breakaway support struts from stem (enlarged 1.10mm width, 0.60mm root neck, 0.55mm shelf land) with an expanded $0.28\text{ mm}$ shelf release gap.
 - **Integrated Slit Shrouds / Inserts**: In-place backside chimneys ($Z \in [-2.47, 0.00]\text{ mm}$) at $X = -7.853\text{ mm}$ and $+8.453\text{ mm}$, channels $1.10 \times 3.00\text{ mm}$. Supported in 45° print orientation by twin 0.90mm vertical breakaway struts (+50% thicker) under the 32.5° overhanging back wall with a calibrated $0.28\text{ mm}$ release gap and a 1.20mm open center window clearing the slit holes.
 - **Captive PIP Safety Lever Supports**:
   - **Plunger Support (Protruding from Base Pad)**: Central column ($1.80 \times 1.80\text{ mm}$) rising directly from the bed pad ($Z' = 0.60\text{ mm}$) through the baseplate through-hole, branching at $Z' = 13.00\text{ mm}$ into a twin-tine fork ($X \in [8.484, 9.284]$ and $[11.284, 12.084]$) supporting both lateral edges of the $3.60\text{ mm}$ plunger blade with an open $2.00\text{ mm}$ central window and a $0.28\text{ mm}$ release gap.
   - **Cantilever (Cam Tab) Support**: Central column rising from the $45^\circ$ baseplate floor ($Z' = 12.19\text{ mm}$) with a $0.70 \times 0.70\text{ mm}$ easy-snap twist-off neck, branching into a twin-tine fork ($X \in [5.65, 6.15]$ and $[7.05, 7.55]$) supporting both lateral edges of the $1.90\text{ mm}$ cam tab with an open $0.90\text{ mm}$ central window and a $0.28\text{ mm}$ release gap.
   - **Lever Shaft (Hub Barrel) Support**: Central column rising from the $45^\circ$ baseplate seating rib/floor ($Z' = 13.61\text{ mm}$) with a $0.70 \times 0.70\text{ mm}$ easy-snap twist-off neck, branching at $Z' = 21.00\text{ mm}$ into a Y-fork head ($X \in [7.85, 9.35]\text{ mm}$, center $X = 8.60\text{ mm}$, $1.45\text{ mm}$ clearance to Bracket 4 wall) with twin $0.45\text{ mm}$ tines and a central V-notch supporting the floating cylindrical hub barrel of the captive lever shaft with a $0.28\text{ mm}$ release gap.
 - **Backplate Support Fins (Under 45° Incline)**: 5 vertical fins rising from the $0.60\text{ mm}$ bed pad: Outer pair ($X = \pm 14.00\text{ mm}$, $Y \in [-3.00, 10.00]\text{ mm}$), Center fin ($X = 0.00\text{ mm}$, extended to $Y \in [-3.00, 14.00]\text{ mm}$ for full upper backplate safety support), and Inner pair (Left fin at $X = -8.00\text{ mm}$, Right fin shifted to $X = +6.80\text{ mm}$ to clear the through-hole left boundary at $X = 7.61\text{ mm}$ and provide $+1.28\text{ mm}$ open air gap to the PIP lever plunger blade, $Y \in [-5.80, 14.00]\text{ mm}$). Equipped with $0.24\text{ mm}$ release gap and $4.50\text{ mm}$ pitch breakaway tines.

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
