# Automotive 120V AC Outlet Sub-Housing — Architecture & Engineering Quick Reference

> High-density architectural reference for developers and autonomous agents.

---

## 1. System Function & Kinematic Summary
- **Intermediate Sub-Housing Baseplate**: Retains OEM stamped brass conductive contacts and mounts the safety interlock rocker.
- **Interlock Mechanism**: Right plug blade engages the elevated direct belly cam ($105^\circ$ bellcrank, calibrated blunt rounded bullnose apex at $Y = 2.58\text{ mm}, Z = 7.80\text{ mm}$, elevated knee at $Z = 10.80\text{ mm}$) rotating the shaft axle ($Y = 9.279\text{ mm}, Z = 12.590\text{ mm}$) to drive the extended plunger downwards ($Z \le -7.00\text{ mm}$, $+0.50\text{ mm}$ reach extension) through the baseplate floor through-hole ($Y \in [8.57, 13.75]\text{ mm}$), decisively actuating a PCB momentary tactile switch at $Y = 12.40\text{ mm}$ with small rotation angle ($\theta_{\text{trip}} = 5.65^\circ$). The throat opening between the Half Moon front guide wall ($Y = -3.25\text{ mm}$) and the rotated cam maintains guaranteed $\ge 6.35\text{ mm}$ clearance (up to $6.42\text{ mm}$ at bottom-out), ensuring full plug blade insertion without binding, wedging, or relying on excessive theoretical rotation. The cam arm features a thickened beam ($2.50\text{ mm}$ to $3.82\text{ mm}$, over $4\times$ thicker than razor wedge) and a 100% self-supporting 45° print contour with generous tangential stress-relief fillets returning cleanly to the $\varnothing 4.20\text{ mm}$ hub barrel without hanging material or artificial mid-air overhangs.
- **Print Optimization**: Main part is tilted 45° with baked-in breakaway support fins (0.24mm release gap, 4.5mm pitch; inner fin pair with left fin at $X = -8.00\text{ mm}$ and right fin shifted to $X = +6.80\text{ mm}$ to ensure $+1.28\text{ mm}$ clearance from the PIP lever plunger blade), monolithic $0.60\text{ mm}$ bed pad ($48.0 \times 33.0\text{ mm}$) with targeted slit hole relief apertures, hardcoded 45° stem-anchored breakaway twin struts supporting the bottom clips (0.28mm release gap under shelf, enlarged 1.10mm width, 0.60mm root neck), breakaway support struts under the back side of each integrated slit insert (0.28mm release gap), dedicated breakaway plunger support strut rising from base pad (0.28mm release gap), dedicated breakaway cantilever (cam tab) support strut (0.28mm release gap), and a dedicated breakaway lever shaft support strut ($0.70 \times 0.85\text{ mm}$ trunk, $0.68\text{ mm}$ wide head with twin $0.26\text{ mm}$ lands and a calibrated $0.48\text{ mm}$ release gap) supporting the floating cylindrical hub barrel, ensuring clean, sag-free printing in PC-FR.

---

## 2. Global Coordinates & Critical Datums
- **Scale Factor**: Calibrated from SVG pixel coordinates:
  $$\text{SCALE} = 0.349787\text{ mm/pixel}, \quad X_0 = 128.65\text{ px}, \quad Y_0 = 128.65\text{ px}$$
- **Axle Datum**: $Y_{\text{axle}} = 9.279\text{ mm}, \quad Z_{\text{axle}} = 12.590\text{ mm}$
- **Shaft Sockets**: Fully enclosed $360^\circ$ teardrop journal ($\varnothing 3.50\text{ mm}$), $0.35\text{ mm}$ radial clearance around $\varnothing 2.80\text{ mm}$ shaft pin for smooth Print-in-Place pivot.
- **Towers & Rear Bridge**: Left: $X \in [3.90, 5.40]\text{ mm}$, Right: $X \in [13.10, 14.60]\text{ mm}$ ($7.70\text{ mm}$ clear gap, $0.225\text{ mm}$ lateral clearance per side to $7.25\text{ mm}$ wide $\varnothing 4.20\text{ mm}$ hub barrel; $0.45\text{ mm}$ total axial float). Features a thick rounded arch crown ($R_y = 2.85\text{ mm}, R_z = 3.00\text{ mm}$, apex at $Z = 15.59\text{ mm}$, providing $1.25\text{ mm}$ solid plastic roof over the teardrop bore). Towers are united across the rear by a monolithic cross-tie bridge ($X \in [5.40, 13.10]\text{ mm}$, $Y \in [11.75, 12.85]\text{ mm}$, $Z \in [12.60, 15.00]\text{ mm}$, $2.40\text{ mm}$ tall, $0.37\text{ mm}$ clearance behind hub) permanently preventing tower spreading.
- **Z-Elevation Datum (Main Baseplate)**:
  - $Z = 0.00\text{ mm}$: Flat build datum.
  - $Z \in [0.00, 1.00]\text{ mm}$: Floor plate ($1.00\text{ mm}$).
  - $Z \in [1.00, 1.50]\text{ mm}$: Stiffener grid ribs ($0.50\text{ mm}$).
  - $Z \in [1.00, 2.15]\text{ mm}$: Brass seating ribs ($1.15\text{ mm}$ elevation).
  - $Z \in [1.00, 5.60]\text{ mm}$: Guide brackets ($4.60\text{ mm}$ tall).
  - $Z \in [1.00, 6.77]\text{ mm}$: Outer perimeter wall & snap clips ($6.77\text{ mm}$ tall).
  - $Z \in [1.00, 10.50]\text{ mm}$: Center curved D-wall ($9.50\text{ mm}$ tall above floor, base extended to $Y = -5.05\text{ mm}$ as brass insert backstop, front apex calibrated to $Y = -3.25\text{ mm}$ with $45^\circ$ flared foot at $Z \in [1.00, 2.15]\text{ mm}$ ramping forward to $Y = -2.45\text{ mm}$).
  - $Z \in [1.00, 15.59]\text{ mm}$: Support towers & monolithic cross-tie bridge ($14.59\text{ mm}$ tall above floor, apex at $Z = 15.59\text{ mm}$, solid rounded arch crown).
