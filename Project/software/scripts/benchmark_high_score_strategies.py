import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))

from interception_selector import SimpleInterceptionSelector
from hoop_crossing import evaluate_hoop_crossing
from optimal_control_planner import (
    JointLimits,
    MultiStepNLPController,
    build_tcp_pose_function,
    evaluate_plan_safety,
    hoop_normal_from_tcp_rotation,
    load_project_robot,
)
from strategy_benchmark import (
    CandidateEvaluation,
    select_earliest_nlp_feasible,
    select_latest_nlp_feasible,
    select_simple_geometric,
    select_smart_cost,
    select_uncertainty_guard_feasible,
    summarize_strategy_rows,
)
from trajectory_predictor import LinearKalmanTrajectoryPredictor, TrajectoryPrediction
from utils.ball_simulation import BallSimulation, GRAVITY


def run_benchmark(
    seeds: list[int],
    output_dir: Path,
    max_candidate_distance: float,
    max_candidates: int,
    success_tolerance: float,
    measurement_noise_std: float = 1e-3,
    orientation_weight: float = 10.0,
    normal_alignment_weight: float = 5.0,
):
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)
    workspace_center, _ = tcp_pose(q0)
    workspace_center = np.asarray(workspace_center, dtype=float).reshape(3)

    candidate_rows = []
    strategy_rows = []
    for seed in seeds:
        prediction, current_time, true_future = _make_prediction(seed, measurement_noise_std=measurement_noise_std)
        candidates = _evaluate_common_candidate_pool(
            seed=seed,
            prediction=prediction,
            true_future=true_future,
            current_time=current_time,
            workspace_center=workspace_center,
            robot=robot,
            tcp_pose=tcp_pose,
            limits=limits,
            q0=q0,
            dq0=dq0,
            max_candidate_distance=max_candidate_distance,
            max_candidates=max_candidates,
            success_tolerance=success_tolerance,
            orientation_weight=orientation_weight,
            normal_alignment_weight=normal_alignment_weight,
        )
        candidate_rows.extend(_candidate_to_row(candidate) for candidate in candidates)
        strategy_rows.extend(
            [
                select_simple_geometric(candidates).to_row(seed),
                select_earliest_nlp_feasible(candidates).to_row(seed),
                select_latest_nlp_feasible(candidates).to_row(seed),
                select_uncertainty_guard_feasible(candidates).to_row(seed),
                select_smart_cost(candidates).to_row(seed),
            ]
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_strategy_rows(strategy_rows)
    payload = {
        "settings": {
            "seeds": seeds,
            "max_candidate_distance_m": max_candidate_distance,
            "max_candidates": max_candidates,
            "success_tolerance_m": success_tolerance,
            "measurement_noise_std_m": measurement_noise_std,
            "orientation_weight": orientation_weight,
            "normal_alignment_weight": normal_alignment_weight,
            "candidate_pool": "same future/height/workspace-filtered candidate list for every strategy",
            "success_definition": "NLP success, hoop-plane crossing inside hoop_radius - ball_radius, and zero safety penalty.",
        },
        "summary": summary,
        "strategy_rows": strategy_rows,
        "candidate_rows": candidate_rows,
    }
    metrics_path = output_dir / "strategy_benchmark.json"
    summary_csv_path = output_dir / "strategy_summary_table.csv"
    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_summary_csv(summary_csv_path, summary)
    return metrics_path, summary_csv_path, payload


def _make_prediction(seed: int, measurement_noise_std: float = 1e-3):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=0.01, measurement_std=measurement_noise_std)
    for _ in range(80):
        simulation.update(0.01)
        measurement = simulation.positions[0] + np.random.normal(0.0, measurement_noise_std, size=3)
        predictor.step(measurement)
    prediction = predictor.predict(horizon=0.8, dt=0.02)
    true_future = _true_future_from_simulation(simulation, prediction.times, predictor.time)
    return prediction, predictor.time, true_future


def _true_future_from_simulation(simulation: BallSimulation, times: np.ndarray, current_time: float) -> TrajectoryPrediction:
    positions = simulation.positions.copy()
    velocities = simulation.velocities.copy()
    future_positions = []
    last_time = float(current_time)
    for time in times:
        dt = float(time) - last_time
        positions = positions + velocities * dt + 0.5 * GRAVITY * dt**2
        velocities = velocities + GRAVITY * dt
        for i in range(positions.shape[0]):
            if positions[i, 2] < BallSimulation.ball_radius:
                positions[i, 2] = BallSimulation.ball_radius
                velocities[i, 2] *= -0.8
                if velocities[i, 2] < 0.05:
                    velocities[i, 2] = 0
        future_positions.append(positions[0].copy())
        last_time = float(time)
    return TrajectoryPrediction(times=times.copy(), positions=np.asarray(future_positions))


