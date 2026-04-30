# Robotics 课程作业仓库

[English](README.md) | [中文](README.zh-CN.md)

这个仓库包含 Robotics 课程的 Homework A、Homework B，以及最终的 reverse-hoops robot arm project。

## 最终交付文件

### Project

- 最终报告 PDF：`Project/outputs/report/final_report_research_grade_v12.pdf`
- 报告 LaTeX 源文件：`Project/report_template/template.tex`
- 项目题目说明：`Project/hoops_description.pdf`
- 主要代码实现：`Project/software/`
- 主要实验输出和报告图：`Project/outputs/`

### Homework A

- 答案 PDF：`Homework A/Homework_A_answers.pdf`
- 答案 Word：`Homework A/Homework_A_answers.docx`
- 代码 notebook：`Homework A/Homework_A_coding_questions.ipynb`
- 原始题目：`Homework A/homework4.pdf`

### Homework B

- 答案 PDF：`Homework B/Homework_B_answers.pdf`
- 答案 Word：`Homework B/Homework_B_answers.docx`
- 代码 notebook：`Homework B/Homework_B_coding_questions.ipynb`
- 原始题目：`Homework B/homework8.pdf`

## Project 文件夹说明

`Project/` 是最终项目的主要工作区。关键文件如下：

- `Project/hoops_description.pdf`  
  老师给的原始项目说明，包含四个 task。
- `Project/known_conditions.md`  
  对项目已知条件、任务要求、常量和成功判据的整理。
- `Project/course_knowledge_map.md`  
  将项目任务与课程知识点对应起来的 map。
- `Project/AGENT_PROTOCOL.md`  
  本项目中人与 agent 协作、实验执行、报告写作的 protocol。
- `Project/task_plan.md` 和 `Project/progress.md`  
  项目计划和执行记录。
- `Project/PROJECT_ENV.md`  
  Conda 环境和运行环境说明。

### `Project/software/`

项目的核心 Python 代码和脚本。

- `trajectory_predictor.py`  
  线性 Kalman filter 和小球未来轨迹预测。
- `interception_selector.py`  
  Task 2 的简单几何接球点选择器。
- `optimal_control_planner.py`  
  UR10 的 finite-horizon nonlinear program 控制器。
- `hoop_crossing.py`  
  hoop plane crossing、radial error 和成功判据。
- `strategy_benchmark.py`  
  Task 4 策略 benchmark 的共享逻辑。
- `smart_interception_selector.py`  
  feasibility-aware 的智能接球点选择器。
- `robot_description/`  
  URDF、mesh 和机器人模型资源。
- `scripts/`  
  验证、benchmark、图像渲染和 Meshcat replay 脚本。
- `tests/`  
  项目代码的单元测试。
- `hoops.ipynb`  
  课程项目原始 notebook 入口。

常用脚本：

- `scripts/validate_task1_prediction.py`
- `scripts/validate_task2_interception.py`
- `scripts/validate_task3_nlp_layer1.py`
- `scripts/benchmark_high_score_strategies.py`
- `scripts/render_high_score_figures.py`
- `scripts/render_task4_meshcat_report_scene.py`
- `scripts/replay_task4_meshcat.py`

### `Project/outputs/`

报告中使用的实验结果、图和验证输出。

- `outputs/report/`  
  最终报告 PDF。
- `outputs/task1/`  
  Kalman filter 轨迹预测图。
- `outputs/task2_dist1p0/`  
  报告中使用的 Task 2 几何接球点选择图。
- `outputs/task3/`  
  Task 3 NLP 计划图、关节限制图和验证指标。
- `outputs/task4/`  
  报告中使用的最终 Meshcat 场景截图。
- `outputs/high_score/`  
  50-seed benchmark、noise sensitivity、Pareto 图、几何定义图和失败诊断图。

## 复现 Project 检查

使用 `Project/PROJECT_ENV.md` 中记录的 `robotics` Conda 环境。

从 `Project/software/` 目录运行：

```powershell
conda run -n robotics python -m unittest discover -s tests
conda run -n robotics python scripts/benchmark_high_score_strategies.py
conda run -n robotics python scripts/render_high_score_figures.py
```

LaTeX 报告源码位于 `Project/report_template/`。最终渲染好的报告已经提交在 `Project/outputs/report/`。

## 备注

- 旧版中间报告 PDF 和过时的可视化文件已经清理。
- Project 保留了最终报告需要引用的 evidence figures 和 benchmark outputs。
- 当前最终报告是 `Project/outputs/report/final_report_research_grade_v12.pdf`。
