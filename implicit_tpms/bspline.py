"""B-spline utilities matching the TPMS2STEP reimplementation spec."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BSplineSurfaceSpec:
    control_points: np.ndarray
    degree_u: int
    degree_v: int
    knots_u: np.ndarray
    knots_v: np.ndarray
    multiplicities_u: np.ndarray | None = None
    multiplicities_v: np.ndarray | None = None


def clamped_uniform_knot(num_ctrl: int, degree: int = 3) -> np.ndarray:
    if num_ctrl <= degree:
        raise ValueError("num_ctrl must be greater than degree")
    knots = [0.0] * (degree + 1)
    interior_count = num_ctrl - degree - 1
    for i in range(1, interior_count + 1):
        knots.append(i / (interior_count + 1))
    knots += [1.0] * (degree + 1)
    return np.array(knots, dtype=float)


def find_span(degree: int, n: int, t: float, knots: np.ndarray) -> int:
    if abs(t - knots[n + 1]) <= 1e-12:
        return n
    low = degree
    high = n + 1
    while high - low > 1:
        mid = (high + low) >> 1
        if t < knots[mid] - 1e-7:
            high = mid
        else:
            low = mid
    return low


def basis_functions(degree: int, span: int, t: float, knots: np.ndarray) -> np.ndarray:
    basis = np.zeros(degree + 1, dtype=float)
    left = np.zeros(degree + 1, dtype=float)
    right = np.zeros(degree + 1, dtype=float)
    basis[0] = 1.0
    for j in range(1, degree + 1):
        left[j] = t - knots[span + 1 - j]
        right[j] = knots[span + j] - t
        saved = 0.0
        for r in range(j):
            denom = right[r + 1] + left[j - r]
            temp = 0.0 if abs(denom) < 1e-14 else basis[r] / denom
            basis[r] = saved + right[r + 1] * temp
            saved = left[j - r] * temp
        basis[j] = saved
    return basis


def evaluate_surface_grid(
    control_points: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    knots_u: np.ndarray,
    knots_v: np.ndarray,
    degree_u: int = 3,
    degree_v: int = 3,
) -> np.ndarray:
    control_points = np.asarray(control_points, dtype=float)
    u = np.asarray(u, dtype=float).reshape(-1)
    v = np.asarray(v, dtype=float).reshape(-1)
    if u.shape != v.shape:
        raise ValueError("u and v arrays must have the same shape")

    nu = control_points.shape[0] - 1
    nv = control_points.shape[1] - 1
    result = np.zeros((u.size, 3), dtype=float)
    for index, (ui, vi) in enumerate(zip(u, v)):
        span_u = find_span(degree_u, nu, ui, knots_u)
        span_v = find_span(degree_v, nv, vi, knots_v)
        bu = basis_functions(degree_u, span_u, ui, knots_u)
        bv = basis_functions(degree_v, span_v, vi, knots_v)
        point = np.zeros(3, dtype=float)
        for lu in range(degree_u + 1):
            iu = span_u - degree_u + lu
            for lv in range(degree_v + 1):
                iv = span_v - degree_v + lv
                point += bu[lu] * bv[lv] * control_points[iu, iv]
        result[index] = point
    return result

