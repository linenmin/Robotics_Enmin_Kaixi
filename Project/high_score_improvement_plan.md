# High-Score Improvement Plan

## Goal

把当前可运行的 Task 1-4 系统升级成更接近高分报告标准的实验与可视化证据链。核心目标不是多堆图，而是让每个实验都直接回答 PDF 要求，并能经得起严格教授质疑。

## Guiding Standard

- 不把单 seed 结果当成强证据。
- 不把 `tcp` 到球心的距离自动等同于“球穿过篮筐”。
- 不把 Task 4 写成单纯参数调优。
- 不隐藏失败样本。
- 不牺牲 8 页报告空间，图表必须承担明确证据功能。

## Phase 1: 统一实验定义与公平 baseline

**Status:** completed

### 目标

重构 Task 4 benchmark，让 simple、earliest feasible、smart 三种策略使用同一个候选池和同一个 NLP evaluator。

### 要做

- 固定候选池：同一条预测轨迹、同一批时间点、同一组高度/时间基础过滤。
- 定义三种策略：
  - `simple_geometric`: Task 2 风格，最早通过几何过滤的候选点。
  - `earliest_nlp_feasible`: 最早满足 NLP 成功和 hoop tolerance 的候选点。
  - `smart_cost`: 在可行候选点中按时间、误差、加速度、速度、安全代价评分。
- 多 seed benchmark 默认 50 seeds，可通过参数跑 100 seeds。
- 输出每个 seed 的候选点表、策略选择表、失败原因表。

### 验收标准

- 三种策略使用相同 candidate pool。
- 每个策略都有 success rate、mean/std catch time、mean/std terminal error、constraint violation count。
- 若 smart 比 earliest feasible 更晚，必须有更低控制代价或更大安全裕度解释。

### 主要产物

- `software/scripts/benchmark_high_score_strategies.py`
- `outputs/high_score/strategy_benchmark.json`
- `outputs/high_score/strategy_summary_table.csv`

### 结果

- 50 seeds completed.
- `simple_geometric`: success rate `0.00`, mean attempted catch time `1.295 s`.
- `earliest_nlp_feasible`: success rate `0.98`, mean successful catch time `1.386 s`, mean terminal error `0.00944 m`.
- `smart_cost`: success rate `0.98`, mean successful catch time `1.429 s`, mean terminal error `0.00154 m`.
- Interpretation: smart cost is not faster than earliest feasible. Its stronger claim is lower terminal error and lower control effort at the same success rate. This must be written honestly.

## Phase 2: 增加真正的 hoop crossing 成功指标

**Status:** completed

### 目标

把成功定义从“`tcp` 到目标点小于 3 cm”升级为“球中心穿过篮筐平面且径向误差小于 `hoop_radius - ball_radius`”。

### 要做

- 从篮筐最终位姿得到 hoop center 和 hoop normal。
- 用预测球轨迹或真实仿真轨迹找到穿过 hoop plane 的时刻。
- 计算穿越点到 hoop center 的径向距离。
- 记录：
  - `plane_crossing_exists`
  - `crossing_time_s`
  - `radial_error_m`
  - `effective_tolerance_m = 0.03`
  - `passes_through_hoop`
- 对没有穿越平面的样本保留失败原因。

### 验收标准

- 单元测试覆盖正交穿环、偏心错过、未穿越平面三种情况。
- benchmark success 使用 hoop crossing 指标，而不是只用 terminal error。
- 报告可以清楚解释球半径和篮筐半径只留下 3 cm 容差。

### 主要产物

- `software/hoop_crossing.py`
- `software/tests/test_hoop_crossing.py`
- 更新 high-score benchmark JSON。

### 结果

- 50 seeds completed with hoop-plane crossing success.
- `simple_geometric`: success rate `0.00`.
- `earliest_nlp_feasible`: success rate `0.96`, mean successful radial error `0.0104 m`.
- `smart_cost`: success rate `0.96`, mean successful radial error `0.00613 m`.
- Effective tolerance is `0.03 m` from `0.15 m - 0.12 m`.
- Interpretation: smart cost gives lower radial error and lower control usage. Earliest feasible gives shorter successful catch time.

