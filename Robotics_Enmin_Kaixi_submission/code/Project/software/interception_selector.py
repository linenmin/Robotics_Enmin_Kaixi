from dataclasses import dataclass

import numpy as np

from trajectory_predictor import TrajectoryPrediction


@dataclass(frozen=True)
class CandidateDecision:
    index: int
    time: float
    position: np.ndarray
    status: str


@dataclass(frozen=True)
class InterceptionPoint:
    success: bool
    time: float | None
    position: np.ndarray | None
    index: int | None
    reason: str
    candidates: list[CandidateDecision]


class SimpleInterceptionSelector:
    """Selects the earliest usable point on a predicted ball trajectory."""

    def __init__(
        self,
        current_time: float,
        min_lead_time: float = 0.20,
        z_min: float = 0.35,
        workspace_center: np.ndarray | None = None,
        max_workspace_distance: float | None = None,
    ):
        self.current_time = float(current_time)
        self.min_lead_time = float(min_lead_time)
        self.z_min = float(z_min)
        self.workspace_center = None if workspace_center is None else np.asarray(workspace_center, dtype=float)
        self.max_workspace_distance = None if max_workspace_distance is None else float(max_workspace_distance)

    def select(self, prediction: TrajectoryPrediction) -> InterceptionPoint:
        self._validate_prediction(prediction)
        candidate_decisions = []

        for index, (time, position) in enumerate(zip(prediction.times, prediction.positions, strict=True)):
            status = self._candidate_status(float(time), position)
            decision = CandidateDecision(index=index, time=float(time), position=position.copy(), status=status)
            candidate_decisions.append(decision)

            if status == "accepted":
                return InterceptionPoint(
                    success=True,
                    time=float(time),
                    position=position.copy(),
                    index=index,
                    reason="accepted",
                    candidates=candidate_decisions,
                )

        return InterceptionPoint(
            success=False,
            time=None,
            position=None,
            index=None,
            reason="no_candidate",
            candidates=candidate_decisions,
        )

    def _candidate_status(self, time: float, position: np.ndarray) -> str:
        if not np.isfinite(time) or not np.all(np.isfinite(position)):
            return "non_finite"

        if time <= self.current_time + self.min_lead_time:
            return "too_soon"

        if position[2] < self.z_min:
            return "too_low"

        if self.workspace_center is not None and self.max_workspace_distance is not None:
            distance = np.linalg.norm(position - self.workspace_center)
            if distance > self.max_workspace_distance:
                return "too_far"

        return "accepted"

    @staticmethod
    def _validate_prediction(prediction: TrajectoryPrediction):
        if prediction.times.ndim != 1:
            raise ValueError("prediction.times must be a 1D array")
        if prediction.positions.ndim != 2 or prediction.positions.shape[1] != 3:
            raise ValueError("prediction.positions must have shape (N, 3)")
        if len(prediction.times) != len(prediction.positions):
            raise ValueError("prediction.times and positions must have the same length")
