import argparse
import sys
from pathlib import Path

import meshcat.geometry as mg
import numpy as np
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


def render_scene(seed: int, output_html: Path, camera_view: str, show_target_markers: bool, simple_max_distance: float):
    prediction, observed, current_time = _make_prediction(seed)
    robot = load_project_robot(SOFTWARE_DIR)
    tcp_pose = build_tcp_pose_function(robot)
    limits = JointLimits.from_robot(robot)
    q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
    dq0 = np.zeros(robot.model.nv)
    workspace_center, _ = tcp_pose(q0)
    workspace_center = np.asarray(workspace_center, dtype=float).reshape(3)

    simple_result = _select_simple(prediction, current_time, workspace_center, simple_max_distance)
    smart_result = _select_smart(robot, tcp_pose, limits, prediction, current_time, q0, dq0, workspace_center)
    controller = _controller_for_time(robot, tcp_pose, smart_result.time, current_time)
    plan = controller.plan(q0=q0, dq0=dq0, target_position=smart_result.position)
    safety = evaluate_plan_safety(robot, tcp_pose, plan.q)

    viz = MeshcatVisualizer(robot.model, robot.collision_model, robot.visual_model)
    viz.initViewer(loadModel=False, open=False)
    viz.viewer.delete()
    viz.loadViewerModel(rootNodeName="task4_report_ur10")
    viz.displayFrames(False)
    viz.display(plan.q[-1])
    _add_clean_scene(viz, prediction, observed, simple_result, smart_result, show_target_markers)
    _set_report_camera(viz, camera_view)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(viz.viewer.static_html(), encoding="utf-8")
    return {
        "html": str(output_html),
        "terminal_error_m": float(plan.terminal_error),
        "min_tcp_table_clearance_m": float(safety["min_tcp_table_clearance_m"]),
        "simple_time_s": None if not simple_result.success else float(simple_result.time),
        "smart_time_s": float(smart_result.time),
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


def _select_simple(prediction, current_time, workspace_center, max_workspace_distance: float):
    selector = SimpleInterceptionSelector(
        current_time=current_time,
        min_lead_time=0.12,
        z_min=0.35,
        workspace_center=workspace_center,
        max_workspace_distance=max_workspace_distance,
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


def _add_clean_scene(viz, prediction, observed, simple_result, smart_result, show_target_markers: bool):
    viewer = viz.viewer
    viewer["task4_report/caught_ball"].set_object(mg.Sphere(BallSimulation.ball_radius), mg.MeshPhongMaterial(color=0x4DAF4A))
    viewer["task4_report/caught_ball"].set_transform(translation_matrix(smart_result.position))
    if show_target_markers:
        marker_offset = np.array([0.0, -0.16, 0.0])
        marker_radius = 0.05
        if simple_result.success:
            viewer["task4_report/simple_target_marker"].set_object(
                mg.Sphere(marker_radius),
                mg.MeshPhongMaterial(color=0xE41A1C, opacity=0.9),
            )
            viewer["task4_report/simple_target_marker"].set_transform(translation_matrix(simple_result.position + marker_offset))
        viewer["task4_report/smart_target_marker"].set_object(
            mg.Sphere(marker_radius),
            mg.MeshPhongMaterial(color=0xFFD700, opacity=0.9),
        )
        viewer["task4_report/smart_target_marker"].set_transform(translation_matrix(smart_result.position + marker_offset))

    for i, pos in enumerate(prediction.positions[::4]):
        viewer[f"task4_report/predicted_path/{i:02d}"].set_object(mg.Sphere(0.018), mg.MeshPhongMaterial(color=0x77DD77, opacity=0.28))
        viewer[f"task4_report/predicted_path/{i:02d}"].set_transform(translation_matrix(pos))
    for i, pos in enumerate(observed[::10]):
        viewer[f"task4_report/observed_path/{i:02d}"].set_object(mg.Sphere(0.012), mg.MeshPhongMaterial(color=0x555555, opacity=0.35))
        viewer[f"task4_report/observed_path/{i:02d}"].set_transform(translation_matrix(pos))


def _set_report_camera(viz, camera_view: str):
    viewer = viz.viewer
    viewer["/Cameras/default/rotated"].set_object(mg.PerspectiveCamera(fov=46))
    if camera_view == "side":
        viewer["/Cameras/default"].set_transform(translation_matrix([1.05, -4.0, 1.05]))
    elif camera_view == "front":
        viewer["/Cameras/default"].set_transform(translation_matrix([-2.4, 0.15, 1.25]))
    else:
        viewer["/Cameras/default"].set_transform(translation_matrix([1.8, -2.4, 1.35]))
    viewer["/Cameras/default/rotated/<object>"].set_property("position", [0, 0, 0])


def parse_args():
    parser = argparse.ArgumentParser(description="Render a clean Meshcat UR10 scene for the report.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-html", type=Path, default=Path("../outputs/task4/task4_report_mesh_scene_seed0.html"))
    parser.add_argument("--camera-view", choices=["three-quarter", "side", "front"], default="three-quarter")
    parser.add_argument("--show-target-markers", action="store_true")
    parser.add_argument("--simple-max-distance", type=float, default=0.85)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = render_scene(args.seed, args.output_html, args.camera_view, args.show_target_markers, args.simple_max_distance)
    for key, value in result.items():
        print(f"{key}: {value}")
