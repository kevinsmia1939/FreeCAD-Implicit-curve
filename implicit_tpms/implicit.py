"""Implicit TPMS scalar fields."""

from __future__ import annotations

import numpy as np


def evaluate_field(family: str, x, y, z):
    """Evaluate a normalized TPMS implicit field on arrays."""
    if family == "gyroid":
        return (
            np.sin(x) * np.cos(y)
            + np.sin(y) * np.cos(z)
            + np.sin(z) * np.cos(x)
        )
    if family == "diamond":
        return (
            np.sin(x) * np.sin(y) * np.sin(z)
            + np.sin(x) * np.cos(y) * np.cos(z)
            + np.cos(x) * np.sin(y) * np.cos(z)
            + np.cos(x) * np.cos(y) * np.sin(z)
        )
    if family == "schwarz_p":
        return np.cos(x) + np.cos(y) + np.cos(z)
    raise ValueError(f"Unsupported TPMS family: {family!r}")

