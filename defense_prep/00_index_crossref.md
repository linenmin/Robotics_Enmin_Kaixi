# Robotics 口试 — 主交叉索引（Master Cross-Reference Index）

**口试时间：** 2026 年 6 月 18 日 · 机械系（Celestijnenlaan 300），房间见 `202606_robotics_defenses_v2.pdf`。
**形式：** 不做 presentation。教授提前读 3 份报告，针对 homework 和 project 提问 / 要求澄清。**带笔记本电脑，准备现场跑代码。**
**评分警告：** 用了课程没覆盖的方法、或与课程明显不同的记号，会被狠扣分。下面每个方法都连回具体某节课的笔记，这样你随时能说「这就是 Lecture Y 里的 X」。

本文件把 3 份报告的每个知识点映射到对应 L 笔记章节。抽考卡片在 `01`–`03`，现场跑代码预案在 `04`。

---

## L 笔记 legend（绝对路径）

| 代号 | 笔记文件 |
|---|---|
| **L1** | `A:\obsidian_philip\Master of Artificial Intelligence\Robotics\L1 - Kinematics (catch up)\L1 - Kinematics (catch up).md` |
| **L2** | `...\L2 - Kinematics and Dynamics\L2 - Kinematics and Dynamics.md` |
| **L3a** | `...\L3 - Robot Control\01 - joint space control\01 - joint space control.md` |
| **L3b** | `...\L3 - Robot Control\02 - task space control\02 - task space control.md` |
| **L3c** | `...\L3 - Robot Control\03 - robots in contact\03 - robots in contact.md` |
| **L4** | `...\L4 - constraint-based task specification\L4 - constraint-based task specification.md` |
| **L5** | `...\L5 - motion planning\L5 - motion planning.md` |
| **L6** | `...\L6 - estimation and probabilistic robotics\L6 - estimation and probabilistic robotics.md` |

引用方式：`L6 › 第48–55页 · 卡尔曼滤波器` = 打开 L6 笔记，搜该标题文字。

---

## A. Homework A 知识地图

| # | 报告里的主题 | 对应 course method | 笔记章节 | 大概率被问 |
|---|---|---|---|---|
| A-Q1 | 逆位置运动学：1 / 2 / ∞ 个解 | IK solution multiplicity、workspace boundary singularity、base 轴上 redundant DOF | **L1** › 模块一：构型空间; 模块二：旋转 | 为什么边界上 singular？为什么 base 轴上 ∞ 解？ |
| A-Q2 | 滚动硬币到达目标 config | nonholonomic constraints、C-space reachability、闭环 maneuver | **L1** › 模块一：构型空间（Configuration Space） | 约束去掉的是「瞬时运动方向」，不是「构型」。停车类比。 |
| A-Q3 | 旋转矩阵 → exponential coordinates ω̂θ | SO(3) matrix log、axis-angle、`tr(R)=1+2cosθ`、`ω̂=(R−Rᵀ)/(2sinθ)` | **L1** › 模块二：刚体运动 — 旋转 (SO(3), log map) | 非唯一性：`(−ω,−θ)` 同一个 R。`sinθ=0` 怎么办？ |
| A-Q4 | 点机器人路径规划 | visibility graph + A* search、多边形障碍下的 completeness | **L5** › 模块四：搜索法（P.21–31, A*）; 模块一：基础概念 (C-space, free space) | 为什么最短路径一定过障碍物顶点？heuristic admissible 吗？ |

## B. Homework B 知识地图

| # | 报告里的主题 | 对应 course method | 笔记章节 | 大概率被问 |
|---|---|---|---|---|
| B-Q1 | Gaussian-mixture prior + linear-Gaussian 测量的后验 | Bayes rule `p(x∣z)∝p(z∣x)p(x)`、sampling、degenerate Gaussian = point mass | **L6** › 第16–19页 · 贝叶斯公式; 第46–47页 · 正态分布下的预测与贝叶斯更新 | 为什么后验不是单个 Gaussian？x=1 的 spike 怎么了？ |
| B-Q2 | `‖q̇‖≤1` 约束下平面内最大 EE 速度 | manipulability ellipsoid、`A=EᵀJ_p`、SVD、`v_max=σ_max(A)=√λ_max(AAᵀ)` | **L3b** › 模块四：伪逆理论与奇异值分解（P.24–44）; 模块一：位姿误差与几何雅可比 | 为什么可达集是 ellipse？singularity 时怎样？Gram–Schmidt 干嘛用？ |
| B-Q3 | 惯性参数 10-vector 变换 + physical realizability | `μ=[m, mc, I]ᵀ`、parallel-axis theorem、`m>0`、I_c SPD、triangle inequalities | **L6** › 第72–80页 · 动力学对质量参数的线性性; 第81–86页 · 参数辨识与可实现性 | 为什么先 shift 到 CoM 再 rotate I？为什么主惯量要满足三角不等式？ |
| B-Q4 | 自然 vs 人工约束（peg / plane / wedge） | task frame、reciprocity `wᵀt=0`、ideal contact、Ad_T 的 frame-invariance | **L3c** › 模块一：接触约束理论 | 为什么正好 6 个拆成 natural+artificial？wedge 为什么产生 τ_x 不产生 τ_y？ |

