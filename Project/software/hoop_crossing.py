from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HoopCrossingResult:
    plane_crossing_exists: bool
    passes_through_hoop: bool
    crossing_time: float | None
    crossing_point: np.ndarray | None
    radial_error: float | None
    effective_tolerance: float
    signed_distance_before: float | None
    signed_distance_after: float | None
    reason: str


def evaluate_hoop_crossing(
    times: np.ndarray,
    ball_positions: np.ndarray,
    hoop_center: np.ndarray,
    hoop_normal: np.ndarray,
    hoop_radius: float,
    ball_radius: float,
) -> HoopCrossingResult:
    times = np.asarray(times, dtype=float)
    ball_positions = np.asarray(ball_positions, dtype=float)
    hoop_center = np.asarray(hoop_center, dtype=float).reshape(3)
    hoop_normal = np.asarray(hoop_normal, dtype=float).reshape(3)
    normal_norm = float(np.linalg.norm(hoop_normal))
    if normal_norm == 0.0:
        raise ValueError("hoop_normal must be nonzero")
    hoop_normal = hoop_normal / normal_norm
    _validate_inputs(times, ball_positions)

    effective_tolerance = float(hoop_radius - ball_radius)
    signed_distances = (ball_positions - hoop_center.reshape(1, 3)) @ hoop_normal
    crossing_index = _first_crossing_index(signed_distances)
    if crossing_index is None:
        return HoopCrossingResult(
            plane_crossing_exists=False,
            passes_through_hoop=False,
            crossing_time=None,
            crossing_point=None,
            radial_error=None,
            effective_tolerance=effective_tolerance,
            signed_distance_before=None,
            signed_distance_after=None,
            reason="no_plane_crossing",
        )

    i = crossing_index
    before = float(signed_distances[i])
    after = float(signed_distances[i + 1])
    alpha = _crossing_alpha(before, after)
    crossing_time = float(times[i] + alpha * (times[i + 1] - times[i]))
    crossing_point = ball_positions[i] + alpha * (ball_positions[i + 1] - ball_positions[i])
    radial_vector = crossing_point - hoop_center
    radial_vector = radial_vector - float(radial_vector @ hoop_normal) * hoop_normal
    radial_error = float(np.linalg.norm(radial_vector))
    passes = bool(radial_error <= effective_tolerance + 1e-12)
    return HoopCrossingResult(
        plane_crossing_exists=True,
        passes_through_hoop=passes,
        crossing_time=crossing_time,
        crossing_point=crossing_point,
        radial_error=radial_error,
        effective_tolerance=effective_tolerance,
        signed_distance_before=before,
        signed_distance_after=after,
        reason="passes_through_hoop" if passes else "outside_effective_radius",
    )


def _validate_inputs(times: np.ndarray, ball_positions: np.ndarray):
    if times.ndim != 1:
        raise ValueError("times must be a 1D array")
    if ball_positions.ndim != 2 or ball_positions.shape[1] != 3:
        raise ValueError("ball_positions must have shape (N, 3)")
    if len(times) != len(ball_positions):
        raise ValueError("times and ball_positions must have the same length")
    if len(times) < 2:
        raise ValueError("at least two samples are required")


def _first_crossing_index(signed_distances: np.ndarray) -> int | None:
    for index in range(len(signed_distances) - 1):
        before = signed_distances[index]
        after = signed_distances[index + 1]
        if before == 0.0 or before * after <= 0.0:
            return index
    return None


def _crossing_alpha(before: float, after: float) -> float:
    denominator = before - after
    if abs(denominator) < 1e-12:
        return 0.0
    return float(before / denominator)