## Phase 3: 接入完整仿真 replay / controller wrapper

**Status:** completed

### 目标

证明算法不是只在离线脚本里“画到目标点”，而是能形成完整仿真过程：预测、选择、规划、重放。

### 要做

- 建立一个不改教学 notebook 主结构的 Python wrapper。
- 运行顺序：
  1. 用测量更新 Kalman filter；
  2. 生成预测轨迹；
  3. 选择接球点；
  4. 规划 NLP 关节轨迹；
  5. 用 Meshcat replay 展示完整 UR10 和球。
- 记录仿真时间、选择时间、接球时间、最终穿环指标。

### 验收标准

- 能一条命令复现完整 seed replay。
- 输出 Meshcat HTML、报告 PNG、JSON summary。
- 不要求实时计算，但仿真时间逻辑必须一致。

### 主要产物

- `software/scripts/run_full_catch_pipeline.py`
- `outputs/high_score/full_pipeline_seed*.json`
- `outputs/high_score/full_pipeline_mesh_side.png`

### 结果

- `software/scripts/run_full_catch_pipeline.py` created.
- Seed 0 pipeline generated:
  - `outputs/high_score/full_pipeline_seed0.json`
  - `outputs/high_score/full_pipeline_meshcat_replay_seed0.html`
  - `outputs/high_score/full_pipeline_side_scene_seed0.html`
- The wrapper records strategy rows, Meshcat replay output, side-scene output, terminal error, and safety summary.

## Phase 4: 加强安全与碰撞证据

**Status:** completed

### 目标

把当前 “conservative sphere/table approximation” 写得更可信，并尽量增加可验证的安全指标。

### 要做

- 保留当前 table clearance、frame clearance、self-sphere clearance。
- 增加 per-link minimum clearance table。
- 检查 Pinocchio collision model 是否可用；如果 collision pairs 为空，明确记录原因。
- 可选：为关键 link 添加 capsule/sphere 近似，比单个 frame sphere 更贴近实体。

### 验收标准

- 每个成功样本都有最小 table/self clearance。
- 报告不声称 full mesh collision，除非真的实现并验证。
- 若使用近似，必须说明 conservative approximation 的局限。

### 主要产物

- `outputs/high_score/safety_summary.csv`
- 更新 Task 3 / Task 4 result review。

### 结果

- Safety clearance fields are now included in `outputs/high_score/strategy_benchmark.json` and `strategy_summary_table.csv`.
- 50-seed successful smart-cost minimum clearances:
  - min tcp table clearance `0.441 m`;
  - min frame table clearance `0.115 m`;
  - min self-sphere clearance `0.149 m`.
- Interpretation: the evidence remains an approximation, but it is now numeric and reportable.

## Phase 5: 多 seed Task 1 预测质量实验

**Status:** completed

### 目标

把 Task 1 从单 seed 验证升级为稳定的统计证据。

### 要做

- 跑 50 seeds 的 Kalman filter prediction validation。
- 统计 measurement RMSE、filtered RMSE、future prediction error。
- 输出均值、标准差、95th percentile。
- 检查 covariance 是否稳定。

### 验收标准

- 报告 Task 1 不只展示一条轨迹，还能说明 filter 在模拟分布下稳定。
- 图表紧凑，不超过一个小图或一行表。

### 主要产物

- `software/scripts/benchmark_task1_prediction.py`
- `outputs/high_score/task1_prediction_benchmark.json`

### 结果

- 50 seeds completed.
- Mean measurement RMSE: `0.00174 m`.
- Mean filtered RMSE: `0.000900 m`.
- Mean future prediction RMSE over 0.5 s: `0.00351 m`.
- 95th percentile future prediction RMSE: `0.00635 m`.
- Covariance remained symmetric and positive semidefinite across all seeds.

## Phase 6: 报告级可视化重做

**Status:** completed

### 目标

把当前调试图改成报告图。重点是可读性、统一色彩语义、字号、caption 信息量，以及 8 页内的证据密度。

### 要做