## C. Project 知识地图（reverse-hoops UR10）

| Task | 报告里的主题 | 对应 course method | 笔记章节 | 大概率被问 |
|---|---|---|---|---|
| T1 | 球轨迹估计 | linear **Kalman filter**、constant-velocity + gravity process model、innovation update | **L6** › 第48–55页 · 卡尔曼滤波器; 第20–23页 · 贝叶斯滤波器算法; 第63–71页 · 状态增广/离散化 | 为什么 KF 不用 EKF / particle filter？covariance 对比 30 mm clearance 说明什么？ |
| T1 | 为什么不用 EKF / PF | linear-Gaussian 下 KF = Bayes-optimal MMSE；这里 EKF 退化成 KF；PF 只增加 sampling noise | **L6** › 第30页 · 两种近似方法; 第56–57页 · 扩展卡尔曼滤波器 | 被追问「模型真的是 linear 吗？」→ 两次 bounce 之间 linear，gravity 是已知输入。 |
| T2 | 简单几何选点；reactive baseline | C-space reachability proxy、**damped Jacobian pseudo-inverse** 速度控制 | **L5** › 模块一：基础概念; **L3b** › 模块四：伪逆理论与SVD (damped pinv) | reactive 控制器为什么失败（0%）？「追得上 ≠ 在对的时间到对的地方」。 |
| T3 | 约束轨迹优化（NLP） | direct-transcription **optimal control**、二阶 joint dynamics、hard/soft constraints | **L5** › 模块三：最优控制法（P.13–20）; **L4** › 模块三：控制即优化; 模块四：约束类型与特征变量 | 哪些是 hard、哪些 soft，为什么？为什么 direct transcription 而非 single-step？ |
| T3 | hoop 朝向 / table / self-collision | path inequality constraints、`Rzz≥0`、link-sphere proxy（≈ signed-distance） | **L4** › 模块四：约束类型; **L5** › 模块二：有符号距离函数（P.9–12） | 为什么用 sphere proxy 不用 exact mesh？exact 需要什么（non-smooth SDF 约束）？ |
| T4 | feasibility-aware 选点；time-accuracy 权衡 | candidate sampling + cost ranking、free-time optimal control | **L5** › 模块三：最优控制法 (free-time); 模块四：搜索法 (sampling); **L4** › 模块六：柔性轨迹 | 为什么瓶颈是选点不是估计？min-jerk：时间越短 accel 峰值越高。 |

---

## 跨报告共享概念（一个答案覆盖多个问题）

| 概念 | 出现在 | 单一最佳笔记 |
|---|---|---|
| Jacobian + SVD / pseudo-inverse / singularities | B-Q2, T2, T3 | **L3b** › 模块四（P.24–44） |
| Bayes filter → Kalman | B-Q1, T1 | **L6** › 模块二 + 模块四 |
| C-space, free space, reachability | A-Q2, A-Q4, T2 | **L5** › 模块一; **L1** › 模块一 |
| optimization-as-control, hard vs soft constraints | T3, T4, B-Q4 | **L4** › 模块三 + 模块四 |
| 惯性参数 / dynamics 线性性 | B-Q3 | **L6** › 模块六（第72–86页） |

---

## 每份报告一句话主旨（背下来）

- **HW A：** 标准 kinematics + 一个完整且最优的点机器人 planner（visibility graph + A*）。
- **HW B：** 四个短证明 — Bayes 后验、SVD 推 manipulability ellipse、惯性参数变换 + realizability、natural/artificial 接触约束。
- **Project：** *「选点规则最重要。」* KF 和 NLP 固定不变，只改 candidate selection；feasibility-aware time-first 选点把成功率从 **0% 提到 98%**。
