from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import casadi as ca
import numpy as np
import pinocchio as pin
from pinocchio import casadi as cpin


def hoop_normal_from_tcp_rotation(rotation):
    return rotation[:, 2]


@dataclass(frozen=True)
class JointLimits:
    lower: np.ndarray
    upper: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray

    @classmethod
    def from_robot(cls, robot, acceleration_limit: float = 2.0):
        nv = robot.model.nv
        return cls(
            lower=np.asarray(robot.model.lowerPositionLimit, dtype=float),
            upper=np.asarray(robot.model.upperPositionLimit, dtype=float),
            velocity=np.asarray(robot.model.velocityLimit, dtype=float),
            acceleration=acceleration_limit * np.ones(nv),
        )


@dataclass(frozen=True)
class NLPPlanResult:
    success: bool
    status: str
    q: np.ndarray
    dq: np.ndarray
    ddq: np.ndarray
    tcp_positions: np.ndarray
    terminal_error: float
    objective_value: float
    solve_time_s: float
    iter_count: int
    terminal_normal_alignment: float
    min_tcp_top_z: float

    @property
    def first_ddq(self) -> np.ndarray:
        return self.ddq[0].copy()


def load_project_robot(software_dir: Path):
    software_dir = Path(software_dir)
    urdf_path = software_dir / "robot_description" / "ur10_robot.urdf"
    mesh_dir = software_dir / "robot_description" / "meshes"
    return pin.RobotWrapper.BuildFromURDF(str(urdf_path), str(mesh_dir))


def build_tcp_pose_function(robot):
    cmodel = cpin.Model(robot.model)
    cdata = cmodel.createData()
    q = ca.SX.sym("q", robot.model.nq)
    cpin.forwardKinematics(cmodel, cdata, q)
    cpin.updateFramePlacements(cmodel, cdata)
    tcp_id = robot.model.getFrameId("tcp")
    placement = cdata.oMf[tcp_id]
    return ca.Function("tcp_pose", [q], [placement.translation, placement.rotation])


