"""Configuration objects for implicit TPMS generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TPMSFamily = Literal["gyroid", "diamond", "schwarz_p"]
OutputMode = Literal["surface", "splines"]


@dataclass(frozen=True)
class TPMSConfig:
    family: TPMSFamily = "schwarz_p"
    cells: tuple[int, int, int] = (1, 1, 1)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    resolution: int = 48
    bspline_layers: int = 48
    isovalue: float = 0.0
    mode: OutputMode = "surface"
