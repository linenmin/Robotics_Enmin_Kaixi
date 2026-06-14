import unittest

import numpy as np

from interception_selector import SimpleInterceptionSelector
from trajectory_predictor import TrajectoryPrediction


class SimpleInterceptionSelectorTest(unittest.TestCase):
    def test_selects_earliest_future_candidate_that_passes_filters(self):
        prediction = TrajectoryPrediction(
            times=np.array([0.85, 0.90, 1.00, 1.10]),
            positions=np.array(
                [
                    [1.0, 0.0, 0.20],
                    [0.9, 0.1, 0.45],
                    [0.8, 0.1, 0.55],
                    [0.7, 0.1, 0.50],
                ],
                dtype=float,
            ),
        )
        selector = SimpleInterceptionSelector(current_time=0.80, min_lead_time=0.10, z_min=0.40)

        result = selector.select(prediction)

        self.assertTrue(result.success)
        self.assertEqual(result.index, 2)
        self.assertAlmostEqual(result.time, 1.00)
        np.testing.assert_allclose(result.position, prediction.positions[2])
        self.assertEqual(result.reason, "accepted")
        self.assertEqual(result.candidates[0].status, "too_soon")
        self.assertEqual(result.candidates[1].status, "too_soon")
        self.assertEqual(result.candidates[2].status, "accepted")

    def test_returns_failure_when_no_candidate_is_valid(self):
        prediction = TrajectoryPrediction(
            times=np.array([0.90, 1.00]),
            positions=np.array([[0.8, 0.0, 0.20], [0.7, 0.0, 0.25]], dtype=float),
        )
        selector = SimpleInterceptionSelector(current_time=0.80, min_lead_time=0.05, z_min=0.40)

        result = selector.select(prediction)

        self.assertFalse(result.success)
        self.assertEqual(result.reason, "no_candidate")
        self.assertIsNone(result.position)
        self.assertEqual([candidate.status for candidate in result.candidates], ["too_low", "too_low"])

    def test_rejects_nan_candidate_positions(self):
        prediction = TrajectoryPrediction(
            times=np.array([0.95, 1.00]),
            positions=np.array([[np.nan, 0.0, 0.5], [0.8, 0.0, 0.5]], dtype=float),
        )
        selector = SimpleInterceptionSelector(current_time=0.80, min_lead_time=0.05, z_min=0.40)

        result = selector.select(prediction)

        self.assertTrue(result.success)
        self.assertEqual(result.index, 1)
        self.assertEqual(result.candidates[0].status, "non_finite")

    def test_can_use_workspace_distance_as_a_basic_reachability_filter(self):
        prediction = TrajectoryPrediction(
            times=np.array([1.00, 1.10]),
            positions=np.array([[2.5, 0.0, 1.0], [1.0, 0.0, 1.0]], dtype=float),
        )
        selector = SimpleInterceptionSelector(
            current_time=0.80,
            min_lead_time=0.05,
            z_min=0.40,
            workspace_center=np.array([0.7, 0.0, 0.6]),
            max_workspace_distance=1.0,
        )

        result = selector.select(prediction)

        self.assertTrue(result.success)
        self.assertEqual(result.index, 1)
        self.assertEqual(result.candidates[0].status, "too_far")


if __name__ == "__main__":
    unittest.main()
