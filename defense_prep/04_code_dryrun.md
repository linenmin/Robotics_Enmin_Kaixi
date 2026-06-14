# 现场跑代码预案（Live-Code Dry-Run Prep）

口试规则：**「Bring your notebook computer and be ready to run your code.」** 教授可能说「show me X」或「change Y and rerun」。本文件是你的 runbook + 跑的时候要讲的解释。

**出门前 checklist：**
- [ ] `conda activate robotics` 能用（Python 3.13.13）。见 `Project/PROJECT_ENV.md`。
- [ ] `example-robot-data-loaders` 的 path fix 已就位（`.pth` → `D:/Anaconda3/envs/robotics/...`）。换台机器这个路径会断 —— 心里有数。
- [ ] **离线先全跑一遍**，让图/HTML 都生成、cache 预热。别让第一次运行发生在现场。
- [ ] 打开 `hoops.ipynb`、两个 homework notebook、一个开在 `Project/software/` 的终端。
- [ ] 预先生成一个 Meshcat replay HTML（seed 0），知道怎么打开。
- [ ] 小事：`README.md` 写的是 `final_report_research_grade_v12.pdf`，实际文件是 `v13`。如果他们翻 repo，主动说一句是 v13。

---

## Homework A — Q4 visibility-graph planner
**文件：** `Homework A/Homework_A_coding_questions.ipynb`（2 个 cell，自包含：`dist`、segment-intersection、visibility graph、A*）。

**跑：** 打开 notebook → Run All。预期路径 `(2.60,2.60)→(2.05,3.75)→(4.00,5.00)→(6.05,6.85)→(7.45,7.30)`，长度 **7.822886**，图 `homework4_q4_path.png`。

**若说「change the obstacles / move the goal and rerun」：**
- 改 `obstacle*` 顶点列表或 `goal`，重跑。planner 每次重建 visibility graph 和 A* —— 没有 hardcode 的路径。
- 边跑边讲：「nodes = start+goal+所有顶点；edges = collision-free segments；A* with Euclidean heuristic」。

**可能的现场 ask：**「Make the goal unreachable（围起来）」→ A* 返回无路径；解释 completeness：没有 collision-free segment 链时它正确报告失败。

---

## Homework B — Q1 Bayes posterior sampling
**文件：** `Homework B/Homework_B_coding_questions.ipynb`（采样 + matplotlib histogram）。

**跑：** Run All → prior samples（seed 42）mean ≈ −0.008, std ≈ 1.229；posterior mean ≈ 0.303, std ≈ 0.390；histogram `Fig.1`。

**若说「change the measurement z and rerun」：**
- z 是变量；设比如 `z = 2.0` 重跑。posterior 连续部分移向 x=z/2；*跑之前先预测*移动方向（显示你懂）。
- 「change the noise σ (0.3)」：σ 越小 → likelihood 越尖 → posterior 被更狠拉向 x=z/2，x=1 spike 失更多权重。

**可能的现场 ask：**「Show the spike at x=1 explicitly」→ 它是 degenerate component；在样本里像个 delta 状的 bar。解释你把 variance-0 建模成 point mass。

> 注：HW B 的 Q2/Q3/Q4 是解析题（无代码）。若被要求「为 Q2 数值算 v_max」，可在 scratch cell 现场做：`numpy.linalg.svd(E.T @ Jp)` → 最大 singular value。把这一行准备好。

---

## Project — 重头戏

所有命令的工作目录：`Project/software/`。输出落在 `../outputs/`。

### 最快「证明它能跑」—— Meshcat catch replay
```bash
python scripts/replay_task4_meshcat.py --seed 0
```
打开一个 HTML：grey=观测过去、green=预测、red=简单几何选点、yellow=选中的 feasible catch，UR10 挥 hoop 去接。**这是你的招牌画面** —— 预先生成好，秒开。

