import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import PillowWriter, FuncAnimation

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


def render_animation(
    seed: int,
    output_path: Path,
    steps: int,
    dt: float,
    prediction_horizon: float,
    prediction_dt: float,
    max_nlp_candidates: int,
):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=dt)
    observed = []
    for _ in range(steps):
        simulation.update(dt)
        predictor.step(simulation.get_positions()[0])
        observed.append(simulation.positions[0].copy())

    prediction = predictor.predict(horizon=prediction_horizon, dt=prediction_dt)
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)
    initial_tcp, _ = tcp_pose(q0)
    workspace_center = np.asarray(initial_tcp, dtype=float).reshape(3)

    simple_selector = SimpleInterceptionSelector(
        current_time=predictor.time,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=0.85,
    )
    simple_result = simple_selector.select(prediction)

    evaluator = _make_evaluator(robot, tcp_pose, limits, predictor.time)
    smart_selector = SmartInterceptionSelector(
        current_time=predictor.time,
        planner=evaluator,
        q0=q0,
        dq0=dq0,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=1.15,
        max_candidates=max_nlp_candidates,
        success_tolerance=0.03,
    )
    smart_result = smart_selector.select(prediction)
    if not smart_result.success:
        raise RuntimeError(f"Smart selector failed: {smart_result.reason}")

    nlp_dt = 0.05
    available_time = max(0.25, smart_result.time - predictor.time)
    horizon_steps = int(np.clip(np.ceil(available_time / nlp_dt), 16, 30))
    controller = MultiStepNLPController(
        robot=robot,
        tcp_pose_function=tcp_pose,
        horizon_steps=horizon_steps,
        dt=nlp_dt,
        terminal_weight=1_500.0,
        control_weight=2e-2,
        velocity_weight=1e-3,
    )
    plan = controller.plan(q0=q0, dq0=dq0, target_position=smart_result.position)
    safety = evaluate_plan_safety(robot, tcp_pose, plan.q)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _animate(
        observed=np.asarray(observed),
        prediction=prediction,
        tcp_positions=plan.tcp_positions,
        simple_result=simple_result,
        smart_result=smart_result,
        current_time=predictor.time,
        safety=safety,
        seed=seed,
        output_path=output_path,
    )
    return {
        "seed": seed,
        "output": str(output_path),
        "simple_time_s": None if not simple_result.success else float(simple_result.time),
        "smart_time_s": float(smart_result.time),
        "smart_terminal_error_m": float(plan.terminal_error),
        "smart_status": plan.status,
        "smart_safety": safety,
    }


def _make_evaluator(robot, tcp_pose, limits, current_time):
    def controller_factory(candidate_time: float):
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
        )

    return NLPPlannerEvaluator(
        controller_factory=controller_factory,
        velocity_limits=limits.velocity,
        safety_evaluator=lambda q: evaluate_plan_safety(robot, tcp_pose, q),
    )