class MultiStepNLPController:
    def __init__(
        self,
        robot,
        tcp_pose_function,
        horizon_steps: int = 20,
        dt: float = 0.05,
        terminal_weight: float = 1_000.0,
        control_weight: float = 1e-2,
        velocity_weight: float = 1e-3,
        orientation_weight: float = 10.0,
        table_height: float = 0.0125,
        tcp_table_margin: float = 0.05,
    ):
        self.robot = robot
        self.tcp_pose_function = tcp_pose_function
        self.horizon_steps = int(horizon_steps)
        self.dt = float(dt)
        self.terminal_weight = float(terminal_weight)
        self.control_weight = float(control_weight)
        self.velocity_weight = float(velocity_weight)
        self.orientation_weight = float(orientation_weight)
        self.table_height = float(table_height)
        self.tcp_table_margin = float(tcp_table_margin)
        self.limits = JointLimits.from_robot(robot)

    def plan(
        self,
        q0: np.ndarray,
        dq0: np.ndarray,
        target_position: np.ndarray,
        target_normal: np.ndarray | None = None,
        normal_alignment_weight: float = 0.0,
    ) -> NLPPlanResult:
        q0 = np.asarray(q0, dtype=float)
        dq0 = np.asarray(dq0, dtype=float)
        target_position = np.asarray(target_position, dtype=float).reshape(3)
        normalized_target_normal = None
        if target_normal is not None:
            normalized_target_normal = np.asarray(target_normal, dtype=float).reshape(3)
            norm = float(np.linalg.norm(normalized_target_normal))
            if norm <= 1e-12:
                raise ValueError("target_normal must be nonzero")
            normalized_target_normal = normalized_target_normal / norm

        n = self.robot.model.nv
        horizon = self.horizon_steps
        dt = self.dt

        opti = ca.Opti()
        q = opti.variable(horizon + 1, n)
        dq = opti.variable(horizon + 1, n)
        ddq = opti.variable(horizon, n)

        opti.subject_to(q[0, :].T == q0)
        opti.subject_to(dq[0, :].T == dq0)

        objective = 0
        for k in range(horizon):
            q_next = q[k, :].T + dq[k, :].T * dt + 0.5 * ddq[k, :].T * dt**2
            dq_next = dq[k, :].T + ddq[k, :].T * dt
            opti.subject_to(q[k + 1, :].T == q_next)
            opti.subject_to(dq[k + 1, :].T == dq_next)
            objective += self.control_weight * ca.sumsqr(ddq[k, :])
            objective += self.velocity_weight * ca.sumsqr(dq[k + 1, :])

        opti.subject_to(opti.bounded(self._repeat_row(self.limits.lower, horizon + 1), q, self._repeat_row(self.limits.upper, horizon + 1)))
        opti.subject_to(opti.bounded(self._repeat_row(-self.limits.velocity, horizon + 1), dq, self._repeat_row(self.limits.velocity, horizon + 1)))
        opti.subject_to(opti.bounded(self._repeat_row(-self.limits.acceleration, horizon), ddq, self._repeat_row(self.limits.acceleration, horizon)))

        terminal_tcp, terminal_rotation = self.tcp_pose_function(q[horizon, :].T)
        terminal_error_expr = terminal_tcp - target_position
        objective += self.terminal_weight * ca.sumsqr(terminal_error_expr)
        objective += self.orientation_weight * (1.0 - terminal_rotation[2, 2]) ** 2
        if normalized_target_normal is not None and normal_alignment_weight > 0.0:
            terminal_normal = hoop_normal_from_tcp_rotation(terminal_rotation)
            alignment = ca.dot(terminal_normal, normalized_target_normal)
            objective += float(normal_alignment_weight) * (1.0 - alignment**2)
        for k in range(horizon + 1):
            tcp_position_k, tcp_rotation_k = self.tcp_pose_function(q[k, :].T)
            opti.subject_to(tcp_position_k[2] >= self.table_height + self.tcp_table_margin)
            opti.subject_to(tcp_rotation_k[2, 2] >= 0.0)
        opti.minimize(objective)

        self._set_initial_guess(opti, q, dq, ddq, q0, dq0)
        opti.solver(
            "ipopt",
            {
                "expand": True,
                "print_time": False,
            },
            {
                "print_level": 0,
                "sb": "yes",
                "max_iter": 300,
                "tol": 1e-5,
                "acceptable_tol": 1e-4,
            },
        )

        start_time = perf_counter()
        iter_count = 0
        try:
            solution = opti.solve()
            solve_time_s = perf_counter() - start_time
            stats = opti.stats()
            iter_count = int(stats.get("iter_count", stats.get("iter_count_total", 0)) or 0)
            q_plan = np.asarray(solution.value(q), dtype=float)
            dq_plan = np.asarray(solution.value(dq), dtype=float)
            ddq_plan = np.asarray(solution.value(ddq), dtype=float)
            objective_value = float(solution.value(objective))
            status = "Solve_Succeeded"
            success = True
        except RuntimeError as exc:
            solve_time_s = perf_counter() - start_time
            stats = opti.stats()
            iter_count = int(stats.get("iter_count", stats.get("iter_count_total", 0)) or 0)
            q_plan = np.asarray(opti.debug.value(q), dtype=float)
            dq_plan = np.asarray(opti.debug.value(dq), dtype=float)
            ddq_plan = np.asarray(opti.debug.value(ddq), dtype=float)
            objective_value = float("nan")
            status = str(exc).splitlines()[0]
            success = False

        tcp_positions = self._evaluate_tcp_positions(q_plan)
        terminal_error = float(np.linalg.norm(tcp_positions[-1] - target_position))
        _, terminal_rotation_value = self.tcp_pose_function(q_plan[-1])
        terminal_normal_value = hoop_normal_from_tcp_rotation(np.asarray(terminal_rotation_value, dtype=float))
        if normalized_target_normal is None:
            terminal_normal_alignment = float("nan")
        else:
            terminal_normal_alignment = float(abs(np.dot(terminal_normal_value, normalized_target_normal)))
        min_tcp_top_z = self._min_tcp_top_z(q_plan)
        return NLPPlanResult(
            success=success,
            status=status,
            q=q_plan,
            dq=dq_plan,
            ddq=ddq_plan,
            tcp_positions=tcp_positions,
            terminal_error=terminal_error,
            objective_value=objective_value,
            solve_time_s=solve_time_s,
            iter_count=iter_count,
            terminal_normal_alignment=terminal_normal_alignment,
            min_tcp_top_z=min_tcp_top_z,
        )

    def _set_initial_guess(self, opti, q, dq, ddq, q0, dq0):
        for k in range(self.horizon_steps + 1):
            opti.set_initial(q[k, :], q0)
            opti.set_initial(dq[k, :], dq0)
        opti.set_initial(ddq, np.zeros((self.horizon_steps, self.robot.model.nv)))

    def _evaluate_tcp_positions(self, q_plan: np.ndarray) -> np.ndarray:
        positions = []
        for qk in q_plan:
            position, _ = self.tcp_pose_function(qk)
            positions.append(np.asarray(position, dtype=float).reshape(3))
        return np.vstack(positions)

    def _min_tcp_top_z(self, q_plan: np.ndarray) -> float:
        values = []
        for qk in q_plan:
            _, rotation = self.tcp_pose_function(qk)
            values.append(float(np.asarray(rotation, dtype=float)[2, 2]))
        return float(np.min(values))

    @staticmethod
    def _repeat_row(values: np.ndarray, rows: int) -> np.ndarray:
        return np.tile(np.asarray(values, dtype=float).reshape(1, -1), (rows, 1))


