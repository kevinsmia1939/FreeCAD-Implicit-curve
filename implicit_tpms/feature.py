"""FreeCAD FeaturePython object for implicit TPMS generation."""

from __future__ import annotations

from .config import TPMSConfig
from .generator import generate_tpms_shape


FAMILY_LABELS = ("Schwarz P", "Gyroid", "Diamond")
FAMILY_TO_KEY = {"Gyroid": "gyroid", "Diamond": "diamond", "Schwarz P": "schwarz_p"}
MODE_LABELS = ("Solid", "Surface")


class ImplicitTPMSFeature:
    def __init__(self, obj):
        obj.Proxy = self
        self._add_properties(obj)

    def _add_properties(self, obj):
        obj.addProperty("App::PropertyEnumeration", "Family", "TPMS", "TPMS family")
        obj.Family = FAMILY_LABELS
        obj.Family = "Schwarz P"

        obj.addProperty("App::PropertyEnumeration", "Mode", "TPMS", "Output mode")
        obj.Mode = MODE_LABELS
        obj.Mode = "Solid"

        for name, default in (("CellsX", 1), ("CellsY", 1), ("CellsZ", 1), ("Resolution", 36)):
            obj.addProperty("App::PropertyInteger", name, "TPMS", name)
            setattr(obj, name, default)

        for name, default in (
            ("OffsetPlus", 0.1),
            ("OffsetMinus", 0.0),
            ("Tolerance", 0.005),
            ("CellScaleX", 1.0),
            ("CellScaleY", 1.0),
            ("CellScaleZ", 1.0),
            ("IsoValue", 0.0),
            ("WallThickness", 0.12),
            ("SewingTolerance", 1e-3),
        ):
            obj.addProperty("App::PropertyFloat", name, "TPMS", name)
            setattr(obj, name, default)

        obj.addProperty("App::PropertyInteger", "MaxErrorIterations", "TPMS", "Maximum fitting iterations")
        obj.MaxErrorIterations = 1

    def execute(self, obj):
        config = TPMSConfig(
            family=FAMILY_TO_KEY.get(obj.Family, "schwarz_p"),
            cells=(max(1, obj.CellsX), max(1, obj.CellsY), max(1, obj.CellsZ)),
            offset_plus=obj.OffsetPlus,
            offset_minus=obj.OffsetMinus,
            tolerance=max(1e-6, obj.Tolerance),
            max_error_iterations=max(1, obj.MaxErrorIterations),
            scale=(obj.CellScaleX, obj.CellScaleY, obj.CellScaleZ),
            resolution=max(12, obj.Resolution),
            isovalue=obj.IsoValue,
            wall_thickness=max(1e-6, obj.WallThickness),
            mode="solid" if obj.Mode == "Solid" else "surface",
            sewing_tolerance=max(1e-9, obj.SewingTolerance),
        )
        obj.Shape = generate_tpms_shape(config)


class ImplicitTPMSViewProvider:
    def __init__(self, view_obj):
        view_obj.Proxy = self

    def attach(self, view_obj):
        self.ViewObject = view_obj

    def getDisplayModes(self, view_obj):
        return ["Shaded", "Wireframe"]

    def getDefaultDisplayMode(self):
        return "Shaded"

    def setDisplayMode(self, mode):
        return mode

    def updateData(self, fp, prop):
        return

    def onChanged(self, view_obj, prop):
        return

    def getIcon(self):
        return ""