### 单 seed 完整 pipeline（benchmark + scene + replay）
```bash
python scripts/run_full_catch_pipeline.py --seed 0
```
跑 KF prediction → candidate selection → 每个 candidate 的 Task-3 NLP → hoop-crossing 检查，并渲染场景。较慢；他们要端到端时才现场跑。

### 逐 task 验证脚本（对应报告里的图）
| 现场 ask | 命令 | 显示 |
|---|---|---|
| "Show the Kalman filter" | `python scripts/validate_task1_prediction.py` | filtered vs measured vs true z；RMSE（filtered 0.90 mm, 0.5 s pred 3.51 mm） |
| "Show the simple selector" | `python scripts/validate_task2_interception.py` | 采样轨迹 + 选中点 `[1.224, −0.119, 1.074]` |
| "Show the NLP solve" | `python scripts/validate_task3_nlp_layer1.py` | 20.1 mm terminal error，accel 触 ±2 rad/s²，~15 IPOPT iters |
| "Reproduce the benchmark" | `python scripts/benchmark_high_score_strategies.py --seeds 0 1 2` | 每 seed success/time/TCP/radial（现场用几个 seed，全 50 慢） |
| "Reactive baseline = 0%?" | `python scripts/benchmark_reactive_baseline.py --seeds 0 1 2` | 最近 TCP-to-ball ≈ 0.176 m，从不进 30 mm |

### 跑测试（证明代码是真的，快）
```bash
pytest -q          # 在 Project/software/ 下
```
7 个测试文件：trajectory_predictor、interception_selector、optimal_control_planner、hoop_crossing、safety_metrics、smart_interception_selector、strategy_benchmark。

---

## 「改参数重跑」—— 预判这些

| 他们改… | 在哪 | 你预测会发生啥 |
|---|---|---|
| seed | `--seed N` / `--seeds N` | 不同 throw。大多数成功；seed 11 是已知失败（lateral outlier）。 |
| acceleration limit | `optimal_control_planner.py` 里的 NLP bound | 调大 → 边缘 seed（含 11）更可能成功；它是 binding constraint。调小 → 更多失败。 |
| weight w_o（upright cost） | NLP cost | 成功率维持 ~98% —— ablation 显示是 hard R_zz≥0 在起作用，不是这个 soft cost。 |
| measurement noise | `--measurement-noise-std` | 升到 10 mm，成功率仍 ~95%；estimation 不是瓶颈。 |
| candidate 数 / workspace radius | benchmark args（`max_candidates`, `max_candidate_distance`） | candidate 更多 ≠ 救回 seed 11（试过 16 cand / 1.35 m）。 |
| time-first → late-feasible | selector 选择 | catch 更慢，radial error 更低（5.75 vs 11.24 mm），同样 98%。 |

---

## 他们可能打开文件问的代码级问题
- **`trajectory_predictor.py`** —「predict 和 update 在哪？」指 KF step：用 F/Bg 预测 mean+cov，再用 H,R 做 innovation 修正。init v=0, 大 P_v。
- **`optimal_control_planner.py`** —「show me the hard constraints」指 joint pos/vel/accel bounds、`ztcp≥htable+mtcp`、`Rzz≥0`；以及 soft cost 项及权重 w_p=1500, w_u, w_v, w_o=10, w_n=5。CasADi 符号构建，IPOPT 求解，Pinocchio 出 FK。
- **`hoop_crossing.py`** —「怎么算成功？」ball center 必须穿过 hoop plane 且在 r_h−r_b=30 mm radial band 内。
- **`interception_selector.py`** vs **`smart_interception_selector.py`** — 简单几何（0%）vs feasibility-aware time-first（98%）。这个差别*就是*项目的论点。

**现场崩了的黄金法则：** 别慌，说出它*本应*显示啥，指向 `Project/outputs/` 里预先生成的图/输出，讲清概念。他们考的是理解，不是你的笔记本。
