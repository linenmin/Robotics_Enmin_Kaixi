# Task 2 Brief and Decision Memo

## Task 2 Brief

**任务描述**：使用一个简单策略，从 Task 1 预测出的球未来轨迹中选择机器人应该接球的位置。这个任务只决定 interception point，不计算机械臂运动。

**输入**：`TrajectoryPrediction.times` 和 `TrajectoryPrediction.positions`，机器人初始 `tcp` 位置约 `[0.712, 0.162, 0.634]`，球半径 `0.12 m`，篮筐内圈半径 `0.15 m`。

**输出**：一个 `InterceptionPoint` 数据结构，包含接球时间、接球位置、选择原因和候选点筛选状态。Task 3 控制器会把它作为目标。

**评分点**：必须说明策略是 simple strategy；接球点必须来自 predicted trajectory；策略要考虑未来时间、高度和粗略可达性；不能把 Task 2 写成 Task 4 的最优策略。

**课程依据**：C5 P4-P5 定义 configuration space 和 free space；C5 P10-P12 用 signed distance 描述碰撞/自由空间；C5 P29-P30 说明 sampling methods 适合从候选点中找可行解；C3-1 P13 提醒选点后仍要沿轨迹控制，不能直接跳目标。

**主要风险**：只选最近球点会选到已经过去或太低的点；只看球不看机器人会选到明显不可达点；策略如果过度优化，会和 Task 4 的 smarter strategy 重复。

## Task 2 决策备忘

**范围**：本轮只做接球点选择器，不做机器人控制，也不做碰撞优化。

**课程依据**：
- C5 P4-P5：候选点必须属于简化 free space，至少不能明显不可达。
- C5 P29-P30：从预测轨迹采样候选点，逐个检查，比连续空间盲搜更适合 simple strategy。
- C3-1 P13：选出的点只是目标，后续 Task 3 仍需要控制轨迹跟踪。

**方案选项**：
- 方案 A：规则过滤后选最早可行点。过滤未来时间窗口、高度、粗略工作空间半径和接近初始 `tcp` 的距离。优势：简单、稳定、容易解释。风险：不保证最优。
- 方案 B：选预测轨迹中离当前 `tcp` 最近的点。优势：实现最短。风险：可能太晚、太低，且不一定给机器人留下运动时间。
- 方案 C：对所有候选点打分，综合时间、距离、高度和控制代价。优势：效果可能更好。风险：更像 Task 4，提前消耗 smarter strategy 的空间。

**推荐**：选方案 A。它直接满足 PDF 的 simple strategy，同时保留 Task 4 的升级空间。报告可以诚实说明它只做粗略可达性检查，不处理完整关节约束和碰撞。

**验证方式**：
- 用 Task 1 的预测轨迹生成候选点表，标记每个点通过/拒绝原因。
- 画出 predicted trajectory、accepted candidates 和 selected interception point。
- 检查选择点时间在未来，位置来自预测轨迹，高度不低于阈值，且不明显远离机器人工作空间。

**任务完成标准**：
- 最低通过：选择器能从 `TrajectoryPrediction` 返回一个未来接球点；若无可行点，返回明确失败原因。
- 课程/报告达标：报告能说明 candidate sampling、simple free-space filtering、粗略可达性和 Task 4 的局限衔接。
- 工程验收：至少一条 Task 1 预测轨迹生成候选点筛选图和 JSON 指标；selected point 必须来自预测点；无 NaN；不能选择过去时间或低于 `z_min` 的点。

**报告空间预算**：约 1.0 页，240 英文词，1 张小图或 1 个候选筛选表。

**需要你决定**：
1. 是否批准方案 A 作为 Task 2 实现路线。
2. 是否接受第一版只做粗略工作空间过滤，把严格关节/碰撞可行性留到 Task 3 和 Task 4。
