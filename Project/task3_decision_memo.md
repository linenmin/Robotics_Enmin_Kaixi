# Task 3 Brief and Decision Memo

## Task 3 Brief

**任务描述**：使用 optimization-based controller 计算 UR10 机械臂运动，让末端篮筐在接球时间到达 Task 2 选择的接球点。控制器必须考虑篮筐朝向、避免碰撞，并遵守关节位置、速度和加速度限制。

**输入**：当前关节位置 `q`、关节速度 `dq`、Task 2 的 `InterceptionPoint`、URDF/Pinocchio robot model、关节限制、100 Hz 控制周期。

**输出**：每个控制步的 6 维关节加速度 `ddq`，以及验证日志：`tcp` 到目标误差、关节限制余量、姿态指标、table/self-collision 近似指标。

**评分点**：必须是 optimization-based controller；必须写清优化变量、目标函数、约束；必须区分 hard constraints 和 soft objectives；必须处理或诚实近似处理 ring orientation、self/table collision、joint position/velocity/acceleration limits。

**课程依据**：C3 P20 说明不要直接 IK 跳目标；C3 P26 对应 resolved acceleration control；C3 P74 对应 damped pseudo-inverse 稳定性；C3 P83-P96 对应多任务和优先级；C4 P21-P24 对应 acceleration constraints、equality/inequality constraints；C4 P51 对应每个采样时刻的 instantaneous optimization；C5 P10-P12 对应碰撞 signed distance 或近似安全距离。

**主要风险**：完整多步 NLP 很容易卡在建模和求解器调参；只做 clipped pseudo-inverse 不满足 optimization-based 要求；精确 mesh self-collision 入口当前不完整，`collision_model.collisionPairs` 初始为 0。

## Task 3 决策备忘

**范围**：本轮实现和验证机器人控制器的多步 NLP Python 脚本，不同步 notebook，不做 Task 4 的 smarter interception selection。

**课程依据**：
- C3 P26：控制输入是关节加速度，可把 `tcp` 目标加速度写成 $J(q)\ddot{q}+\dot{J}(q,\dot{q})\dot{q}$。
- C4 P22/P24/P51：每个控制周期解一个带约束的 instantaneous optimization，硬约束和 soft objective 分开。
- C3 P83-P96：接球、姿态、避碰和关节限制是多任务问题，重要性不同。

**方案选项**：
- 方案 A：每步解 6 维 acceleration-level constrained least-squares。变量是 `ddq`。Hard constraints 限制 `ddq`、下一步 `dq`、下一步 `q`；soft objectives 追踪 `tcp` 目标、保持篮筐朝向、减小控制量。优势：符合 optimization-based，规模小，适合 100 Hz。风险：只看短时一步，可能不如多步规划稳。
- 方案 B：用 CasADi 建多步 horizon NLP，变量包含整段 `q,dq,ddq`。优势：最贴近 optimal control。风险：实现和调参成本高，容易卡求解器，Task 3 进度风险大。
- 方案 C：damped pseudo-inverse + clip。优势：最快能动。风险：不是严格 optimization-based，报告难以满足 PDF 要求，只适合作为 fallback baseline。

**推荐**：选方案 B。它最符合 optimal control / nonlinear programming 的高分报告形态，也能完整写出整段状态、控制、目标函数和约束。我们分两层实现：第一层先做可运行的多步 NLP，变量包含 `q,dq,ddq`，约束包含积分和关节限制，目标包含终端 `tcp` 误差与控制平滑；第二层再加入篮筐朝向、table clearance 和 bounding-sphere safety 近似。保留方案 A/C 作为调试 fallback，但不作为最终主线。

**验证方式**：
- 优化器结构测试：解向量包含 `q,dq,ddq`，horizon dynamics 约束维度正确。
- 离线规划测试：从 `q0` 到 Task 2 接球点求解一段轨迹，记录 solver status、terminal `tcp` error 和约束余量。
- 约束日志：检查 joint limits、ring top direction、table clearance、bounding-sphere self-distance 近似。
- 图表：画 `tcp` 轨迹 vs selected point、终端误差、关节速度/加速度限制余量。

**任务完成标准**：
- 最低通过：多步 NLP 能返回有限的 `q,dq,ddq` 轨迹；`ddq` 第一项可作为控制输入；终端 `tcp` 距离明显低于初始距离。
- 课程/报告达标：报告明确写出 horizon variables、discrete dynamics constraints、terminal objective、control smoothness、hard joint constraints、soft orientation/safety objectives，并引用 optimal control、resolved acceleration、hard/soft task priorities。
- 工程验收：测试覆盖轨迹 shape、dynamics consistency、joint position/velocity/acceleration limits；优化日志无 NaN；solver status 和约束余量写入 JSON；table/ring orientation/self-collision 近似指标写入 JSON。

**报告空间预算**：约 2.4 页，520 英文词，1-2 张图，1 个小表列优化变量、目标和约束。

**需要你决定**：
1. 已批准方案 B 作为 Task 3 实现路线。
2. 第一版允许使用 table height 和 link/tcp bounding sphere 近似碰撞检查，并在报告中明确说明这是 conservative approximation。
