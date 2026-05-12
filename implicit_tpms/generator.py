"""Generate FreeCAD Part shapes from stacked implicit TPMS contour curves."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .config import TPMSConfig
from .implicit import evaluate_field


@dataclass(frozen=True)
class _Contour:
    points: np.ndarray
    centroid: np.ndarray
    area: float
    closed: bool


_EDGE_ENDPOINTS = (
    ((0, 0), (1, 0)),
    ((1, 0), (1, 1)),
    ((1, 1), (0, 1)),
    ((0, 1), (0, 0)),
)


def _domain(config: TPMSConfig):
    cells = tuple(max(1, int(value)) for value in config.cells)
    scale = tuple(float(value) for value in config.scale)
    extent = tuple(2.0 * math.pi * cells[index] for index in range(3))
    return cells, scale, extent


def _interpolate_edge(p0, p1, v0, v1, level):
    denom = v1 - v0
    t = 0.5 if abs(denom) <= 1e-12 else (level - v0) / denom
    return p0 + np.clip(t, 0.0, 1.0) * (p1 - p0)


def _slice_segments(config: TPMSConfig, z_value: float, samples: int):
    _cells, scale, extent = _domain(config)
    xs = np.linspace(0.0, extent[0], samples)
    ys = np.linspace(0.0, extent[1], samples)
    x_grid, y_grid = np.meshgrid(xs, ys, indexing="ij")
    field = evaluate_field(config.family, x_grid, y_grid, z_value)

    segments = []
    for i in range(samples - 1):
        for j in range(samples - 1):
            values = np.array(
                (
                    field[i, j],
                    field[i + 1, j],
                    field[i + 1, j + 1],
                    field[i, j + 1],
                ),
                dtype=float,
            )
            if np.all(values < config.isovalue) or np.all(values >= config.isovalue):
                continue

            corners = np.array(
                (
                    (xs[i] * scale[0], ys[j] * scale[1], z_value * scale[2]),
                    (xs[i + 1] * scale[0], ys[j] * scale[1], z_value * scale[2]),
                    (xs[i + 1] * scale[0], ys[j + 1] * scale[1], z_value * scale[2]),
                    (xs[i] * scale[0], ys[j + 1] * scale[1], z_value * scale[2]),
                ),
                dtype=float,
            )

            points = []
            for edge_index, (start, end) in enumerate(_EDGE_ENDPOINTS):
                start_index = edge_index
                end_index = (edge_index + 1) % 4
                start_inside = values[start_index] < config.isovalue
                end_inside = values[end_index] < config.isovalue
                if start_inside == end_inside:
                    continue
                points.append(
                    _interpolate_edge(
                        corners[start_index],
                        corners[end_index],
                        values[start_index],
                        values[end_index],
                        config.isovalue,
                    )
                )

            if len(points) == 2:
                segments.append((points[0], points[1]))
            elif len(points) == 4:
                center_value = float(values.mean())
                if center_value < config.isovalue:
                    segments.append((points[0], points[1]))
                    segments.append((points[2], points[3]))
                else:
                    segments.append((points[0], points[3]))
                    segments.append((points[1], points[2]))

    return segments


def _point_key(point: np.ndarray, precision: int = 9):
    return tuple(np.round(point, precision))


def _stitch_segments(segments):
    unused = [tuple(np.asarray(point, dtype=float) for point in segment) for segment in segments]
    polylines = []
    while unused:
        start, end = unused.pop()
        line = [start, end]
        changed = True
        while changed:
            changed = False
            first_key = _point_key(line[0])
            last_key = _point_key(line[-1])
            for index, (a, b) in enumerate(unused):
                a_key = _point_key(a)
                b_key = _point_key(b)
                if a_key == last_key:
                    line.append(b)
                elif b_key == last_key:
                    line.append(a)
                elif b_key == first_key:
                    line.insert(0, a)
                elif a_key == first_key:
                    line.insert(0, b)
                else:
                    continue
                unused.pop(index)
                changed = True
                break
        polylines.append(np.asarray(line, dtype=float))
    return polylines


def _polygon_area_xy(points: np.ndarray):
    x = points[:, 0]
    y = points[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _slice_contours(config: TPMSConfig, z_value: float, samples: int):
    contours = []
    for points in _stitch_segments(_slice_segments(config, z_value, samples)):
        if len(points) < 3:
            continue
        closed = np.linalg.norm(points[0] - points[-1]) <= 1e-7
        if closed:
            points = points[:-1]
        area = _polygon_area_xy(points) if closed and len(points) >= 3 else 0.0
        if closed and abs(area) <= 1e-7:
            continue
        contours.append(
            _Contour(
                points=points,
                centroid=points.mean(axis=0),
                area=area,
                closed=closed,
            )
        )
    return contours


def _resample(points: np.ndarray, count: int, closed: bool):
    chain = np.vstack((points, points[0])) if closed else points
    lengths = np.linalg.norm(np.diff(chain, axis=0), axis=1)
    perimeter = float(lengths.sum())
    if perimeter <= 1e-12:
        return np.repeat(points[:1], count, axis=0)

    cumulative = np.concatenate(([0.0], np.cumsum(lengths)))
    targets = np.linspace(0.0, perimeter, count, endpoint=not closed)
    result = []
    segment_index = 0
    for target in targets:
        while segment_index < len(lengths) - 1 and cumulative[segment_index + 1] < target:
            segment_index += 1
        segment_length = lengths[segment_index]
        t = 0.0 if segment_length <= 1e-12 else (target - cumulative[segment_index]) / segment_length
        result.append(chain[segment_index] + t * (chain[segment_index + 1] - chain[segment_index]))
    return np.asarray(result, dtype=float)


def _best_rotation(source: np.ndarray, target: np.ndarray):
    best_index = 0
    best_score = float("inf")
    for index in range(len(target)):
        score = float(np.linalg.norm(source - np.roll(target, -index, axis=0), axis=1).sum())
        if score < best_score:
            best_score = score
            best_index = index
    rotated = np.roll(target, -best_index, axis=0)
    reversed_target = target[::-1]
    for index in range(len(reversed_target)):
        candidate = np.roll(reversed_target, -index, axis=0)
        score = float(np.linalg.norm(source - candidate, axis=1).sum())
        if score < best_score:
            best_score = score
            rotated = candidate
    return rotated


def _match_contours(lower: list[_Contour], upper: list[_Contour], max_distance: float):
    matches = []
    used = set()
    for lower_contour in lower:
        best_index = None
        best_score = float("inf")
        for index, upper_contour in enumerate(upper):
            if index in used:
                continue
            if lower_contour.closed != upper_contour.closed:
                continue
            distance = float(np.linalg.norm(lower_contour.centroid[:2] - upper_contour.centroid[:2]))
            if distance > max_distance:
                continue
            if lower_contour.closed:
                area_ratio = abs(abs(lower_contour.area) - abs(upper_contour.area)) / max(
                    abs(lower_contour.area),
                    abs(upper_contour.area),
                    1e-9,
                )
            else:
                area_ratio = 0.0
            score = distance + area_ratio * max_distance
            if score < best_score:
                best_score = score
                best_index = index
        if best_index is not None:
            used.add(best_index)
            matches.append((lower_contour, upper[best_index]))
    return matches


def _bspline_wire(points: np.ndarray, closed: bool):
    import Part
    from FreeCAD import Vector

    chain = np.vstack((points, points[0])) if closed else points
    vectors = [Vector(*point) for point in chain]
    if len(vectors) < 4:
        return Part.Wire([Part.makePolygon(vectors)])
    curve = Part.BSplineCurve()
    try:
        curve.interpolate(vectors)
        return Part.Wire([curve.toShape()])
    except Exception:
        return Part.Wire([Part.makePolygon(vectors)])


def _loft_pair(lower: _Contour, upper: _Contour, sample_count: int):
    import Part
    from FreeCAD import Vector

    lower_points = _resample(lower.points, sample_count, lower.closed)
    upper_points = _resample(upper.points, sample_count, upper.closed)
    if lower.closed:
        upper_points = _best_rotation(lower_points, upper_points)
    try:
        return Part.makeLoft(
            [_bspline_wire(lower_points, lower.closed), _bspline_wire(upper_points, upper.closed)],
            False,
            False,
            False,
        )
    except Exception:
        faces = []
        face_count = sample_count if lower.closed else sample_count - 1
        for index in range(face_count):
            next_index = (index + 1) % sample_count
            quad = [
                Vector(*lower_points[index]),
                Vector(*lower_points[next_index]),
                Vector(*upper_points[next_index]),
                Vector(*upper_points[index]),
                Vector(*lower_points[index]),
            ]
            try:
                faces.append(Part.Face(Part.makePolygon(quad)))
            except Exception:
                continue
        if not faces:
            raise
        return Part.Shell(faces)


def generate_tpms_shape(config: TPMSConfig):
    """Generate a native FreeCAD shape by lofting stacked implicit contours."""
    import Part

    _cells, scale, extent = _domain(config)
    samples = max(16, int(config.resolution))
    slice_count = max(4, int(config.slice_count))
    z_values = np.linspace(0.0, extent[2], slice_count)
    contours_by_slice = [_slice_contours(config, z_value, samples) for z_value in z_values]

    max_step = max(extent[0] * scale[0], extent[1] * scale[1]) / max(4.0, samples / 2.0)
    shapes = []
    sample_count = min(96, max(24, samples * 2))
    for lower, upper in zip(contours_by_slice, contours_by_slice[1:]):
        for lower_contour, upper_contour in _match_contours(lower, upper, max_step):
            try:
                shapes.append(_loft_pair(lower_contour, upper_contour, sample_count))
            except Exception:
                continue

    if not shapes:
        raise RuntimeError(
            "No TPMS contour surfaces were generated. Try a higher resolution or a different isovalue."
        )

    if len(shapes) == 1:
        return shapes[0]

    compound = Part.Compound(shapes)
    if hasattr(compound, "removeSplitter"):
        try:
            return compound.removeSplitter()
        except Exception:
            return compound
    return compound
