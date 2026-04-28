# Robotics Project Progress

## 2026-04-28

### Completed

- 阅读并应用 `pi-planning-with-files` 技能，开始使用落盘计划文件。
- 阅读并应用 `agent-discord-notify` 技能，确认任务完成后需要尝试 Discord 通知。
- 阅读并应用 `project-env-manager` 技能，检查项目环境记录。
- 检查 `Robotics/Project` 文件结构。
- 阅读 `hoops_description.pdf`。
- 阅读 `exercise_0_software_environment/README.md`。
- 抽取 `0_setup.ipynb` 和 `software/hoops.ipynb` 内容。
- 阅读 `utils/ball_simulation.py` 和 `utils/transformations.py`。
- 初步检查 `ur10_robot.urdf` 结构。
- 列出 Robotics 课程课件和作业文件。
- 检查本机 Conda 环境列表。
- 测试现有 Conda 环境是否包含项目关键依赖。
- 创建 `task_plan.md`、`findings.md`、`progress.md`。

### Conda Environment Check

Command:

```powershell
conda env list
```

Found:

- `base`
- `gpu_env`
- `raw2Event`
- `tf_work_hpc`
- `vela`

Checked imports:

```python
import numpy, casadi, pinocchio, meshcat, matplotlib
```

Result:

- Existing environments failed at least on `casadi`.
- Current recommendation: create dedicated `py13roboticscourse` environment from the provided YAML.

### Conceptual Clarification

“不要求实时运行” means computation time is not graded as a real-time constraint. It does not mean the physical interception can happen after the ball lands. The simulated ball still follows time-indexed physics; the algorithm must choose an interception before the useful part of the trajectory ends.

### Files Created

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\task_plan.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\findings.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\progress.md`

### Next

1. Create or confirm the dedicated Conda environment.
2. Run `0_setup.ipynb`.
3. Run `software/hoops.ipynb` until Meshcat visualization opens.
4. Extract high-value course material from C3/C4/C5/C6.
5. Convert findings into a concrete implementation and debugging protocol.

### Environment Setup Completed

Created Conda environment:

```powershell
conda env create -n robotics -f D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\py13roboticscourse_env.yml
```

Verified:

```powershell
conda run -n robotics python --version
```

Result:

```text
Python 3.13.13
```

Core package smoke test passed:

```python
import numpy, casadi, matplotlib, pandas, pinocchio, meshcat
from pinocchio import casadi as cpin
```

### Notebook Verification

Executed successfully:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\0_setup.ipynb`
- Output: `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\0_setup.executed.ipynb`

Executed successfully:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\software\hoops.ipynb`
- Output: `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\software\hoops.executed.ipynb`

### Environment Fixes Applied

The provided Conda YAML installed `example-robot-data`, but on Windows/Python 3.13 the import `from example_robot_data import load` was not initially available.

Fixes:

- Installed loader only:

```powershell
conda run -n robotics python -m pip install --no-deps example-robot-data-loaders
```

- Added path file:

```text
D:\Anaconda3\envs\robotics\Lib\site-packages\example_robot_data_loaders.pth
```

- Patched:

```text
D:\Anaconda3\envs\robotics\Lib\site-packages\cmeel.prefix\lib\python3.13\site-packages\example_robot_data\path.py
```

to point to:

```text
D:/Anaconda3/envs/robotics/Library/share/example-robot-data/robots
```

### Known Conditions Table

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\known_conditions.md`

Contents include:

- task summary and scene objects
- ball simulation parameters
- UR10 joint names, limits, and initial configuration
- control loop frequencies and simulation duration
- hard constraints from the PDF
- currently implemented modules vs missing modules
- first-version implementation roadmap

Key discovery:

- the platform is not mobile; `world_joint` is fixed, and there are no wheel/mobile-base joints in the URDF.
- the current notebook uses `np.clip(...)` without assignment, so limit clipping is not actually applied yet.

### Course Knowledge Map

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_knowledge_map.md`

Rendered key lecture pages into visual contact sheets:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_page_images\task1_state_estimation.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_page_images\task2_interception_planning.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_page_images\task3_optimization_control.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_page_images\task3_constraints.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\course_page_images\task4_smarter_strategy.png`

Mapped the project tasks to:

- C6 Bayes/Kalman filtering and tracking process models for ball trajectory prediction.
- C5 motion planning, signed distance functions, optimal control, and sampling for interception point selection.
- C3 task-space control, resolved acceleration control, damped pseudo-inverse, and stack of tasks for robot control.
- C4 constraint-based programming for acceleration/velocity/position constraints and instantaneous optimization.
- C3 minimum jerk notes for the tradeoff between shorter interception time and higher peak velocity/acceleration.

