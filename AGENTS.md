# Project Instructions & Agent Guidelines

## Repository Structure & File Placement

1. **Testing and Inspection Scripts**:
   - All tests, verification scripts, geometric inspection scripts, dimension checks, and exploratory visualization scripts **must always be created inside the `testing/` directory**.
   - Temporary diagnostic plots or inspection render images generated during analysis or testing should also be saved inside `testing/`.

2. **Root Directory Integrity**:
   - The root directory must remain clean and contain only core production files:
     - Main pipeline scripts: `build_part.py`, `build_shaft.py`, `generate_labeled_preview.py`
     - Master source geometry: `part.svg`
     - Production CAD & Mesh deliverables: `part.stl`, `part.obj`, `part.scad`, `shaft_rocker.*`, `slit_insert.*`, `cooling_tower.*`, `complete_assembly.*`
     - Primary project previews: `part_preview.png`, `labeled_part_preview.png`
     - Documentation & config: `README.md`, `AGENTS.md`, `.gitignore`

3. **Running Testing Scripts**:
   - Testing scripts inside `testing/` can import from parent or execute against root CAD files by resolving paths relative to the project root.
