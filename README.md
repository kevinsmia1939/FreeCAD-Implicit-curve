# Implicit TPMS FreeCAD Workbench

This workbench creates implicit TPMS surfaces as native FreeCAD `Part` shapes.

## Commands

- `Create Schwarz P`
- `Create Gyroid`
- `Create Diamond`
- `Recompute TPMS`

Each command creates a `Part::FeaturePython` object with editable properties:

- `Family`
- `Mode`
- `CellsX`, `CellsY`, `CellsZ`
- `Resolution`
- `SliceCount`
- `IsoValue`
- `CellScaleX`, `CellScaleY`, `CellScaleZ`

## Dependency

The current generator uses `numpy` to sample the implicit field on stacked
planes. Each plane is converted into contour curves with marching squares; the
curves are resampled, converted to FreeCAD B-spline wires, and lofted between
adjacent slices.

## Implementation Note

The output is a surface-first MVP. Topology changes between slices are matched
conservatively by contour type and centroid proximity, so ambiguous split/merge
regions may be skipped until dedicated branch handling is added.
