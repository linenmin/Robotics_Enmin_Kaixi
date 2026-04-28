# Task 1 Result Review

## 任务结论

**结论**：通过 Task 1 的 Python 脚本阶段验收。当前实现只覆盖球轨迹预测，不控制机器人，也不修改 notebook。

## 完成标准对照

| 标准 | 结果 |
|---|---|
| 最低通过：`TrajectoryPredictor.step()` 能从连续测量更新 6 维球状态 | 满足。`LinearKalmanTrajectoryPredictor.state` 为 `[px, py, pz, vx, vy, vz]`。 |
| 最低通过：`predict()` 能输出未来时间戳和三维位置 | 满足。`TrajectoryPrediction.times` 和 `positions` 已通过单元测试。 |
| 课程/报告达标：体现 Bayes filter prediction/update、innovation、covariance | 满足。实现使用线性预测、measurement innovation、Kalman gain 和 Joseph-form covariance update。 |
| 课程/报告达标：能解释为什么不用 particle filter/EKF | 满足。理由已写入 `task1_decision_memo.md`，本问题是低维、线性、高斯噪声模型。 |
| 工程验收：生成 measured/filtered/predicted 图 | 满足。输出 `outputs/task1/task1_trajectory_prediction.png`。 |
| 工程验收：预测曲线符合重力抛物线 | 满足。图中未来预测沿 z 方向自然下降，符合已知重力输入。 |
| 工程验收：无 NaN | 满足。验证指标 `prediction_has_nan = false`。 |
| 工程验收：covariance 对称且非负 | 满足。`covariance_is_symmetric = true`，最小特征值 `1.46e-07`。 |
| 工程验收：预测点只包含未来时间 | 满足。`prediction_has_only_future_times = true`。 |

## 证据

验证命令：

```powershell
conda run -n robotics python -m unittest tests.test_trajectory_predictor
conda run -n robotics python scripts\validate_task1_prediction.py --seed 7 --output-dir ..\outputs\task1
```

验证指标：

| 指标 | 数值 |
|---|---:|
| measurement RMSE | `0.001815 m` |
| filtered RMSE | `0.000981 m` |
| final filtered error | `0.001262 m` |
| prediction points | `26` |

输出文件：

- `outputs/task1/task1_metrics.json`
- `outputs/task1/task1_trajectory_prediction.png`

## 异常

None。

## 是否可写入报告

可以。报告里建议使用一张紧凑图展示 measured、filtered 和 future prediction，并用 1 个短段落解释 Kalman filter 的选择。

## 下一步

进入 Task 2：基于 `TrajectoryPrediction` 的未来点，设计简单接球点选择策略。
