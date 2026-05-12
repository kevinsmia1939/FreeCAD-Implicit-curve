"""FreeCAD FeaturePython object for implicit TPMS generation."""

from __future__ import annotations

from .config import TPMSConfig
from .generator import generate_tpms_shape


FAMILY_LABELS = ("Schwarz P", "Gyroid", "Diamond")
FAMILY_TO_KEY = {"Gyroid": "gyroid", "Diamond": "diamond", "Schwarz P": "schwarz_p"}
MODE_LABELS = ("Surface", "Spline Layers")


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
        obj.Mode = "Surface"

        for name, default in (
            ("CellsX", 1),
            ("CellsY", 1),
            ("CellsZ", 1),
            ("Resolution", 36),
            ("BSplineLayers", 36),
        ):
            obj.addProperty("App::PropertyInteger", name, "TPMS", name)
            setattr(obj, name, default)

        for name, default in (
            ("CellScaleX", 1.0),
            ("CellScaleY", 1.0),
            ("CellScaleZ", 1.0),
            ("IsoValue", 0.0),
        ):
            obj.addProperty("App::PropertyFloat", name, "TPMS", name)
            setattr(obj, name, default)

    def execute(self, obj):
        bspline_layers = getattr(obj, "BSplineLayers", getattr(obj, "SliceCount", 36))
        config = TPMSConfig(
            family=FAMILY_TO_KEY.get(obj.Family, "schwarz_p"),
            cells=(max(1, obj.CellsX), max(1, obj.CellsY), max(1, obj.CellsZ)),
            scale=(obj.CellScaleX, obj.CellScaleY, obj.CellScaleZ),
            resolution=max(12, obj.Resolution),
            bspline_layers=max(2, bspline_layers),
            isovalue=obj.IsoValue,
            mode="splines" if obj.Mode == "Spline Layers" else "surface",
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
