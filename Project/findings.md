# Robotics Project Findings

## Project Summary

项目是一个“反向投篮”机器人任务：球被抛向机器人，机器人末端装着篮筐圈，需要移动篮筐让球穿过。

## Important Clarification: “不要求实时运行”是什么意思？

这句话不是说机器人可以慢慢反应到球落地以后再接球，也不是说真实世界中不需要反应速度。

它的意思是：在这个课程仿真项目里，老师不考察你的算法计算耗时。你可以在仿真循环里“暂停现实时间”来算轨迹和优化控制，只要你的算法在仿真时间意义上能给出合理动作即可。

通俗类比：

- 真实机器人：球飞过来只给你 1 秒，电脑也必须在 1 秒内算完。
- 这个项目：球在仿真里飞 1 秒，但你电脑可以花更久计算。计算完以后再把结果用于仿真控制。

所以“不要求实时”主要降低的是工程难度，不是取消“接球要赶在球落地前”的物理要求。

## Is the Ball Trajectory Fixed?

不是完全固定。

从 `utils/ball_simulation.py` 看：

- 球初始位置默认在 `[5.0, 0, 2.0]`。
- 球受到重力影响，会沿抛物线飞。
- 程序会随机选择一个目标区域点，然后设置球的初速度。
- `get_positions()` 返回的位置还会加入标准差约 `1e-3 m` 的噪声，也就是 1 mm。

如果固定随机种子，轨迹可以复现；如果不固定随机种子，每次目标点可能不同，因此轨迹也会不同。

## PDF Project Requirements

来自 `hoops_description.pdf`：

- 使用机器人手臂移动末端篮筐。
- 球会被抛向机器人。
- 机器人需要让球成功穿过篮筐。
- 要实现球轨迹预测。
- 要选择球轨迹上的拦截点。
- 要用优化式控制器计算机械臂运动。
- 要满足关节位置、速度、加速度限制。
- 每个关节加速度限制为 `2 rad/s^2`。
- 篮筐不能上侧朝地面。
- 要避免自碰撞和与桌子碰撞。
- 球半径 `120 mm`。
- 篮筐内半径 `150 mm`。
- 球位置测量噪声为独立正态噪声，均值 0，标准差 `1 mm`。
- 没有实时计算要求。

## Main Notebook: `software/hoops.ipynb`

当前 notebook 是项目骨架。

已完成：

- 导入库。
- 读取 UR10 机器人 URDF。
- 读取篮筐和机器人 mesh。
- 创建 Meshcat 可视化。
- 显示 `world` 和 `tcp` 坐标系。
- 定义球的可视化函数。
- 定义仿真循环。

未完成：

- `TrajectoryPredictor.step()` 是空的。
- `TrajectoryPredictor.predict()` 是空的。
- `Controller.step()` 只是占位返回 `ACCELERATION_LIMIT`，不是真正控制。
- 没有轨迹预测图。
- 没有拦截点选择逻辑。
- 没有优化控制器。
- 没有碰撞或约束检查。

## Ball Simulation

`utils/ball_simulation.py` 是球的物理仿真。

核心模型：

- 位置根据速度和重力更新。
- 速度根据重力更新。
- 球落到地面附近会反弹，竖直速度乘以 `-0.8`。
- 返回测量值时加 1 mm 级别噪声。

这适合用状态估计方法，例如：

- 简单最小二乘拟合抛物线。
- Kalman filter。
- Extended Kalman filter 不一定必要，因为这里球的运动模型基本是线性的。

## Robot Description

`robot_description/ur10_robot.urdf` 描述 UR10 机械臂、篮筐、桌子和 `tcp`。

关键点：

- UR10 有 6 个主要旋转关节。
- 每个关节有位置和速度限制。
- `tcp` 是 tool center point，可以理解为篮筐中心点。
- 篮筐模型来自 `hoop_ring.stl`。
- 可视化 mesh 和碰撞 mesh 分开存放。

## Existing Conda Environments

本机已有环境：

- `base`
- `gpu_env`
- `raw2Event`
- `tf_work_hpc`
- `vela`

初步检查结果：

- 这些环境均缺少 `casadi`。
- 因此不适合直接作为本项目运行环境。
- 项目自带 `exercise_0_software_environment/py13roboticscourse_env.yml`，建议新建专用环境。

## Course Materials Found

在 `Robotics` 目录中发现课件：

- C1: kinematics catch-up
- C2: kinematics dynamics
- C3: joint space control, minimum jerk trajectory, task space control, robots in contact, impedance control
- C4: constraint-based robot programming
- C5: motion planning
- C6: probabilistic robotics
- C7: learning from demonstration
- C8: reinforcement learning

最相关的初步判断：

- C6 对应球轨迹估计。
- C5 对应拦截点和运动规划。
- C3 对应关节空间/任务空间控制。
- C4 对应约束、优化、碰撞和姿态限制。
