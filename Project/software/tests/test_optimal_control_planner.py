import unittest
from pathlib import Path

import numpy as np

from optimal_control_planner import (
    JointLimits,
    MultiStepNLPController,
    build_tcp_pose_function,
    load_project_robot,
)


class MultiStepNLPControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.software_dir = Path(__file__).resolve().parents[1]
        cls.robot = load_project_robot(cls.software_dir)
        cls.tcp_pose = build_tcp_pose_function(cls.robot)

    def test_plans_feasible_trajectory_for_nearby_tcp_target(self):
        q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
        dq0 = np.zeros(6)
        current_tcp, _ = self.tcp_pose(q0)
        target = np.asarray(current_tcp).reshape(3) + np.array([0.03, 0.0, 0.02])

        controller = MultiStepNLPController(
            robot=self.robot,
            tcp_pose_function=self.tcp_pose,
            horizon_steps=8,
            dt=0.05,
        )
        result = controller.plan(q0=q0, dq0=dq0, target_position=target)

        self.assertTrue(result.success, result.status)
        self.assertEqual(result.q.shape, (9, 6))
        self.assertEqual(result.dq.shape, (9, 6))
        self.assertEqual(result.ddq.shape, (8, 6))
        self.assertTrue(np.all(np.isfinite(result.q)))
        self.assertTrue(np.all(np.isfinite(result.dq)))
        self.assertTrue(np.all(np.isfinite(result.ddq)))
        self.assertLess(result.terminal_error, 0.08)
        self.assertGreaterEqual(result.solve_time_s, 0.0)
        self.assertIsInstance(result.iter_count, int)
        self.assertGreaterEqual(result.min_tcp_top_z, -1e-7)

    def test_accepts_terminal_normal_alignment_objective(self):
        q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
        dq0 = np.zeros(6)
        current_tcp, _ = self.tcp_pose(q0)
        target = np.asarray(current_tcp).reshape(3) + np.array([0.02, 0.0, 0.02])

        controller = MultiStepNLPController(
            robot=self.robot,
            tcp_pose_function=self.tcp_pose,
            horizon_steps=6,
            dt=0.05,
        )
        result = controller.plan(
            q0=q0,
            dq0=dq0,
            target_position=target,
            target_normal=np.array([1.0, 0.0, 0.0]),
            normal_alignment_weight=1.0,
        )

        self.assertTrue(result.success, result.status)
        self.assertTrue(np.isfinite(result.terminal_normal_alignment))

    def test_planned_trajectory_respects_joint_limits(self):
        q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
        dq0 = np.zeros(6)
        current_tcp, _ = self.tcp_pose(q0)
        target = np.asarray(current_tcp).reshape(3) + np.array([0.02, 0.01, 0.02])

        controller = MultiStepNLPController(
            robot=self.robot,
            tcp_pose_function=self.tcp_pose,
            horizon_steps=6,
            dt=0.05,
        )
        result = controller.plan(q0=q0, dq0=dq0, target_position=target)
        limits = JointLimits.from_robot(self.robot)

        self.assertTrue(result.success, result.status)
        self.assertLessEqual(np.max(np.abs(result.ddq)), limits.acceleration[0] + 1e-7)
        self.assertGreaterEqual(result.min_tcp_top_z, -1e-7)
        self.assertTrue(np.all(result.dq <= limits.velocity + 1e-7))
        self.assertTrue(np.all(result.dq >= -limits.velocity - 1e-7))
        self.assertTrue(np.all(result.q <= limits.upper + 1e-7))
        self.assertTrue(np.all(result.q >= limits.lower - 1e-7))


if __name__ == "__main__":
    unittest.main()
