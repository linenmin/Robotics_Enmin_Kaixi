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
    figure_pdf_path = output_dir / "task1_trajectory_prediction.pdf"
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
        figure_pdf_path=figure_pdf_path,
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


def plot_prediction(times, measurements, filtered_positions, true_positions, prediction, figure_path, figure_pdf_path):
    fig, axes = plt.subplots(2, 1, figsize=(8.7, 6.0), constrained_layout=True)
    ax_z, ax_err = axes

    ax_z.plot(times, true_positions[:, 2], label="true z", color="black", linewidth=1.8)
    ax_z.scatter(times, measurements[:, 2], label="measured z", s=10, alpha=0.45, color="tab:orange")
    ax_z.plot(times, filtered_positions[:, 2], label="filtered z", color="tab:blue", linewidth=1.5)
    ax_z.plot(prediction.times, prediction.positions[:, 2], label="0.5 s prediction", color="tab:green", linestyle="--", linewidth=1.8)
    ax_z.axvline(times[-1], color="0.45", linestyle=":", linewidth=1.0)
    ax_z.text(times[-1] + 0.01, np.min(true_positions[:, 2]) + 0.05, "prediction starts", fontsize=9, color="0.35")
    ax_z.set_ylabel("height z [m]")
    ax_z.set_title("Kalman tracking and forward prediction")
    ax_z.grid(True, alpha=0.25)
    ax_z.legend(loc="best", fontsize=8.5, ncol=2)

    measurement_error = np.linalg.norm(measurements - true_positions, axis=1) * 1000.0
    filtered_error = np.linalg.norm(filtered_positions - true_positions, axis=1) * 1000.0
    ax_err.plot(times, measurement_error, color="tab:orange", alpha=0.75, label="measurement error")
    ax_err.plot(times, filtered_error, color="tab:blue", linewidth=1.6, label="filtered error")
    ax_err.set_xlabel("time [s]")
    ax_err.set_ylabel("position error [mm]")
    ax_err.set_title("Zoom on measurement noise and filter correction")
    ax_err.grid(True, alpha=0.25)
    ax_err.legend(loc="best", fontsize=8.5)

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.savefig(figure_path, dpi=260)
    fig.savefig(figure_pdf_path)
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