### Agent Protocol and Report Template

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\AGENT_PROTOCOL.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\titlepage.tex`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\assets\sedes.pdf`

Protocol decisions:

- each PDF task uses a 5-phase workflow: Task Brief, Decision Memo, Implementation, Result Review, Report Integration.
- decision memos must stay under 500 Chinese words and present options when there is a real tradeoff.
- report text must be in English, concise, direct, and tied to course vocabulary.
- final LaTeX output must use Tectonic when available, then PDF pages must be rendered to images for visual inspection.

Tectonic status:

- `tectonic` was not found on the current `PATH`.
- search under `D:\BaiduNetdiskWorkspace\Leuven\8th\ANN & DL` did not find a `tectonic` executable.
- found Codex plugin Tectonic at `C:\Users\Lem17\.codex\plugins\cache\openai-bundled\latex-tectonic\0.1.0\bin\tectonic.exe`.
- verified Tectonic 0.16.9 can compile `Project/report_template/template.tex`.

### Task 1 Entry

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task1_decision_memo.md`

Decision memo recommendation:

- implement a linear Kalman filter for ball trajectory prediction.
- use state `[px, py, pz, vx, vy, vz]`.
- treat gravity as a known input.
- use the measured ball position as the Kalman measurement.
- validate with measured/filtered/predicted trajectory plots and prediction error checks.

Protocol update:

- every decision memo must now define explicit task completion criteria before implementation starts.
- result reviews must compare implementation results against those criteria.

### Task 1 Implementation

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\trajectory_predictor.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_trajectory_predictor.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\validate_task1_prediction.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task1_result_review.md`

Verification:

```powershell
conda run -n robotics python -m unittest tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task1_prediction.py --seed 7 --output-dir ..\outputs\task1
```

Results:

- unit tests passed: 2 tests.
- measurement RMSE: `0.001815 m`.
- filtered RMSE: `0.000981 m`.
- covariance symmetric: `true`.
- minimum covariance eigenvalue: `1.46e-07`.
- predictions contain only future timestamps and no NaN.

Generated evidence:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task1\task1_metrics.json`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task1\task1_trajectory_prediction.png`

### Task 2 Entry

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task2_decision_memo.md`

Decision memo recommendation:

- implement a simple interception point selector.
- sample candidate points from the Task 1 predicted trajectory.
- filter by future time, height, rough workspace distance, and distance from the initial `tcp`.
- choose the earliest feasible candidate.
- keep strict joint/collision feasibility for Task 3 and smarter scoring for Task 4.

### Task 2 Implementation

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\interception_selector.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_interception_selector.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\validate_task2_interception.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task2_result_review.md`

Verification:

```powershell
conda run -n robotics python -m unittest tests.test_interception_selector tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task2_interception.py --seed 7 --output-dir ..\outputs\task2
```

Results:

- unit tests passed: 6 tests.
- selected index: `23`.
- selected time: `1.280 s`.
- selected position: `[1.447, -0.113, 1.632] m`.
- selected point comes from predicted trajectory, is future-only, is above `z_min`, and has no NaN.

Generated evidence:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task2\task2_metrics.json`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task2\task2_interception_selection.png`

Task 2 threshold update:

- `max_tcp_distance` default changed from `1.35 m` to `0.85 m` after Task 3 feasibility testing.
- The selected point changed to index `27`, time `1.360 s`, position `[1.224, -0.119, 1.074] m`.
- This remains a simple feasibility filter, not Task 4 smarter scoring.

### Task 3 Entry

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task3_decision_memo.md`

Decision memo recommendation:

- user approved switching Task 3 from方案 A to方案 B for higher score potential.
- implement a multi-step optimal-control NLP with `q,dq,ddq` over a horizon.
- first build a runnable layer with discrete dynamics, joint limits, terminal `tcp` objective, and control smoothness.
- then add ring orientation and conservative table/bounding-sphere safety metrics.
- validate table/ring/self-collision with conservative geometric approximations first, because the loaded collision model currently has zero collision pairs.

### Task 3 Implementation

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\optimal_control_planner.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_optimal_control_planner.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_safety_metrics.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\validate_task3_nlp_layer1.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task3_result_review.md`

Verification:

```powershell
conda run -n robotics python -m unittest tests.test_safety_metrics tests.test_optimal_control_planner tests.test_interception_selector tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task3_nlp_layer1.py --task2-metrics ..\outputs\task2\task2_metrics.json --output-dir ..\outputs\task3 --horizon-steps 28 --dt 0.05
```

Results:

- unit tests passed: 9 tests.
- solver status: `Solve_Succeeded`.
- terminal tcp-target error: `0.020 m`.
- max absolute acceleration: `1.9996 rad/s^2`.
- joint position, velocity, and acceleration limits satisfied.
- ring top does not face the ground: `min_tcp_top_z = 0.732`.
- table and approximate self-sphere safety metrics are positive.

