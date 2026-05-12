# Implicit TPMS FreeCAD Workbench

This workbench creates implicit TPMS surfaces and thickened solids as native
FreeCAD `Part` shapes.

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
- `IsoValue`
- `WallThickness`
- `CellScaleX`, `CellScaleY`, `CellScaleZ`
- `OffsetPlus`, `OffsetMinus`, `Tolerance`, `MaxErrorIterations`
- `SewingTolerance`

## Dependency

The current generator uses `numpy` and, when available, `scikit-image` for
isosurface extraction, then converts the triangles into a FreeCAD `Part.Shell`
or `Part.Solid`. If `scikit-image` is not installed, it falls back to a bundled
marching-tetrahedra extractor.

Install `scikit-image` into FreeCAD's Python environment for faster extraction:

```bash
python -m pip install scikit-image
```

## Implementation Note

The included `implicit_tpms.bspline` module implements the B-spline basis and
surface evaluation utilities described in `tpms2step_python_reimplementation_spec.md`.
The current FreeCAD object is an MVP faceted B-rep backend; the B-spline TPMS
patch fitting and symmetry assembly from the spec can be layered behind the same
`TPMSConfig` and FeaturePython properties.
