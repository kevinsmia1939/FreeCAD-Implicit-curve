"""FreeCAD GUI entry point for the Implicit TPMS workbench."""

import os
import sys

import FreeCADGui


def _module_dir():
    path = globals().get("__file__")
    if path:
        return os.path.dirname(os.path.abspath(path))

    for base in [os.getcwd(), *sys.path]:
        if not base:
            continue
        candidate = os.path.abspath(base)
        if os.path.isdir(os.path.join(candidate, "implicit_tpms")):
            return candidate
    return ""


class ImplicitTPMSWorkbench(Workbench):
    MenuText = "Implicit TPMS"
    ToolTip = "Create implicit TPMS surfaces and solids as native Part shapes"

    def Initialize(self):
        from implicit_tpms.commands import register_commands

        register_commands()
        commands = [
            "ImplicitTPMS_CreateSchwarzP",
            "ImplicitTPMS_CreateGyroid",
            "ImplicitTPMS_CreateDiamond",
            "ImplicitTPMS_Recompute",
        ]
        self.appendToolbar("Implicit TPMS", commands)
        self.appendMenu("Implicit TPMS", commands)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def GetClassName(self):
        return "Gui::PythonWorkbench"


_icon_dir = _module_dir()
ImplicitTPMSWorkbench.Icon = (
    os.path.join(_icon_dir, "implicit_tpms", "icons", "workbench.svg")
    if _icon_dir
    else ""
)

FreeCADGui.addWorkbench(ImplicitTPMSWorkbench())
