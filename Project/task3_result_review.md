# Task 3 Result Review

## 任务结论

**结论**：通过 Task 3 的第一版高分路线验收。当前实现使用多步 NLP，而不是逐步 pseudo-inverse。它规划整段 `q,dq,ddq` 轨迹，并把第一步 `ddq` 作为可执行控制输入。

## 完成标准对照

| 标准 | 结果 |
|---|---|
| 最低通过：多步 NLP 返回有限的 `q,dq,ddq` 轨迹 | 满足。`NLPPlanResult` 包含完整轨迹，测试和验证均无 NaN。 |
| 最低通过：`ddq` 第一项可作为控制输入 | 满足。`first_ddq` 为 6 维有限向量。 |
| 最低通过：终端 `tcp` 距离明显低于初始距离 | 满足。误差从 `0.731 m` 降到 `0.020 m`。 |
| 课程/报告达标：明确 horizon variables 和 dynamics constraints | 满足。变量为 `q_0...q_N`、`dq_0...dq_N`、`ddq_0...ddq_{N-1}`，约束为离散二阶积分。 |
| 课程/报告达标：明确 hard constraints 和 soft objectives | 满足。Hard constraints 包含 joint position/velocity/acceleration limits；soft objectives 包含 terminal `tcp` error、control smoothness、velocity regularization 和 ring orientation。 |
| 课程/报告达标：体现 optimal control / resolved acceleration / task priorities | 满足。实现对应 C5 optimal control、C3 acceleration-level control 和 C4 hard/soft constraints。 |
| 工程验收：测试覆盖 shape、dynamics/limits、安全指标 | 满足。`unittest` 共 9 个测试通过。 |
| 工程验收：关节限制满足 | 满足。`q_within_limits = true`，`dq_within_limits = true`，`ddq_within_limits = true`。 |
| 工程验收：table/ring/self-collision 近似指标写入 JSON | 满足。`safety` 字段已写入 `task3_layer1_metrics.json`。 |

## 证据

验证命令：

```powershell
conda run -n robotics python -m unittest tests.test_safety_metrics tests.test_optimal_control_planner tests.test_interception_selector tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task3_nlp_layer1.py --task2-metrics ..\outputs\task2\task2_metrics.json --output-dir ..\outputs\task3 --horizon-steps 28 --dt 0.05
```

验证指标：

| 指标 | 数值 |
|---|---:|
| solver status | `Solve_Succeeded` |
| initial tcp-target distance | `0.731 m` |
| terminal tcp-target distance | `0.020 m` |
| distance reduction | `0.711 m` |
| max abs ddq | `1.9996 rad/s^2` |
| max velocity ratio | `0.640` |
| min tcp top z | `0.732` |
| min tcp table clearance | `0.622 m` |
| min frame table clearance | `0.115 m` |
| min self-sphere clearance | `0.163 m` |

输出文件：

- `outputs/task3/task3_layer1_metrics.json`
- `outputs/task3/task3_layer1_plan.png`

## 异常

Task 3 的结果依赖 Task 2 的接球点可达性。诊断显示原来的 `max_tcp_distance = 1.35 m` 会选到太远太高的点，NLP 终端误差约 `0.72 m`。将 simple feasibility filter 调整为 `0.85 m` 后，终端误差降到 `0.020 m`。这仍属于简单可达性过滤，不是 Task 4 的 smarter scoring。

## 是否可写入报告

可以。报告应把本方法写成 finite-horizon nonlinear program with hard joint constraints and soft task objectives。碰撞部分应写成 conservative geometric approximation，而不是 full mesh collision。

## 下一步

进入 Task 4：在多个候选接球点上运行可达性/优化代价评估，选择成功率更高、时间更短的 interception point，并与 Task 2 简单策略对比。
