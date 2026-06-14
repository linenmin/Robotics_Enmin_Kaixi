import unittest

import numpy as np

from strategy_benchmark import (
    CandidateEvaluation,
    summarize_strategy_rows,
    select_earliest_nlp_feasible,
    select_latest_nlp_feasible,
    select_simple_geometric,
    select_smart_cost,
)


def candidate(index, time, feasible, terminal_error, max_abs_ddq=1.0, max_velocity_ratio=0.2):
    return CandidateEvaluation(
        seed=0,
        index=index,
        time=time,
        position=np.array([time, 0.0, 1.0]),
        geometric_status="accepted",
        nlp_success=feasible,
        passes_hoop=True,
        terminal_error=terminal_error,
        max_abs_ddq=max_abs_ddq,
        max_abs_ddq_joint=3,
        max_velocity_ratio=max_velocity_ratio,
        max_velocity_ratio_joint=2,
        safety_penalty=0.0,
        solver_status="fake",
        solve_time_s=0.12,
        iter_count=14,
        terminal_normal_alignment=0.8,
        plane_crossing_exists=feasible,
        crossing_time=time,
        radial_error=terminal_error,
        effective_tolerance=0.03,
        crossing_reason="passes_through_hoop" if feasible else "outside_effective_radius",
    )


class StrategyBenchmarkTest(unittest.TestCase):
    def test_strategies_select_from_the_same_candidate_pool(self):
        candidates = [
            candidate(0, 1.00, False, 0.20),
            candidate(1, 1.20, True, 0.020, max_abs_ddq=1.9),
            candidate(2, 1.30, True, 0.007, max_abs_ddq=0.8),
            candidate(3, 1.40, True, 0.005, max_abs_ddq=0.5),
        ]

        simple = select_simple_geometric(candidates)
        earliest = select_earliest_nlp_feasible(candidates)
        latest = select_latest_nlp_feasible(candidates)
        smart = select_smart_cost(candidates)

        self.assertEqual(simple.selected_index, 0)
        self.assertFalse(simple.success)
        self.assertEqual(earliest.selected_index, 1)
        self.assertTrue(earliest.success)
        self.assertEqual(latest.selected_index, 3)
        self.assertTrue(latest.success)
        self.assertEqual(smart.selected_index, 2)
        self.assertTrue(smart.success)
        self.assertEqual(simple.candidate_pool_size, 4)
        self.assertEqual(earliest.candidate_pool_size, 4)
        self.assertEqual(latest.candidate_pool_size, 4)
        self.assertEqual(smart.candidate_pool_size, 4)

    def test_summary_reports_success_rate_and_time_statistics(self):
        rows = [
            select_simple_geometric([candidate(0, 1.0, False, 0.20)]).to_row(seed=0),
            select_simple_geometric([candidate(0, 1.1, True, 0.02)]).to_row(seed=1),
            select_earliest_nlp_feasible([candidate(0, 1.2, True, 0.01)]).to_row(seed=0),
            select_earliest_nlp_feasible([candidate(0, 1.4, True, 0.02)]).to_row(seed=1),
        ]

        summary = summarize_strategy_rows(rows)

        self.assertEqual(summary["simple_geometric"]["n"], 2)
        self.assertEqual(summary["simple_geometric"]["success_count"], 1)
        self.assertAlmostEqual(summary["simple_geometric"]["success_rate"], 0.5)
        self.assertAlmostEqual(summary["earliest_nlp_feasible"]["mean_success_catch_time_s"], 1.3)
        self.assertAlmostEqual(summary["earliest_nlp_feasible"]["mean_success_radial_error_m"], 0.015)
        self.assertAlmostEqual(summary["earliest_nlp_feasible"]["mean_success_solve_time_s"], 0.12)
        self.assertAlmostEqual(summary["earliest_nlp_feasible"]["mean_success_iter_count"], 14.0)
        self.assertGreater(summary["earliest_nlp_feasible"]["std_success_catch_time_s"], 0.0)


if __name__ == "__main__":
    unittest.main()
