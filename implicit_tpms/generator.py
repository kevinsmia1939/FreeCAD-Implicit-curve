"""Generate FreeCAD Part shapes from implicit TPMS fields."""

from __future__ import annotations

import math

import numpy as np

from .config import TPMSConfig
from .implicit import evaluate_field
from .marching import marching_cubes


def _sample_field(config: TPMSConfig):
    cells = tuple(max(1, int(v)) for v in config.cells)
    resolution = max(12, int(config.resolution))
    counts = tuple(c * resolution + 1 for c in cells)
    sx, sy, sz = config.scale
    extent = (2.0 * math.pi * cells[0], 2.0 * math.pi * cells[1], 2.0 * math.pi * cells[2])

    xs = np.linspace(0.0, extent[0], counts[0])
    ys = np.linspace(0.0, extent[1], counts[1])
    zs = np.linspace(0.0, extent[2], counts[2])
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    field = evaluate_field(config.family, x, y, z)

    spacing = (
        sx * extent[0] / max(1, counts[0] - 1),
        sy * extent[1] / max(1, counts[1] - 1),
        sz * extent[2] / max(1, counts[2] - 1),
    )
    return field, spacing


def _surface_volume(config: TPMSConfig):
    field, spacing = _sample_field(config)
    if config.mode == "solid":
        half_thickness = max(1e-6, abs(config.wall_thickness) * 0.5)
        volume = np.abs(field - config.isovalue) - half_thickness
        level = 0.0
    else:
        volume = field
        level = config.isovalue
    return volume, level, spacing


def generate_tpms_mesh(config: TPMSConfig):
    """Generate vertices and triangle indices for the configured TPMS."""
    volume, level, spacing = _surface_volume(config)
    vertices, faces = marching_cubes(volume, level, spacing)
    return vertices, faces


def generate_tpms_shape(config: TPMSConfig):
    """Generate a native FreeCAD Part shape made from planar triangular faces."""
    import Part
    from FreeCAD import Vector

    vertices, triangles = generate_tpms_mesh(config)
    faces = []
    for tri in triangles:
        points = [Vector(*vertices[index]) for index in tri]
        if (
            points[0].distanceToPoint(points[1]) <= 1e-9
            or points[1].distanceToPoint(points[2]) <= 1e-9
            or points[2].distanceToPoint(points[0]) <= 1e-9
        ):
            continue
        wire = Part.makePolygon([points[0], points[1], points[2], points[0]])
        try:
            faces.append(Part.Face(wire))
        except Exception:
            continue

    if not faces:
        raise RuntimeError("No TPMS faces were generated. Try a higher resolution or different isovalue.")

    shell = Part.Shell(faces)
    if config.mode == "solid":
        try:
            return Part.Solid(shell).removeSplitter()
        except Exception:
            return shell
    return shell.removeSplitter() if hasattr(shell, "removeSplitter") else shell
