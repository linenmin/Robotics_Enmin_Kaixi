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
from optimal_control_planner import (
    JointLimits,
    MultiStepNLPController,
    build_tcp_pose_function,
    evaluate_plan_safety,
    load_project_robot,
)
from smart_interception_selector import NLPPlannerEvaluator, SmartInterceptionSelector
from trajectory_predictor import LinearKalmanTrajectoryPredictor
from utils.ball_simulation import BallSimulation


def run_benchmark(
    seeds: list[int],
    steps: int,
    dt: float,
    prediction_horizon: float,
    prediction_dt: float,
    min_lead_time: float,
    z_min: float,
    simple_max_distance: float,
    smart_max_distance: float,
    max_nlp_candidates: int,
    success_tolerance: float,
    nlp_dt: float,
    output_dir: Path,
):
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)
    workspace_center = _initial_tcp_position(tcp_pose, q0)

    rows = []
    candidate_rows = []
    for seed in seeds:
        prediction, current_time = _make_prediction(seed, steps, dt, prediction_horizon, prediction_dt)
        evaluator = _make_evaluator(robot, tcp_pose, limits, current_time, nlp_dt)

        simple_selector = SimpleInterceptionSelector(
            current_time=current_time,
            min_lead_time=min_lead_time,
            z_min=z_min,
            workspace_center=workspace_center,
            max_workspace_distance=simple_max_distance,
        )
        simple_result = simple_selector.select(prediction)
        simple_eval = _evaluate_simple_result(simple_result, evaluator, q0, dq0, success_tolerance)

        smart_selector = SmartInterceptionSelector(
            current_time=current_time,
            planner=evaluator,
            q0=q0,
            dq0=dq0,
            min_lead_time=min_lead_time,
            z_min=z_min,
            workspace_center=workspace_center,
            max_workspace_distance=smart_max_distance,
            max_candidates=max_nlp_candidates,
            success_tolerance=success_tolerance,
        )
        smart_result = smart_selector.select(prediction)

        rows.extend(
            [
                _strategy_row(seed, "simple", simple_result, simple_eval),
                _strategy_row(seed, "smart", smart_result, smart_result.selected),
            ]
        )
        for candidate in smart_result.candidates:
            candidate_rows.append(_candidate_row(seed, candidate))

    output_dir.mkdir(parents=True, exist_ok=True)
    summary = _summarize(rows)
    payload = {
        "settings": {
            "seeds": seeds,
            "steps": steps,
            "dt": dt,
            "prediction_horizon": prediction_horizon,
            "prediction_dt": prediction_dt,
            "min_lead_time": min_lead_time,
            "z_min": z_min,
            "simple_max_distance_m": simple_max_distance,
            "smart_max_distance_m": smart_max_distance,
            "max_nlp_candidates": max_nlp_candidates,
            "success_tolerance_m": success_tolerance,
            "nlp_dt": nlp_dt,
        },
        "summary": summary,
        "rows": rows,
        "smart_candidate_rows": candidate_rows,
    }
    metrics_path = output_dir / "task4_benchmark.json"
    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    comparison_figure = output_dir / "task4_simple_vs_smart.png"
    candidate_figure = output_dir / "task4_candidate_scores.png"
    _plot_comparison(rows, summary, comparison_figure)
    _plot_candidates(candidate_rows, candidate_figure)
    return metrics_path, comparison_figure, candidate_figure, payload


def _make_prediction(seed: int, steps: int, dt: float, prediction_horizon: float, prediction_dt: float):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=dt)
    for _ in range(steps):
        simulation.update(dt)
        predictor.step(simulation.get_positions()[0])
    return predictor.predict(horizon=prediction_horizon, dt=prediction_dt), predictor.time


def _make_evaluator(robot, tcp_pose, limits, current_time: float, nlp_dt: float):
    def controller_factory(candidate_time: float):
        available_time = max(0.25, candidate_time - current_time)
        horizon_steps = int(np.clip(np.ceil(available_time / nlp_dt), 16, 30))
        return MultiStepNLPController(
            robot=robot,
            tcp_pose_function=tcp_pose,
            horizon_steps=horizon_steps,
            dt=nlp_dt,
            terminal_weight=1_500.0,
            control_weight=2e-2,
            velocity_weight=1e-3,
        )

    return NLPPlannerEvaluator(
        controller_factory=controller_factory,
        velocity_limits=limits.velocity,
        safety_evaluator=lambda q: evaluate_plan_safety(robot, tcp_pose, q),
    )


