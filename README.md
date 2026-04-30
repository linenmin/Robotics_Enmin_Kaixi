# Robotics Coursework Repository

[English](README.md) | [中文](README.zh-CN.md)

This repository contains the Robotics homework submissions and the final reverse-hoops robot arm project.

## Final Deliverables

### Project

- Final report PDF: `Project/outputs/report/final_report_research_grade_v12.pdf`
- Report source: `Project/report_template/template.tex`
- Project statement: `Project/hoops_description.pdf`
- Main implementation: `Project/software/`
- Main benchmark outputs and report figures: `Project/outputs/`

### Homework A

- Answer document (PDF): `Homework A/Homework_A_answers.pdf`
- Answer document (Word): `Homework A/Homework_A_answers.docx`
- Coding source notebook: `Homework A/Homework_A_coding_questions.ipynb`
- Original homework statement: `Homework A/homework4.pdf`

### Homework B

- Answer document (PDF): `Homework B/Homework_B_answers.pdf`
- Answer document (Word): `Homework B/Homework_B_answers.docx`
- Coding source notebook: `Homework B/Homework_B_coding_questions.ipynb`
- Original homework statement: `Homework B/homework8.pdf`

## Project Folder Guide

`Project/` is the main project workspace. The most important files are:

- `Project/hoops_description.pdf`  
  Original project brief with the four required tasks.
- `Project/known_conditions.md`  
  Human-readable summary of the project assumptions, task requirements, constants, and success criteria.
- `Project/course_knowledge_map.md`  
  Map from project tasks to relevant course concepts.
- `Project/AGENT_PROTOCOL.md`  
  Collaboration and report-writing protocol used during the project.
- `Project/task_plan.md` and `Project/progress.md`  
  Work plan and execution log.
- `Project/PROJECT_ENV.md`  
  Conda environment notes for running the project.

### `Project/software/`

Core Python implementation and scripts.

- `trajectory_predictor.py`  
  Linear Kalman filter and future ball trajectory prediction.
- `interception_selector.py`  
  Simple geometric interception-point selector.
- `optimal_control_planner.py`  
  Finite-horizon UR10 nonlinear program.
- `hoop_crossing.py`  
  Hoop-plane crossing and radial-error success metric.
- `strategy_benchmark.py`  
  Shared strategy benchmark logic for Task 4.
- `smart_interception_selector.py`  
  Feasibility-aware interception selector.
- `robot_description/`  
  URDF, meshes, and robot assets.
- `scripts/`  
  Validation, benchmarking, figure rendering, and Meshcat replay scripts.
- `tests/`  
  Unit tests for the project code.
- `hoops.ipynb`  
  Original notebook entry point from the course project.

Useful scripts:

- `scripts/validate_task1_prediction.py`
- `scripts/validate_task2_interception.py`
- `scripts/validate_task3_nlp_layer1.py`
- `scripts/benchmark_high_score_strategies.py`
- `scripts/render_high_score_figures.py`
- `scripts/render_task4_meshcat_report_scene.py`
- `scripts/replay_task4_meshcat.py`

### `Project/outputs/`

Generated evidence used by the report.

- `outputs/report/`  
  Final report PDF.
- `outputs/task1/`  
  Kalman filter prediction figures.
- `outputs/task2_dist1p0/`  
  Task 2 geometric interception selection figure used in the report.
- `outputs/task3/`  
  Task 3 NLP plan, joint-limit figure, and validation metrics.
- `outputs/task4/`  
  Final Meshcat scene screenshot used in the report.
- `outputs/high_score/`  
  Main 50-seed benchmark outputs, sensitivity sweeps, Pareto figure, geometry figure, and failure diagnostics.

## Reproducing Project Checks

Use the `robotics` Conda environment documented in `Project/PROJECT_ENV.md`.

From `Project/software/`:

```powershell
conda run -n robotics python -m unittest discover -s tests
conda run -n robotics python scripts/benchmark_high_score_strategies.py
conda run -n robotics python scripts/render_high_score_figures.py
```

The LaTeX report source is in `Project/report_template/`. The final rendered report is already committed under `Project/outputs/report/`.

## Notes

- Old intermediate report PDFs and obsolete visualization files have been removed.
- The project keeps final report evidence figures and benchmark outputs because they support the submitted report.
- `Project/outputs/report/final_report_research_grade_v12.pdf` is the current final report.