def _animate(observed, prediction, tcp_positions, simple_result, smart_result, current_time, safety, seed, output_path):
    frames = max(len(prediction.times), len(tcp_positions))
    tcp_interp = _resample(tcp_positions, frames)
    ball_interp = _resample(prediction.positions, frames)
    smart_frame = _time_to_frame(smart_result.time, prediction.times, frames)
    simple_frame = None if not simple_result.success else _time_to_frame(simple_result.time, prediction.times, frames)

    fig = plt.figure(figsize=(8.8, 6.0))
    ax = fig.add_subplot(111, projection="3d")
    _set_axes(ax, observed, prediction.positions, tcp_positions)

    ax.plot(observed[:, 0], observed[:, 1], observed[:, 2], color="0.25", linewidth=1.5, label="observed ball")
    ax.plot(
        prediction.positions[:, 0],
        prediction.positions[:, 1],
        prediction.positions[:, 2],
        color="tab:green",
        linestyle="--",
        linewidth=1.5,
        label="predicted ball",
    )
    ax.plot(tcp_positions[:, 0], tcp_positions[:, 1], tcp_positions[:, 2], color="tab:blue", linewidth=1.5, label="planned hoop center")
    if simple_result.success:
        ax.scatter(
            [simple_result.position[0]],
            [simple_result.position[1]],
            [simple_result.position[2]],
            color="tab:red",
            s=60,
            label="simple target",
        )
    ax.scatter(
        [smart_result.position[0]],
        [smart_result.position[1]],
        [smart_result.position[2]],
        color="gold",
        edgecolor="black",
        s=90,
        label="smart catch target",
    )

    ball_marker = ax.scatter([], [], [], color="tab:green", s=80, edgecolor="black")
    tcp_marker = ax.scatter([], [], [], color="tab:blue", s=70)
    hoop_line, = ax.plot([], [], [], color="tab:blue", linewidth=2.0)
    title = ax.set_title("")
    ax.legend(loc="upper left", fontsize=8)

    def update(frame):
        ball = ball_interp[frame]
        tcp = tcp_interp[frame]
        ball_marker._offsets3d = ([ball[0]], [ball[1]], [ball[2]])
        tcp_marker._offsets3d = ([tcp[0]], [tcp[1]], [tcp[2]])
        ring = _vertical_ring(tcp, radius=0.15)
        hoop_line.set_data(ring[:, 0], ring[:, 1])
        hoop_line.set_3d_properties(ring[:, 2])
        phase = "moving to reachable future point"
        if frame >= smart_frame:
            phase = "catch point reached"
        elif simple_frame is not None and frame >= simple_frame:
            phase = "simple point passed, still infeasible"
        title.set_text(
            f"Task 4 smart catch, seed {seed} | "
            f"t={prediction.times[min(frame, len(prediction.times)-1)]:.2f}s | {phase}\n"
            f"terminal error={smart_result.selected.terminal_error:.3f} m, "
            f"min tcp table clearance={safety['min_tcp_table_clearance_m']:.3f} m"
        )
        return ball_marker, tcp_marker, hoop_line, title

    animation = FuncAnimation(fig, update, frames=frames, interval=90, blit=False)
    animation.save(output_path, writer=PillowWriter(fps=12))
    plt.close(fig)


def _resample(points, frames):
    points = np.asarray(points, dtype=float)
    source = np.linspace(0.0, 1.0, len(points))
    target = np.linspace(0.0, 1.0, frames)
    return np.vstack([np.interp(target, source, points[:, axis]) for axis in range(3)]).T


def _time_to_frame(time, prediction_times, frames):
    if len(prediction_times) == 0:
        return 0
    fraction = (time - prediction_times[0]) / max(prediction_times[-1] - prediction_times[0], 1e-9)
    return int(np.clip(round(fraction * (frames - 1)), 0, frames - 1))


def _vertical_ring(center, radius):
    theta = np.linspace(0.0, 2.0 * np.pi, 80)
    return np.column_stack(
        [
            np.full_like(theta, center[0]),
            center[1] + radius * np.cos(theta),
            center[2] + radius * np.sin(theta),
        ]
    )


def _set_axes(ax, observed, prediction, tcp_positions):
    all_points = np.vstack([observed, prediction, tcp_positions])
    mins = all_points.min(axis=0)
    maxs = all_points.max(axis=0)
    center = 0.5 * (mins + maxs)
    radius = 0.55 * np.max(maxs - mins)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(max(0.0, center[2] - radius), center[2] + radius)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")
    ax.view_init(elev=22, azim=-62)
    ax.grid(True, alpha=0.35)


def parse_args():
    parser = argparse.ArgumentParser(description="Render an explanatory Task 4 catch animation.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("../outputs/task4/task4_smart_catch_seed0.gif"))
    parser.add_argument("--steps", type=int, default=80)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--prediction-horizon", type=float, default=0.8)
    parser.add_argument("--prediction-dt", type=float, default=0.02)
    parser.add_argument("--max-nlp-candidates", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = render_animation(
        seed=args.seed,
        output_path=args.output,
        steps=args.steps,
        dt=args.dt,
        prediction_horizon=args.prediction_horizon,
        prediction_dt=args.prediction_dt,
        max_nlp_candidates=args.max_nlp_candidates,
    )
    for key, value in result.items():
        print(f"{key}: {value}")
