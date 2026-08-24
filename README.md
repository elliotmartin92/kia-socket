# Parametric 3D CAD Model & Generator Documentation

This repository contains the complete parametric CAD generation pipeline for the custom enclosure baseplate with precision mechanical features, snap clips, guide brackets, shaft support towers, and internal ribs.

---

## 1. Quick Start & Regeneration Commands

To rebuild all 3D CAD assets and 2D/3D annotated blueprints from source:

```bash
# Generate 3D models (part.stl, part.obj, part.scad, part_preview.png)
py -3 build_part.py

# Generate high-resolution dimensioned feature blueprints (labeled_part_preview.png)
py -3 generate_labeled_preview.py
```

### Generated Output Files
| File | Description |
| :--- | :--- |
| **`part.stl`** / **`part.obj`** | Main baseplate with **100% planar flat bottom ($Z = 0.00\text{ mm}$)** for support-free 3D printing. |
| **`shaft_rocker.stl`** / **`shaft_rocker.obj`** | Separate 3D-printable enlarged heavy-duty shaft/rocker mechanism with $\varnothing 2.80\text{ mm}$ axle pins, $\varnothing 4.20\text{ mm}$ hub, input cam, and $\ge 6.5\text{ mm}$ reach plunger. Pre-oriented flat on build bed ($Z = 0.00\text{ mm}$). |
| **`shaft_rocker_assembled.stl`** | Shaft/rocker mechanism positioned in exact assembly coordinates seated in the towers. |
| **`shaft_rocker.scad`** | OpenSCAD parametric source file for the shaft/rocker mechanism. |
| **`slit_insert.stl`** / **`slit_insert.obj`** | Separate 3D-printable backside slit wall insert with integrated indexing registration key. |
| **`slit_inserts_pair.stl`** | Two inserts pre-arranged side-by-side on a single build plate for 1-click 3D printing. |
| **`cooling_tower.stl`** / **`cooling_tower.obj`** | Sacrificial cooling column ($\varnothing 8.00\text{ mm} \times 14.50\text{ mm}$ tall) to guarantee dedicated cooling time per layer on delicate tower tips. |
| **`complete_assembly.stl`** / **`complete_assembly.obj`** | Complete 1-click 3D print plate with the main baseplate, both separate slit inserts, shaft rocker, and sacrificial cooling tower pre-arranged side-by-side on the **same flat print plane ($Z = 0.00\text{ mm}$)**. |
| **`part.scad`** | OpenSCAD source file representing the exact baseplate geometry. |
| **`labeled_part_preview.png`** | 3-panel blueprint showing top-down dimensioned feature map, 3D isometric assembly, and kinematic stroke cross-section. |
| **`part_preview.png`** | 3-panel multi-angle view (Top-Down, 3D Perspective, Bottom View). |

---

## 2. Coordinate System & Global Units

- **Units**: All dimensions are in **millimeters ($\text{mm}$)**.
- **Origin $(0, 0, 0)$**: Geometric center of the main body circle/profile.
- **Scale Factor**: Calibrated from SVG pixel coordinates:
  $$\text{SCALE} = 0.349787\text{ mm/pixel}, \quad X_0 = 128.65\text{ px}, \quad Y_0 = 128.65\text{ px}$$
- **$Z$-Axis Elevations (Main Part)**:
  - $Z = 0.00\text{ mm}$: 100% Flat build-plate datum (zero support needed under main floor).
  - $Z \in [0.00, 1.00]\text{ mm}$: Solid base floor plate ($1.00\text{ mm}$ thick).
  - $Z \in [1.00, 1.50]\text{ mm}$: Internal floor stiffener grid ribs ($0.50\text{ mm}$ tall).
  - $Z \in [1.00, 4.60]\text{ mm}$: Guide brackets ($4.60\text{ mm}$ total height).
  - $Z \in [1.00, 6.77]\text{ mm}$: Outer perimeter wall, snap clip stems, bottom arch wall, and bridge rib ($6.77\text{ mm}$ height).
  - $Z \in [1.00, 10.50]\text{ mm}$: Center curved feature with internal rib ($10.50\text{ mm}$ total height).
  - $Z \in [1.00, 14.09]\text{ mm}$: Shaft support towers ($13.09\text{ mm}$ height above floor, total $14.09\text{ mm}$).
