import argparse
import json
import sys
from pathlib import Path

import numpy as np

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))

from trajectory_predictor import LinearKalmanTrajectoryPredictor
from utils.ball_simulation import BallSimulation


def run_benchmark(seeds: list[int], output_dir: Path, steps: int, dt: float, prediction_horizon: float, prediction_dt: float):
    rows = []
    for seed in seeds:
        rows.append(_run_one_seed(seed, steps, dt, prediction_horizon, prediction_dt))
    summary = _summarize(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "settings": {
            "seeds": seeds,
            "steps": steps,
            "dt": dt,
            "prediction_horizon": prediction_horizon,
            "prediction_dt": prediction_dt,
        },
        "summary": summary,
        "rows": rows,
    }
    metrics_path = output_dir / "task1_prediction_benchmark.json"
    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return metrics_path, payload


def _run_one_seed(seed: int, steps: int, dt: float, prediction_horizon: float, prediction_dt: float):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=dt)
    measurements = []
    true_positions = []
    filtered_positions = []
    for _ in range(steps):
        simulation.update(dt)
        measurement = simulation.get_positions()[0]
        state = predictor.step(measurement)
        measurements.append(measurement.copy())
        true_positions.append(simulation.positions[0].copy())
        filtered_positions.append(state[:3].copy())

    prediction = predictor.predict(horizon=prediction_horizon, dt=prediction_dt)
    future_truth = _future_truth_from_state(simulation, prediction_dt, len(prediction.times))
    prediction_errors = np.linalg.norm(prediction.positions - future_truth, axis=1)
    measurement_errors = np.linalg.norm(np.asarray(measurements) - np.asarray(true_positions), axis=1)
    filtered_errors = np.linalg.norm(np.asarray(filtered_positions) - np.asarray(true_positions), axis=1)
    return {
        "seed": seed,
        "measurement_rmse_m": _rmse(measurement_errors),
        "filtered_rmse_m": _rmse(filtered_errors),
        "future_prediction_rmse_m": _rmse(prediction_errors),
        "future_prediction_max_error_m": float(np.max(prediction_errors)),
        "final_filtered_error_m": float(filtered_errors[-1]),
        "covariance_is_symmetric": bool(np.allclose(predictor.covariance, predictor.covariance.T)),
        "min_covariance_eigenvalue": float(np.linalg.eigvalsh(predictor.covariance).min()),
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


def _summarize(rows: list[dict]):
    keys = [
        "measurement_rmse_m",
        "filtered_rmse_m",
        "future_prediction_rmse_m",
        "future_prediction_max_error_m",
        "final_filtered_error_m",
        "min_covariance_eigenvalue",
    ]
    summary = {}
    for key in keys:
        values = np.asarray([row[key] for row in rows], dtype=float)
        summary[key] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
            "p95": float(np.percentile(values, 95)),
            "max": float(np.max(values)),
        }
    summary["all_covariances_symmetric"] = bool(all(row["covariance_is_symmetric"] for row in rows))
    summary["all_covariances_psd"] = bool(all(row["min_covariance_eigenvalue"] >= -1e-12 for row in rows))
    return summary


def _rmse(errors: np.ndarray):
    return float(np.sqrt(np.mean(np.asarray(errors, dtype=float) ** 2)))


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-seed Task 1 Kalman prediction benchmark.")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(50)))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--prediction-horizon", type=float, default=0.5)
    parser.add_argument("--prediction-dt", type=float, default=0.02)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, result = run_benchmark(
        seeds=args.seeds,
        output_dir=args.output_dir,
        steps=args.steps,
        dt=args.dt,
        prediction_horizon=args.prediction_horizon,
        prediction_dt=args.prediction_dt,
    )
    print(json.dumps(result["summary"], indent=2))
    print(f"metrics: {metrics_file}")
