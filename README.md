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
- `BSplineLayers`
- `IsoValue`
- `CellScaleX`, `CellScaleY`, `CellScaleZ`

`Mode` controls the output:

- `Spline Layers` shows only the generated B-spline contour layers.
- `Surface` lofts surfaces between matched contour layers.

Use `BSplineLayers` to control how many stacked B-spline layers are generated
through the cell in the Z direction. `Resolution` controls the in-plane contour
sampling density for each layer.

## Dependency

The current generator uses `numpy` to sample the implicit field on stacked
planes. Each plane is converted into contour curves with marching squares; the
curves are resampled, converted to FreeCAD B-spline wires, and either shown
directly or lofted between adjacent layers.

## Implementation Note

The output is a surface-first MVP. Topology changes between slices are matched
conservatively by contour type and centroid proximity, so ambiguous split/merge
regions may be skipped until dedicated branch handling is added.
