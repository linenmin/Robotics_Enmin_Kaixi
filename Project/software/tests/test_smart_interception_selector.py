import unittest
from dataclasses import dataclass

import numpy as np

from smart_interception_selector import NLPPlannerEvaluator, SmartInterceptionSelector
from trajectory_predictor import TrajectoryPrediction


@dataclass(frozen=True)
class FakePlan:
    success: bool
    terminal_error: float
    max_abs_ddq: float
    max_velocity_ratio: float
    safety_metrics: dict
    status: str = "fake"


class FakePlanner:
    def __init__(self, plans_by_time):
        self.plans_by_time = plans_by_time
        self.calls = []

    def evaluate_candidate(self, q0, dq0, time, position):
        self.calls.append((float(time), position.copy()))
        return self.plans_by_time[round(float(time), 2)]


class SmartInterceptionSelectorTest(unittest.TestCase):
    def test_selects_reachable_candidate_instead_of_earliest_geometric_candidate(self):
        prediction = TrajectoryPrediction(
            times=np.array([1.00, 1.20, 1.40]),
            positions=np.array(
                [
                    [0.80, 0.20, 0.70],
                    [0.90, 0.15, 0.75],
                    [1.00, 0.10, 0.80],
                ]
            ),
        )
        planner = FakePlanner(
            {
                1.00: FakePlan(False, 0.20, 2.0, 0.6, {"min_tcp_table_clearance_m": 0.20}),
                1.20: FakePlan(True, 0.012, 1.4, 0.4, {"min_tcp_table_clearance_m": 0.20}),
                1.40: FakePlan(True, 0.025, 0.8, 0.2, {"min_tcp_table_clearance_m": 0.20}),
            }
        )
        selector = SmartInterceptionSelector(
            current_time=0.80,
            planner=planner,
            q0=np.zeros(6),
            dq0=np.zeros(6),
            min_lead_time=0.10,
            z_min=0.35,
            success_tolerance=0.03,
        )

        result = selector.select(prediction)

        self.assertTrue(result.success)
        self.assertEqual(result.index, 1)
        self.assertEqual(result.reason, "selected_feasible_candidate")
        self.assertEqual(len(planner.calls), 3)
        self.assertLess(result.selected.terminal_error, 0.03)

    def test_reports_failure_when_no_candidate_is_feasible(self):
        prediction = TrajectoryPrediction(
            times=np.array([1.00]),
            positions=np.array([[0.80, 0.20, 0.70]]),
        )
        planner = FakePlanner(
            {
                1.00: FakePlan(False, 0.12, 2.0, 0.9, {"min_tcp_table_clearance_m": 0.20}),
            }
        )
        selector = SmartInterceptionSelector(
            current_time=0.80,
            planner=planner,
            q0=np.zeros(6),
            dq0=np.zeros(6),
            min_lead_time=0.10,
            z_min=0.35,
            success_tolerance=0.03,
        )

        result = selector.select(prediction)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "no_feasible_candidate")
        self.assertEqual(result.index, 0)
        self.assertGreater(result.selected.terminal_error, 0.03)

    def test_shortlist_keeps_geometrically_promising_candidate_before_nlp(self):
        prediction = TrajectoryPrediction(
            times=np.array([1.00, 1.20]),
            positions=np.array(
                [
                    [1.60, 0.20, 0.80],
                    [0.75, 0.18, 0.70],
                ]
            ),
        )
        planner = FakePlanner(
            {
                1.20: FakePlan(True, 0.01, 1.0, 0.3, {"min_tcp_table_clearance_m": 0.20}),
            }
        )
        selector = SmartInterceptionSelector(
            current_time=0.80,
            planner=planner,
            q0=np.zeros(6),
            dq0=np.zeros(6),
            min_lead_time=0.10,
            z_min=0.35,
            workspace_center=np.array([0.712, 0.162, 0.634]),
            max_workspace_distance=2.0,
            max_candidates=1,
        )

        result = selector.select(prediction)

        self.assertTrue(result.success)
        self.assertEqual(result.index, 1)
        self.assertEqual(len(planner.calls), 1)

    def test_nlp_planner_evaluator_extracts_constraint_metrics(self):
        class FakeController:
            def plan(self, q0, dq0, target_position):
                return type(
                    "PlanResult",
                    (),
                    {
                        "success": True,
                        "status": "Solve_Succeeded",
                        "terminal_error": 0.01,
                        "ddq": np.array([[0.5, -1.5]]),
                        "dq": np.array([[0.0, 0.4], [0.2, -0.6]]),
                        "q": np.zeros((2, 2)),
                    },
                )()

        evaluator = NLPPlannerEvaluator(
            controller_factory=lambda time: FakeController(),
            velocity_limits=np.array([1.0, 2.0]),
            safety_evaluator=lambda q: {"min_tcp_table_clearance_m": 0.10},
        )

        evaluation = evaluator.evaluate_candidate(np.zeros(2), np.zeros(2), 1.3, np.array([1.0, 0.0, 0.7]))

        self.assertTrue(evaluation.success)
        self.assertEqual(evaluation.status, "Solve_Succeeded")
        self.assertAlmostEqual(evaluation.max_abs_ddq, 1.5)
        self.assertAlmostEqual(evaluation.max_velocity_ratio, 0.3)
        self.assertEqual(evaluation.safety_metrics["min_tcp_table_clearance_m"], 0.10)


if __name__ == "__main__":
    unittest.main()