- 生成组合图：
  - 左：Task 2 风格 x-z / z-time trajectory plot；
  - 右：同视角 UR10 Meshcat side view，红点 simple，黄点 smart，绿球真实接球位置。
- 重做 Task 4 benchmark 图：
  - success rate；
  - catch time boxplot；
  - hoop radial error boxplot；
  - constraint violation stacked bar。
- 统一字体、线宽、marker 大小。
- 检查图中文字是否在缩到报告宽度后仍可读。

### 验收标准

- 每张图有一个明确论点。
- 红/黄/绿语义在所有图一致。
- 没有遮挡、图例不挡关键数据、字号可读。
- 至少用 PNG 读图检查一次。

### 主要产物

- `outputs/high_score/figure_task2_task4_side_by_side.png`
- `outputs/high_score/figure_strategy_benchmark.png`

### 结果

- `software/scripts/render_high_score_figures.py` created.
- `figure_strategy_benchmark.png` shows success rate, successful catch time, hoop radial error, and max acceleration.
- `figure_task2_task4_side_by_side.png` aligns the Task 2 trajectory plot with a side-view UR10 mesh scene.
- Visual inspection completed. Captions and color semantics are readable, and the marker meanings are stated below the panels.

## Phase 7: 报告集成和页数验收

**Status:** completed

### 目标

把最终证据压缩进 8 页正文，确保符合 protocol 的写作规则和 LaTeX 渲染规则。

### 要做

- 写英文报告草稿。
- 用 Tectonic 渲染。
- 导出 PDF 页面为 PNG。
- 检查页数、caption、溢出、引用、图表可读性。
- 删除不必要的背景和调试细节。

### 验收标准

- 正文不超过 8 页。
- 四个 PDF tasks 都有直接回答。
- 每个 task 至少有一个数字或图作为证据。
- Task 2 和 Task 4 区分清楚。
- 碰撞近似、非实时计算、候选池公平性写清楚。

### 主要产物

- `report_template/report.tex` 或更新后的 `template.tex`
- final PDF
- rendered page PNGs

### 结果

- Final report text integrated into `report_template/template.tex`.
- Tectonic compiled the report successfully:
  - `report_template/final_report.pdf`
  - `report_template/build/template.pdf`
- PDF pages exported and inspected:
  - `report_template/rendered_pages/page-1.png` through `page-5.png`
- Page count:
  - page 1: title page;
  - pages 2-4: report body, 3 pages total;
  - page 5: references.
- Visual inspection passed: figures fit inside the margins, captions are readable, the table does not overflow, and the report stays below the 8-page body limit.

## Execution Order

1. Phase 1：先统一 benchmark，解决“baseline 不公平”和“shorter time 证据不足”。
2. Phase 2：加入 hoop crossing 指标，修正成功定义。
3. Phase 3：跑完整 pipeline replay，证明系统闭环可复现。
4. Phase 4：补安全证据。
5. Phase 5：补 Task 1 多 seed 稳定性。
6. Phase 6：重做报告图。
7. Phase 7：写报告并渲染验收。

## Phase 8: V7 Clarity, Metrics, and Figure Revision

**Status:** completed

### 目标

根据最终人工审查反馈，把报告从“结果充分”进一步改成“指标定义清晰、公式可追踪、每张图都有解释、失败机制可诊断”的提交版本。

### 要做

- 将关键公式改成带编号的 `equation` 环境。
- 对 Kalman filter 模型、reactive baseline、NLP objective 和 constraints 逐一解释变量含义。
- 放大 Figure 2，并改用 PDF 格式，确保 measured / filtered / true 的区别可见。
- 将 Figure 3 改成水平 hoop 的 success-metric 示意图，避免竖直 hoop 造成概念误解。
- 放大 Figure 4 / Figure 5，并在正文中解释图里反映的机制。
- 将 Figure 6 改为 PDF，并裁剪 side-view mesh 图。
- 删除报告正文里的 Course Connection、环境版本、脚本命令和 git/commit 信息。
- 将 `A downstream Task 4 sweep...` 和 covariance ablation 移到 Task 4 系统鲁棒性讨论。
- 定义容易歧义的 benchmark 指标：TCP、Radial、Max ddq、IPOPT、self-collision clearance proxy。
- 进一步诊断 seed 11 失败原因，查看 rejected / failed candidates 是否被关节限制、加速度限制或 hoop-crossing 几何限制挡住。