- **Separate Slit Insert Dimensions**:
  - $Z \in [0.00, 2.47]\text{ mm}$: Wall body ($3.80\text{ mm} \times 5.60\text{ mm}$ outer, $1.20\text{ mm} \times 3.50\text{ mm}$ inner clearance channel for $0.77\text{ mm} \times 3.10\text{ mm}$ part).
  - $Z \in [2.47, 3.32]\text{ mm}$: Indexing registration key ($2.00\text{ mm} \times 4.30\text{ mm} \times 0.85\text{ mm}$) with continuous $1.20\text{ mm} \times 3.50\text{ mm}$ core.

---

## 3. Comprehensive Feature Specifications

```
                              TOP TAB (8.20mm Wide, fits 8.33mm Gap)
                              +-------------------+
                             /                     \
                            /   [TOWER 1] [TOWER 2] \  <-- Shaft Axis (Y = 9.28mm, Z = 12.59mm)
           Snap Clip (135°) |      (2.45mm throat)  | Snap Clip (45°)
                            |   [Through-Hole]      |
                            |   5.35 x 4.51 mm      |
                            |                       |
       Left Side Ear (7.70)-|   [BRACKETS]          |- Right Side Ear (7.70mm Wide, fits 8.30mm Gap)
                            |   [CENTER ARCH WALL]  |
                            |   (10.50mm tall)      |
          Snap Clip (211.3°)|                       | Snap Clip (327.5°)
                            \   [SLIT 1]  [SLIT 2]  / (4.42mm from ears, 8.47mm from tabs)
                             \  1.20x3.50 1.20x3.50/
                              +---+             +---+
                              |   | [U-ARCH 5mm]|   |
                              |   | (7.95mm H)  |   |
                              +---+-------------+---+
                              LEFT TAB       RIGHT TAB
```

### 3.1. Bottom Central U-Arch & Inset Wall (Config 1)
- **Arch Interior Clearance Width**: **$5.00\text{ mm}$** ($R_{\text{inner}} = 2.50\text{ mm}$, centered on $X \in [-2.50, +2.50]\text{ mm}$).
- **Arch Wall Thickness**: **$1.20\text{ mm}$** ($R_{\text{outer}} = 3.70\text{ mm}$, $X \in [-3.70, +3.70]\text{ mm}$).
- **Total Outer Height in $Y$**: **$7.95\text{ mm}$**
  - Base at Inset Bottom Exterior Wall: $Y = -16.650\text{ mm}$
  - Outer Arch Apex: $Y = -8.700\text{ mm}$ ($-16.650 + 7.950\text{ mm}$)
  - Inner Arch Apex: $Y = -9.900\text{ mm}$ ($6.75\text{ mm}$ inner clearance height)
  - Semicircle Arc Center: $Y = -12.400\text{ mm}$ (Straight tangent legs: $4.25\text{ mm}$ in $Y$).
- **Inset Bottom Exterior Wall Notch**:
  - Inset depth: $1.889\text{ mm}$ in $+Y$ (from bottom tabs at $Y = -18.539\text{ mm}$ to inset wall at $Y = -16.650\text{ mm}$).
  - Notch outer sidewalls: placed at **$X = \pm 2.500\text{ mm}$**, aligning with the **interior sidewalls of the arch**.
  - Floor: Solid continuous $1.00\text{ mm}$ floor within the inset wall.