def _controller_for_time(robot, tcp_pose, candidate_time: float, current_time: float, orientation_weight: float = 10.0):
    nlp_dt = 0.05
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
        orientation_weight=orientation_weight,
    )


def _evaluate_common_candidate_pool(
    seed: int,
    prediction,
    true_future,
    current_time: float,
    workspace_center: np.ndarray,
    robot,
    tcp_pose,
    limits,
    q0: np.ndarray,
    dq0: np.ndarray,
    max_candidate_distance: float,
    max_candidates: int,
    success_tolerance: float,
    orientation_weight: float,
    normal_alignment_weight: float,
):
    geometric_selector = SimpleInterceptionSelector(
        current_time=current_time,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=max_candidate_distance,
    )
    accepted = []
    for index, (time, position) in enumerate(zip(prediction.times, prediction.positions, strict=True)):
        status = geometric_selector._candidate_status(float(time), position)
        if status == "accepted":
            accepted.append((index, float(time), position.copy(), status))
    accepted = sorted(accepted, key=lambda item: item[1])[:max_candidates]

    candidates = []
    for index, time, position, status in accepted:
        controller = _controller_for_time(robot, tcp_pose, time, current_time, orientation_weight=orientation_weight)
        target_normal = _trajectory_direction(prediction.positions, index)
        plan = controller.plan(
            q0=q0,
            dq0=dq0,
            target_position=position,
            target_normal=target_normal,
            normal_alignment_weight=normal_alignment_weight,
        )
        safety_metrics = evaluate_plan_safety(robot, tcp_pose, plan.q)
        safety_penalty = _safety_penalty(safety_metrics)
        terminal_error = float(plan.terminal_error)
        hoop_center, hoop_rotation = tcp_pose(plan.q[-1])
        hoop_center = np.asarray(hoop_center, dtype=float).reshape(3)
        hoop_rotation = np.asarray(hoop_rotation, dtype=float)
        hoop_normal = hoop_normal_from_tcp_rotation(hoop_rotation)
        predicted_crossing = evaluate_hoop_crossing(
            times=prediction.times,
            ball_positions=prediction.positions,
            hoop_center=hoop_center,
            hoop_normal=hoop_normal,
            hoop_radius=0.15,
            ball_radius=BallSimulation.ball_radius,
        )
        true_crossing = evaluate_hoop_crossing(
            times=true_future.times,
            ball_positions=true_future.positions,
            hoop_center=hoop_center,
            hoop_normal=hoop_normal,
            hoop_radius=0.15,
            ball_radius=BallSimulation.ball_radius,
        )
        position_uncertainty = None
        if prediction.covariances is not None:
            position_uncertainty = float(np.sqrt(np.trace(prediction.covariances[index])))
        candidates.append(
            CandidateEvaluation(
                seed=seed,
                index=index,
                time=time,
                position=position,
                geometric_status=status,
                nlp_success=bool(plan.success),
                passes_hoop=bool(true_crossing.passes_through_hoop),
                terminal_error=terminal_error,
                max_abs_ddq=float(np.max(np.abs(plan.ddq))),
                max_velocity_ratio=float(np.max(np.abs(plan.dq) / limits.velocity.reshape(1, -1))),
                safety_penalty=safety_penalty,
                solver_status=str(plan.status),
                solve_time_s=float(plan.solve_time_s),
                iter_count=int(plan.iter_count),
                terminal_normal_alignment=float(plan.terminal_normal_alignment),
                position_uncertainty_m=position_uncertainty,
                predicted_radial_error=predicted_crossing.radial_error,
                plane_crossing_exists=bool(true_crossing.plane_crossing_exists),
                crossing_time=true_crossing.crossing_time,
                radial_error=true_crossing.radial_error,
                effective_tolerance=true_crossing.effective_tolerance,
                crossing_reason=true_crossing.reason,
                min_tcp_table_clearance=float(safety_metrics.get("min_tcp_table_clearance_m", float("nan"))),
                min_frame_table_clearance=float(safety_metrics.get("min_frame_table_clearance_m", float("nan"))),
                min_self_sphere_clearance=float(safety_metrics.get("min_self_sphere_clearance_m", float("nan"))),
                ring_top_faces_ground=bool(safety_metrics.get("ring_top_faces_ground", False)),
            )
        )
    return candidates


