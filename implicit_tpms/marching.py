"""Isosurface extraction for the FreeCAD workbench."""

from __future__ import annotations

import numpy as np


def marching_cubes(volume: np.ndarray, level: float, spacing: tuple[float, float, float]):
    """Return vertices and triangular faces for an isosurface.

    The preferred backend is scikit-image. A dependency-free marching tetrahedra
    fallback keeps the workbench usable in plain FreeCAD Python environments.
    """
    try:
        from skimage.measure import marching_cubes as sk_marching_cubes

        vertices, faces, _normals, _values = sk_marching_cubes(
            volume.astype(np.float32, copy=False),
            level=level,
            spacing=spacing,
            allow_degenerate=False,
        )
        return vertices, faces.astype(np.int64, copy=False)
    except Exception:
        return marching_tetrahedra(volume, level, spacing)


_CUBE_POINTS = np.array(
    (
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 1, 1),
    ),
    dtype=float,
)

_CUBE_INDEX = _CUBE_POINTS.astype(int)

_TETS = (
    (0, 5, 1, 6),
    (0, 1, 2, 6),
    (0, 2, 3, 6),
    (0, 3, 7, 6),
    (0, 7, 4, 6),
    (0, 4, 5, 6),
)


def _interpolate(p0, p1, v0, v1, level):
    denom = v1 - v0
    t = 0.5 if abs(denom) < 1e-12 else (level - v0) / denom
    return p0 + np.clip(t, 0.0, 1.0) * (p1 - p0)


def _emit_tet(vertices, faces, points, values, level):
    inside = [idx for idx, value in enumerate(values) if value < level]
    outside = [idx for idx, value in enumerate(values) if value >= level]
    if not inside or len(inside) == 4:
        return

    def add_triangle(triangle):
        start = len(vertices)
        vertices.extend(triangle)
        faces.append((start, start + 1, start + 2))

    if len(inside) == 1:
        a = inside[0]
        tri = [_interpolate(points[a], points[b], values[a], values[b], level) for b in outside]
        add_triangle(tri)
    elif len(inside) == 3:
        a = outside[0]
        tri = [_interpolate(points[a], points[b], values[a], values[b], level) for b in inside]
        add_triangle((tri[0], tri[2], tri[1]))
    else:
        a, b = inside
        c, d = outside
        p_ac = _interpolate(points[a], points[c], values[a], values[c], level)
        p_ad = _interpolate(points[a], points[d], values[a], values[d], level)
        p_bc = _interpolate(points[b], points[c], values[b], values[c], level)
        p_bd = _interpolate(points[b], points[d], values[b], values[d], level)
        add_triangle((p_ac, p_bc, p_bd))
        add_triangle((p_ac, p_bd, p_ad))


def marching_tetrahedra(volume: np.ndarray, level: float, spacing: tuple[float, float, float]):
    """Dependency-free isosurface extractor used when scikit-image is absent."""
    volume = np.asarray(volume, dtype=float)
    nx, ny, nz = volume.shape
    spacing_array = np.asarray(spacing, dtype=float)
    vertices: list[np.ndarray] = []
    faces: list[tuple[int, int, int]] = []

    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                cube_values = np.array(
                    [volume[i + di, j + dj, k + dk] for di, dj, dk in _CUBE_INDEX],
                    dtype=float,
                )
                if np.all(cube_values < level) or np.all(cube_values >= level):
                    continue

                origin = np.array((i, j, k), dtype=float) * spacing_array
                cube_points = origin + _CUBE_POINTS * spacing_array
                for tet in _TETS:
                    tet_points = cube_points[list(tet)]
                    tet_values = cube_values[list(tet)]
                    _emit_tet(vertices, faces, tet_points, tet_values, level)

    if not vertices:
        return np.empty((0, 3), dtype=float), np.empty((0, 3), dtype=np.int64)
    return np.asarray(vertices, dtype=float), np.asarray(faces, dtype=np.int64)
