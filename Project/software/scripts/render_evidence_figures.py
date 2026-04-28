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


OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#F0E442",
    "black": "#000000",
}


def render_all(benchmark_path: Path, output_dir: Path, seeds: list[int], noise_levels_mm: list[float]):
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))

    noise_payload = run_noise_sweep(seeds=seeds, noise_levels_mm=noise_levels_mm)
    noise_path = output_dir / "noise_sensitivity.json"
    noise_path.write_text(json.dumps(noise_payload, indent=2), encoding="utf-8")

    paths = {
        "noise": output_dir / "figure_noise_sensitivity.png",
        "failure": output_dir / "figure_failure_diagnostics.png",
        "cost": output_dir / "figure_candidate_cost_landscape.png",
        "system": output_dir / "figure_system_block.png",
    }
    plot_noise_sensitivity(noise_payload, paths["noise"])
    plot_failure_diagnostics(benchmark, paths["failure"])
    plot_candidate_cost_landscape(benchmark, paths["cost"])
    plot_system_block(paths["system"])
    return noise_path, paths


def run_noise_sweep(seeds: list[int], noise_levels_mm: list[float]):
    rows = []
    for noise_mm in noise_levels_mm:
        noise_std = float(noise_mm) / 1000.0
        for seed in seeds:
            rows.append(_run_prediction(seed=seed, measurement_std=noise_std))
    summary = {}
    for noise_mm in noise_levels_mm:
        selected = [row for row in rows if row["measurement_std_m"] == float(noise_mm) / 1000.0]
        future = np.asarray([row["future_prediction_rmse_m"] for row in selected], dtype=float)
        filtered = np.asarray([row["filtered_rmse_m"] for row in selected], dtype=float)
        summary[str(float(noise_mm))] = {
            "n": len(selected),
            "measurement_std_m": float(noise_mm) / 1000.0,
            "mean_filtered_rmse_m": float(np.mean(filtered)),
            "mean_future_prediction_rmse_m": float(np.mean(future)),
            "p95_future_prediction_rmse_m": float(np.percentile(future, 95)),
            "max_future_prediction_rmse_m": float(np.max(future)),
        }
    return {"settings": {"seeds": seeds, "noise_levels_mm": noise_levels_mm}, "summary": summary, "rows": rows}


def _run_prediction(seed: int, measurement_std: float):
    rng = np.random.default_rng(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=0.01, measurement_std=measurement_std)
    true_positions = []
    filtered_positions = []
    measurements = []
    for _ in range(80):
        simulation.update(0.01)
        truth = simulation.positions[0].copy()
        measurement = truth + rng.normal(0.0, measurement_std, size=3)
        state = predictor.step(measurement)
        true_positions.append(truth)
        filtered_positions.append(state[:3].copy())
        measurements.append(measurement)

    prediction = predictor.predict(horizon=0.5, dt=0.02)
    future_truth = _future_truth_from_state(simulation, 0.02, len(prediction.times))
    measurement_errors = np.linalg.norm(np.asarray(measurements) - np.asarray(true_positions), axis=1)
    filtered_errors = np.linalg.norm(np.asarray(filtered_positions) - np.asarray(true_positions), axis=1)
    prediction_errors = np.linalg.norm(prediction.positions - future_truth, axis=1)
    return {
        "seed": int(seed),
        "measurement_std_m": float(measurement_std),
        "measurement_rmse_m": _rmse(measurement_errors),
        "filtered_rmse_m": _rmse(filtered_errors),
        "future_prediction_rmse_m": _rmse(prediction_errors),
        "future_prediction_max_error_m": float(np.max(prediction_errors)),
    }


def _future_truth_from_state(simulation: BallSimulation, prediction_dt: float, steps: int):
    positions = simulation.positions.copy()
    velocities = simulation.velocities.copy()
    truth = []
    gravity = np.array([0.0, 0.0, -9.81])
    for _ in range(steps):
        positions = positions + velocities * prediction_dt + 0.5 * gravity * prediction_dt**2
        velocities = velocities + gravity * prediction_dt
        truth.append(positions[0].copy())
    return np.asarray(truth)


def plot_noise_sensitivity(payload: dict, output_path: Path):
    levels = [float(key) for key in payload["summary"].keys()]
    levels.sort()
    means = [payload["summary"][str(level)]["mean_future_prediction_rmse_m"] * 1000.0 for level in levels]
    p95 = [payload["summary"][str(level)]["p95_future_prediction_rmse_m"] * 1000.0 for level in levels]
    max_values = [payload["summary"][str(level)]["max_future_prediction_rmse_m"] * 1000.0 for level in levels]

    fig, ax = plt.subplots(figsize=(5.2, 3.3), constrained_layout=True)
    ax.plot(levels, means, marker="o", color=OKABE_ITO["blue"], label="mean")
    ax.plot(levels, p95, marker="s", color=OKABE_ITO["orange"], label="95th percentile")
    ax.plot(levels, max_values, marker="^", color=OKABE_ITO["purple"], label="max")
    ax.axhline(30.0, color="black", linestyle="--", linewidth=1.0, label="hoop radial clearance")
    ax.set_xlabel("measurement noise standard deviation [mm]")
    ax.set_ylabel("0.5 s prediction RMSE [mm]")
    ax.set_title("Kalman prediction sensitivity")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    _clean_axes(ax)
    fig.savefig(output_path, dpi=260)
    plt.close(fig)


