import unittest

import numpy as np

from hoop_crossing import evaluate_hoop_crossing


class HoopCrossingTest(unittest.TestCase):
    def test_detects_centered_crossing_inside_effective_radius(self):
        result = evaluate_hoop_crossing(
            times=np.array([0.0, 1.0]),
            ball_positions=np.array([[-1.0, 0.01, 0.0], [1.0, 0.01, 0.0]]),
            hoop_center=np.zeros(3),
            hoop_normal=np.array([1.0, 0.0, 0.0]),
            hoop_radius=0.15,
            ball_radius=0.12,
        )

        self.assertTrue(result.plane_crossing_exists)
        self.assertTrue(result.passes_through_hoop)
        self.assertAlmostEqual(result.crossing_time, 0.5)
        self.assertAlmostEqual(result.radial_error, 0.01)
        self.assertAlmostEqual(result.effective_tolerance, 0.03)

    def test_rejects_crossing_outside_effective_radius(self):
        result = evaluate_hoop_crossing(
            times=np.array([0.0, 1.0]),
            ball_positions=np.array([[-1.0, 0.04, 0.0], [1.0, 0.04, 0.0]]),
            hoop_center=np.zeros(3),
            hoop_normal=np.array([1.0, 0.0, 0.0]),
            hoop_radius=0.15,
            ball_radius=0.12,
        )

        self.assertTrue(result.plane_crossing_exists)
        self.assertFalse(result.passes_through_hoop)
        self.assertGreater(result.radial_error, result.effective_tolerance)

    def test_reports_no_crossing_when_ball_stays_on_one_side(self):
        result = evaluate_hoop_crossing(
            times=np.array([0.0, 1.0]),
            ball_positions=np.array([[0.2, 0.0, 0.0], [1.0, 0.0, 0.0]]),
            hoop_center=np.zeros(3),
            hoop_normal=np.array([1.0, 0.0, 0.0]),
            hoop_radius=0.15,
            ball_radius=0.12,
        )

        self.assertFalse(result.plane_crossing_exists)
        self.assertFalse(result.passes_through_hoop)
        self.assertIsNone(result.crossing_time)
        self.assertIsNone(result.radial_error)


if __name__ == "__main__":
    unittest.main()
