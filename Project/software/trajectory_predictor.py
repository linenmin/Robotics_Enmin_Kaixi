from dataclasses import dataclass

import numpy as np


GRAVITY = np.array([0.0, 0.0, -9.81], dtype=float)


@dataclass(frozen=True)
class TrajectoryPrediction:
    times: np.ndarray
    positions: np.ndarray


class LinearKalmanTrajectoryPredictor:
    """Linear Kalman filter for one ballistic ball."""

    def __init__(
        self,
        dt: float,
        measurement_std: float = 1e-3,
        acceleration_noise_std: float = 0.5,
        gravity: np.ndarray = GRAVITY,
    ):
        self.dt = float(dt)
        self.measurement_std = float(measurement_std)
        self.acceleration_noise_std = float(acceleration_noise_std)
        self.gravity = np.asarray(gravity, dtype=float)

        self.state = np.zeros(6, dtype=float)
        self.covariance = np.eye(6, dtype=float)
        self.time = 0.0
        self.initialized = False

        self._h = np.hstack([np.eye(3), np.zeros((3, 3))])
        self._r = (self.measurement_std**2) * np.eye(3)

    def step(self, measurement: np.ndarray) -> np.ndarray:
        measurement = self._as_position(measurement)

        if not self.initialized:
            self.state[:3] = measurement
            self.state[3:] = 0.0
            self.covariance = np.diag([self.measurement_std**2] * 3 + [10.0] * 3)
            self.time = self.dt
            self.initialized = True
            return self.state.copy()

        f, control, q = self._model_matrices(self.dt)
        predicted_state = f @ self.state + control
        predicted_covariance = f @ self.covariance @ f.T + q

        innovation = measurement - self._h @ predicted_state
        innovation_covariance = self._h @ predicted_covariance @ self._h.T + self._r
        kalman_gain = predicted_covariance @ self._h.T @ np.linalg.inv(innovation_covariance)

        self.state = predicted_state + kalman_gain @ innovation
        identity = np.eye(6)
        kh = kalman_gain @ self._h
        self.covariance = (identity - kh) @ predicted_covariance @ (identity - kh).T
        self.covariance += kalman_gain @ self._r @ kalman_gain.T
        self.covariance = 0.5 * (self.covariance + self.covariance.T)
        self.time += self.dt

        return self.state.copy()

    def predict(self, horizon: float = 2.0, dt: float | None = None) -> TrajectoryPrediction:
        if not self.initialized:
            return TrajectoryPrediction(times=np.array([], dtype=float), positions=np.empty((0, 3)))

        prediction_dt = self.dt if dt is None else float(dt)
        steps = int(np.ceil(float(horizon) / prediction_dt)) + 1
        offsets = prediction_dt * np.arange(1, steps + 1)

        positions = []
        for offset in offsets:
            position = self.state[:3] + self.state[3:] * offset + 0.5 * self.gravity * offset**2
            positions.append(position)

        return TrajectoryPrediction(
            times=self.time + offsets,
            positions=np.vstack(positions),
        )

    def _model_matrices(self, dt: float):
        f = np.eye(6)
        f[:3, 3:] = dt * np.eye(3)

        control = np.zeros(6, dtype=float)
        control[:3] = 0.5 * self.gravity * dt**2
        control[3:] = self.gravity * dt

        q = self._white_acceleration_covariance(dt)
        return f, control, q

    def _white_acceleration_covariance(self, dt: float) -> np.ndarray:
        q_block = np.array(
            [
                [dt**4 / 4.0, dt**3 / 2.0],
                [dt**3 / 2.0, dt**2],
            ],
            dtype=float,
        )
        q = np.zeros((6, 6), dtype=float)
        variance = self.acceleration_noise_std**2
        for axis in range(3):
            indices = [axis, axis + 3]
            q[np.ix_(indices, indices)] = variance * q_block
        return q

    @staticmethod
    def _as_position(measurement: np.ndarray) -> np.ndarray:
        position = np.asarray(measurement, dtype=float)
        if position.shape == (1, 3):
            position = position[0]
        if position.shape != (3,):
            raise ValueError(f"Expected one 3D ball position, got shape {position.shape}")
        return position