def _evaluate_simple_result(result, evaluator, q0, dq0, success_tolerance: float):
    if not result.success:
        return None
    evaluation = evaluator.evaluate_candidate(q0, dq0, result.time, result.position)
    safety_penalty = _safety_penalty(evaluation.safety_metrics)
    feasible = bool(evaluation.success and evaluation.terminal_error <= success_tolerance and safety_penalty == 0.0)
    return type(
        "SimpleEvaluation",
        (),
        {
            "feasible": feasible,
            "terminal_error": evaluation.terminal_error,
            "max_abs_ddq": evaluation.max_abs_ddq,
            "max_velocity_ratio": evaluation.max_velocity_ratio,
            "safety_metrics": evaluation.safety_metrics,
            "solver_status": evaluation.status,
            "status": "feasible" if feasible else "infeasible",
            "score": float("nan"),
        },
    )()


def _strategy_row(seed: int, strategy: str, result, evaluation):
    if result is None or not result.success or evaluation is None:
        return {
            "seed": seed,
            "strategy": strategy,
            "success": False,
            "reason": getattr(result, "reason", "no_result"),
            "selected_index": None,
            "catch_time_s": None,
            "terminal_error_m": None,
            "max_abs_ddq": None,
            "max_velocity_ratio": None,
            "solver_status": None,
            "min_tcp_table_clearance_m": None,
            "min_frame_table_clearance_m": None,
            "min_self_sphere_clearance_m": None,
        }
    return {
        "seed": seed,
        "strategy": strategy,
        "success": bool(evaluation.feasible),
        "reason": result.reason,
        "selected_index": int(result.index),
        "catch_time_s": float(result.time),
        "selected_position_m": result.position.tolist(),
        "terminal_error_m": float(evaluation.terminal_error),
        "max_abs_ddq": float(evaluation.max_abs_ddq),
        "max_velocity_ratio": float(evaluation.max_velocity_ratio),
        "solver_status": str(evaluation.solver_status),
        "min_tcp_table_clearance_m": float(evaluation.safety_metrics.get("min_tcp_table_clearance_m", float("nan"))),
        "min_frame_table_clearance_m": float(evaluation.safety_metrics.get("min_frame_table_clearance_m", float("nan"))),
        "min_self_sphere_clearance_m": float(evaluation.safety_metrics.get("min_self_sphere_clearance_m", float("nan"))),
    }


def _candidate_row(seed: int, candidate):
    return {
        "seed": seed,
        "index": int(candidate.index),
        "time_s": float(candidate.time),
        "position_m": candidate.position.tolist(),
        "status": candidate.status,
        "score": float(candidate.score),
        "feasible": bool(candidate.feasible),
        "terminal_error_m": float(candidate.terminal_error),
        "max_abs_ddq": float(candidate.max_abs_ddq),
        "max_velocity_ratio": float(candidate.max_velocity_ratio),
        "solver_status": candidate.solver_status,
        "min_tcp_table_clearance_m": float(candidate.safety_metrics.get("min_tcp_table_clearance_m", float("nan"))),
        "min_frame_table_clearance_m": float(candidate.safety_metrics.get("min_frame_table_clearance_m", float("nan"))),
        "min_self_sphere_clearance_m": float(candidate.safety_metrics.get("min_self_sphere_clearance_m", float("nan"))),
    }


def _summarize(rows):
    summary = {}
    for strategy in sorted({row["strategy"] for row in rows}):
        selected = [row for row in rows if row["strategy"] == strategy]
        successful = [row for row in selected if row["success"]]
        summary[strategy] = {
            "n": len(selected),
            "success_count": len(successful),
            "success_rate": len(successful) / len(selected) if selected else 0.0,
            "mean_catch_time_s": _mean(successful, "catch_time_s"),
            "mean_terminal_error_m": _mean(successful, "terminal_error_m"),
            "mean_max_abs_ddq": _mean(successful, "max_abs_ddq"),
            "mean_max_velocity_ratio": _mean(successful, "max_velocity_ratio"),
            "mean_attempt_catch_time_s": _mean(selected, "catch_time_s"),
            "mean_attempt_terminal_error_m": _mean(selected, "terminal_error_m"),
            "mean_attempt_max_abs_ddq": _mean(selected, "max_abs_ddq"),
            "mean_attempt_max_velocity_ratio": _mean(selected, "max_velocity_ratio"),
            "constraint_violation_count": sum(_has_constraint_violation(row) for row in selected),
        }
    return summary