def plot_failure_diagnostics(benchmark: dict, output_path: Path):
    rows = benchmark["strategy_rows"]
    failed_seeds = sorted(
        {
            row["seed"]
            for row in rows
            if row["strategy"] == "earliest_nlp_feasible" and not row["success"]
        }
    )
    candidate_rows = [row for row in benchmark["candidate_rows"] if row["seed"] in failed_seeds]
    if not candidate_rows:
        candidate_rows = benchmark["candidate_rows"][:8]

    fig, ax = plt.subplots(figsize=(5.4, 3.4), constrained_layout=True)
    for seed in sorted({row["seed"] for row in candidate_rows}):
        selected = [row for row in candidate_rows if row["seed"] == seed]
        times = [row["time_s"] for row in selected]
        radial = [
            np.nan if row.get("radial_error_m") is None else row["radial_error_m"] * 1000.0
            for row in selected
        ]
        ax.plot(times, radial, marker="o", linewidth=1.2, label=f"seed {seed}")
    ax.axhline(30.0, color="black", linestyle="--", linewidth=1.0, label="tolerance")
    ax.set_xlabel("candidate catch time [s]")
    ax.set_ylabel("hoop radial error [mm]")
    ax.set_title("Failure seeds miss the hoop-crossing tolerance")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    _clean_axes(ax)
    fig.savefig(output_path, dpi=260)
    plt.close(fig)


def plot_candidate_cost_landscape(benchmark: dict, output_path: Path):
    seed = int(benchmark["settings"]["seeds"][0])
    rows = [row for row in benchmark["candidate_rows"] if row["seed"] == seed]
    times = np.asarray([row["time_s"] for row in rows], dtype=float)
    terminal = np.asarray([row["terminal_error_m"] for row in rows], dtype=float) * 1000.0
    radial = np.asarray([np.nan if row["radial_error_m"] is None else row["radial_error_m"] for row in rows], dtype=float) * 1000.0
    ddq = np.asarray([row["max_abs_ddq"] for row in rows], dtype=float)
    success = np.asarray([row["success"] for row in rows], dtype=bool)

    fig, axes = plt.subplots(3, 1, figsize=(5.4, 5.0), sharex=True, constrained_layout=True)
    axes[0].plot(times, terminal, marker="o", color=OKABE_ITO["blue"])
    axes[0].set_ylabel("TCP error [mm]")
    axes[1].plot(times, radial, marker="o", color=OKABE_ITO["green"])
    axes[1].axhline(30.0, color="black", linestyle="--", linewidth=1.0)
    axes[1].set_ylabel("radial error [mm]")
    axes[2].plot(times, ddq, marker="o", color=OKABE_ITO["orange"])
    axes[2].axhline(2.0, color="black", linestyle="--", linewidth=1.0)
    axes[2].set_ylabel("max |ddq|")
    axes[2].set_xlabel("candidate catch time [s]")
    axes[0].set_title(f"Candidate diagnostics for seed {seed}")
    for ax in axes:
        for x, ok in zip(times, success, strict=True):
            if ok:
                ax.axvspan(x - 0.003, x + 0.003, color=OKABE_ITO["green"], alpha=0.12)
        ax.grid(True, alpha=0.25)
        _clean_axes(ax)
    fig.savefig(output_path, dpi=260)
    plt.close(fig)


def plot_system_block(output_path: Path):
    fig, ax = plt.subplots(figsize=(7.6, 2.1), constrained_layout=True)
    ax.set_axis_off()
    boxes = [
        ("noisy ball\npositions", 0.08),
        ("Kalman\nfilter", 0.25),
        ("future\ntrajectory", 0.42),
        ("candidate\nselection", 0.59),
        ("UR10 NLP\ncontroller", 0.76),
        ("hoop-crossing\ncheck", 0.92),
    ]
    for label, x in boxes:
        rect = plt.Rectangle((x - 0.06, 0.36), 0.12, 0.32, facecolor="#f5f5f5", edgecolor="black", linewidth=1.0)
        ax.add_patch(rect)
        ax.text(x, 0.52, label, ha="center", va="center", fontsize=8.5)
    for (_, x0), (_, x1) in zip(boxes[:-1], boxes[1:], strict=True):
        ax.annotate("", xy=(x1 - 0.068, 0.52), xytext=(x0 + 0.068, 0.52), arrowprops={"arrowstyle": "->", "lw": 1.2})
    ax.text(0.50, 0.14, "Shared timeline: prediction time, candidate time, UR10 motion, and hoop crossing use one clock.", ha="center", fontsize=8.5)
    fig.savefig(output_path, dpi=260)
    plt.close(fig)


def _rmse(errors: np.ndarray):
    return float(np.sqrt(np.mean(np.asarray(errors, dtype=float) ** 2)))


def _clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def parse_args():
    parser = argparse.ArgumentParser(description="Render supporting evidence figures for the robotics report.")
    parser.add_argument("--benchmark", type=Path, default=Path("../outputs/high_score/strategy_benchmark.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(50)))
    parser.add_argument("--noise-levels-mm", type=float, nargs="+", default=[1.0, 3.0, 5.0, 10.0])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    noise_file, figure_paths = render_all(
        benchmark_path=args.benchmark,
        output_dir=args.output_dir,
        seeds=args.seeds,
        noise_levels_mm=args.noise_levels_mm,
    )
    print(f"noise: {noise_file}")
    for name, path in figure_paths.items():
        print(f"{name}: {path}")
