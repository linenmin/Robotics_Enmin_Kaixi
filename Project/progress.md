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

### Phase 7 Experiment-Rationale Revision

User feedback: the report-map table was unnecessary for a short report, and the report needed more visible experimental reasoning. The revised report removes the map and uses the space for experiment design choices.

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report_revised.pdf`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\rendered_pages\page-1.png` through `page-7.png`

Revision changes:

- removed the report-map table;
- added a short experimental-design paragraph in the setup section;
- expanded Task 1 to explain why the validation uses measurement RMSE, filtered RMSE, future-prediction RMSE, and covariance checks;
- expanded Task 2 to explain the purpose of the simple baseline, the rough workspace threshold, and the rejection-count evidence;
- expanded Task 3 to explain why a finite-horizon NLP was chosen instead of a single-step pseudo-inverse controller;
- expanded Task 4 to explain why the experiment compares simple geometric, earliest NLP-feasible, and smart cost strategies on the same candidate pool.

Verification:

- Tectonic compilation succeeded.
- Exported 7 pages total.
- Body pages are pages 2-6, 5 pages total.
- Visual inspection passed for the revised setup, Task 2/3 transition, Task 4 benchmark page, and final summary page.
- Banned wording and sentence-pattern scan returned no matches.
- `final_report.pdf` could not be overwritten because another process had the file open, so the current compiled revision is saved as `final_report_revised.pdf`.

### Research-Grade Report Revision

根据第四轮严格审查，完成了一次结构性升级，而不是小修：

- 将报告主线改为可证伪 thesis：核心瓶颈是 feasibility-aware candidate selection，而不是单纯估计器或控制器。
- 将 Task 标题改成功能性标题，并保留 `addresses Task X`，方便老师按 PDF 核分。
- 明确 open-loop 架构，并分离 planner terminal error、predicted radial error、true-ball radial error。
- 新增 no-prediction reactive baseline：50 seeds 成功率 0%，平均 closest TCP-ball distance 为 `0.176 m`。
- 将最终 benchmark 的成功判据改为真实球轨迹的 hoop-plane crossing，而不是预测轨迹 crossing。
- 新增 KF covariance diagnostic：协方差主要随预测时间单调增长，未改善 failure seed 区分，因此保留为诊断而非最终 selector 主项。
- 新增 geometry definition figure、candidate-selection Pareto/tradeoff figure、failure velocity diagnostic figure。
- 更新课程知识点对齐段：C4 constraint-based programming、C5 direct-transcription optimal control、C3 RAC/SOT/minimum-jerk 对照。

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\trajectory_predictor.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\strategy_benchmark.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\benchmark_high_score_strategies.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\benchmark_reactive_baseline.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\render_high_score_figures.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`

Generated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report_research_grade_v3.pdf`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\high_score\reactive_baseline.json`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\high_score\figure_hoop_geometry_definition.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\high_score\figure_candidate_pareto.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\high_score\figure_failure_velocity_diagnostics.png`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\outputs\high_score\candidate_pareto_scan.json`

Verification:

- `conda run -n robotics python -m unittest discover -s tests` passed: 19 tests.
- Tectonic compilation succeeded.
- Final PDF has 7 pages total: title page, 5 body pages, references.
- Rendered PDF pages inspected for text overflow and figure/table readability.
- Banned wording and first-person scan returned no matches.

### Sixth Review High-Score Revision

根据第六轮严格审查，完成以下非小修级改进：

- 删除报告中会误导读者的 KF covariance 具体毫米数，改为说明 covariance 在当前 process-noise setting 下偏保守，最终只作为 diagnostic。
- 将 balanced cost 从 late-like 策略重新调成真实中间 Pareto 点：50-seed success rate 仍为 `98%`，平均成功接球时间 `1.411 s`，平均 radial error `5.91 mm`。
- 将 Pareto scan 改为与 final smart cost 相同的 cost 形式，避免图和表使用两套权衡逻辑。
- 重跑主 benchmark、reactive baseline 和 high-score figures。
- 补充报告中的候选过滤证据：396 个 candidate NLP 全部收敛，164 个通过 hoop-crossing check，平均每个 seed 7.9 个候选、3.3 个可行 catch。
- 补充 \(w_o\in\{0,1,10,50\}\) orientation soft-cost ablation：time-first success rate 都为 `98%`，说明 hard top-side constraint 和 pose-aware normal term 决定最终几何。
- 按用户要求删除报告中的 git/commit 相关 reproducibility 文字。

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\strategy_benchmark.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\benchmark_high_score_strategies.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\render_high_score_figures.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_strategy_benchmark.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`

