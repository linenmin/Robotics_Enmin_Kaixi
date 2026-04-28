# Robotics Project 课件知识点 Map

本文档按 `hoops_description.pdf` 中的 4 个项目任务，把相关课件知识点映射到后续实现与报告写作。整理时同时使用了 PDF 文本检索和关键页图像阅读。

## 0. 使用过的课件与图像检查

### 重点课件

| 课件 | 主要作用 |
|---|---|
| `C6/prob_robotics.pdf` | 球轨迹预测、Bayes filter、Kalman filter、tracking process model |
| `C3/03_task_space_control.pdf` | 末端 `tcp` 控制、Jacobian、resolved motion/acceleration、pseudo-inverse、stack of tasks |
| `C4/constraint-based-robot-programming_v3.pdf` | 约束式控制、速度/加速度 resolution、soft/hard constraints、instantaneous optimization |
| `C5/H02A4A_motion_planning(1).pdf` | 接球点选择、configuration/free space、collision signed distance、optimal control、RRT/PRM |
| `C3/02_minimum_jerk_trajectory.pdf` | 平滑轨迹、minimum jerk、速度/加速度峰值与时间的关系 |
| `C3/01_joint_space_control_v2.pdf` | joint-space 控制、不要直接跳目标、需要 trajectory/controller |

### 已渲染检查的关键页图板

| 图板 | 内容 |
|---|---|
| `course_page_images/task1_state_estimation.png` | C6: Bayes filter、Kalman measurement update、tracking process model |
| `course_page_images/task2_interception_planning.png` | C5: C-space/free space、signed distance、optimal control、RRT |
| `course_page_images/task3_optimization_control.png` | C3: task-space control、resolved motion/acceleration、weighted/damped pseudo-inverse、stack of tasks |
| `course_page_images/task3_constraints.png` | C4: first/second order constraints、acceleration constraints、sensor constraints、instantaneous optimization |
| `course_page_images/task4_smarter_strategy.png` | C3 minimum jerk: smoothness、peak velocity、peak acceleration |

## 1. Task 1: 从球位置测量预测球轨迹

PDF 任务原文含义：

> Implement a prediction of the ball's trajectory from measurements of its position. Choose one of the filters for state estimation you know from the class and motivate your choice.

### 1.1 对应课件知识点

| 课件页 | 知识点 | 对本项目的意义 |
|---|---|---|
| C6 P21 | Bayes filter 是 Kalman filter 和 particle filter 的基础 | 报告里可以先说明本问题是“从测量更新状态 belief”的标准状态估计问题 |
| C6 P24 | Bayes filter 由 prediction step 和 measurement update 组成 | `TrajectoryPredictor.step()` 可以对应这两个阶段：先按物理模型预测，再用球位置测量修正 |
| C6 P31 | Bayes filter 两类近似：particle filter 和 Kalman filter | 本项目球运动近似线性、高斯噪声已知，所以 Kalman filter 比 particle filter 更自然 |
| C6 P53 | Kalman filter measurement update，innovation、covariance | 球位置测量是 $z_t = H_t x_t + b_t + \rho_t$，噪声为 1 mm 正态噪声 |
| C6 P56 | Kalman filter remarks，协方差数值稳定、Joseph form | 实现时要注意协方差矩阵对称/半正定，必要时用 Joseph form 或对称化 |
| C6 P63 | NEES/NIS 可用于仿真中验证 EKF/KF | 因为仿真里可访问真实球位置，可以用预测误差/创新检查滤波器是否合理 |
| C6 P71-P72 | tracking application 的 process model，状态包含位置、速度、加速度 | 球轨迹预测可用 tracking model：每个轴建状态，z 轴加入已知重力或加速度项 |

### 1.2 图像阅读得到的注意点

从 C6 图板可以看到，课件不是只讲“拟合曲线”，而是强调：

