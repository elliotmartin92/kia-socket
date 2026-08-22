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
| **`slit_insert.stl`** / **`slit_insert.obj`** | Separate 3D-printable backside slit wall insert with integrated indexing registration key. |
| **`slit_inserts_pair.stl`** | Two inserts pre-arranged side-by-side on a single build plate for 1-click 3D printing. |
| **`complete_assembly.stl`** / **`complete_assembly.obj`** | Complete 1-click 3D print plate with the main baseplate and both separate slit inserts pre-arranged side-by-side on the **same flat print plane ($Z = 0.00\text{ mm}$)**. |
| **`part.scad`** | OpenSCAD source file representing the exact geometry. |
| **`labeled_part_preview.png`** | 2-panel blueprint showing top-down dimensioned feature map and 3D isometric perspective. |
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
  - $Z \in [1.00, 13.59]\text{ mm}$: Shaft support towers ($12.59\text{ mm}$ height above floor, total $13.59\text{ mm}$).
- **Separate Slit Insert Dimensions**:
  - $Z \in [0.00, 2.47]\text{ mm}$: Wall body ($3.65\text{ mm} \times 5.55\text{ mm}$ outer, $1.05\text{ mm} \times 3.35\text{ mm}$ inner clearance channel for $0.75\text{ mm} \times 3.00\text{ mm}$ part).
  - $Z \in [2.47, 3.32]\text{ mm}$: Indexing registration key ($1.85\text{ mm} \times 4.15\text{ mm} \times 0.85\text{ mm}$) with continuous $1.05\text{ mm} \times 3.35\text{ mm}$ core.

---

## 3. Comprehensive Feature Specifications

