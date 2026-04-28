from dataclasses import dataclass
from statistics import mean, stdev

import numpy as np


@dataclass(frozen=True)
class CandidateEvaluation:
    seed: int
    index: int
    time: float
    position: np.ndarray
    geometric_status: str
    nlp_success: bool
    passes_hoop: bool
    terminal_error: float
    max_abs_ddq: float
    max_velocity_ratio: float
    safety_penalty: float
    solver_status: str
    plane_crossing_exists: bool = False
    crossing_time: float | None = None
    radial_error: float | None = None
    effective_tolerance: float | None = None
    crossing_reason: str = ""
    min_tcp_table_clearance: float | None = None
    min_frame_table_clearance: float | None = None
    min_self_sphere_clearance: float | None = None
    ring_top_faces_ground: bool = False

    @property
    def success(self) -> bool:
        return bool(self.nlp_success and self.passes_hoop and self.safety_penalty == 0.0)


@dataclass(frozen=True)
class StrategySelection:
    strategy: str
    success: bool
    selected_index: int | None
    selected_time: float | None
    selected_terminal_error: float | None
    selected_max_abs_ddq: float | None
    selected_max_velocity_ratio: float | None
    selected_solver_status: str | None
    selected_crossing_time: float | None
    selected_radial_error: float | None
    selected_effective_tolerance: float | None
    selected_min_tcp_table_clearance: float | None
    selected_min_frame_table_clearance: float | None
    selected_min_self_sphere_clearance: float | None
    selected_ring_top_faces_ground: bool | None
    reason: str
    candidate_pool_size: int

    def to_row(self, seed: int) -> dict:
        return {
            "seed": int(seed),
            "strategy": self.strategy,
            "success": bool(self.success),
            "selected_index": self.selected_index,
            "catch_time_s": self.selected_time,
            "terminal_error_m": self.selected_terminal_error,
            "max_abs_ddq": self.selected_max_abs_ddq,
            "max_velocity_ratio": self.selected_max_velocity_ratio,
            "solver_status": self.selected_solver_status,
            "crossing_time_s": self.selected_crossing_time,
            "radial_error_m": self.selected_radial_error,
            "effective_tolerance_m": self.selected_effective_tolerance,
            "min_tcp_table_clearance_m": self.selected_min_tcp_table_clearance,
            "min_frame_table_clearance_m": self.selected_min_frame_table_clearance,
            "min_self_sphere_clearance_m": self.selected_min_self_sphere_clearance,
            "ring_top_faces_ground": self.selected_ring_top_faces_ground,
            "reason": self.reason,
            "candidate_pool_size": self.candidate_pool_size,
        }


def select_simple_geometric(candidates: list[CandidateEvaluation]) -> StrategySelection:
    accepted = [candidate for candidate in candidates if candidate.geometric_status == "accepted"]
    if not accepted:
        return _empty_selection("simple_geometric", "no_geometric_candidate", len(candidates))
    selected = min(accepted, key=lambda candidate: candidate.time)
    return _selection("simple_geometric", selected, len(candidates), "selected_earliest_geometric")


def select_earliest_nlp_feasible(candidates: list[CandidateEvaluation]) -> StrategySelection:
    feasible = [candidate for candidate in candidates if candidate.geometric_status == "accepted" and candidate.success]
    if not feasible:
        return _best_failed_selection("earliest_nlp_feasible", candidates)
    selected = min(feasible, key=lambda candidate: candidate.time)
    return _selection("earliest_nlp_feasible", selected, len(candidates), "selected_earliest_feasible")


def select_smart_cost(candidates: list[CandidateEvaluation]) -> StrategySelection:
    feasible = [candidate for candidate in candidates if candidate.geometric_status == "accepted" and candidate.success]
    if not feasible:
        return _best_failed_selection("smart_cost", candidates)
    selected = min(feasible, key=_smart_cost)
    return _selection("smart_cost", selected, len(candidates), "selected_lowest_cost")