- belief 需要同时维护均值和不确定性；
- measurement update 依赖 innovation，也就是“测量值与预测测量值的差”；
- tracking process model 里明确出现了连续时间到离散时间的系统矩阵；
- process noise 和 sample period 相关，不应该随便填一个常数。

### 1.3 推荐实现选择

建议第一版使用 **线性 Kalman filter**，而不是 EKF 或 particle filter。

理由：

- 球的位置更新模型在重力已知时基本是线性的；
- 题目明确给了测量噪声是独立正态分布；
- 课程 C6 明确把 Kalman filter 作为 Bayes filter 在 normal distribution/linear system 下的近似；
- 相比 particle filter，KF 更容易解释、参数更少、报告更清楚。

### 1.4 建议状态定义

简单稳定版本：

$$
x =
\begin{bmatrix}
p_x & p_y & p_z & v_x & v_y & v_z
\end{bmatrix}^T
$$

离散时间预测：

$$
p_{t+1} = p_t + v_t \Delta t + \frac{1}{2}g\Delta t^2
$$

$$
v_{t+1} = v_t + g\Delta t
$$

测量模型：

$$
z_t =
\begin{bmatrix}
p_x & p_y & p_z
\end{bmatrix}^T
+ \rho_t
$$

其中：

$$
R = (0.001)^2 I_3
$$

### 1.5 高分注意点

- 不要只说“我拟合了一条抛物线”，要明确说这是一个状态估计问题。
- 要说明为什么不用 EKF：模型已经线性，EKF 的线性化优势不明显。
- 要说明为什么不用 particle filter：本问题低维、高斯噪声、线性模型，particle filter 复杂度不必要。
- 可以在仿真中画出 measured positions、estimated trajectory、predicted trajectory。

## 2. Task 2: 简单策略选择接球点

PDF 任务原文含义：

> Use a simple strategy to determine a point on the ball's predicted trajectory at which the robot should catch the ball.

### 2.1 对应课件知识点

| 课件页 | 知识点 | 对本项目的意义 |
|---|---|---|
| C5 P4-P5 | configuration space、free space、basic motion planning problem | 接球点不能只看球，还要看机器人是否可达、是否碰撞、是否违反关节限制 |
| C5 P10-P12 | signed distance function，sdf > 0 无碰撞，sdf = 0 接触，sdf < 0 穿透 | 后续可用 signed distance 或近似几何距离检查桌子/自碰撞 |
| C5 P14-P15 | motion planning 可以表述成 optimal control，包含 dynamics、equality/inequality constraints、stagewise cost | 简单接球点可以先不做全局优化，但要为后续优化策略留接口 |
| C5 P29-P30 | sampling methods、RRT | 如果接球点候选很多，可以采样候选点并检查可达性，而不是连续空间盲搜 |
| C3-1 P13 | 从一个 pose 到另一个 pose 不应直接跳目标，要沿 planned trajectory 跟踪 | 选定接球点后，机器人运动也要有轨迹/控制过程 |

### 2.2 图像阅读得到的注意点

从 C5 图板能看到，motion planning 的核心不是“找一个目标点”这么简单，而是：

- 起点、终点、自由空间 $\mathcal{X}_{free}$ 都要定义；
- 障碍物和关节限制属于 free space 的一部分；
- signed distance 图明确表示“无碰撞约束”可以写成 $sdf(A,B) \ge 0$；
- RRT 图显示 sampling 方法适合复杂空间中的可达性搜索。

### 2.3 简单策略建议

第一版可以这样做：

1. 用 Task 1 的预测器生成未来 `0.2s - 2.0s` 的球轨迹点。
2. 过滤掉已经太晚或太低的点，例如 `z < 0.3m`。
3. 过滤掉离机器人明显太远的点，例如离 `base_link` 或初始 `tcp` 太远。
4. 选择最早一个满足条件的点作为 intercept point。

可以先用近似判断：