- **Perimeter Clips (4x)**: $45^\circ, 135^\circ, 211.3^\circ, 327.5^\circ$. Independent calibrated retention shelf elevations: Top clips ($45^\circ, 135^\circ$) lowered to $Z = 3.97\text{ mm}$ ($\Delta Z = -0.75\text{ mm}$, closing the SIM tool axial play gap and preventing baseplate back-out during plug insertion); Bottom clips ($211.3^\circ, 327.5^\circ$) lowered to $Z = 4.35\text{ mm}$ ($\Delta Z = -0.37\text{ mm}$, closing remaining half-SIM gap). Radial hook depths: $1.80\text{ mm}$ for $45^\circ, 135^\circ, 211.3^\circ$, and calibrated $1.85\text{ mm}$ for $327.5^\circ$ (+0.05mm reach for reliable latching without excessive insertion force); $0.20\text{ mm}$ crown ease, $0.53\text{ mm}$ blunt land, $2.07\text{ mm}$ solid hoop ring. Bottom clips feature 3-prong anti-sag breakaway trident supports ($0.80\text{ mm}$ and $0.90\text{ mm}$ lands at $t = -1.25, 0.00, +1.25\text{ mm}$, $0.60\text{ mm}$ root neck) with direct central apex support and a calibrated $0.29\text{ mm}$ shelf release gap ($Z_{\text{top}} = 4.06\text{ mm}$), eliminating PC-FR overhang droop without thermal welding.
- **Integrated Slit Shrouds / Inserts**: In-place backside chimneys ($Z \in [-2.47, 0.00]\text{ mm}$) at $X = -7.853\text{ mm}$ and $+8.453\text{ mm}$, channels $1.10 \times 3.00\text{ mm}$. Supported in 45° print orientation by twin 0.90mm contoured breakaway saddles under the 32.5° overhanging back wall with an expanded $0.23\text{ mm}$ release gap (half measure from 0.18mm) and a 1.40mm open center window clearing the slit holes.
- **Captive PIP Safety Lever Supports**:
  - **Plunger Support (Protruding from Base Pad)**: Central column ($1.80 \times 1.80\text{ mm}$) rising directly from the bed pad ($Z' = 0.60\text{ mm}$) through the baseplate through-hole, branching into a 3-tine fork supporting both lateral edges and center apex of the $3.60\text{ mm}$ plunger blade with a calibrated $0.20\text{ mm}$ release gap.
  - **Cantilever (Cam Tab) Support**: Central column rising from the $45^\circ$ baseplate floor ($Z' = 12.19\text{ mm}$) with a $1.10 \times 1.10\text{ mm}$ floor neck, branching into a twin-tine fork ($X \in [5.65, 6.20]$ and $[7.00, 7.55]$) supporting both lateral edges of the $1.90\text{ mm}$ cam tab with an expanded $0.25\text{ mm}$ release gap (half measure from 0.20mm).
  - **Lever Shaft (Hub Barrel) Support**: Rigid breakaway column centered at $X_c = 8.85\text{ mm}$ rising from the base floor ($Z' = 13.61\text{ mm}$) with an easy-snap $0.65 \times 0.65\text{ mm}$ floor neck and widened $0.70\text{ mm}\,(X) \times 0.85\text{ mm}\,(Y)$ trunk (+140% area), branching at $Z' = 21.50\text{ mm}$ into a $0.68\text{ mm}$ wide Y-fork head with twin $0.26\text{ mm}$ micro-chisel lands supporting the floating cylindrical hub barrel with a calibrated $0.48\text{ mm}$ release gap ($Z'_{\text{lowest}} = 26.473\text{ mm}$, top at $Z' = 25.993\text{ mm}$), ensuring $> 0.92\text{ mm}$ clearance to the active cam tab / lever arm, $0.49\text{ mm}$ to the plunger blade, and $1.75\text{ mm}$ to Bracket 4.
- **Backplate Support Fins (Under 45° Incline)**: 5 vertical fins rising from the $0.60\text{ mm}$ bed pad: Outer pair ($X = \pm 14.00\text{ mm}$, $Y \in [-3.00, 10.00]\text{ mm}$), Center fin ($X = 0.00\text{ mm}$, extended to $Y \in [-3.00, 14.00]\text{ mm}$ for full upper backplate safety support), and Inner pair (Left fin at $X = -8.00\text{ mm}$, Right fin shifted to $X = +6.80\text{ mm}$ to clear the through-hole left boundary at $X = 7.61\text{ mm}$ and provide $+1.28\text{ mm}$ open air gap to the PIP lever plunger blade, $Y \in [-5.80, 14.00]\text{ mm}$). Equipped with calibrated $0.26\text{ mm}$ release gap (half measure from 0.24mm) and $4.50\text{ mm}$ pitch breakaway tines.

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
