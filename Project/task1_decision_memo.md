# Task 1 Brief and Decision Memo

## Task 1 Brief

**任务描述**：从带噪声的球位置测量中估计球的当前状态，并预测未来轨迹。PDF 还要求选择一个课堂学过的 state estimation filter，并解释选择理由。

**输入**：`BallSimulation.get_positions()` 返回的球位置测量，控制周期 `dt = 0.01 s`，已知重力 `[0, 0, -9.81] m/s^2`，测量噪声标准差 `1 mm`。

**输出**：`TrajectoryPredictor.step()` 更新球状态估计，`TrajectoryPredictor.predict()` 输出未来一段时间的预测位置序列。后续 Task 2 会从这些预测点中选择接球点。

**评分点**：必须预测球轨迹；必须选择并说明一个课堂 filter；报告中要体现 prediction step、measurement update、innovation、covariance 等 C6 术语。

**课程依据**：C6 P21/P24 是 Bayes filter 框架；C6 P31 说明 Kalman filter 是线性高斯系统下的近似；C6 P53/P56 给出 measurement update、innovation 和 covariance 处理；C6 P71-P72 给出 tracking process model。

**主要风险**：只做抛物线拟合会弱化“filter”要求；过程噪声设得太随意会让估计抖动或过度自信；预测轨迹若不带时间戳，Task 2 无法判断未来可达点。

## Task 1 决策备忘

**范围**：本轮只设计并实现球轨迹预测，不控制机械臂。

**课程依据**：
- C6 P24：Bayes filter 包含 prediction step 和 measurement update，正好对应每个仿真步的估计更新。
- C6 P53：Kalman update 使用 innovation 和 covariance，能自然处理 1 mm 高斯位置噪声。
- C6 P71-P72：tracking model 把位置、速度、加速度放进状态转移；本项目可把重力作为已知输入。

**方案选项**：
- 方案 A：线性 Kalman filter，状态为 `[px, py, pz, vx, vy, vz]`，重力作为 z 方向已知输入。优势：最贴合线性高斯假设和课堂内容。风险：需要合理设置过程噪声。
- 方案 B：滑动窗口最小二乘拟合抛物线。优势：实现快、直观。风险：不是严格 filter，报告得分依据较弱。
- 方案 C：EKF 或 particle filter。优势：形式更通用。风险：本模型近似线性，复杂度不必要，解释反而显得牵强。

**推荐**：选方案 A。题目给了独立高斯测量噪声，球在空中受已知重力，模型可以写成线性系统。Kalman filter 能用课堂语言解释，并且后续能输出带时间的未来轨迹。

**验证方式**：
- 画 measured positions、filtered positions、future prediction。
- 检查一到多步预测误差、innovation 大小、covariance 是否稳定。
- 确认 `predict()` 输出未来时间戳和位置，且不会把已过去的点交给 Task 2。

**任务完成标准**：
- 最低通过：`TrajectoryPredictor.step()` 能从连续测量更新 6 维球状态，`predict()` 能输出未来时间戳和三维位置。
- 课程/报告达标：报告能明确写出 Bayes filter 的 prediction/update 结构、Kalman innovation、covariance，以及为什么不用 particle filter/EKF。
- 工程验收：至少一条仿真轨迹生成 measured/filtered/predicted 图；预测曲线符合重力抛物线；无 NaN；covariance 保持对称且非负；预测点只包含未来时间。

**报告空间预算**：约 1.3 页，330 英文词，1 张轨迹图，可选 1 个小表说明噪声和状态定义。

**需要你决定**：
1. 是否批准方案 A 作为 Task 1 实现路线。
2. 是否允许我把预测器逻辑先写成可复用 Python 模块，再同步到 notebook。
