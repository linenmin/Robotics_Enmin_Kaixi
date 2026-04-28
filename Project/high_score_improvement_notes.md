# High-Score Improvement Notes

## Initial Professor-Style Review

### Strong Points

- Task 1 uses a defensible linear Kalman filter with known gravity and Gaussian position noise.
- Task 3 uses a finite-horizon NLP with explicit `q`, `dq`, and `ddq` variables.
- Task 4 already compares simple and smart strategies over multiple seeds.
- Meshcat visualizations now show full UR10 geometry and side-view correspondence.

### Main Weaknesses

- Task 4 currently proves higher success rate more strongly than shorter interception time.
- The simple and smart strategies do not use exactly the same candidate pool in the current benchmark.
- Success is still mostly measured by terminal `tcp` error, not by direct hoop-plane crossing.
- Collision handling is approximate and must not be overstated.
- Some figures are still debugging figures rather than final report figures.

### Key Decision

Do not jump directly to the report. First strengthen the experimental evidence, then rebuild report figures, then write the report.

## Phase 1 Result

The fair benchmark changed the Task 4 interpretation.

| Strategy | Success Rate | Mean Successful Time [s] | Mean Successful Error [m] | Mean Max Accel [rad/s^2] | Mean Velocity Ratio |
|---|---:|---:|---:|---:|---:|
| simple_geometric | 0.00 | n/a | n/a | n/a | n/a |
| earliest_nlp_feasible | 0.98 | 1.386 | 0.00944 | 1.9998 | 0.481 |
| smart_cost | 0.98 | 1.429 | 0.00154 | 1.5126 | 0.328 |

Professor-style interpretation: smart cost should not claim shorter time than earliest feasible. It should claim comparable success rate, much lower terminal error, and lower control usage. The "shorter interception time" part should be handled by reporting earliest feasible as a time-minimizing feasible baseline.

## Phase 2 Result

The success definition now uses direct hoop-plane crossing.

| Strategy | Success Rate | Mean Successful Time [s] | Mean Radial Error [m] | Mean Max Accel [rad/s^2] | Mean Velocity Ratio |
|---|---:|---:|---:|---:|---:|
| simple_geometric | 0.00 | n/a | n/a | n/a | n/a |
| earliest_nlp_feasible | 0.96 | 1.383 | 0.0104 | 1.9999 | 0.494 |
| smart_cost | 0.96 | 1.429 | 0.00613 | 1.5025 | 0.321 |

Professor-style interpretation: direct hoop crossing slightly lowers the success rate from the Phase 1 proxy. The result is still strong because both feasible strategies stay far below the 0.03 m effective radial tolerance on average. The report must distinguish time-minimizing feasible selection from cost-minimizing smart selection.

## Phase 3 Result

The full pipeline wrapper now gives one-command reproducibility for a seed.

For seed 0:

- simple_geometric fails at `1.300 s`;
- earliest_nlp_feasible succeeds at `1.380 s` with radial error `0.00304 m`;
- smart_cost succeeds at `1.420 s` with radial error `0.00187 m`;
- smart_cost uses lower acceleration and velocity ratio.

Professor-style interpretation: this wrapper helps defend reproducibility. It does not by itself prove real-time operation, and the report should keep the distinction between offline computation and simulation-time catch clear.

## Phase 4 Result

The high-score benchmark now reports safety clearance fields, not only a binary violation count.

For smart_cost successful cases:

- minimum tcp table clearance: `0.441 m`;
- minimum frame table clearance: `0.115 m`;
- minimum self-sphere clearance: `0.149 m`.

Professor-style interpretation: this is still conservative geometric evidence, not full mesh collision checking. The report should say conservative clearance approximation and avoid claiming exact collision-free proof.

## Phase 5 Result

Task 1 now has multi-seed evidence.

- Measurement RMSE mean: `0.00174 m`.
- Filtered RMSE mean: `0.000900 m`.
- Future prediction RMSE mean over 0.5 s: `0.00351 m`.
- 95th percentile future prediction RMSE: `0.00635 m`.

Professor-style interpretation: this is a strong result for the estimator. It shows the filter reduces measurement noise and keeps future prediction error well below the 3 cm hoop tolerance over the horizon used for interception selection.

## Phase 6 Result

Two report-level figures are ready:

- `outputs/high_score/figure_strategy_benchmark.png`
- `outputs/high_score/figure_task2_task4_side_by_side.png`

Professor-style interpretation: these figures are stronger than the earlier debugging plots. The strategy benchmark makes the tradeoff explicit. The side-by-side figure connects the abstract trajectory selection plot to the physical UR10 geometry.
