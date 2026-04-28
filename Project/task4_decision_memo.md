# Task 4 Brief and Decision Memo

## Task 4 Brief

**任务描述**：实现一个 smarter interception strategy，用更高成功率和更短接球时间选择接球点。它必须比 Task 2 的 simple sampled filter 更聪明，并且要能用结果对比证明改进。

**输入**：Task 1 的预测轨迹、Task 3 的多步 NLP 控制器、机器人关节/姿态/安全指标、Task 2 的简单策略结果。

**输出**：一个 `SmartInterceptionSelector`，从多个候选接球点中返回最优点，并生成候选评分表、对比指标和可视化。

**评分点**：必须说明 smarter strategy 智能在哪里；必须比较 simple strategy 与 smarter strategy；必须关注 higher success rate 和 shorter interception time；不能只写“调了阈值”。

**课程依据**：C5 P14-P15 支持 free-time optimal control 和 stagewise/terminal cost；C5 P29-P30 支持 sampling candidate times；C3 minimum jerk P1-P2 说明时间越短，速度/加速度峰值越高；C3 P83-P96 和 C4 P24 支持用 hard/soft task priorities 评价候选点。

**主要风险**：每个候选点都跑 NLP 会变慢；过度追求短时间会导致加速度/速度峰值过高；如果只用 Task 2 的距离阈值，会显得不够 smarter。

## Task 4 决策备忘

**范围**：本轮只做 smarter interception point selection 和对比实验，不改 Task 3 NLP 的核心约束结构。

**课程依据**：
- C5 P14-P15：把接球时间和接球点看成带代价的 optimal control selection。
- C5 P29-P30：沿预测轨迹采样候选时间，再评估可行性。
- C3 minimum jerk P1-P2：短时间会推高速度/加速度峰值，所以评分必须同时看 time 和 feasibility。

**方案选项**：
- 方案 A：对候选点逐个运行 Task 3 NLP，按 terminal error、接球时间、加速度余量、速度余量和安全指标打分。优势：最贴合已有控制器，报告证据强。风险：计算较慢。
- 方案 B：只用几何启发式评分，例如 `tcp` 距离、高度、时间。优势：快。风险：和 Task 2 区别不够大，不能真正证明成功率更高。
- 方案 C：混合策略。先用几何筛掉明显差的点，再对少量候选点跑 NLP 评分。优势：比 A 快，比 B 有控制可行性证据。风险：实现稍复杂。

**推荐**：选方案 C。它能体现 C5 sampling，又能用 Task 3 NLP 给出真实可达性和约束风险。报告中可写成 two-stage candidate evaluation：cheap geometric prefilter followed by NLP feasibility scoring。

**验证方式**：
- 从同一条预测轨迹生成候选接球点表。
- 对 Task 2 simple selected point 和 Task 4 smart selected point 分别运行 Task 3 NLP。
- 在多个随机 seed 上重复实验，至少报告 success rate、mean catch time、mean terminal error、constraint violation count 和 solver status。
- 比较 terminal error、catch time、max acceleration、max velocity ratio、safety metrics 和 feasibility。
- 画候选评分图和 simple vs smart 多 seed 对比表。

**任务完成标准**：
- 最低通过：`SmartInterceptionSelector` 能返回一个来自预测轨迹的未来点，并附带候选评分表；若无可行点，返回失败原因。
- 课程/报告达标：报告能说明 sampling、cost function、feasibility checking、time vs acceleration tradeoff，并明确它比 Task 2 多了 NLP-based reachability scoring。
- 高分证据：多 seed benchmark 证明 smart strategy 不只是单例有效。结果至少包含 simple vs smart 的成功率、平均接球时间、平均终端误差、速度/加速度裕度和安全指标。若 smart 接球时间更晚，必须用更高成功率或更低约束风险解释。
- 工程验收：生成 simple vs smart 对比 JSON 和图；smart 策略的成功率不低于 simple 策略；所有约束指标无 NaN；joint position、velocity、acceleration limits 满足；失败 seed 必须保留原因。

**报告空间预算**：约 1.3 页，320 英文词，1 个对比表或 1 张候选评分图。

**需要你决定**：
1. 是否批准方案 C 作为 Task 4 实现路线。
2. 是否接受 Task 4 的“更聪明”定义为 NLP-based feasibility and cost scoring，而不是重新设计完整全局 motion planner。
