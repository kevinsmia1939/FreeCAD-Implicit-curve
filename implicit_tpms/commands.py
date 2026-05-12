"""FreeCAD GUI commands for the implicit TPMS workbench."""

from __future__ import annotations

import FreeCAD
import FreeCADGui

from .feature import ImplicitTPMSFeature, ImplicitTPMSViewProvider


def _make_object(family: str):
    doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("ImplicitTPMS")
    obj = doc.addObject("Part::FeaturePython", f"Implicit_{family.replace(' ', '_')}")
    ImplicitTPMSFeature(obj)
    obj.Family = family
    if FreeCAD.GuiUp:
        ImplicitTPMSViewProvider(obj.ViewObject)
    doc.recompute()
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    return obj


class _CreateTPMSCommand:
    def __init__(self, family: str):
        self.family = family

    def GetResources(self):
        return {
            "MenuText": f"Create {self.family}",
            "ToolTip": f"Create a {self.family} implicit TPMS feature",
            "Pixmap": "",
        }

    def Activated(self):
        _make_object(self.family)

    def IsActive(self):
        return True


class _RecomputeCommand:
    def GetResources(self):
        return {
            "MenuText": "Recompute TPMS",
            "ToolTip": "Recompute the active document",
            "Pixmap": "",
        }

    def Activated(self):
        if FreeCAD.ActiveDocument:
            FreeCAD.ActiveDocument.recompute()

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


def register_commands():
    FreeCADGui.addCommand("ImplicitTPMS_CreateSchwarzP", _CreateTPMSCommand("Schwarz P"))
    FreeCADGui.addCommand("ImplicitTPMS_CreateGyroid", _CreateTPMSCommand("Gyroid"))
    FreeCADGui.addCommand("ImplicitTPMS_CreateDiamond", _CreateTPMSCommand("Diamond"))
    FreeCADGui.addCommand("ImplicitTPMS_Recompute", _RecomputeCommand())

