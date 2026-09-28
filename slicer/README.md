# Slicer Print Project Files (.3mf)

## Overview
This directory contains pre-configured 3D printer project files for Bambu Studio / OrcaSlicer / PrusaSlicer.

## Files
- `complete_assembly_printed.3mf`: Slicer project containing the complete 1-click build plate layout (baseplate tilted 45° with support fins, shaft rocker with breakaway frame, pair of slit inserts, and cooling column).
- `complete_assembly_test.3mf`: Experimental multi-body slicer setup for print testing.

## Recommended Print Settings
- **Layer Height**: 0.16 mm (Optimal) or 0.20 mm (Standard).
- **Supports**: Disabled (all production parts feature baked-in sacrificial breakaway frames or 45° self-supporting overhangs).
- **Walls / Perimeters**: 4 walls minimum.
- **Infill**: 30% Gyroid or Grid.
- **Material**: PETG, ABS, ASA, or high-temp PC/Nylon (due to automotive in-cabin temperature swings).
