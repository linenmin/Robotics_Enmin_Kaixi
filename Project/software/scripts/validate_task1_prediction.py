import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))

from trajectory_predictor import LinearKalmanTrajectoryPredictor
from utils.ball_simulation import BallSimulation


def run_validation(seed: int, steps: int, dt: float, prediction_horizon: float, prediction_dt: float, output_dir: Path):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=dt)

    times = []
    true_positions = []
    measurements = []
    filtered_positions = []

    for step in range(steps):
        simulation.update(dt)
        measurement = simulation.get_positions()[0]
        state = predictor.step(measurement)

        times.append((step + 1) * dt)
        true_positions.append(simulation.positions[0].copy())
        measurements.append(measurement.copy())
        filtered_positions.append(state[:3].copy())

    prediction = predictor.predict(horizon=prediction_horizon, dt=prediction_dt)

    times = np.asarray(times)
    true_positions = np.asarray(true_positions)
    measurements = np.asarray(measurements)
    filtered_positions = np.asarray(filtered_positions)

    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / "task1_trajectory_prediction.png"
    metrics_path = output_dir / "task1_metrics.json"

    metrics = compute_metrics(
        measurements=measurements,
        filtered_positions=filtered_positions,
        true_positions=true_positions,
        covariance=predictor.covariance,
        prediction=prediction,
        current_time=predictor.time,
    )
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    plot_prediction(
        times=times,
        measurements=measurements,
        filtered_positions=filtered_positions,
        true_positions=true_positions,
        prediction=prediction,
        figure_path=figure_path,
    )

    return metrics_path, figure_path, metrics


def compute_metrics(measurements, filtered_positions, true_positions, covariance, prediction, current_time):
    measurement_errors = measurements - true_positions
    filtered_errors = filtered_positions - true_positions
    covariance_eigenvalues = np.linalg.eigvalsh(covariance)

    return {
        "measurement_rmse_m": rmse(measurement_errors),
        "filtered_rmse_m": rmse(filtered_errors),
        "final_filtered_error_m": float(np.linalg.norm(filtered_errors[-1])),
        "covariance_is_symmetric": bool(np.allclose(covariance, covariance.T, atol=1e-10)),
        "min_covariance_eigenvalue": float(np.min(covariance_eigenvalues)),
        "prediction_has_only_future_times": bool(np.all(prediction.times > current_time)),
        "prediction_has_nan": bool(np.isnan(prediction.positions).any()),
        "num_prediction_points": int(prediction.positions.shape[0]),
    }


def rmse(errors):
    return float(np.sqrt(np.mean(np.sum(errors**2, axis=1))))


def plot_prediction(times, measurements, filtered_positions, true_positions, prediction, figure_path):
    fig = plt.figure(figsize=(10.0, 4.5))
    ax_3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax_z = fig.add_subplot(1, 2, 2)

    ax_3d.plot(true_positions[:, 0], true_positions[:, 1], true_positions[:, 2], label="true", color="black")
    ax_3d.scatter(
        measurements[:, 0],
        measurements[:, 1],
        measurements[:, 2],
        label="measured",
        s=6,
        alpha=0.35,
        color="tab:orange",
    )
    ax_3d.plot(
        filtered_positions[:, 0],
        filtered_positions[:, 1],
        filtered_positions[:, 2],
        label="filtered",
        color="tab:blue",
    )
    ax_3d.plot(
        prediction.positions[:, 0],
        prediction.positions[:, 1],
        prediction.positions[:, 2],
        label="future prediction",
        color="tab:green",
        linestyle="--",
    )
    ax_3d.set_xlabel("x [m]")
    ax_3d.set_ylabel("y [m]")
    ax_3d.set_zlabel("z [m]")
    ax_3d.legend(loc="upper left", fontsize=8)

    ax_z.plot(times, true_positions[:, 2], label="true z", color="black")
    ax_z.scatter(times, measurements[:, 2], label="measured z", s=6, alpha=0.35, color="tab:orange")
    ax_z.plot(times, filtered_positions[:, 2], label="filtered z", color="tab:blue")
    ax_z.plot(prediction.times, prediction.positions[:, 2], label="predicted z", color="tab:green", linestyle="--")
    ax_z.set_xlabel("time [s]")
    ax_z.set_ylabel("z [m]")
    ax_z.grid(True, alpha=0.3)
    ax_z.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Task 1 ball trajectory prediction.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--prediction-horizon", type=float, default=0.5)
    parser.add_argument("--prediction-dt", type=float, default=0.02)
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/task1"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, figure_file, result = run_validation(
        args.seed,
        args.steps,
        args.dt,
        args.prediction_horizon,
        args.prediction_dt,
        args.output_dir,
    )
    print(json.dumps(result, indent=2))
    print(f"metrics: {metrics_file}")
    print(f"figure: {figure_file}")