def _mean(rows, key: str):
    values = [row[key] for row in rows if row.get(key) is not None and np.isfinite(row[key])]
    return None if not values else float(np.mean(values))


def _has_constraint_violation(row):
    if not row["success"]:
        return True
    return bool(
        row["max_abs_ddq"] > 2.0 + 1e-6
        or row["max_velocity_ratio"] > 1.0 + 1e-6
        or row["min_tcp_table_clearance_m"] < 0.0
        or row["min_frame_table_clearance_m"] < 0.0
        or row["min_self_sphere_clearance_m"] < 0.0
    )


def _safety_penalty(metrics):
    return (
        max(0.0, -float(metrics.get("min_tcp_table_clearance_m", 0.0)))
        + max(0.0, -float(metrics.get("min_frame_table_clearance_m", 0.0)))
        + max(0.0, -float(metrics.get("min_self_sphere_clearance_m", 0.0)))
        + (1.0 if metrics.get("ring_top_faces_ground", False) else 0.0)
    )


def _initial_tcp_position(tcp_pose, q0):
    position, _ = tcp_pose(q0)
    return np.asarray(position, dtype=float).reshape(3)


def _plot_comparison(rows, summary, figure_path):
    strategies = ["simple", "smart"]
    success_rates = [summary.get(strategy, {}).get("success_rate", 0.0) for strategy in strategies]
    mean_errors = [summary.get(strategy, {}).get("mean_terminal_error_m") or 0.0 for strategy in strategies]
    mean_times = [summary.get(strategy, {}).get("mean_catch_time_s") or 0.0 for strategy in strategies]

    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5))
    colors = ["tab:gray", "tab:blue"]
    axes[0].bar(strategies, success_rates, color=colors)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("success rate")
    axes[1].bar(strategies, mean_errors, color=colors)
    axes[1].set_ylabel("mean terminal error [m]")
    axes[2].bar(strategies, mean_times, color=colors)
    axes[2].set_ylabel("mean catch time [s]")
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def _plot_candidates(candidate_rows, figure_path):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    if candidate_rows:
        times = np.array([row["time_s"] for row in candidate_rows])
        errors = np.array([row["terminal_error_m"] for row in candidate_rows])
        feasible = np.array([row["feasible"] for row in candidate_rows])
        ax.scatter(times[~feasible], errors[~feasible], color="tab:red", label="infeasible", alpha=0.75)
        ax.scatter(times[feasible], errors[feasible], color="tab:blue", label="feasible", alpha=0.85)
    ax.axhline(0.03, color="black", linestyle="--", linewidth=1.0, label="ball-center tolerance")
    ax.set_xlabel("candidate catch time [s]")
    ax.set_ylabel("terminal tcp error [m]")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark Task 4 smart interception strategy.")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--prediction-horizon", type=float, default=0.8)
    parser.add_argument("--prediction-dt", type=float, default=0.02)
    parser.add_argument("--min-lead-time", type=float, default=0.12)
    parser.add_argument("--z-min", type=float, default=0.35)
    parser.add_argument("--simple-max-distance", type=float, default=0.85)
    parser.add_argument("--smart-max-distance", type=float, default=1.15)
    parser.add_argument("--max-nlp-candidates", type=int, default=5)
    parser.add_argument("--success-tolerance", type=float, default=0.03)
    parser.add_argument("--nlp-dt", type=float, default=0.05)
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/task4"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, comparison_file, candidate_file, result = run_benchmark(
        seeds=args.seeds,
        steps=args.steps,
        dt=args.dt,
        prediction_horizon=args.prediction_horizon,
        prediction_dt=args.prediction_dt,
        min_lead_time=args.min_lead_time,
        z_min=args.z_min,
        simple_max_distance=args.simple_max_distance,
        smart_max_distance=args.smart_max_distance,
        max_nlp_candidates=args.max_nlp_candidates,
        success_tolerance=args.success_tolerance,
        nlp_dt=args.nlp_dt,
        output_dir=args.output_dir,
    )
    print(json.dumps(result["summary"], indent=2))
    print(f"metrics: {metrics_file}")
    print(f"comparison figure: {comparison_file}")
    print(f"candidate figure: {candidate_file}")
