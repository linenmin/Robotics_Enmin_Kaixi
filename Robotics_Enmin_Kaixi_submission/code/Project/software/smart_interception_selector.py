from dataclasses import dataclass

import numpy as np

from interception_selector import SimpleInterceptionSelector
from trajectory_predictor import TrajectoryPrediction


@dataclass(frozen=True)
class CandidateScore:
    index: int
    time: float
    position: np.ndarray
    status: str
    score: float
    terminal_error: float
    max_abs_ddq: float
    max_velocity_ratio: float
    safety_metrics: dict
    solver_status: str
    feasible: bool


@dataclass(frozen=True)
class PlannerEvaluation:
    success: bool
    status: str
    terminal_error: float
    max_abs_ddq: float
    max_velocity_ratio: float
    safety_metrics: dict


@dataclass(frozen=True)
class SmartInterceptionResult:
    success: bool
    time: float | None
    position: np.ndarray | None
    index: int | None
    reason: str
    selected: CandidateScore | None
    candidates: list[CandidateScore]


class SmartInterceptionSelector:
    """Ranks interception candidates with geometric filtering and planner feedback."""

    def __init__(
        self,
        current_time: float,
        planner,
        q0: np.ndarray,
        dq0: np.ndarray,
        min_lead_time: float = 0.20,
        z_min: float = 0.35,
        workspace_center: np.ndarray | None = None,
        max_workspace_distance: float | None = None,
        max_candidates: int | None = None,
        success_tolerance: float = 0.03,
        time_weight: float = 0.20,
        terminal_error_weight: float = 100.0,
        acceleration_weight: float = 0.20,
        velocity_weight: float = 0.20,
        safety_penalty_weight: float = 50.0,
    ):
        self.current_time = float(current_time)
        self.planner = planner
        self.q0 = np.asarray(q0, dtype=float)
        self.dq0 = np.asarray(dq0, dtype=float)
        self.max_candidates = None if max_candidates is None else int(max_candidates)
        self.success_tolerance = float(success_tolerance)
        self.time_weight = float(time_weight)
        self.terminal_error_weight = float(terminal_error_weight)
        self.acceleration_weight = float(acceleration_weight)
        self.velocity_weight = float(velocity_weight)
        self.safety_penalty_weight = float(safety_penalty_weight)
        self.workspace_center = None if workspace_center is None else np.asarray(workspace_center, dtype=float)
        self.geometric_selector = SimpleInterceptionSelector(
            current_time=current_time,
            min_lead_time=min_lead_time,
            z_min=z_min,
            workspace_center=workspace_center,
            max_workspace_distance=max_workspace_distance,
        )

    def select(self, prediction: TrajectoryPrediction) -> SmartInterceptionResult:
        SimpleInterceptionSelector._validate_prediction(prediction)
        geometric_candidates = self._geometric_candidates(prediction)
        if not geometric_candidates:
            return SmartInterceptionResult(False, None, None, None, "no_geometric_candidate", None, [])

        scores = []
        for candidate in geometric_candidates:
            plan = self.planner.evaluate_candidate(self.q0, self.dq0, candidate.time, candidate.position)
            scores.append(self._score_candidate(candidate, plan))

        selected = min(scores, key=lambda item: (not item.feasible, item.score, item.time))
        success = bool(selected.feasible)
        reason = "selected_feasible_candidate" if success else "no_feasible_candidate"
        return SmartInterceptionResult(
            success=success,
            time=selected.time,
            position=selected.position.copy(),
            index=selected.index,
            reason=reason,
            selected=selected,
            candidates=scores,
        )

    def _geometric_candidates(self, prediction: TrajectoryPrediction):
        candidates = []
        for index, (time, position) in enumerate(zip(prediction.times, prediction.positions, strict=True)):
            status = self.geometric_selector._candidate_status(float(time), position)
            if status == "accepted":
                candidates.append(_GeometricCandidate(index, float(time), position.copy()))
        if self.max_candidates is None:
            return candidates
        return sorted(candidates, key=self._geometric_rank)[: self.max_candidates]

    def _geometric_rank(self, candidate) -> tuple[float, float]:
        if self.workspace_center is None:
            return (candidate.time, 0.0)
        distance = float(np.linalg.norm(candidate.position - self.workspace_center))
        return (distance, candidate.time)

    def _score_candidate(self, candidate, plan) -> CandidateScore:
        terminal_error = float(plan.terminal_error)
        max_abs_ddq = float(plan.max_abs_ddq)
        max_velocity_ratio = float(plan.max_velocity_ratio)
        safety_metrics = dict(plan.safety_metrics)
        safety_penalty = self._safety_penalty(safety_metrics)
        feasible = bool(plan.success and terminal_error <= self.success_tolerance and safety_penalty == 0.0)
        score = (
            self.terminal_error_weight * terminal_error
            + self.time_weight * candidate.time
            + self.acceleration_weight * max_abs_ddq
            + self.velocity_weight * max_velocity_ratio
            + self.safety_penalty_weight * safety_penalty
        )
        if not feasible:
            score += 1_000.0
        return CandidateScore(
            index=candidate.index,
            time=candidate.time,
            position=candidate.position.copy(),
            status="feasible" if feasible else "infeasible",
            score=float(score),
            terminal_error=terminal_error,
            max_abs_ddq=max_abs_ddq,
            max_velocity_ratio=max_velocity_ratio,
            safety_metrics=safety_metrics,
            solver_status=str(plan.status),
            feasible=feasible,
        )

    @staticmethod
    def _safety_penalty(safety_metrics: dict) -> float:
        penalty = 0.0
        tcp_clearance = float(safety_metrics.get("min_tcp_table_clearance_m", 0.0))
        frame_clearance = float(safety_metrics.get("min_frame_table_clearance_m", 0.0))
        self_clearance = float(safety_metrics.get("min_self_sphere_clearance_m", 0.0))
        if safety_metrics.get("ring_top_faces_ground", False):
            penalty += 1.0
        penalty += max(0.0, -tcp_clearance)
        penalty += max(0.0, -frame_clearance)
        penalty += max(0.0, -self_clearance)
        return float(penalty)


@dataclass(frozen=True)
class _GeometricCandidate:
    index: int
    time: float
    position: np.ndarray


class NLPPlannerEvaluator:
    """Adapts a time-indexed NLP controller to the selector scoring API."""

    def __init__(self, controller_factory, velocity_limits: np.ndarray, safety_evaluator):
        self.controller_factory = controller_factory
        self.velocity_limits = np.asarray(velocity_limits, dtype=float)
        self.safety_evaluator = safety_evaluator

    def evaluate_candidate(self, q0: np.ndarray, dq0: np.ndarray, time: float, position: np.ndarray) -> PlannerEvaluation:
        controller = self.controller_factory(float(time))
        result = controller.plan(q0=np.asarray(q0, dtype=float), dq0=np.asarray(dq0, dtype=float), target_position=np.asarray(position, dtype=float))
        max_abs_ddq = float(np.max(np.abs(result.ddq)))
        max_velocity_ratio = float(np.max(np.abs(result.dq) / self.velocity_limits.reshape(1, -1)))
        return PlannerEvaluation(
            success=bool(result.success),
            status=str(result.status),
            terminal_error=float(result.terminal_error),
            max_abs_ddq=max_abs_ddq,
            max_velocity_ratio=max_velocity_ratio,
            safety_metrics=dict(self.safety_evaluator(result.q)),
        )
