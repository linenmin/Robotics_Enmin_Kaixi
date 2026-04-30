# Robotics Project Task Plan

## Goal

把 `Robotics/Project` 这个机器人接球项目从“看懂要求”推进到“可运行、可调试、可迭代拿分”的状态。当前优先级不是直接写最终算法，而是先建立稳定环境、明确题目条件、对齐课程知识点，再制定人和 agent 的协作守则。

## Key Questions

- 题目说“不要求实时运行”，这是否意味着小球轨迹固定？
- 本机已有 Conda 环境是否能复用，还是应该创建课程专用环境？
- 项目给了哪些已知条件、哪些代码骨架、哪些任务缺口？
- 老师课件里哪些内容最贴合本项目，能作为实现和报告的高分依据？
- 后续调试时，人和 agent 如何交互，避免盲目改代码？

## Phase 1: 打通运行环境

**Status:** in_progress

### Tasks

- [x] 列出本机已有 Conda 环境。
- [x] 检查项目是否已有环境记录文件。
- [x] 初步测试现有环境是否包含关键依赖。
- [x] 创建或确认项目专用环境。
- [x] 运行 `exercise_0_software_environment/0_setup.ipynb`。
- [x] 运行 `software/hoops.ipynb` 到可视化窗口可打开。
- [x] 记录最终环境到 `PROJECT_ENV.md`。

### Current Decision

现有 Conda 环境包括 `base`、`gpu_env`、`raw2Event`、`tf_work_hpc`、`vela`。这些环境初步检查都缺少 `casadi`，因此不建议直接复用。已根据课程提供的 `py13roboticscourse_env.yml` 创建专用 Conda 环境 `robotics`。

### Environment Candidate

```powershell
conda activate robotics
```

## Phase 2: 整理题目条件和任务要求

**Status:** in_progress

### Tasks

- [x] 阅读 `hoops_description.pdf`。
- [x] 阅读 `software/hoops.ipynb` 当前代码骨架。
- [x] 阅读 `utils/ball_simulation.py` 和 `utils/transformations.py`。
- [x] 初步阅读 `robot_description/ur10_robot.urdf`。
- [x] 用可视化确认机器人、篮筐、球、桌子的空间关系。
- [x] 整理所有硬性约束：关节位置、速度、加速度、篮筐朝向、碰撞、球/篮筐半径。
- [x] 整理所有需要我们实现的空白模块。
- [x] 创建 `known_conditions.md` 已知条件表。

## Phase 3: 翻找课件并对齐高分关键点

**Status:** in_progress

### Candidate Course Materials

- `C1/H02A4A_kinematics_catch-up.pdf`
- `C2/H02A4A_kinematics_dynamics.pdf`
- `C3/01_joint_space_control_v2.pdf`
- `C3/02_minimum_jerk_trajectory.pdf`
- `C3/03_task_space_control.pdf`
- `C4/constraint-based-robot-programming_v3.pdf`
- `C5/H02A4A_motion_planning(1).pdf`
- `C6/prob_robotics.pdf`
- `C7/Learning_from_demonstration_2025_2026(1).pdf`
- `C8/H02A4A_reinforcement_learning.pdf`

### Hypothesis

这个项目最可能需要结合：

- 概率机器人学 / 状态估计：用于从带噪声的球位置预测轨迹。
- 运动规划：用于选择机器人能到达的拦截点。
- 任务空间控制 / 优化控制：用于让机械臂末端篮筐移动到目标位姿。
- 约束式机器人编程：用于表达关节限制、碰撞限制、篮筐朝向限制。

### Tasks

- [x] 提取每份相关课件的目录和关键词。
- [x] 找到与项目四个 task 直接对应的课程公式/方法。
- [x] 建立“项目任务 -> 课程知识点 -> 可实现代码”的映射表。
- [x] 标注报告中应该主动解释的设计选择。
- [x] 创建 `course_knowledge_map.md`。

## Phase 4: 制定代码调试反馈级别人和 agent 交互计划

**Status:** in_progress

### Draft Rules

- 环境问题优先修环境，不通过改代码绕过缺包。
- 每次只改一个清晰模块，例如轨迹预测、拦截点选择、控制器、约束检查。
- 每次改动后必须有最小验证：单元测试、notebook cell 输出、仿真截图或轨迹图。
- 对失败结果保留日志，包括输入条件、报错、图像现象、尝试过的修复。
- agent 每轮先说明要验证的假设，再动代码。
- 用户负责反馈视觉现象和课程评分偏好，agent 负责把反馈转为可测试改动。

### Tasks

- [x] 写出项目调试协议。
- [x] 写出 notebook 运行/截图/日志的反馈模板。
- [x] 写出每个算法模块的验收标准。
- [x] 决定是否需要建立分支、测试脚本或实验记录目录。
- [x] 创建 `AGENT_PROTOCOL.md` 和 `report_template/`。

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| `ModuleNotFoundError: No module named 'casadi'` | 检查 `vela`、`gpu_env`、`tf_work_hpc`、`raw2Event`、`base` 是否可复用 | 判定现有环境不适合直接复用；已新建 `robotics` |
| `ModuleNotFoundError: No module named 'example_robot_data'` | 执行 `0_setup.ipynb` | 安装 `example-robot-data-loaders` 的 Python loader，并添加 `.pth` 路径 |
| `OSError: talos_data\robots\talos_reduced.urdf not found` | 加载 `load("talos")` | 修正 loader 的 `path.py`，指向 Conda 中真实数据目录 |