Generated evidence:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task3\task3_layer1_metrics.json`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task3\task3_layer1_plan.png`

### Git Checkpoint

Committed and pushed current Project work:

```text
985ff5e feat(project): add robotics task planning and controllers
```

Branch:

```text
main -> origin/main
```

### Task 4 Entry

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task4_decision_memo.md`

Decision memo recommendation:

- implement a two-stage smarter interception selector.
- first run a cheap geometric prefilter over candidate trajectory points.
- then run Task 3 NLP feasibility/cost scoring on a short list of candidates.
- compare simple vs smart by terminal error, catch time, max acceleration, velocity ratio, and safety metrics.
- upgrade validation from a single seed to a multi-seed benchmark, because the report needs evidence for success rate and not only one selected example.

### Task 4 Implementation

Created:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\smart_interception_selector.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_smart_interception_selector.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\benchmark_task4_strategy.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task4_result_review.md`

Verification:

```powershell
conda run -n robotics python -m unittest tests.test_safety_metrics tests.test_optimal_control_planner tests.test_interception_selector tests.test_trajectory_predictor tests.test_smart_interception_selector
conda run -n robotics python scripts\benchmark_task4_strategy.py
```

Results:

- unit tests passed: 13 tests.
- benchmark seeds: 0 through 9.
- simple strategy success rate: `0.00`.
- smart strategy success rate: `1.00`.
- simple mean attempt terminal error: `0.257 m`.
- smart mean terminal error: `0.00136 m`.
- simple mean attempt catch time: `1.340 s`.
- smart mean catch time: `1.428 s`.
- smart mean max acceleration: `1.495 rad/s^2`.
- smart mean velocity ratio: `0.329`.
- smart constraint violations: `0`.

Generated evidence:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_benchmark.json`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_simple_vs_smart.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_candidate_scores.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_smart_catch_seed0.gif`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_meshcat_replay_seed0.html` (local standalone Meshcat replay, intentionally ignored by git because it is large)
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_report_mesh_scene_seed0_cropped.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_report_mesh_scene_seed0_side_cropped.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\task4\task4_side_mesh_with_task2_markers_cropped.png`

Full UR10 Meshcat replay:

```powershell
conda run -n robotics python scripts\replay_task4_meshcat.py --seed 0
```

Report static UR10 mesh scene:

```powershell
conda run -n robotics python scripts\render_task4_meshcat_report_scene.py --seed 0
conda run -n robotics python scripts\render_task4_meshcat_report_scene.py --seed 0 --camera-view side --output-html ..\outputs\task4\task4_report_mesh_scene_seed0_side.html
conda run -n robotics python scripts\render_task4_meshcat_report_scene.py --seed 0 --camera-view side --show-target-markers --simple-max-distance 1.0 --output-html ..\outputs\task4\task4_side_mesh_with_task2_markers.html
```

### Phase 7 Report Integration

Final report integration completed.

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\high_score_improvement_plan.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\task_plan.md`

Generated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report.pdf`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-1.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-2.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-3.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-4.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-5.png`

Verification:

```powershell
C:\Users\Lem17\.codex\plugins\cache\openai-bundled\latex-tectonic\0.1.0\bin\tectonic.exe --outdir build template.tex
pdftoppm -png -r 150 build\template.pdf build\pages\page
```

Result:

- Tectonic compilation succeeded.
- Exported 5 pages total: title page, 3 body pages, and references.
- Body page count is below the 8-page limit.
- Visual page inspection passed for figure placement, caption readability, table width, and obvious overflow.

### Phase 7 Professor-Style Report Revision

After strict review, the first report draft was technically correct but too compressed. It answered the tasks, but the task logic was not easy enough for a grader to scan. The revised report now uses explicit task sections and a question-answer evidence map.

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report.pdf`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-1.png` through `page-7.png`

Revision changes:

- added a report map table that links each PDF task to the submitted answer and evidence;
- rewrote each task as `Question answered`, `Method`, `Evidence`, and where needed `Limitation`;
- added the Task 3 NLP trajectory figure so the optimization controller has direct visual evidence;
- expanded Task 4 to separate the fair benchmark, the time-vs-effort tradeoff, and the smart-vs-earliest-feasible interpretation;
- kept the report within the body limit: title page, 5 body pages, and references.

Verification:

- Tectonic compilation succeeded.
- Exported 7 pages total.
- Body pages are pages 2-6, 5 pages total.
- Visual inspection passed after fixing the report-map table spacing.
- Banned wording and sentence-pattern scan returned no matches.
