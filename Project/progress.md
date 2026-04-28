# Robotics Project Progress

## 2026-04-28

### Completed

- 阅读并应用 `pi-planning-with-files` 技能，开始使用落盘计划文件。
- 阅读并应用 `agent-discord-notify` 技能，确认任务完成后需要尝试 Discord 通知。
- 阅读并应用 `project-env-manager` 技能，检查项目环境记录。
- 检查 `Robotics/Project` 文件结构。
- 阅读 `hoops_description.pdf`。
- 阅读 `exercise_0_software_environment/README.md`。
- 抽取 `0_setup.ipynb` 和 `software/hoops.ipynb` 内容。
- 阅读 `utils/ball_simulation.py` 和 `utils/transformations.py`。
- 初步检查 `ur10_robot.urdf` 结构。
- 列出 Robotics 课程课件和作业文件。
- 检查本机 Conda 环境列表。
- 测试现有 Conda 环境是否包含项目关键依赖。
- 创建 `task_plan.md`、`findings.md`、`progress.md`。

### Conda Environment Check

Command:

```powershell
conda env list
```

Found:

- `base`
- `gpu_env`
- `raw2Event`
- `tf_work_hpc`
- `vela`

Checked imports:

```python
import numpy, casadi, pinocchio, meshcat, matplotlib
```

Result:

- Existing environments failed at least on `casadi`.
- Current recommendation: create dedicated `py13roboticscourse` environment from the provided YAML.

### Conceptual Clarification

“不要求实时运行” means computation time is not graded as a real-time constraint. It does not mean the physical interception can happen after the ball lands. The simulated ball still follows time-indexed physics; the algorithm must choose an interception before the useful part of the trajectory ends.

### Files Created

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\task_plan.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\findings.md`
- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\progress.md`

### Next

1. Create or confirm the dedicated Conda environment.
2. Run `0_setup.ipynb`.
3. Run `software/hoops.ipynb` until Meshcat visualization opens.
4. Extract high-value course material from C3/C4/C5/C6.
5. Convert findings into a concrete implementation and debugging protocol.

### Environment Setup Completed

Created Conda environment:

```powershell
conda env create -n robotics -f D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\py13roboticscourse_env.yml
```

Verified:

```powershell
conda run -n robotics python --version
```

Result:

```text
Python 3.13.13
```

Core package smoke test passed:

```python
import numpy, casadi, matplotlib, pandas, pinocchio, meshcat
from pinocchio import casadi as cpin
```

### Notebook Verification

Executed successfully:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\0_setup.ipynb`
- Output: `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\exercise_0_software_environment\0_setup.executed.ipynb`

Executed successfully:

- `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\software\hoops.ipynb`
- Output: `D:\BaiduNetdiskWorkspace\Leuven\8th\Robotics\Project\software\hoops.executed.ipynb`

### Environment Fixes Applied

The provided Conda YAML installed `example-robot-data`, but on Windows/Python 3.13 the import `from example_robot_data import load` was not initially available.

Fixes:

- Installed loader only:

```powershell
conda run -n robotics python -m pip install --no-deps example-robot-data-loaders
```

- Added path file:

```text
D:\Anaconda3\envs\robotics\Lib\site-packages\example_robot_data_loaders.pth
```

- Patched:

```text
D:\Anaconda3\envs\robotics\Lib\site-packages\cmeel.prefix\lib\python3.13\site-packages\example_robot_data\path.py
```

to point to:

```text
D:/Anaconda3/envs/robotics/Library/share/example-robot-data/robots
```
