"""Configuration objects for implicit TPMS generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TPMSFamily = Literal["gyroid", "diamond", "schwarz_p"]
OutputMode = Literal["surface", "solid"]


@dataclass(frozen=True)
class TPMSConfig:
    family: TPMSFamily = "schwarz_p"
    cells: tuple[int, int, int] = (1, 1, 1)
    offset_plus: float = 0.1
    offset_minus: float = 0.0
    tolerance: float = 0.005
    max_error_iterations: int = 1
    min_control_points_per_edge: int = 10
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    degree_u: int = 3
    degree_v: int = 3
    resolution: int = 48
    isovalue: float = 0.0
    wall_thickness: float = 0.12
    mode: OutputMode = "solid"
    sewing_tolerance: float = 1e-3