### 3.2. Shaft Support Towers with Heavy-Duty Reinforced Retention Cradles
- **Shaft Axis**: **$Y = 9.279\text{ mm}$, $Z = 12.59\text{ mm}$** ($\varnothing 3.00\text{ mm}$ shaft cradle socket, centered directly over the through-hole).
- **Left Tower**: $X \in [3.900, 5.400]\text{ mm}$ ($1.50\text{ mm}$ wall thickness).
- **Right Tower**: $X \in [13.100, 14.600]\text{ mm}$ ($1.50\text{ mm}$ thickness, $0.14\text{ mm}$ clearance right of through-hole).
- **Internal Clearance Between Towers**: **$7.70\text{ mm}$**.
- **Flared Trapezoidal Tower Profile (in Y-Z)**:
  - Base Length in $Y$: **$6.60\text{ mm}$** ($Y \in [6.250, 12.850]\text{ mm}$, shifted $-0.921\text{ mm}$ to align buttress base with top inner wall of Bracket 3 at $Y = 6.250\text{ mm}$).
  - Top Length in $Y$: **$5.63\text{ mm}$** ($Y \in [6.550, 12.180]\text{ mm}$).
- **Positive Heavy-Duty Snap-Fit Retention Cradle**:
  - Socket Diameter: **$\varnothing 3.00\text{ mm}$** (provides $0.20\text{ mm}$ running clearance with $\varnothing 2.80\text{ mm}$ shaft pin).
  - Retention throat constriction gap: **$2.45\text{ mm}$** ($0.35\text{ mm}$ firm positive mechanical interference with $\varnothing 2.80\text{ mm}$ shaft).
  - Wrap angle: **$>250^\circ$**, permanently locking the axle inside the circular $\varnothing 3.00\text{ mm}$ socket.
  - Wide $3.25\text{ mm}$ lead-in funnel with bevels expanding up to $Z = 14.09\text{ mm}$ for smooth downward insertion.
- **Left Tower Dual Lateral Buttress Struts**:
  - **Front Strut**: Base meets the top inner wall of Bracket 3 at **$Y = 6.250\text{ mm}$** ($X \in [1.90, 3.90\text{ mm}]$, $Y \in [6.250, 7.050\text{ mm}]$), sloping directly into the Left Tower at $Z = 13.70\text{ mm}$ with **zero encroachment into Bracket 3's sliding channel**.
  - **Rear Strut**: Full-height triangular rib ($1.20\text{ mm}$ thick in $Y$ at $Y \in [11.650, 12.850\text{ mm}]$, $X \in [1.90, 3.90\text{ mm}]$, $Z \in [1.00, 13.70\text{ mm}]$).
- **Right Tower Reinforcing Bridge Rib**: Spans $X \in [13.10, 20.00]\text{ mm}$ at $Y \in [7.50, 13.00]\text{ mm}$, connecting directly to the outer perimeter wall.

### 3.3. Curved Snap Clips (4x at $45^\circ, 135^\circ, 211.3^\circ, 327.5^\circ$)
- **Perimeter Positions**:
  - Top pair: $45^\circ$ and $135^\circ$ (halfway between top tab and side ears).
  - Bottom pair: **$211.3^\circ$ and $327.5^\circ$** (**$4.42\text{ mm}$ from respective side ears, $8.47\text{ mm}$ from respective bottom tabs**).
