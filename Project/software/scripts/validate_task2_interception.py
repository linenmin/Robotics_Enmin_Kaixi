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

from interception_selector import SimpleInterceptionSelector
from trajectory_predictor import LinearKalmanTrajectoryPredictor
from utils.ball_simulation import BallSimulation


def run_validation(
    seed: int,
    steps: int,
    dt: float,
    prediction_horizon: float,
    prediction_dt: float,
    min_lead_time: float,
    z_min: float,
    max_tcp_distance: float,
    output_dir: Path,
):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=dt)

    observed_times = []
    true_positions = []
    measurements = []

    for step in range(steps):
        simulation.update(dt)
        measurement = simulation.get_positions()[0]
        predictor.step(measurement)

        observed_times.append((step + 1) * dt)
        true_positions.append(simulation.positions[0].copy())
        measurements.append(measurement.copy())

    prediction = predictor.predict(horizon=prediction_horizon, dt=prediction_dt)
    selector = SimpleInterceptionSelector(
        current_time=predictor.time,
        min_lead_time=min_lead_time,
        z_min=z_min,
        workspace_center=np.array([0.712, 0.162, 0.634], dtype=float),
        max_workspace_distance=max_tcp_distance,
    )
    interception = selector.select(prediction)

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "task2_metrics.json"
    figure_path = output_dir / "task2_interception_selection.png"

    metrics = compute_metrics(interception, predictor.time, z_min, max_tcp_distance)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plot_selection(
        observed_times=np.asarray(observed_times),
        measurements=np.asarray(measurements),
        true_positions=np.asarray(true_positions),
        prediction=prediction,
        interception=interception,
        figure_path=figure_path,
    )

    return metrics_path, figure_path, metrics


def compute_metrics(interception, current_time: float, z_min: float, max_tcp_distance: float):
    accepted_count = sum(candidate.status == "accepted" for candidate in interception.candidates)
    rejected_counts = {}
    for candidate in interception.candidates:
        rejected_counts[candidate.status] = rejected_counts.get(candidate.status, 0) + 1

    selected_from_prediction = False
    selected_is_future = False
    selected_above_z_min = False
    selected_has_nan = False
    selected_within_tcp_distance = False
    selected_time = None
    selected_position = None

    if interception.success:
        selected_time = float(interception.time)
        selected_position = interception.position.tolist()
        selected_from_prediction = interception.index is not None
        selected_is_future = bool(interception.time > current_time)
        selected_above_z_min = bool(interception.position[2] >= z_min)
        selected_has_nan = bool(np.isnan(interception.position).any())
        selected_within_tcp_distance = bool(
            np.linalg.norm(interception.position - np.array([0.712, 0.162, 0.634], dtype=float)) <= max_tcp_distance
        )

    return {
        "success": bool(interception.success),
        "reason": interception.reason,
        "selected_index": interception.index,
        "selected_time_s": selected_time,
        "selected_position_m": selected_position,
        "selected_from_prediction": selected_from_prediction,
        "selected_is_future": selected_is_future,
        "selected_above_z_min": selected_above_z_min,
        "selected_has_nan": selected_has_nan,
        "selected_within_tcp_distance": selected_within_tcp_distance,
        "max_tcp_distance_m": max_tcp_distance,
        "num_candidates_checked": len(interception.candidates),
        "num_accepted_candidates_seen": accepted_count,
        "candidate_status_counts": rejected_counts,
    }


def plot_selection(observed_times, measurements, true_positions, prediction, interception, figure_path):
    fig = plt.figure(figsize=(10.0, 4.5))
    ax_3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax_time = fig.add_subplot(1, 2, 2)

    statuses = [candidate.status for candidate in interception.candidates]
    accepted_indices = [candidate.index for candidate in interception.candidates if candidate.status == "accepted"]
    rejected_indices = [candidate.index for candidate in interception.candidates if candidate.status != "accepted"]

    ax_3d.plot(true_positions[:, 0], true_positions[:, 1], true_positions[:, 2], color="black", label="observed true")
    ax_3d.scatter(measurements[:, 0], measurements[:, 1], measurements[:, 2], s=6, alpha=0.35, label="measured")
    ax_3d.plot(
        prediction.positions[:, 0],
        prediction.positions[:, 1],
        prediction.positions[:, 2],
        color="tab:green",
        linestyle="--",
        label="predicted trajectory",
    )
    if rejected_indices:
        rejected = prediction.positions[rejected_indices]
        ax_3d.scatter(rejected[:, 0], rejected[:, 1], rejected[:, 2], color="tab:red", s=14, label="rejected")
    if accepted_indices:
        accepted = prediction.positions[accepted_indices]
        ax_3d.scatter(accepted[:, 0], accepted[:, 1], accepted[:, 2], color="tab:blue", s=18, label="accepted")
    if interception.success:
        ax_3d.scatter(
            [interception.position[0]],
            [interception.position[1]],
            [interception.position[2]],
            color="gold",
            edgecolor="black",
            s=90,
            label="selected",
        )
    ax_3d.set_xlabel("x [m]")
    ax_3d.set_ylabel("y [m]")
    ax_3d.set_zlabel("z [m]")
    ax_3d.legend(loc="upper left", fontsize=8)

    ax_time.plot(observed_times, true_positions[:, 2], color="black", label="observed z")
    ax_time.plot(prediction.times, prediction.positions[:, 2], color="tab:green", linestyle="--", label="predicted z")
    for index, status in enumerate(statuses):
        color = "tab:blue" if status == "accepted" else "tab:red"
        ax_time.scatter(prediction.times[index], prediction.positions[index, 2], color=color, s=18)
    if interception.success:
        ax_time.scatter(interception.time, interception.position[2], color="gold", edgecolor="black", s=90, label="selected")
    ax_time.set_xlabel("time [s]")
    ax_time.set_ylabel("z [m]")
    ax_time.grid(True, alpha=0.3)
    ax_time.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Task 2 simple interception point selection.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--prediction-horizon", type=float, default=0.8)
    parser.add_argument("--prediction-dt", type=float, default=0.02)
    parser.add_argument("--min-lead-time", type=float, default=0.12)
    parser.add_argument("--z-min", type=float, default=0.35)
    parser.add_argument("--max-tcp-distance", type=float, default=0.85)
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/task2"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, figure_file, result = run_validation(
        seed=args.seed,
        steps=args.steps,
        dt=args.dt,
        prediction_horizon=args.prediction_horizon,
        prediction_dt=args.prediction_dt,
        min_lead_time=args.min_lead_time,
        z_min=args.z_min,
        max_tcp_distance=args.max_tcp_distance,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2))
    print(f"metrics: {metrics_file}")
    print(f"figure: {figure_file}")