Generated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report_research_grade_v5.pdf`
- refreshed `Project\outputs\high_score\strategy_benchmark.json`
- refreshed `Project\outputs\high_score\strategy_summary_table.csv`
- refreshed `Project\outputs\high_score\figure_candidate_pareto.png`
- refreshed `Project\outputs\high_score\figure_strategy_benchmark.png`
- refreshed `Project\outputs\high_score\figure_failure_velocity_diagnostics.png`
- orientation ablation outputs under `Project\outputs\high_score\orientation_w0`, `orientation_w1`, `orientation_w10`, and `orientation_w50`

Verification:

- `conda run -n robotics python -m unittest discover -s tests` passed: 20 tests.
- Banned wording, first-person, `git`, and `commit` report scan returned no matches.
- Tectonic compilation succeeded.
- Final PDF has 7 pages total: title page, 5 body pages, references.
- Exported PDF pages to PNG and inspected the setup page, Task 1/2/3 pages, Task 4 table/Pareto page, and final failure-analysis page.

### Seventh Review Final Polish

根据第七轮最终审查，完成低风险但能提高严谨性的最终润色：

- 在 reactive baseline 公式后补充 \(K\) 为 proportional gain，\(\lambda\) 为 damping。
- 在 Task 3 中明确定义 hoop open side：沿 \(+n_{\mathrm{hoop}}\) 方向，球必须从该侧穿过 hoop plane。
- 在 Task 4 中加入量化 thesis 句：feasibility-aware selection 相比 simple attempted catch 只多约 `92 ms`，但成功率从 `0%` 提升到 `98%`。
- 将 Pareto caption 改为 empirical candidate-weight scan，避免被误读成理论 Pareto frontier。
- 扩展 URDF 修正的失败机制叙述：seed 11 best radial error 从 `145.2 mm` 降到 `51.5 mm`，seed 41 恢复到 `24.7 mm` 成功 crossing。
- 更新 failure caption，明确 seed 11 接近 lateral velocity 的 95th percentile，失败机制是 geometry 而非 estimator/NLP。

Generated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report_research_grade_v6.pdf`
- rendered page images under `Project\report_template\rendered_pages\research_grade_v6-*.png`

Verification:

- `conda run -n robotics python -m unittest discover -s tests` passed: 20 tests.
- Banned wording, first-person, `git`, and `commit` report scan returned no matches.
- Tectonic compilation succeeded.
- Final PDF has 7 pages total: title page, 5 body pages, references.
- Rendered pages 3--6 inspected for the changed formula text, Task 4 tradeoff page, and final failure-analysis page.

### Final Review Fixes

第五轮严格审查后的最终修复已完成：

- 修复 Task 3 优化公式中缺失的三个 `+` 号。
- 重新核对 URDF frame 映射：`hoop_ring.stl` 的薄轴在 `tool_link` 的 \(x\)-axis，`tcp_joint` 将该物理 hoop normal 映射到 `tcp` 的 \(z\)-axis。
- 将 benchmark 中的 hoop-plane crossing normal 和 terminal normal-alignment objective 从 `tcp x` 修正为 `tcp z`，与 top-side path constraint \(R_{zz}\ge0\) 统一。
- 重跑 50-seed benchmark：time-first feasible success rate 从 96% 提升到 98%，失败 seed 从 11/41 变为仅 seed 11。
- 删除报告表格中的 covariance guard 冗余行，将其改为 Task 1 中的 covariance diagnostic。
- 补充 Task 4 中 time-first vs late/balanced 的 tradeoff 解释，以及 model-execution gap 数字的一致性解释。
- 更新 failure analysis：seed 11 best radial error 为 `51.5 mm`，16-candidate / 1.35 m workspace mitigation 仍未恢复。

Updated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\optimal_control_planner.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\benchmark_high_score_strategies.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\render_evidence_figures.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\scripts\render_high_score_figures.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\software\tests\test_optimal_control_planner.py`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\template.tex`

Generated:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\homework\Project\report_template\final_report_research_grade_v4.pdf`
- refreshed high-score benchmark and figure outputs under `Project\outputs\high_score`

Verification:

- `conda run -n robotics python -m unittest discover -s tests` passed: 20 tests.
- Tectonic compilation succeeded.
- Final PDF has 7 pages total: title page, 5 body pages, references.
- Rendered pages inspected for formula readability, Task 4 table, Pareto figure, and failure figure.
- Banned wording and first-person scan returned no matches.
