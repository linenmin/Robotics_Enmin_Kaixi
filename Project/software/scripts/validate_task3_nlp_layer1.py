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

from optimal_control_planner import (
    JointLimits,
    MultiStepNLPController,
    build_tcp_pose_function,
    evaluate_plan_safety,
    load_project_robot,
)


def run_validation(task2_metrics_path: Path, output_dir: Path, horizon_steps: int, dt: float):
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)

    task2_metrics = json.loads(task2_metrics_path.read_text(encoding="utf-8"))
    target_position = np.asarray(task2_metrics["selected_position_m"], dtype=float)

    initial_tcp, _ = tcp_pose(q0)
    initial_tcp = np.asarray(initial_tcp, dtype=float).reshape(3)

    controller = MultiStepNLPController(
        robot=robot,
        tcp_pose_function=tcp_pose,
        horizon_steps=horizon_steps,
        dt=dt,
        terminal_weight=1_500.0,
        control_weight=2e-2,
        velocity_weight=1e-3,
    )
    result = controller.plan(q0=q0, dq0=dq0, target_position=target_position)
    limits = JointLimits.from_robot(robot)

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = compute_metrics(result, target_position, initial_tcp, limits)
    metrics["safety"] = evaluate_plan_safety(robot, tcp_pose, result.q)
    metrics_path = output_dir / "task3_layer1_metrics.json"
    figure_path = output_dir / "task3_layer1_plan.png"
    joint_figure_path = output_dir / "task3_joint_limits.png"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    plot_plan(result, target_position, figure_path)
    plot_joint_limits(result, limits, dt, joint_figure_path)

    return metrics_path, figure_path, joint_figure_path, metrics


def compute_metrics(result, target_position, initial_tcp, limits):
    terminal_distance = float(np.linalg.norm(result.tcp_positions[-1] - target_position))
    initial_distance = float(np.linalg.norm(initial_tcp - target_position))
    return {
        "success": bool(result.success),
        "status": result.status,
        "initial_tcp_distance_m": initial_distance,
        "terminal_tcp_distance_m": terminal_distance,
        "distance_reduction_m": initial_distance - terminal_distance,
        "terminal_error_m": float(result.terminal_error),
        "objective_value": float(result.objective_value),
        "solve_time_s": float(result.solve_time_s),
        "iter_count": int(result.iter_count),
        "terminal_normal_alignment": None if np.isnan(result.terminal_normal_alignment) else float(result.terminal_normal_alignment),
        "min_tcp_top_z": float(result.min_tcp_top_z),
        "q_has_nan": bool(np.isnan(result.q).any()),
        "dq_has_nan": bool(np.isnan(result.dq).any()),
        "ddq_has_nan": bool(np.isnan(result.ddq).any()),
        "max_abs_ddq": float(np.max(np.abs(result.ddq))),
        "max_abs_dq_ratio": float(np.max(np.abs(result.dq) / limits.velocity)),
        "q_within_limits": bool(np.all(result.q <= limits.upper + 1e-7) and np.all(result.q >= limits.lower - 1e-7)),
        "dq_within_limits": bool(np.all(result.dq <= limits.velocity + 1e-7) and np.all(result.dq >= -limits.velocity - 1e-7)),
        "ddq_within_limits": bool(np.all(result.ddq <= limits.acceleration + 1e-7) and np.all(result.ddq >= -limits.acceleration - 1e-7)),
        "first_ddq": result.first_ddq.tolist(),
    }


def plot_plan(result, target_position, figure_path):
    steps = np.arange(result.tcp_positions.shape[0])
    errors = np.linalg.norm(result.tcp_positions - target_position.reshape(1, 3), axis=1)

    fig = plt.figure(figsize=(10.0, 4.5))
    ax_3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax_err = fig.add_subplot(1, 2, 2)

    ax_3d.plot(
        result.tcp_positions[:, 0],
        result.tcp_positions[:, 1],
        result.tcp_positions[:, 2],
        color="tab:blue",
        marker="o",
        markersize=3,
        label="planned tcp",
    )
    ax_3d.scatter(
        [target_position[0]],
        [target_position[1]],
        [target_position[2]],
        color="gold",
        edgecolor="black",
        s=90,
        label="Task 2 target",
    )
    ax_3d.set_xlabel("x [m]")
    ax_3d.set_ylabel("y [m]")
    ax_3d.set_zlabel("z [m]")
    ax_3d.legend(loc="upper left", fontsize=8)

    ax_err.plot(steps, errors, color="tab:blue", marker="o", markersize=3)
    ax_err.set_xlabel("NLP knot")
    ax_err.set_ylabel("tcp-target distance [m]")
    ax_err.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)


def plot_joint_limits(result, limits, dt: float, figure_path: Path):
    q_time = np.arange(result.q.shape[0]) * dt
    ddq_time = np.arange(result.ddq.shape[0]) * dt
    joint_labels = [f"q{i + 1}" for i in range(result.q.shape[1])]

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 6.6), sharex=False, constrained_layout=True)
    fig.patch.set_facecolor("white")

    for joint_index, label in enumerate(joint_labels):
        axes[0].plot(q_time, result.q[:, joint_index], linewidth=1.4, label=label)
        axes[1].plot(q_time, result.dq[:, joint_index], linewidth=1.4)
        axes[2].plot(ddq_time, result.ddq[:, joint_index], linewidth=1.4)

    axes[0].set_ylabel("position [rad]")
    axes[1].set_ylabel("velocity [rad/s]")
    axes[2].set_ylabel("acceleration [rad/s$^2$]")
    axes[2].set_xlabel("plan time [s]")

    axes[0].set_title("Joint trajectory and limits")
    for joint_index in range(result.q.shape[1]):
        axes[0].axhline(limits.lower[joint_index], color="0.75", linewidth=0.7, linestyle=":")
        axes[0].axhline(limits.upper[joint_index], color="0.75", linewidth=0.7, linestyle=":")
    axes[1].axhline(float(np.min(limits.velocity)), color="black", linewidth=0.9, linestyle="--")
    axes[1].axhline(float(-np.min(limits.velocity)), color="black", linewidth=0.9, linestyle="--")
    axes[2].axhline(float(np.min(limits.acceleration)), color="black", linewidth=0.9, linestyle="--")
    axes[2].axhline(float(-np.min(limits.acceleration)), color="black", linewidth=0.9, linestyle="--")

    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].legend(ncol=6, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    fig.savefig(figure_path, dpi=240)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Task 3 layer-1 multi-step NLP.")
    parser.add_argument("--task2-metrics", type=Path, default=Path("../outputs/task2/task2_metrics.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("../outputs/task3"))
    parser.add_argument("--horizon-steps", type=int, default=18)
    parser.add_argument("--dt", type=float, default=0.05)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    metrics_file, figure_file, joint_figure_file, result = run_validation(
        task2_metrics_path=args.task2_metrics,
        output_dir=args.output_dir,
        horizon_steps=args.horizon_steps,
        dt=args.dt,
    )
    print(json.dumps(result, indent=2))
    print(f"metrics: {metrics_file}")
    print(f"figure: {figure_file}")
    print(f"joint_figure: {joint_figure_file}")