## Latest Status: Report V7 Clarity Revision

**Status:** completed on 2026-04-30

### Completed

- 根据用户审查意见重新检查 `AGENT_PROTOCOL.md` 和老师 PDF 要求。
- 将报告中的关键公式改为自动编号形式，并在正文解释公式变量和约束含义。
- 加强 Task 1 的滤波器选择理由：明确线性高斯模型下 Kalman filter 的 Bayes-optimal MMSE 性质，并说明 EKF / particle filter 为什么不适合作为主方案。
- 将 Task 4 相关的 noise downstream sweep 和 covariance ablation 从 Task 1 迁移到 Task 4 的系统鲁棒性讨论。
- 将易混淆指标在表格 caption 和正文中定义清楚：
  - `TCP [mm]`：NLP 终点 hoop center 到预测目标点的误差；
  - `Radial [mm]`：真实球轨迹穿过 hoop plane 时的平面径向误差；
  - `Max ddq`：整条计划中所有关节和 knot 的最大绝对加速度；
  - `IPOPT`：成功样本的平均迭代次数；
  - `Self-collision clearance proxy`：球/胶囊近似的后验 clearance 指标，不声称 full mesh collision。
- 重新生成并使用 PDF 格式图：
  - `outputs/task1/task1_trajectory_prediction.pdf`
  - `outputs/task2_dist1p0/task2_interception_selection.pdf`
  - `outputs/task3/task3_layer1_plan.pdf`
  - `outputs/task3/task3_joint_limits.pdf`
  - `outputs/high_score/figure_hoop_geometry_definition.pdf`
  - `outputs/high_score/figure_task2_task4_side_by_side.pdf`
  - `outputs/high_score/figure_candidate_pareto.pdf`
  - `outputs/high_score/figure_failure_velocity_diagnostics.pdf`
- 放大 Task 1、Task 3、Task 4 关键图，并裁剪 side-view mesh 图。
- 将 Figure 3 改为水平 hoop 的几何定义图，避免与真实接球场景的直觉冲突。
- 补充 Figure 4 / Figure 5 的文字解释：Task 3 的瓶颈主要是加速度约束，不是转速约束。
- 增加 seed 11 的失败机制诊断：
  - 7 个 shortlisted candidates 全部 NLP 收敛并穿过 hoop plane；
  - 但全部超过 30 mm radial tolerance；
  - radial error 从 758 mm 降到 51.5 mm；
  - 早期候选主要饱和 joint 3 加速度，后期候选主要饱和 joint 2 加速度；
  - 因此失败机制是 acceleration-limited geometry，而不是 estimator 或 solver failure。
- 删除报告正文中的 Course Connection、环境版本、脚本命令和 git/commit 相关内容。
- 更新 `AGENT_PROTOCOL.md`：关键数字和图表必须解释工程含义；表格中容易歧义的指标必须定义。

### Verification

- `conda run -n robotics python -m unittest discover -s tests` passed: 20 tests.
- Tectonic bundled compiler succeeded.
- Final report body has 6 pages, below the 8-page body limit.
- Exported PDF pages were visually inspected for figure readability, text overflow, and equation numbering.
- Report text scan returned no matches for first-person wording, banned phrases, Course Connection, environment package versions, script commands, git, or commit.
- Discord notification sent successfully.

### Current Output

- Final report PDF: `outputs/report/final_report_research_grade_v7.pdf`
- Source report: `report_template/template.tex`

## Next Action

当前实现和报告已进入提交前状态。下一步只剩两类可选动作：

1. 用户人工浏览 `outputs/report/final_report_research_grade_v12.pdf`，确认图像观感和内容取舍。
2. 若用户确认无进一步修改，则执行最终 git 提交和推送。

## Latest Status: Report V12 Final Polish and Cleanup

**Status:** completed on 2026-04-30

### Completed

- 根据最终审查反馈完成报告最后一轮可读性修订。
- 保留 Figure 6 的 Meshcat 截图，不再重渲染；只在正文补充 Figure 6 引用，说明红色 simple geometric candidate 与黄色 feasibility-aware catch 的含义。
- 在正文补充 Figure 8 引用，明确 seed 11 位于 50-seed lateral-velocity 分布的 95th-percentile 附近。
- 解释 Task 2 standalone validation 的 `0.85 m` workspace radius 与 Task 4 benchmark 的 `1.15 m` shared candidate radius 为什么不同，并说明这会让 50-seed simple geometric mean catch time 早于 standalone pick。
- 明确 covariance-rejection ablation 的工程含义：使用保守的 `0.18 m` forward-covariance threshold，且 50 seeds 中选择结果与 time-first feasible 一致。
- 在 Eq. (6) 解释中补充：
  - acceleration / velocity 指 joint acceleration 和 joint velocity；
  - normal-alignment cost 是 orientation-symmetric；
  - `R_{zz} >= 0` path constraint 选择 upright branch。
- 压缩冗余文字，删除重复的 `time weight 15.0` 叙述。
- 用户已删除多余旧版 PDF；当前 `outputs/report/` 仅保留 `final_report_research_grade_v12.pdf` 和 `template.pdf`。

### Verification

- Bundled Tectonic compilation succeeded.
- Current rendered PDF: `outputs/report/final_report_research_grade_v12.pdf`.
- PDF has 9 total pages: title page + 7 body pages + references page.
- Body length remains within the 8-page report limit.

### Current Next Step

执行最终 git commit 和 push。