def evaluate_plan_safety(
    robot,
    tcp_pose_function,
    q_plan: np.ndarray,
    table_height: float = 0.0125,
    sphere_radius: float = 0.10,
):
    q_plan = np.asarray(q_plan, dtype=float)
    frame_names = ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link", "wrist_3_link", "tcp"]
    existing_frame_ids = []
    for name in frame_names:
        frame_id = robot.model.getFrameId(name)
        if frame_id < len(robot.model.frames):
            existing_frame_ids.append(frame_id)

    data = robot.model.createData()
    min_tcp_top_z = float("inf")
    min_tcp_table_clearance = float("inf")
    min_frame_table_clearance = float("inf")
    min_self_sphere_clearance = float("inf")

    for q in q_plan:
        tcp_position, tcp_rotation = tcp_pose_function(q)
        tcp_position = np.asarray(tcp_position, dtype=float).reshape(3)
        tcp_rotation = np.asarray(tcp_rotation, dtype=float)
        min_tcp_top_z = min(min_tcp_top_z, float(tcp_rotation[2, 2]))
        min_tcp_table_clearance = min(min_tcp_table_clearance, float(tcp_position[2] - table_height))

        pin.forwardKinematics(robot.model, data, q)
        pin.updateFramePlacements(robot.model, data)
        frame_positions = []
        for frame_id in existing_frame_ids:
            position = np.asarray(data.oMf[frame_id].translation, dtype=float)
            frame_positions.append(position)
            min_frame_table_clearance = min(min_frame_table_clearance, float(position[2] - table_height))

        for i in range(len(frame_positions)):
            for j in range(i + 3, len(frame_positions)):
                clearance = float(np.linalg.norm(frame_positions[i] - frame_positions[j]) - 2.0 * sphere_radius)
                min_self_sphere_clearance = min(min_self_sphere_clearance, clearance)

    return {
        "min_tcp_top_z": min_tcp_top_z,
        "ring_top_faces_ground": bool(min_tcp_top_z < 0.0),
        "min_tcp_table_clearance_m": min_tcp_table_clearance,
        "min_frame_table_clearance_m": min_frame_table_clearance,
        "min_self_sphere_clearance_m": min_self_sphere_clearance,
        "table_height_m": float(table_height),
        "self_sphere_radius_m": float(sphere_radius),
    }
