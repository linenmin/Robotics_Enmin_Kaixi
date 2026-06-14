import numpy as np
import unittest

from trajectory_predictor import LinearKalmanTrajectoryPredictor


def simulate_ball(dt, steps):
    position = np.array([5.0, 0.0, 2.0], dtype=float)
    velocity = np.array([-2.0, 0.2, 6.0], dtype=float)
    gravity = np.array([0.0, 0.0, -9.81], dtype=float)
    positions = []

    for _ in range(steps):
        position = position + velocity * dt + 0.5 * gravity * dt**2
        velocity = velocity + gravity * dt
        positions.append(position.copy())

    return np.array(positions)


class LinearKalmanTrajectoryPredictorTest(unittest.TestCase):
    def test_tracks_state_and_predicts_future_positions(self):
        dt = 0.01
        trajectory = simulate_ball(dt, 80)
        predictor = LinearKalmanTrajectoryPredictor(dt=dt)

        for measurement in trajectory[:60]:
            predictor.step(measurement)

        prediction = predictor.predict(horizon=0.5, dt=0.05)

        self.assertEqual(predictor.state.shape, (6,))
        self.assertEqual(prediction.times.shape, (11,))
        self.assertEqual(prediction.positions.shape, (11, 3))
        self.assertTrue(np.all(prediction.times > predictor.time))
        self.assertTrue(np.all(np.isfinite(prediction.positions)))

        expected_first_future = trajectory[64]
        self.assertLess(np.linalg.norm(prediction.positions[0] - expected_first_future), 0.08)

    def test_covariance_remains_symmetric_and_non_negative(self):
        dt = 0.01
        trajectory = simulate_ball(dt, 40)
        predictor = LinearKalmanTrajectoryPredictor(dt=dt)

        for measurement in trajectory:
            predictor.step(measurement)

        covariance = predictor.covariance

        self.assertTrue(np.allclose(covariance, covariance.T, atol=1e-10))
        self.assertGreater(np.min(np.linalg.eigvalsh(covariance)), -1e-10)


if __name__ == "__main__":
    unittest.main()