def summarize_strategy_rows(rows: list[dict]) -> dict:
    summary = {}
    for strategy in sorted({row["strategy"] for row in rows}):
        selected = [row for row in rows if row["strategy"] == strategy]
        successful = [row for row in selected if row["success"]]
        summary[strategy] = {
            "n": len(selected),
            "success_count": len(successful),
            "success_rate": len(successful) / len(selected) if selected else 0.0,
            "mean_attempt_catch_time_s": _mean(selected, "catch_time_s"),
            "std_attempt_catch_time_s": _std(selected, "catch_time_s"),
            "mean_success_catch_time_s": _mean(successful, "catch_time_s"),
            "std_success_catch_time_s": _std(successful, "catch_time_s"),
            "mean_success_terminal_error_m": _mean(successful, "terminal_error_m"),
            "std_success_terminal_error_m": _std(successful, "terminal_error_m"),
            "mean_success_radial_error_m": _mean(successful, "radial_error_m"),
            "std_success_radial_error_m": _std(successful, "radial_error_m"),
            "mean_success_max_abs_ddq": _mean(successful, "max_abs_ddq"),
            "mean_success_max_velocity_ratio": _mean(successful, "max_velocity_ratio"),
            "min_success_tcp_table_clearance_m": _min(successful, "min_tcp_table_clearance_m"),
            "min_success_frame_table_clearance_m": _min(successful, "min_frame_table_clearance_m"),
            "min_success_self_sphere_clearance_m": _min(successful, "min_self_sphere_clearance_m"),
            "failure_count": len(selected) - len(successful),
        }
    return summary


def _smart_cost(candidate: CandidateEvaluation) -> float:
    return (
        0.20 * candidate.time
        + 100.0 * candidate.terminal_error
        + 0.20 * candidate.max_abs_ddq
        + 0.20 * candidate.max_velocity_ratio
        + 50.0 * candidate.safety_penalty
    )


def _selection(strategy: str, selected: CandidateEvaluation, pool_size: int, reason: str) -> StrategySelection:
    return StrategySelection(
        strategy=strategy,
        success=selected.success,
        selected_index=selected.index,
        selected_time=float(selected.time),
        selected_terminal_error=float(selected.terminal_error),
        selected_max_abs_ddq=float(selected.max_abs_ddq),
        selected_max_velocity_ratio=float(selected.max_velocity_ratio),
        selected_solver_status=selected.solver_status,
        selected_crossing_time=selected.crossing_time,
        selected_radial_error=selected.radial_error,
        selected_effective_tolerance=selected.effective_tolerance,
        selected_min_tcp_table_clearance=selected.min_tcp_table_clearance,
        selected_min_frame_table_clearance=selected.min_frame_table_clearance,
        selected_min_self_sphere_clearance=selected.min_self_sphere_clearance,
        selected_ring_top_faces_ground=selected.ring_top_faces_ground,
        reason=reason,
        candidate_pool_size=pool_size,
    )


def _empty_selection(strategy: str, reason: str, pool_size: int) -> StrategySelection:
    return StrategySelection(
        strategy,
        False,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        reason,
        pool_size,
    )


def _best_failed_selection(strategy: str, candidates: list[CandidateEvaluation]) -> StrategySelection:
    accepted = [candidate for candidate in candidates if candidate.geometric_status == "accepted"]
    if not accepted:
        return _empty_selection(strategy, "no_geometric_candidate", len(candidates))
    selected = min(accepted, key=lambda candidate: (candidate.terminal_error, candidate.time))
    return _selection(strategy, selected, len(candidates), "no_feasible_candidate")


def _mean(rows: list[dict], key: str):
    values = _finite_values(rows, key)
    return None if not values else float(mean(values))


def _std(rows: list[dict], key: str):
    values = _finite_values(rows, key)
    return 0.0 if len(values) == 1 else (None if not values else float(stdev(values)))


def _min(rows: list[dict], key: str):
    values = _finite_values(rows, key)
    return None if not values else float(min(values))


def _finite_values(rows: list[dict], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if value is not None and np.isfinite(value):
            values.append(float(value))
    return values
