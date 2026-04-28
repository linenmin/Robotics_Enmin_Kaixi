import unittest
from pathlib import Path

import numpy as np

from optimal_control_planner import build_tcp_pose_function, evaluate_plan_safety, load_project_robot


class SafetyMetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.software_dir = Path(__file__).resolve().parents[1]
        cls.robot = load_project_robot(cls.software_dir)
        cls.tcp_pose = build_tcp_pose_function(cls.robot)

    def test_initial_pose_has_upward_tcp_top_axis_and_table_clearance(self):
        q0 = np.array([0.0, -1.9, 1.9, -1.6, -1.6, 0.0])
        q_plan = np.vstack([q0, q0])

        metrics = evaluate_plan_safety(self.robot, self.tcp_pose, q_plan)

        self.assertGreater(metrics["min_tcp_top_z"], 0.0)
        self.assertGreater(metrics["min_tcp_table_clearance_m"], 0.0)
        self.assertFalse(metrics["ring_top_faces_ground"])


if __name__ == "__main__":
    unittest.main()