```text
候选点 = 预测轨迹上的点
保留条件 = 时间在未来 + 高度合适 + 位置靠近机器人工作空间
选择规则 = 最早可行点
```

### 2.4 高分注意点

- 篮筐半径只有 0.15 m，球半径 0.12 m，理论上球心通过篮筐中心的容差只剩大约 0.03 m。
- 所以接球点不是只要“差不多在圈附近”，精度要求其实挺高。
- 简单策略应明确承认它的局限：只检查粗略可达性，不保证最优。
- 这会自然引出 Task 4 的 smarter strategy。

## 3. Task 3: 优化控制器让机器人接球

PDF 任务原文含义：

> Compute the required motion to catch the ball with the robot arm with an optimization-based controller. The ring may never face with its top side towards the ground. Avoid self-collisions and collisions with the table. Respect the joint limits on position, velocity, and acceleration.

### 3.1 对应课件知识点

| 课件页 | 知识点 | 对本项目的意义 |
|---|---|---|
| C3 P20 | How NOT to do task space control | 不建议离线采样 task-space 轨迹后直接 IK，再丢给 joint controller |
| C3 P24 | resolved motion rate control | 可以用 Jacobian 把 `tcp` 误差转成关节速度方向 |
| C3 P26 | resolved acceleration rate control | 项目控制输入是关节加速度 `ddq`，这一页直接对应控制器设计 |
| C3 P40 | reference point 很重要，通常 body twist Jacobian 有用 | 本项目必须明确控制的是 `tcp`，不是 wrist 或 tool_link 其他点 |
| C3 P74 | damped pseudo-inverse | 靠近奇异位形时要阻尼，避免关节速度/加速度爆炸 |
| C3 P83-P96 | multiple simultaneous tasks、priorities、stack of tasks、hierarchical QP | 接球、保持篮筐朝向、避碰、关节限制是多任务/多约束问题 |
| C4 P21 | first order vs second order constraints | 本项目是 acceleration control，更接近 second-order resolution |
| C4 P22 | acceleration resolution under constraints | 关节加速度、速度、位置限制应一起考虑 |
| C4 P24 | constraints can be equality/inequality/velocity constraints，priorities/soft weights | 任务目标和安全约束可能冲突，需要 hard/soft 区分 |
| C4 P51 | 每个 sample time 优化 control velocity，100-250 Hz，instantaneous optimization | 本项目 100 Hz 控制频率与课件中的 constraint-based reactive control 很贴合 |
| C5 P14-P18 | optimal control / nonlinear programming | 可以把多步接球运动写成 CasADi NLP |

### 3.2 图像阅读得到的注意点

从 C3 图板：

- P20 明确写了 naive task-space control 的问题：inverse position kinematics 不唯一，数值求 IK 可能贵，joint controller 不知道速度/加速度信息。
- P26 的 resolved acceleration rate control 正好给出 $\ddot{x}$、$J(q)$、$\dot{J}(q,\dot{q})$、$\ddot{q}$ 的关系。
- P83-P96 的 stack of tasks 图说明有些任务 critical，有些任务次要，这很适合“接球 vs 避碰/朝向/关节限制”。

从 C4 图板：

- P22 的 phase-plane 图说明只靠即时加速度可能会因为速度/位置限制而不可行。
- P24 明确区分 equality、inequality、velocity constraints，并提到 known motion 可以转为 feedforward。
- P51 强调 instantaneous optimization 只考虑 kinematic model，不预测未来；若需要预测未来，要扩展到 MPC。

### 3.3 控制器实现建议

可以分两级做。

#### Level 1: 可跑通的 task-space 控制

先实现：

- 计算当前 `tcp` 位姿；
- 计算目标接球点与当前 `tcp` 的位置误差；
- 用 Jacobian 生成期望关节速度或加速度；
- 加上 damping 和 clip。

这一级先不保证高分，但能让机器人动向目标。

#### Level 2: 优化式控制器

用 CasADi 构造短时域优化：

变量：

