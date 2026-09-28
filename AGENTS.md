# Project Instructions & Agent Guidelines

## 1. Repository Structure & Directory Roles

- **Root Directory (`/`)**: Must remain clean, reserved strictly for primary production deliverables and core pipeline scripts:
  - Main pipeline generators: `build_part.py`, `build_shaft.py`, `generate_labeled_preview.py`
  - Master source geometry: `part.svg`
  - Production CAD & mesh deliverables: `part.stl`, `part.obj`, `part.scad`, `shaft_rocker.*`, `slit_insert.*`, `cooling_tower.*`, `complete_assembly.*`
  - Primary preview diagrams: `part_preview.png`, `labeled_part_preview.png`
  - Documentation & config: `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `.gitignore`
- **Accessories (`accessories/tower_clamp/`)**: Optional or modular add-on accessories (e.g., anti-spreading tower prongs clamps and their generator `build_clamp.py`).
- **Slicer Profiles (`slicer/`)**: Pre-configured slicer project files (`*.3mf`).
- **Testing & Diagnostics (`testing/`)**:
  - All test scripts, verification scripts, geometric inspection scripts, and exploratory visualization scripts **must always reside in `testing/`**.
  - Temporary diagnostic plots (`*.png`) or inspection renders should also be saved inside `testing/`.
  - See `testing/README.md` for the test catalog and execution guide.

## 2. Context Window & Efficiency Guidelines

- **Quick Architecture Reference**: Read `ARCHITECTURE.md` first for critical datums, coordinates, and layer stacks before reading large source files.
- **Git & Terminal Cleanliness**: Use concise commands (e.g., `git status -s`, targeted file lookups) to avoid flooding the context window with long recursive directory listings.
- **Running Tests**: Run tests from the repository root: `py -3 testing/<script_name>.py`.