- **Wall Following**: Matches the exact curved contour of the outer ($R \approx 19.25\text{ mm}$) and inner ($R \approx 18.05\text{ mm}$) wall.
- **Beam Dimensions**: **$4.20\text{ mm}$ wide curved beam** (leaves $0.80\text{ mm}$ total margin / $0.40\text{ mm}$ per side for smooth insertion into $5.00\text{ mm}$ mating holes).
- **Flex Isolation**: Two $0.35\text{ mm}$ vertical through-slots (minimal printable clearance for a $0.4\text{ mm}$ nozzle) from $Z = 3.07\text{ mm}$ to $Z = 6.77\text{ mm}$ isolating the cantilever beam.
- **Hook Geometry ($Z \in [4.97, 6.77\text{ mm}$)**:
  - Undercut retention shelf at $Z = 4.97\text{ mm}$ projecting $+1.59\text{ mm}$ radially outward.
  - Sloped lead-in ramp tapering up to top outer wall apex at $Z = 6.77\text{ mm}$.
  - Inner wall face: 100% flush, smooth, continuous cylinder.
- **Built-In Sacrificial Support Towers (4x Breakaway Mini-Pillars)**:
  - Small vertical support tower ($0.90\text{ mm} \times 2.00\text{ mm}$) directly under the horizontal overhang shelf of each clip.
  - Base flat on the print bed ($Z = 0.00\text{ mm}$) with an adhesion foot ($1.50\text{ mm} \times 2.80\text{ mm}$).
  - Rises to $Z = 4.82\text{ mm}$ with a small chisel contact interface ($0.15\text{ mm}$ breakaway gap under the $Z = 4.97\text{ mm}$ shelf) for effortless snap-off removal without marring.

### 3.4. Center Curved Feature with Dividing Rib (Option 1A)
- **Position**: Centered between Brackets 3 & 4 at $X_c = +6.279\text{ mm}$.
- **Width**: $4.30\text{ mm}$ ($X \in [4.129, 8.429]\text{ mm}$).
- **Depth in $Y$**: $1.62\text{ mm}$ (Base: $Y = -4.069\text{ mm}$, Apex: $Y = -2.449\text{ mm}$).
- **Offset**: $2.00\text{ mm}$ in $+Y$ above the horizontal bracket step datum ($Y = -6.069\text{ mm}$).
- **Wall & Rib Thickness**: $0.60\text{ mm}$ wall + $0.60\text{ mm}$ internal dividing rib along $X = 6.279\text{ mm}$.
- **Total Height**: **$10.50\text{ mm}$** ($Z \in [1.00, 10.50]\text{ mm}$).

### 3.5. Guide Brackets (4 Brackets / 2 Pairs - Adjusted Top Gaps)
- **Left Pair (Brackets 1 & 2)**: $X \in [-10.79, -1.77]\text{ mm}$.
- **Right Pair (Brackets 3 & 4)**: $X \in [+1.77, +10.79]\text{ mm}$.
- **Bracket 3 Full Geometry (Identical to Bracket 1)**:
  - Slot width: **$0.86\text{ mm}$** ($X \in [2.851, 3.708]\text{ mm}$, identical to Bracket 1).
  - Hook lip width: **$1.00\text{ mm}$** ($X \in [3.708, 4.705]\text{ mm}$, identical to Bracket 1).
  - Lower face of top hook raised to $Y = 4.800\text{ mm}$ (giving $+0.22\text{ mm}$ extra vertical fit clearance).
  - Upper pocket depth extended to $Y = 6.250\text{ mm}$ (giving $+0.20\text{ mm}$ extra vertical pocket clearance).
- **Height**: $4.60\text{ mm}$ ($Z \in [1.00, 4.60]\text{ mm}$).
- **Wall Thickness**: $0.84\text{ mm}$ nominal.

### 3.6. Backside Slit Protruding Bosses & Press-Fit Detent Inserts (For 0.77mm x 3.10mm Part)
- **Mating Component Fitment**: Custom engineered to comfortably pass a **$0.77\text{ mm} \text{ (thick in X)} \times 3.10\text{ mm} \text{ (long in Y)}$** metal contact blade.
- **Continuous Internal Through-Channel**: **$1.20\text{ mm} \text{ (in X)} \times 3.50\text{ mm} \text{ (in Y)}$** through both the insert and baseplate (+0.43mm in X, +0.40mm in Y generous sliding clearance to prevent FDM print shrinkage binding).
- **Main Baseplate Detent Sockets**: Two **$2.25\text{ mm} \times 4.55\text{ mm}$** female detent sockets cut through the $1.00\text{ mm}$ baseplate floor centered at $X = \pm 8.453\text{ mm}, Y = -13.589\text{ mm}$.
- **Separate Slit Inserts (`slit_insert.stl`)**:
  - Base body: $3.80\text{ mm} \times 5.60\text{ mm} \times 2.47\text{ mm}$ outer shroud ($Z \in [-2.47, 0.00]\text{ mm}$).
  - Male indexing key: $2.00\text{ mm} \times 4.30\text{ mm} \times 0.85\text{ mm}$ tall ($Z \in [0.00, 0.85]\text{ mm}$ in assembly coordinates, $0.40\text{ mm}$ perimeter wall).
  - Clearances: **$0.25\text{ mm}$ total clearance ($0.125\text{ mm}$ per side)** into the baseplate detent socket for smooth, firm press-fit seating without binding or requiring excessive force.
  - Flush horizontal seating shoulder: $0.78\text{ mm}$ wide flat seating rim against $Z = 0.00\text{ mm}$ baseplate bottom.
- **Positioning (Option 1 - Shifted $+1.00\text{ mm}$ in $+Y$)**:
  - $2.00\text{ mm}$ in $+Y$ from inner face of bottom wall ($Y \in [-15.34, -11.99]\text{ mm}$, centered at $Y = -13.664\text{ mm}$).
  - Aligned with leftmost wall of right bracket ($X = +7.853\text{ mm}$) and rightmost wall of left bracket ($X = -7.853\text{ mm}$).
  - Reduces the lead-in gap to the bracket entrance from $5.82\text{ mm}$ to $4.82\text{ mm}$.
- **Complete Assembly Build Plate Layout**: `complete_assembly.stl` arranges the main baseplate, both separate slit inserts, shaft rocker, and sacrificial cooling tower flat on the **same build plane ($Z = 0.00\text{ mm}$)** side-by-side for 1-click support-free 3D printing.

### 3.7. Left and Right Side Ears (8.20mm Width for 8.30mm Enclosure Gap)
- **Position**: Left Side Ear at $X \approx -21.075\text{ mm}$, Right Side Ear at $X \approx +20.200\text{ mm}$ (centered at $Y = 0.00\text{ mm}$).
- **Outer Width in $Y$**: **$8.20\text{ mm}$** ($Y \in [-4.10, +4.10]\text{ mm}$).
- **Mating Enclosure Gap**: $8.30\text{ mm}$ (leaves $0.10\text{ mm}$ total sliding clearance / $0.05\text{ mm}$ per side for a smooth, bind-free sliding fit into the chassis guide slots).

### 3.8. Top Tab (8.20mm Width for 8.33mm Enclosure Gap)
- **Position**: Symmetrically centered along $X = 0.00\text{ mm}$ ($X \in [-4.10, +4.10]\text{ mm}$, Top apex at $Y = 20.01\text{ mm}$).
- **Outer Width in $X$**: **$8.20\text{ mm}$**.
- **Mating Enclosure Gap**: $8.33\text{ mm}$ (leaves $0.13\text{ mm}$ total sliding clearance / $0.065\text{ mm}$ per side for a clean, centered fit into the chassis top indexing slot).

### 3.9. Internal Floor Stiffener Grid
- **Pitch**: $5.20\text{ mm}$ (in $X$) $\times 3.20\text{ mm}$ (in $Y$).
- **Thickness & Height**: $0.60\text{ mm}$ thick, $0.50\text{ mm}$ tall ($Z \in [1.00, 1.50]\text{ mm}$).
- **Connectivity**: Connects directly into outer perimeter walls; excluded under bracket pairs and bottom zone ($Y < -7.17\text{ mm}$).

### 3.10. Enlarged Heavy-Duty Shaft & Rocker Mechanism (PCB Button Actuator)
- **Pivot Axle & Structural Core**:
  - Precision $\varnothing 2.80\text{ mm}$ bearing ends ($R = 1.40\text{ mm}$, $0.10\text{ mm}$ radial clearance fit inside $\varnothing 3.00\text{ mm}$ tower cradles) snapping firmly through the $2.45\text{ mm}$ tower throat ($+47\%$ diameter, $4.72\times$ higher torsional rigidity over $\varnothing 1.90\text{ mm}$).
  - **$\varnothing 4.20\text{ mm}$ heavy-duty structural hub barrel** spanning $X \in [5.50, 13.00]\text{ mm}$ to eliminate shaft deflection, shear, or twisting under spring/switch load.
- **Heavy-Duty Filleted Output Plunger Arm**:
  - **Width in $X$**: Widened to **$4.40\text{ mm}$ in $X$** (centered at $X = 10.284\text{ mm}$ in the $5.35\text{ mm}$ through-hole with $0.48\text{ mm}$ lateral clearances).
  - **Root Thickness in $Y$**: Thickened to **$3.80\text{ mm}$ at the shaft junction** blending into the $\varnothing 4.20\text{ mm}$ central hub barrel to eliminate bending under key insertion.
  - **Tip Contact**: Smoothly tapers to a $2.00\text{ mm}$ nose diameter ($R = 1.00\text{ mm}$) at the switch contact point.
  - **Reach & Stroke**: Reaches **$\ge 6.50\text{ mm}$ below the outer bottom face of the baseplate ($Z \le -6.50\text{ mm}$)**.
  - **Kinematics**: Rotates clockwise around the $Y = 10.200\text{ mm}, Z = 12.59\text{ mm}$ pivot axis to actuate the Y-axis oriented PCB tactile switch with zero through-hole interference.
- **Reinforced Input Cam & Full-Span Monolithic Gusset Web**:
  - $2.70\text{ mm}$ wide input cam tab aligned with the key blade slider track ($X = 7.05\text{ mm}$).
  - Monolithic structural gusset web spanning continuously across the entire opening between the towers ($X \in [5.60, 12.90]\text{ mm}$).

---

## 4. Key Scripts & Code Architecture

- **`build_part.py`**:
  - `get_exact_base_polygon()`: Parses SVG path, aligns bottom notch, and creates through-holes.
  - `create_arch_wall_poly()`: Builds the $7.95\text{ mm}$ tall, $5.00\text{ mm}$ inner width U-arch.
  - `build_clean_shaft_towers_mesh()`: Generates both towers with the $1.65\text{ mm}$ retention cradle.
  - `build_left_tower_struts_mesh()`: Creates the triangular buttress struts on the left tower.
  - `create_center_curved_feature_poly()`: Generates the $10.50\text{ mm}$ tall center feature.
  - `build_exact_3d_model()`: Assemblies all components and cuts flex slots into the wall.
  - `build_indexed_assembly_mesh()`: Places main baseplate, slit inserts, and shaft rocker flat on $Z = 0.00\text{ mm}$ print plate.
- **`build_shaft.py`**:
  - `build_shaft_rocker_mesh()`: Parametric generator for the shaft/rocker mechanism with customizable axle diameter, plunger reach ($Z \le -6.5\text{ mm}$), cam angle, and print bed orientation.
  - `export_shaft_scad()`: Generates parametric OpenSCAD source file (`shaft_rocker.scad`).
- **`generate_labeled_preview.py`**:
  - Generates the 3-panel labeled blueprint: Top-down feature map, 3D isometric assembly, and side kinematic stroke cross-section.
- **`testing/`**:
  - Dedicated directory containing unit tests, dimensional verification scripts, geometric exploration scripts, and inspection renders.

---

## 5. Development & Testing Guidelines

- **Testing Files Location**: All new test scripts, verification scripts, geometric inspection scripts, and one-off diagnostic visualization scripts/renders **must be created inside the `testing/` directory**.
- **Root Directory Cleanliness**: The project root directory is strictly reserved for core build pipeline generators (`build_part.py`, `build_shaft.py`, `generate_labeled_preview.py`), source geometry inputs (`part.svg`), final CAD exports (`.stl`, `.obj`, `.scad`), final documentation previews (`part_preview.png`, `labeled_part_preview.png`), and documentation (`README.md`).


