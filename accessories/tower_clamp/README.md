# Anti-Spreading Tower Prongs Clamp (Auxiliary Accessory)

## Overview
This directory contains the parametric CAD generator and 3D print assets for optional anti-spreading tower clamp collars.

### Function
When high cyclic plug insertion force is experienced, these clamps can optionally be pushed down over the tops of the baseplate shaft support towers ($Z \in [11.20, 14.09]\text{ mm}$) to mechanically bind the left and right tower heads and completely prevent axle pop-out or spreading under severe overload.

> [!NOTE]
> The primary production baseplate now features heavy-duty $240^\circ$ wrap-around retention cradles with dual lateral buttress struts, making auxiliary clamps optional. They are preserved here as a standalone accessory.

## Files
- `build_clamp.py`: Parametric CAD generator script.
- `tower_clamp_bridge.stl` / `.obj` (`tower_clamp.*`): Unified 1-piece monolithic bridge clamp spanning across both towers.
- `tower_clamp_left.stl` / `.obj`: Standalone modular sleeve for Left Tower.
- `tower_clamp_right.stl` / `.obj`: Standalone modular sleeve for Right Tower.
- `tower_clamps_pair.stl`: Both left and right sleeves pre-arranged for printing.
- `tower_clamp.scad`: Parametric OpenSCAD reference model.

## Regeneration
```bash
py -3 accessories/tower_clamp/build_clamp.py
```
