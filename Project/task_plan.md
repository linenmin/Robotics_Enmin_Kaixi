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

**Status:** pending

### Tasks

- [x] 阅读 `hoops_description.pdf`。
- [x] 阅读 `software/hoops.ipynb` 当前代码骨架。
- [x] 阅读 `utils/ball_simulation.py` 和 `utils/transformations.py`。
- [x] 初步阅读 `robot_description/ur10_robot.urdf`。
- [ ] 用可视化确认机器人、篮筐、球、桌子的空间关系。
- [ ] 整理所有硬性约束：关节位置、速度、加速度、篮筐朝向、碰撞、球/篮筐半径。
- [ ] 整理所有需要我们实现的空白模块。

## Phase 3: 翻找课件并对齐高分关键点

**Status:** pending

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

- [ ] 提取每份相关课件的目录和关键词。
- [ ] 找到与项目四个 task 直接对应的课程公式/方法。
- [ ] 建立“项目任务 -> 课程知识点 -> 可实现代码”的映射表。
- [ ] 标注报告中应该主动解释的设计选择。

## Phase 4: 制定代码调试反馈级别人和 agent 交互计划

**Status:** pending

### Draft Rules

- 环境问题优先修环境，不通过改代码绕过缺包。
- 每次只改一个清晰模块，例如轨迹预测、拦截点选择、控制器、约束检查。
- 每次改动后必须有最小验证：单元测试、notebook cell 输出、仿真截图或轨迹图。
- 对失败结果保留日志，包括输入条件、报错、图像现象、尝试过的修复。
- agent 每轮先说明要验证的假设，再动代码。
- 用户负责反馈视觉现象和课程评分偏好，agent 负责把反馈转为可测试改动。

### Tasks

- [ ] 写出项目调试协议。
- [ ] 写出 notebook 运行/截图/日志的反馈模板。
- [ ] 写出每个算法模块的验收标准。
- [ ] 决定是否需要建立分支、测试脚本或实验记录目录。

## Errors Encountered

| Error | Attempt | Resolution |
|---|---|---|
| `ModuleNotFoundError: No module named 'casadi'` | 检查 `vela`、`gpu_env`、`tf_work_hpc`、`raw2Event`、`base` 是否可复用 | 判定现有环境不适合直接复用；已新建 `robotics` |
| `ModuleNotFoundError: No module named 'example_robot_data'` | 执行 `0_setup.ipynb` | 安装 `example-robot-data-loaders` 的 Python loader，并添加 `.pth` 路径 |
| `OSError: talos_data\robots\talos_reduced.urdf not found` | 加载 `load("talos")` | 修正 loader 的 `path.py`，指向 Conda 中真实数据目录 |

## Next Action

环境已打通。下一步进入课件提取和任务条件整理。
