import argparse
import json
import sys
from pathlib import Path

import numpy as np

SOFTWARE_DIR = Path(__file__).resolve().parents[1]
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))

from optimal_control_planner import JointLimits, build_tcp_pose_function, load_project_robot
from utils.ball_simulation import BallSimulation


def run_reactive_baseline(seeds: list[int], output_dir: Path, measurement_noise_std: float = 1e-3):
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)

    rows = []
    for seed in seeds:
        rows.append(_run_one_seed(seed, robot, tcp_pose, limits, q0, dq0, measurement_noise_std))

    output_dir.mkdir(parents=True, exist_ok=True)
    closest = np.array([row["closest_tcp_ball_distance_m"] for row in rows], dtype=float)
    success = np.array([row["success"] for row in rows], dtype=bool)
    payload = {
        "settings": {
            "seeds": seeds,
            "measurement_noise_std_m": measurement_noise_std,
            "controller": "damped Jacobian pseudo-inverse Cartesian velocity tracking of current noisy ball position",
            "success_proxy": "closest TCP-to-true-ball distance <= 0.03 m; this is a favourable proxy because it ignores hoop-plane orientation.",
        },
        "summary": {
            "n": len(rows),
            "success_count": int(np.sum(success)),
            "success_rate": float(np.mean(success)) if len(rows) else 0.0,
            "mean_closest_tcp_ball_distance_m": float(np.mean(closest)) if len(rows) else None,
            "std_closest_tcp_ball_distance_m": float(np.std(closest, ddof=1)) if len(rows) > 1 else 0.0,
            "min_closest_tcp_ball_distance_m": float(np.min(closest)) if len(rows) else None,
            "p95_closest_tcp_ball_distance_m": float(np.percentile(closest, 95)) if len(rows) else None,
        },
        "rows": rows,
    }
    output_path = output_dir / "reactive_baseline.json"
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path, payload


def _run_one_seed(seed: int, robot, tcp_pose, limits: JointLimits, q0: np.ndarray, dq0: np.ndarray, measurement_noise_std: float):
    np.random.seed(seed)
    simulation = BallSimulation()
    for _ in range(80):
        simulation.update(0.01)

    q = q0.copy()
    dq = dq0.copy()
    dt = 0.01
    gain = 2.8
    damping = 5e-2
    steps = 90
    closest_distance = float("inf")
    closest_time = None
    max_velocity_ratio = 0.0
    max_acceleration = 0.0

    for step in range(steps):
        true_ball = simulation.positions[0].copy()
        measurement = true_ball + np.random.normal(0.0, measurement_noise_std, size=3)
        tcp_position, _ = tcp_pose(q)
        tcp_position = np.asarray(tcp_position, dtype=float).reshape(3)
        distance = float(np.linalg.norm(tcp_position - true_ball))
        if distance < closest_distance:
            closest_distance = distance
            closest_time = float(0.80 + step * dt)

        jacobian = _numeric_position_jacobian(tcp_pose, q)
        desired_velocity = gain * (measurement - tcp_position)
        dq_command = _damped_pinv(jacobian, damping) @ desired_velocity
        dq_command = np.clip(dq_command, -limits.velocity, limits.velocity)
        ddq_command = np.clip((dq_command - dq) / dt, -limits.acceleration, limits.acceleration)
        dq = np.clip(dq + ddq_command * dt, -limits.velocity, limits.velocity)
        q = np.clip(q + dq * dt, limits.lower, limits.upper)

        max_velocity_ratio = max(max_velocity_ratio, float(np.max(np.abs(dq) / limits.velocity)))
        max_acceleration = max(max_acceleration, float(np.max(np.abs(ddq_command))))
        simulation.update(dt)

    return {
        "seed": int(seed),
        "success": bool(closest_distance <= 0.03),
        "closest_time_s": closest_time,
        "closest_tcp_ball_distance_m": closest_distance,
        "max_velocity_ratio": max_velocity_ratio,
        "max_abs_ddq": max_acceleration,
    }


def _numeric_position_jacobian(tcp_pose, q: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    base_position, _ = tcp_pose(q)
    base_position = np.asarray(base_position, dtype=float).reshape(3)
    jacobian = np.zeros((3, q.size), dtype=float)
    for joint in range(q.size):
        perturbed = q.copy()
        perturbed[joint] += eps
        position, _ = tcp_pose(perturbed)
        position = np.asarray(position, dtype=float).reshape(3)
        jacobian[:, joint] = (position - base_position) / eps
    return jacobian


def _damped_pinv(jacobian: np.ndarray, damping: float) -> np.ndarray:
    jj_t = jacobian @ jacobian.T
    return jacobian.T @ np.linalg.inv(jj_t + damping**2 * np.eye(jj_t.shape[0]))


def parse_args():
    parser = argparse.ArgumentParser(description="Reactive no-prediction baseline for the hoops project.")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(50)))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/high_score"))
    parser.add_argument("--measurement-noise-std", type=float, default=1e-3)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    path, result = run_reactive_baseline(
        seeds=args.seeds,
        output_dir=args.output_dir,
        measurement_noise_std=args.measurement_noise_std,
    )
    print(json.dumps(result["summary"], indent=2))
    print(f"metrics: {path}")