```
                              TOP TAB (8.22mm Wide)
                              +-------------------+
                             /                     \
                            /   [TOWER 1] [TOWER 2] \  <-- Shaft Axis (Y = 7.67mm, Z = 12.59mm)
           Snap Clip (135°) |      (1.65mm throat)  | Snap Clip (45°)
                            |   [Through-Hole]      |
                            |   5.35 x 4.51 mm      |
                            |                       |
             Left Side Ear -|   [BRACKETS]          |- Right Side Ear
                            |   [CENTER ARCH WALL]  |
                            |   (10.50mm tall)      |
           Snap Clip (225°) |                       | Snap Clip (315°)
                            \   [SLIT 1]  [SLIT 2]  /
                             \  1.05x3.35 1.05x3.35/
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

### 3.2. Shaft Support Towers with Retention Cradles
- **Shaft Axis**: $Y = 7.666\text{ mm}$, $Z = 12.59\text{ mm}$ ($\varnothing 2.00\text{ mm}$ shaft, $R = 1.00\text{ mm}$).
- **Left Tower**: $X \in [4.250, 5.500]\text{ mm}$ ($1.25\text{ mm}$ wall thickness).
- **Right Tower**: $X \in [13.360, 14.610]\text{ mm}$ ($1.25\text{ mm}$ thickness, $0.40\text{ mm}$ clearance right of through-hole).
- **Internal Clearance Between Towers**: **$7.86\text{ mm}$**.
- **Snap-Fit Retention Cradle**:
  - Circle wraps $248.8^\circ$ around the shaft ($34.4^\circ$ above equator).
  - Retention throat constriction gap: **$1.65\text{ mm}$** at $Z = 13.155\text{ mm}$.
  - Top lead-in bevel: $45^\circ$ slope expanding out to $Z = 13.59\text{ mm}$ ($z_{\text{top}}$).
- **Left Tower Buttress Struts**: Two steep triangular ribs ($0.80\text{ mm}$ thick in $Y$), extending $2.35\text{ mm}$ in $-X$ at base ($Z = 1.0\text{ mm}$), sloping directly into the tower at $Z = 11.59\text{ mm}$ ($2\text{ mm}$ below apex).
- **Right Tower Reinforcing Bridge Rib**: Spans $X \in [14.61, 18.20]\text{ mm}$ at $Y = 9.49\text{ mm}$, extruded to full $6.77\text{ mm}$ outer wall height.

### 3.3. Curved Snap Clips (4x at $45^\circ, 135^\circ, 225^\circ, 315^\circ$)
- **Wall Following**: Matches the exact curved contour of the outer ($R \approx 19.25\text{ mm}$) and inner ($R \approx 18.05\text{ mm}$) wall.
- **Flex Isolation**: Two $0.60\text{ mm}$ vertical through-slots from $Z = 3.07\text{ mm}$ to $Z = 6.77\text{ mm}$ isolating a $3.00\text{ mm}$ wide curved beam.
- **Hook Geometry ($Z \in [4.97, 6.77\text{ mm}$)**:
  - Undercut retention shelf at $Z = 4.97\text{ mm}$ projecting $+1.59\text{ mm}$ radially outward.
  - Sloped lead-in ramp tapering up to top outer wall apex at $Z = 6.77\text{ mm}$.
  - Inner wall face: 100% flush, smooth, continuous cylinder.

### 3.4. Center Curved Feature with Dividing Rib (Option 1A)
- **Position**: Centered between Brackets 3 & 4 at $X_c = +6.279\text{ mm}$.
- **Width**: $4.30\text{ mm}$ ($X \in [4.129, 8.429]\text{ mm}$).
- **Depth in $Y$**: $1.62\text{ mm}$ (Base: $Y = -4.069\text{ mm}$, Apex: $Y = -2.449\text{ mm}$).
- **Offset**: $2.00\text{ mm}$ in $+Y$ above the horizontal bracket step datum ($Y = -6.069\text{ mm}$).
- **Wall & Rib Thickness**: $0.60\text{ mm}$ wall + $0.60\text{ mm}$ internal dividing rib along $X = 6.279\text{ mm}$.
- **Total Height**: **$10.50\text{ mm}$** ($Z \in [1.00, 10.50]\text{ mm}$).

### 3.5. Guide Brackets (4 Brackets / 2 Pairs)
- **Left Pair (Brackets 1 & 2)**: $X \in [-10.80, -3.70]\text{ mm}$.
- **Right Pair (Brackets 3 & 4)**: $X \in [+3.70, +10.80]\text{ mm}$.
- **Height**: $4.60\text{ mm}$ ($Z \in [1.00, 4.60]\text{ mm}$).
- **Wall Thickness**: $0.84\text{ mm}$ nominal.

### 3.6. Backside Slit Protruding Bosses & Separate Inserts
- **Hole Dimensions**: Two $1.05\text{ mm} \text{ (in X)} \times 3.35\text{ mm} \text{ (in Y)}$ through-slits (clearance fit to comfortably pass a $0.75\text{ mm} \times 3.00\text{ mm}$ component).
- **Positioning**:
  - $1.00\text{ mm}$ in $+Y$ from inner face of bottom wall ($Y \in [-16.34, -12.99]\text{ mm}$).
  - Aligned with leftmost wall of right bracket ($X = +7.853\text{ mm}$) and rightmost wall of left bracket ($X = -7.853\text{ mm}$).
- **Protruding Walls / Separate Inserts**: $0.80\text{ mm}$ thick wall, protruding **$2.47\text{ mm}$** on the $-Z$ side ($Z \in [-2.47, 0.00]\text{ mm}$).
- **Complete Assembly Build Plate Layout**: `complete_assembly.stl` arranges the main baseplate and both separate slit inserts flat on the **same build plane ($Z = 0.00\text{ mm}$)** side-by-side for 1-click support-free 3D printing.

### 3.7. Internal Floor Stiffener Grid
- **Pitch**: $5.20\text{ mm}$ (in $X$) $\times 3.20\text{ mm}$ (in $Y$).
- **Thickness & Height**: $0.60\text{ mm}$ thick, $0.50\text{ mm}$ tall ($Z \in [1.00, 1.50]\text{ mm}$).
- **Connectivity**: Connects directly into outer perimeter walls; excluded under bracket pairs and bottom zone ($Y < -7.17\text{ mm}$).

---

## 4. Key Scripts & Code Architecture

- **`build_part.py`**:
  - `get_exact_base_polygon()`: Parses SVG path, aligns bottom notch, and creates through-holes.
  - `create_arch_wall_poly()`: Builds the $7.95\text{ mm}$ tall, $5.00\text{ mm}$ inner width U-arch.
  - `build_clean_shaft_towers_mesh()`: Generates both towers with the $1.65\text{ mm}$ retention cradle.
  - `build_left_tower_struts_mesh()`: Creates the triangular buttress struts on the left tower.
  - `create_center_curved_feature_poly()`: Generates the $10.50\text{ mm}$ tall center feature.
  - `build_exact_3d_model()`: Assemblies all components and cuts flex slots into the wall.
- **`generate_labeled_preview.py`**:
  - Generates the two-panel labeled 2D feature map and 3D isometric perspective.
