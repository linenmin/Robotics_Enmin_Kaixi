import argparse
import sys
import time
from pathlib import Path

import meshcat.geometry as mg
import numpy as np
import pinocchio as pin
from meshcat.animation import Animation
from meshcat.transformations import translation_matrix
from pinocchio.visualize import MeshcatVisualizer

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


def build_replay(seed: int, output_html: Path, open_browser: bool, keep_alive_seconds: float):
    prediction, observed, current_time = _make_prediction(seed)
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)
    workspace_center, _ = tcp_pose(q0)
    workspace_center = np.asarray(workspace_center, dtype=float).reshape(3)

    simple_result = _select_simple(prediction, current_time, workspace_center)
    smart_result = _select_smart(robot, tcp_pose, limits, prediction, current_time, q0, dq0, workspace_center)
    if not smart_result.success:
        raise RuntimeError(f"Smart selector failed: {smart_result.reason}")

    controller = _controller_for_time(robot, tcp_pose, smart_result.time, current_time)
    plan = controller.plan(q0=q0, dq0=dq0, target_position=smart_result.position)
    safety = evaluate_plan_safety(robot, tcp_pose, plan.q)

    viz = MeshcatVisualizer(robot.model, robot.collision_model, robot.visual_model)
    viz.initViewer(loadModel=True, open=open_browser)
    viz.loadViewerModel(rootNodeName="task4_ur10")
    viz.displayFrames(True, [robot.model.getFrameId("world"), robot.model.getFrameId("tcp")])
    viz.display(q0)
    _add_scene_objects(viz, observed, prediction, simple_result, smart_result)

    animation = Animation(default_framerate=24)
    _animate_robot(viz, robot, plan.q, animation)
    _animate_ball(viz, prediction.positions, len(plan.q), animation)
    viz.viewer.set_animation(animation, play=True, repetitions=3)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(viz.viewer.static_html(), encoding="utf-8")

    if keep_alive_seconds > 0:
        print(f"Meshcat replay is open. Keeping server alive for {keep_alive_seconds:.0f} seconds.")
        time.sleep(keep_alive_seconds)

    return {
        "seed": seed,
        "html": str(output_html),
        "simple_time_s": None if not simple_result.success else float(simple_result.time),
        "smart_time_s": float(smart_result.time),
        "terminal_error_m": float(plan.terminal_error),
        "solver_status": plan.status,
        "min_tcp_table_clearance_m": float(safety["min_tcp_table_clearance_m"]),
        "ring_top_faces_ground": bool(safety["ring_top_faces_ground"]),
    }


def _make_prediction(seed: int):
    np.random.seed(seed)
    simulation = BallSimulation()
    predictor = LinearKalmanTrajectoryPredictor(dt=0.01)
    observed = []
    for _ in range(80):
        simulation.update(0.01)
        predictor.step(simulation.get_positions()[0])
        observed.append(simulation.positions[0].copy())
    return predictor.predict(horizon=0.8, dt=0.02), np.asarray(observed), predictor.time


def _select_simple(prediction, current_time, workspace_center):
    selector = SimpleInterceptionSelector(
        current_time=current_time,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=0.85,
    )
    return selector.select(prediction)


def _select_smart(robot, tcp_pose, limits, prediction, current_time, q0, dq0, workspace_center):
    evaluator = NLPPlannerEvaluator(
        controller_factory=lambda candidate_time: _controller_for_time(robot, tcp_pose, candidate_time, current_time),
        velocity_limits=limits.velocity,
        safety_evaluator=lambda q: evaluate_plan_safety(robot, tcp_pose, q),
    )
    selector = SmartInterceptionSelector(
        current_time=current_time,
        planner=evaluator,
        q0=q0,
        dq0=dq0,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=1.15,
        max_candidates=5,
        success_tolerance=0.03,
    )
    return selector.select(prediction)


def _controller_for_time(robot, tcp_pose, candidate_time, current_time):
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


def _add_scene_objects(viz, observed, prediction, simple_result, smart_result):
    viewer = viz.viewer
    viewer["task4/ball"].set_object(mg.Sphere(BallSimulation.ball_radius), mg.MeshPhongMaterial(color=0x4DAF4A))
    viewer["task4/smart_target"].set_object(mg.Sphere(0.045), mg.MeshPhongMaterial(color=0xFFD700))
    viewer["task4/smart_target"].set_transform(translation_matrix(smart_result.position))
    if simple_result.success:
        viewer["task4/simple_target"].set_object(mg.Sphere(0.04), mg.MeshPhongMaterial(color=0xE41A1C))
        viewer["task4/simple_target"].set_transform(translation_matrix(simple_result.position))
    for i, pos in enumerate(prediction.positions[::3]):
        viewer[f"task4/predicted_path/{i:02d}"].set_object(mg.Sphere(0.015), mg.MeshPhongMaterial(color=0x77DD77, opacity=0.35))
        viewer[f"task4/predicted_path/{i:02d}"].set_transform(translation_matrix(pos))
    for i, pos in enumerate(observed[::8]):
        viewer[f"task4/observed_path/{i:02d}"].set_object(mg.Sphere(0.012), mg.MeshPhongMaterial(color=0x999999, opacity=0.45))
        viewer[f"task4/observed_path/{i:02d}"].set_transform(translation_matrix(pos))


def _animate_robot(viz, robot, q_plan, animation):
    for frame, q in enumerate(q_plan):
        pin.forwardKinematics(robot.model, viz.data, q)
        pin.updateGeometryPlacements(robot.model, viz.data, robot.visual_model, viz.visual_data)
        for visual in robot.visual_model.geometryObjects:
            visual_name = viz.getViewerNodeName(visual, pin.GeometryType.VISUAL)
            placement = viz.visual_data.oMg[robot.visual_model.getGeometryId(visual.name)]
            transform = placement.homogeneous.copy()
            scale = np.asarray(visual.meshScale).reshape(3)
            transform[:3, :3] = transform[:3, :3] @ np.diag(scale)
            with animation.at_frame(viz.viewer[visual_name], frame) as frame_viz:
                frame_viz.set_transform(transform)
        for frame_id in [robot.model.getFrameId("world"), robot.model.getFrameId("tcp")]:
            frame_name = robot.model.frames[frame_id].name
            placement = viz.data.oMf[frame_id]
            with animation.at_frame(viz.viewer[f"task4_frames/{frame_name}"], frame) as frame_viz:
                frame_viz.set_transform(placement.homogeneous)


def _animate_ball(viz, predicted_positions, frame_count, animation):
    ball_positions = _resample(predicted_positions, frame_count)
    for frame, position in enumerate(ball_positions):
        with animation.at_frame(viz.viewer["task4/ball"], frame) as frame_viz:
            frame_viz.set_transform(translation_matrix(position))


def _resample(points, frames):
    points = np.asarray(points, dtype=float)
    source = np.linspace(0.0, 1.0, len(points))
    target = np.linspace(0.0, 1.0, frames)
    return np.vstack([np.interp(target, source, points[:, axis]) for axis in range(3)]).T


def parse_args():
    parser = argparse.ArgumentParser(description="Replay Task 4 with the complete UR10 Meshcat model.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-html", type=Path, default=Path("../outputs/task4/task4_meshcat_replay_seed0.html"))
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--keep-alive-seconds", type=float, default=90.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = build_replay(
        seed=args.seed,
        output_html=args.output_html,
        open_browser=not args.no_open,
        keep_alive_seconds=args.keep_alive_seconds,
    )
    for key, value in result.items():
        print(f"{key}: {value}")
