# Task 2 Result Review

## 任务结论

**结论**：通过 Task 2 的 Python 脚本阶段验收。当前实现只从 Task 1 的预测轨迹中选择接球点，不计算机器人运动。

## 完成标准对照

| 标准 | 结果 |
|---|---|
| 最低通过：选择器能从 `TrajectoryPrediction` 返回一个未来接球点 | 满足。`SimpleInterceptionSelector.select()` 返回 `InterceptionPoint`。 |
| 最低通过：无可行点时返回明确失败原因 | 满足。无候选点通过时返回 `success = false` 和 `reason = no_candidate`。 |
| 课程/报告达标：说明 candidate sampling | 满足。选择器逐个检查预测轨迹上的采样点。 |
| 课程/报告达标：说明 simple free-space filtering 和粗略可达性 | 满足。过滤条件包括 future lead time、最低高度和宽松 `tcp` 距离上限。 |
| 课程/报告达标：能衔接 Task 4 的局限 | 满足。当前策略选最早可行点，不做评分优化或控制代价比较。 |
| 工程验收：生成候选点筛选图和 JSON 指标 | 满足。输出 `outputs/task2/task2_interception_selection.png` 和 `task2_metrics.json`。 |
| 工程验收：selected point 来自预测点 | 满足。`selected_from_prediction = true`，`selected_index = 23`。 |
| 工程验收：无 NaN | 满足。`selected_has_nan = false`。 |
| 工程验收：不能选择过去时间或低于 `z_min` 的点 | 满足。`selected_is_future = true`，`selected_above_z_min = true`。 |

## 证据

验证命令：

```powershell
conda run -n robotics python -m unittest tests.test_interception_selector tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task2_interception.py --seed 7 --output-dir ..\outputs\task2
```

验证指标：

| 指标 | 数值 |
|---|---:|
| selected index | `27` |
| selected time | `1.360 s` |
| selected position | `[1.224, -0.119, 1.074] m` |
| max tcp distance | `0.85 m` |
| candidates checked | `28` |
| rejected as too soon | `6` |
| rejected as too far | `21` |

输出文件：

- `outputs/task2/task2_metrics.json`
- `outputs/task2/task2_interception_selection.png`

## 异常

None。

## 是否可写入报告

可以。报告里建议把它描述为 a simple sampled candidate filter，而不是 optimization。图可以作为 Task 2 的证据，也能引出 Task 4 的 smarter scoring。

## 下一步

进入 Task 3：使用 Task 2 的接球点作为目标，设计优化式机器人控制器，并开始处理关节限制、篮筐朝向和碰撞相关约束。