$$
q_0, q_1, ..., q_N,\quad \dot{q}_0, ..., \dot{q}_N,\quad \ddot{q}_0, ..., \ddot{q}_{N-1}
$$

目标函数可以包含：

- 终端 `tcp` 到接球点的位置误差；
- 篮筐朝向误差；
- 控制平滑项 $\sum \|\ddot{q}\|^2$；
- 关节靠近限位的惩罚；
- 尽快接球的时间或候选点代价。

约束：

- joint position limits；
- joint velocity limits；
- joint acceleration limits；
- `tcp` 到接球点的终端约束或 soft cost；
- ring top side not facing down；
- table/collision avoidance。

### 3.4 代码层面必须注意

当前 `hoops.ipynb` 中有两个明显工程问题：

1. `dq = 0.0` 是标量，后续最好改成：

```python
dq = np.zeros(robot.model.nv)
```

2. `np.clip(...)` 没有赋值，所以限制没有实际生效。应改成：

```python
ddq = np.clip(ddq, -ACCELERATION_LIMIT, ACCELERATION_LIMIT)
dq = np.clip(dq, -VELOCITY_LIMIT, VELOCITY_LIMIT)
q = np.clip(q, LOWER_POSITION_LIMIT, UPPER_POSITION_LIMIT)
```

不过 `q` 是 configuration，最好谨慎直接 clip；更规范的是让优化器和积分过程保证不越界。

### 3.5 高分注意点

- 报告里要明确 hard constraints 和 soft objectives：
  - hard: 关节位置/速度/加速度限制、安全碰撞、篮筐不能倒扣；
  - soft: 平滑、尽快、离目标更近。
- 不要只说“用了优化”，要写清楚优化变量、目标函数、约束。
- 若暂时没实现完整碰撞检测，至少要说明用了什么近似，例如 table height 限制、关键 link 的 bounding sphere。

## 4. Task 4: 更聪明的接球点策略

PDF 任务原文含义：

> Implement a smarter strategy to determine the interception point for higher success rate and shorter interception time.

### 4.1 对应课件知识点

| 课件页 | 知识点 | 对本项目的意义 |
|---|---|---|
| C5 P14-P15 | free-time optimal control、scaled time | 接球点选择可以变成“在未来不同时间中选一个代价最低且可行的点” |
| C5 P18-P19 | derivative-based nonlinear optimization 的局部性与初始化重要 | 优化策略需要好初值，不然可能找到局部坏解 |
| C5 P23-P24 | A* 和 cost-to-go | 可把接球点候选看成图搜索/代价排序问题 |
| C5 P29-P30 | sampling/RRT | 可以在预测轨迹上采样候选接球时间，再做可达性检查 |
| C3 P74 | damped pseudo-inverse | smarter strategy 应避开奇异位形附近的接球点 |
| C3 P83-P96 | stack of tasks / priorities | 接球点选择不仅考虑球，还要考虑机器人姿态、避碰和次任务 |
| C3 minimum jerk P1-P2 | minimum jerk、peak velocity、peak acceleration 与时间的关系 | 更短接球时间会增加速度/加速度峰值，不一定可行 |
| C4 P42 | flexible trajectories，progress `s` 与时间通过 soft position/velocity constraint 相关 | 可以把接球动作看成随进度推进的柔性轨迹，而不是固定死时间 |

### 4.2 图像阅读得到的注意点

从 minimum jerk 图板可以看到：

- 平滑轨迹的代价与运动时间有关；
- 时间越短，peak velocity 和 peak acceleration 越高；
- 因此“更短接球时间”不是越短越好，必须和加速度限制一起考虑。

从 C5 optimal control 图板可以看到：

- free-time problem 可以用 scaled time $s=t/T$ 处理；
- stagewise cost 和 terminal constraint 可以组合；
- 对本项目来说，接球点和接球时间可以一起被优化。

### 4.3 smarter strategy 建议