### 验收标准

- 报告中所有核心公式都有编号和文字解释。
- 表格里的缩写指标可以独立理解，不需要读者猜测。
- 每个关键图至少有一句正文解释其工程含义。
- Task 1 主要讨论 filter choice，不被 Task 4 robustness 内容喧宾夺主。
- Task 4 的 92 ms 明确表述为 catch-time delay，而不是计算耗时。
- Course/material/background 只保留必要方法语言，不出现单独的 Course Connection 段。
- 环境依赖和脚本命令不进入最终报告正文。
- 正文仍不超过 8 页。

### 结果

- Task 1:
  - 增加 Eq. (1) state definition 和 Eq. (2) linear Gaussian process / measurement model。
  - 明确 Kalman filter 选择理由：线性高斯模型下给出 Bayes-optimal MMSE update 和 analytic covariance。
  - Figure 2 改为更大的 PDF 轨迹图，下方增加 measurement error vs filtered error 放大面板。
- Task 2:
  - Reactive controller 公式编号，并定义 \(K\) 和 \(\lambda\)。
  - Figure 3 改为水平 hoop 几何示意，标出 radial error、30 mm allowed ball-center band 和 open side。
- Task 3:
  - Decision variables、discrete dynamics、NLP objective / constraints 全部编号。
  - 增加公式后解释：\(p^\star\)、\(p_{\mathrm{tcp}}\)、\(n_{\mathrm{hoop}}\)、\(\hat v_{\mathrm{ball}}\)、各 cost term 和 hard constraints。
  - 简化 URDF/TCP normal 说明，明确 \(R_{zz}=e_z^\top R_{\mathrm{tcp}}(q)e_z\)。
  - Figure 4 放大并标出 terminal error 20.1 mm。
  - Figure 5 放大，并在正文解释加速度是主要瓶颈。
  - `Self-sphere proxy` 改为 `self-collision clearance proxy`，并说明它是后验近似，不是 full mesh collision。
- Task 4:
  - 迁入 noise downstream sweep 与 covariance ablation，作为系统鲁棒性证据。
  - 明确 92 ms 是 catch-time delay，不是计算耗时。
  - Figure 6 改用 PDF，side-view mesh 图重新裁剪。
  - Benchmark table caption 定义所有容易歧义的指标。
- Failure analysis:
  - seed 11 的 7 个候选全部 NLP 收敛并穿过 hoop plane，但全部超出 30 mm radial tolerance。
  - early candidates saturate joint 3 acceleration；later candidates saturate joint 2 acceleration。
  - 失败机制定义为 acceleration-limited geometry，而不是 estimator divergence 或 NLP failure。

### 产物

- `outputs/report/final_report_research_grade_v7.pdf`
- `outputs/task1/task1_trajectory_prediction.pdf`
- `outputs/task2_dist1p0/task2_interception_selection.pdf`
- `outputs/task3/task3_layer1_plan.pdf`
- `outputs/task3/task3_joint_limits.pdf`
- `outputs/high_score/figure_hoop_geometry_definition.pdf`
- `outputs/high_score/figure_task2_task4_side_by_side.pdf`
- `outputs/high_score/figure_candidate_pareto.pdf`
- `outputs/high_score/figure_failure_velocity_diagnostics.pdf`

### 验证

- `conda run -n robotics python -m unittest discover -s tests` passed: 20 tests.
- Bundled Tectonic compilation succeeded.
- Final report body is 6 pages, below the 8-page limit.
- PDF pages were rendered and visually inspected.
- Text scan returned no matches for first-person wording, banned phrases, Course Connection, environment package versions, script commands, git, or commit.

## Current Next Step

Phase 1-8 complete. The current best submission candidate is `outputs/report/final_report_research_grade_v7.pdf`. Next step is user review, then final git commit and push if no further report edits are needed.