def _trajectory_direction(positions: np.ndarray, index: int) -> np.ndarray:
    positions = np.asarray(positions, dtype=float)
    if positions.shape[0] < 2:
        return np.array([1.0, 0.0, 0.0])
    if index <= 0:
        direction = positions[1] - positions[0]
    elif index >= positions.shape[0] - 1:
        direction = positions[-1] - positions[-2]
    else:
        direction = positions[index + 1] - positions[index - 1]
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-12:
        return np.array([1.0, 0.0, 0.0])
    return direction / norm


def _safety_penalty(metrics: dict) -> float:
    return float(
        max(0.0, -float(metrics.get("min_tcp_table_clearance_m", 0.0)))
        + max(0.0, -float(metrics.get("min_frame_table_clearance_m", 0.0)))
        + max(0.0, -float(metrics.get("min_self_sphere_clearance_m", 0.0)))
        + (1.0 if metrics.get("ring_top_faces_ground", False) else 0.0)
    )


def _candidate_to_row(candidate: CandidateEvaluation) -> dict:
    return {
        "seed": int(candidate.seed),
        "index": int(candidate.index),
        "time_s": float(candidate.time),
        "position_m": candidate.position.tolist(),
        "geometric_status": candidate.geometric_status,
        "nlp_success": bool(candidate.nlp_success),
        "plane_crossing_exists": bool(candidate.plane_crossing_exists),
        "passes_through_hoop": bool(candidate.passes_hoop),
        "crossing_time_s": candidate.crossing_time,
        "radial_error_m": candidate.radial_error,
        "effective_tolerance_m": candidate.effective_tolerance,
        "crossing_reason": candidate.crossing_reason,
        "success": bool(candidate.success),
        "terminal_error_m": float(candidate.terminal_error),
        "max_abs_ddq": float(candidate.max_abs_ddq),
        "max_velocity_ratio": float(candidate.max_velocity_ratio),
        "safety_penalty": float(candidate.safety_penalty),
        "min_tcp_table_clearance_m": candidate.min_tcp_table_clearance,
        "min_frame_table_clearance_m": candidate.min_frame_table_clearance,
        "min_self_sphere_clearance_m": candidate.min_self_sphere_clearance,
        "ring_top_faces_ground": bool(candidate.ring_top_faces_ground),
        "solver_status": candidate.solver_status,
        "solve_time_s": candidate.solve_time_s,
        "iter_count": candidate.iter_count,
        "terminal_normal_alignment": candidate.terminal_normal_alignment,
        "position_uncertainty_m": candidate.position_uncertainty_m,
        "predicted_radial_error_m": candidate.predicted_radial_error,
    }


def _write_summary_csv(path: Path, summary: dict):
    fieldnames = [
        "strategy",
        "n",
        "success_count",
        "success_rate",
        "mean_attempt_catch_time_s",
        "std_attempt_catch_time_s",
        "mean_success_catch_time_s",
        "std_success_catch_time_s",
        "mean_success_terminal_error_m",
        "std_success_terminal_error_m",
        "mean_success_radial_error_m",
        "std_success_radial_error_m",
        "mean_success_max_abs_ddq",
        "mean_success_max_velocity_ratio",
        "mean_success_solve_time_s",
        "mean_success_iter_count",
        "mean_success_terminal_normal_alignment",
        "min_success_tcp_table_clearance_m",
        "min_success_frame_table_clearance_m",
        "min_success_self_sphere_clearance_m",
        "failure_count",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for strategy, values in summary.items():
            row = {"strategy": strategy}
            row.update(values)
            writer.writerow(row)


def parse_args():
    parser = argparse.ArgumentParser(description="Fair high-score benchmark for interception strategies.")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(50)))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    parser.add_argument("--max-candidate-distance", type=float, default=1.15)
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument("--success-tolerance", type=float, default=0.03)
    parser.add_argument("--measurement-noise-std", type=float, default=1e-3)
    parser.add_argument("--orientation-weight", type=float, default=10.0)
    parser.add_argument("--normal-alignment-weight", type=float, default=5.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, summary_file, result = run_benchmark(
        seeds=args.seeds,
        output_dir=args.output_dir,
        max_candidate_distance=args.max_candidate_distance,
        max_candidates=args.max_candidates,
        success_tolerance=args.success_tolerance,
        measurement_noise_std=args.measurement_noise_std,
        orientation_weight=args.orientation_weight,
        normal_alignment_weight=args.normal_alignment_weight,
    )
    print(json.dumps(result["summary"], indent=2))
    print(f"metrics: {metrics_file}")
    print(f"summary_csv: {summary_file}")