比简单策略更好的做法：

1. 在预测球轨迹上采样多个候选时间：

```text
t_candidate = [0.2, 0.25, 0.30, ..., 2.0]
```

2. 对每个候选接球点计算可行性和代价：

```text
是否未来点
是否高度合适
是否机器人可达
是否离桌子太近
是否会导致篮筐倒扣
估计需要的关节运动量
估计需要的峰值速度/加速度
是否接近奇异位形
```

3. 选择代价最低的可行点：

$$
J = w_t t_{\text{catch}} + w_d \|p_{\text{tcp}} - p_{\text{target}}\| + w_a \|\ddot{q}_{\text{estimate}}\|^2 + w_c \text{constraintPenalty}
$$

### 4.4 简单策略 vs 智能策略对比

| 版本 | 逻辑 | 优点 | 缺点 |
|---|---|---|---|
| 简单策略 | 选最早满足高度/范围的预测点 | 容易实现，容易解释 | 可能不可达，可能加速度太大，可能接近奇异位形 |
| 智能策略 | 对多个候选点估计可达性和代价，选最优 | 成功率高，可解释为优化/规划 | 实现复杂，需要调权重和可行性检查 |

### 4.5 高分注意点

- Task 4 不是单纯“调参数”，而是要清楚说明智能在哪里。
- 推荐报告中做对比实验：
  - 简单策略成功率；
  - 智能策略成功率；
  - 平均接球时间；
  - 违反约束次数；
  - `tcp` 到球心/篮筐中心误差。
- 即使不做完整 RRT，也可以借用 C5 的 sampling 思想：沿球预测轨迹采样候选接球点。

## 5. 总体实现路线与课件对应

| 项目模块 | 推荐方法 | 课件依据 |
|---|---|---|
| 轨迹预测 | Linear Kalman filter with gravity model | C6 P21/P24/P31/P53/P71 |
| 简单接球点 | 预测轨迹采样 + 高度/可达性过滤 | C5 P4/P5/P29 |
| 初版控制器 | Task-space resolved motion / acceleration control | C3 P24/P26 |
| 稳定性处理 | Damped pseudo-inverse | C3 P74 |
| 多约束控制 | CasADi NLP 或 hierarchical/weighted QP 思路 | C3 P96, C4 P21/P22/P24/P51, C5 P14/P18 |
| 碰撞处理 | signed distance 或近似几何安全约束 | C5 P10-P12 |
| 智能接球点 | 候选时间采样 + 代价函数 + 可行性检查 | C5 P14/P15/P29/P30, C3 minimum jerk P1-P2 |

## 6. 需要特别注意的坑

| 坑 | 为什么会出问题 | 对策 |
|---|---|---|
| 把“不要求实时”理解成不用赶时间 | 仿真计算时间不限制，但球在仿真时间里仍会落地/飞过 | 仍需选择未来可达接球点 |
| 只做抛物线拟合，不提滤波 | PDF 明确要求选择课堂 filter 并说明理由 | 使用 KF，并解释高斯/线性假设 |
| 只控制位置，不控制篮筐朝向 | PDF 要求篮筐不能上侧朝地面 | 把 ring orientation 作为约束或高权重任务 |
| 忽略球半径和篮筐半径差 | 有效容差只有约 3 cm | 评估时用球心到篮筐中心线/平面的误差 |
| 直接用 IK 跳目标 | C3 P20 明确指出 naive task-space control 问题 | 使用 feedback control 或优化控制 |
| 没有真正应用 clip | 当前 notebook 的 `np.clip` 未赋值 | 修改为赋值版本，或让优化器保证限制 |
| 接球越快越好 | minimum jerk 说明时间越短速度/加速度峰值越高 | smarter strategy 要同时考虑时间和可行性 |
| 碰撞约束过早做精确 | 完整 mesh collision 复杂 | 第一版可用 table height、bounding sphere、link safety margin 近似 |

