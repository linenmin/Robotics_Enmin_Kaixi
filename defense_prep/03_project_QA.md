# Project — 口试抽考卡（Reverse-Hoops UR10）

每个 task 格式：**你声称了啥 → 教授会问啥（英文）→ 答案（中文 + 英文术语）→ 陷阱。**
笔记链接见 `00_index_crossref.md` 的 legend。来源 memo：`Project/task1..4_decision_memo.md`。

**中心论点（被问「summarize your project」先说这个）：**
> 选点规则最重要（the interception-point rule matters most）。我们固定 Kalman filter 和 NLP controller，只改 candidate-selection 规则。Reactive（无预测）= 0%。预测 + 简单几何选点 = 0%。feasibility-aware **time-first** 选点 = **98%**。所以预测是必要但不充分的；feasibility-aware 选点才是决定性一步。

要张口就来的关键数字：
- Hoop clearance: r_h−r_b = 0.15−0.12 = **30 mm** radial tolerance。
- KF: filtered RMSE 0.90 mm；0.5 s prediction RMSE 3.51 mm（95th pct 6.35 mm）≪ 30 mm。
- NLP: N=28, Δt=0.05 s（1.4 s horizon）；solve ~0.07 s, ~15 IPOPT iters；accel bound ±2 rad/s²。
- Benchmark（50 seeds）：time-first 98%, 1.387 s, TCP 13.18 mm, radial 11.24 mm；late-feasible 98%, 1.433 s, radial 5.75 mm。
- 唯一失败 = seed 11（95th-pct lateral velocity outlier，acceleration-limited geometry）。

---

## Task 1 — Kalman filter 轨迹估计
**你声称：** 状态 x=[p,v]ᵀ；F=constant-velocity，B·g = 已知 gravity input，H=position selection；linear-Gaussian ⇒ KF 是 Bayes-optimal MMSE 且有 analytic covariance。这里 EKF 退化成 KF；PF 只加 sampling noise 无建模收益。从第一个测量初始化，v=0 配大 covariance。
**笔记：** L6 › 第48–55页 卡尔曼滤波器; 第20–23页 贝叶斯滤波器; 第30页 两种近似; 第63–71页 离散化/状态增广。

**Q: Why a Kalman filter and not EKF or particle filter?**（几乎必问）
A: 两次 bounce 之间 dynamics 是 linear 的（constant horizontal velocity + 已知 gravity input），测量是 linear + Gaussian noise。linear-Gaussian 下 KF 是精确的 Bayes-optimal MMSE 估计。EKF 会去线性化一个本来就 linear 的模型 ⇒ 更新式完全一样，没好处。PF 用样本近似一个 Gaussian belief ⇒ 多了 variance，没多建模能力。KF 是最小充分（minimal sufficient）选择。

**Q: Is the model truly linear? Gravity?**
A: gravity 是*已知确定输入*（Bg 项），不是非线性。它在 prediction 里加性进入。非线性（bounce）只在撞击时出现，而我们报告的每个 catch 都在 bounce 之前。

**Q: What is the covariance good for here?**
A: 量化 prediction uncertainty。我们查了 0.5 s forward-prediction covariance 远小于 30 mm hoop clearance（95th pct 6.35 mm），确认估计不是瓶颈。还做了 covariance-rejection ablation —— 它选出相同 candidate，所以在这个 open-loop 设置里 covariance 是诊断性的、非决定性的。

**Q: Why init velocity 0 with large covariance?**
A: t0 没有速度测量；给大初始 velocity covariance 让前几个 position 测量快速修正 v 而不引入偏置。

**陷阱：** 别把 filter 吹过头。你报告自己写了「estimation is not the main bottleneck」。被追问「所以 filter 很 trivial？」→「它是*正确的最小*估计器；工程难点在下游的 selection。」

---

## Task 2 — 简单几何选点 + reactive baseline
**你声称：** 简单规则采样预测轨迹，剔除 太早 / 太低 / 太远 的点（workspace-radius reachability proxy）。在完整检查下 0% 成功。第二个 baseline = damped Jacobian pseudo-inverse Cartesian 速度控制器，无预测 —— 也 0%，最近距离 59.4 mm（≈2× tolerance）。
**笔记：** L5 › 模块一 基础概念; L3b › 模块四 伪逆理论与SVD (damped pinv)。

**Q: Why does the reactive (no-prediction) controller fail?**
A: 它追*当前测到的*球位置。pursuit controller 永远滞后于运动目标；能缩短距离，但无法在对的*时间*到对的地方。最好的 seed 还差 59.4 mm（需要 30 mm）。这证明预测是必要的。

**Q: Write the damped pseudo-inverse law and explain λ.**
A: q̇ = Jᵀ(JJᵀ+λ²I)⁻¹·K(p_ball−p_tcp)。λ 在 singularity 附近阻尼这个逆：没有它，JJᵀ 病态，joint velocity 爆炸。λ 用 tracking accuracy 换数值稳定（Levenberg–Marquardt / damped least squares）。课程：L3b 模块四。

**Q: Why does the *simple geometric* pick also get 0%, even with prediction?**
A: 它只回答「球从空间一个合理区域哪里穿过」。它从不检查 UR10 能否把 hoop 以对的 pose、在 acceleration limits 内送到那里。几何上漂亮的点可能 dynamically infeasible。→ 引出 Task 4。

**陷阱：** 说清楚 0% 是「在*完整* NLP + true hoop-crossing 检查下」，不是说规则不产生点。简单规则的 1.295 s 是*尝试*时间，不是成功 catch。

---

## Task 3 — 约束轨迹优化（NLP）
**你声称：** direct-transcription finite-horizon NLP。决策变量 {q_k, q̇_k, q̈_k}。动力学约束 q_{k+1}=q_k+q̇_k·Δt+½q̈_k·Δt², q̇_{k+1}=q̇_k+q̈_k·Δt。Cost = terminal TCP error（w_p=1500）+ accel（w_u）+ velocity（w_v）+ upright（w_o）+ normal-alignment（w_n）。Hard constraints: joint pos/vel/accel limits、table clearance z_tcp≥h+m、upright R_zz≥0。工具：Pinocchio（FK）、CasADi（symbolic NLP）、IPOPT（solver）。验证：20.1 mm terminal error，accel 触到 ±2 rad/s²，solve 0.07 s/15 iters。
**笔记：** L5 › 模块三 最优控制法（P.13–20）; L4 › 模块三 控制即优化 + 模块四 约束类型; L3b › resolved acceleration。

**Q: Why direct-transcription optimal control instead of a single-step Jacobian / resolved-acceleration controller?**
A: single-step 控制器是 greedy 的 —— 能追 Cartesian 目标，但无法在一个 horizon 上*预算 acceleration*，以便用对的 pose 到达未来的 catch。报告最后一段：Jacobian 控制器不能为未来 catch「省」加速度；closed-form smooth trajectory 不能同时 enforce hoop-crossing + joint limits + orientation。horizon NLP 是同时处理这些的最小 formulation。

**Q: Which constraints are hard, which soft, and why that split?**
A: **Hard**（绝不可违反）：joint position/velocity/acceleration limits、table clearance、upright R_zz≥0 —— 物理/安全可行性。**Soft**（惩罚）：terminal TCP error、normal alignment、accel/velocity 正则、upright 正则 —— 你要权衡的目标。「reach the ball」不能设 hard，因为 infeasible target 会让整个 NLP infeasible；安全必须 hard，这样机器人永不会被命令去弄坏自己。

**Q: What is R_zz and why ≥0?**
A: R_zz = e_zᵀ·R_tcp(q)·e_z，TCP z-axis 的 world-z 分量（= hoop normal，经 fixed tool transform）。R_zz≥0 让 hoop 的 top side 不指向水平面以下（任务要求：ring 永不 top-side 朝下）。每个 knot 上的 hard path constraint。

**Q: You used a link-sphere self-collision proxy, not exact mesh. Why? Is that a weakness?**
A: exact mesh self-collision 加很多 non-smooth signed-distance 约束，伤 IPOPT 收敛。我们要求 planning 后在保守 sphere proxy 下 clearance 为正。更严格版本会把 capsule/sphere signed-distance 约束直接加进 NLP（L5 模块二 SDF）。这是 accuracy-vs-tractability 的有意权衡，并已如实说明。

**Q: The w_o ablation — what did it show?**
A: 扫 w_o∈{0,1,10,50}，成功率维持 98%。所以 upright 行为由 *hard* R_zz≥0 约束和 normal-alignment 项决定，不是 soft terminal upright cost —— 那个 cost 只正则化 pose。很好地证明我们懂哪一项在起作用。

**Q: What's the binding limit — velocity or acceleration?**
A: Acceleration。joint 2 只用了 64% velocity bound，但 acceleration profile 触到 ±2 rad/s²。这个 catch 是 acceleration-limited geometry。

**陷阱：** 分清 **terminal TCP error**（最后 knot 上 hoop-center 到预测目标）和 **radial crossing error**（true ball 在穿过 hoop plane 时对 hoop plane 的误差）。它们是不同的检查；报告刻意把 solver error 和 execution error 分开。混淆这两个最容易显得糊涂。

---

## Task 4 — feasibility-aware 选点（招牌结果）
**你声称：** time-first feasible selector = 通过 predicted-candidate + NLP-feasibility + safety 检查的最早 candidate。Benchmark：对每个 shortlisted candidate 解 Task 3 NLP；成功仅当 NLP 收敛 + true ball 在 30 mm 内穿过 + safety penalty 为 0。396 个 NLP 全收敛，但只 164 个过 hoop-crossing（≈59% 合理 candidate 被否）。time-first 把 0%→98%，比 infeasible 的简单选点晚 92 ms（≈2 control ticks）catch。balanced & late-feasible 作对比（更准、更慢）。
**笔记：** L5 › 模块三 最优控制 (free-time) + 模块四 搜索/采样; L4 › 模块六 柔性轨迹。

**Q: Why is candidate selection the bottleneck, not the estimator or the solver?**
A: 直接证据：396 个 candidate NLP 全收敛（solver 没问题），KF prediction error（≤6.35 mm）远低于 tolerance（estimator 没问题）。但 59% 几何上合理的 candidate 没过 true hoop-crossing —— 机器人*能*解出运动，但很多 catch 时间把 hoop 放到了错的穿越几何。所以决定变量是*选哪个*点/时间。

**Q: Why time-first and not balanced or late-feasible?**
A: 任务明确要求*更短 interception time*。time-first 在相同 98% 成功率下给最早成功 catch（1.387 s）。late-feasible 更准（radial 5.75 vs 11.24 mm）但更慢；balanced 居中。如果目标是 accuracy，我们会选 balanced/late —— 报告里明说了。选择跟随给定任务目标。

**Q: Why does time-first have *worse* TCP/radial error despite equal success?**
A: 它用最紧的运动预算 —— NLP 触到 acceleration bound，没多少余地精修最终 pose。更晚的 candidate 给机器人更多时间把 hoop 与 ball direction 对齐 → 误差更低。成功是二值的（30 mm 内），所以三者即便误差量级不同都达 98%。

**Q: Connect to the course — what course concept is "feasibility-aware sampling"?**
A: 它是在 free-time optimal-control 问题上的 candidate sampling（L5 模块三：scaled time / free-final-time；模块四：sampling-based planning），用 Task 3 NLP 的 optimization feasibility 过滤。min-jerk 直觉（L4/L7）：catch 时间越短 → peak acceleration 越高，所以「最早」被 accel limit 约束 —— 这正是某些早 candidate infeasible 的原因。

**Q: Explain seed 11 (your only failure).**
A: 它是 lateral-velocity outlier（接近 95th pct v_y）。7 个 shortlisted candidate 全解出 NLP 且都穿过 hoop plane，但没一个在 30 mm 内；radial error 从 758 mm（最早，时间内够不着）降到 51.5 mm（最晚）。每个 candidate 都饱和 ±2 rad/s² —— 早的饱和 joint 3，晚的饱和 joint 2。是 acceleration-limited geometry，不是 estimator divergence 或 NLP failure。修复需要更长 horizon 或不同 sampler —— 一次 mitigation run（16 candidate, 1.35 m radius）没救回它。

**陷阱：** 可能被探「98% 是不是运气/对 seed 过拟合？」→ 两个鲁棒性检查：(1) 1–10 mm noise sweep，time-first 在每个 level 维持 95%（20 seeds 时一次失败 = 5%）；(2) covariance-rejection ablation 在全部 50 seeds 选出相同 catch。两者都指向同一结论：决定的是 geometric feasibility，不是 estimator quality。

---

## 可能的「大局」问题（跨 task）
- **"If you had one more week?"** → 救 seed 11：更长 prediction horizon 或更聪明的 candidate sampler；加 exact SDF self-collision 约束；用 MPC 闭环替代 open-loop execution。
- **"Why open-loop execution?"** → simulator 给 ground-truth robot state；我们规划一次后执行。open-loop gap 很小（predicted-to-true radial gap 4.41 mm）。MPC 只对边缘 seed 有帮助。
- **"What's genuinely novel vs given?"** → estimator 和 controller 都是标准的。贡献是把*selection* 隔离为决定变量的 controlled benchmark 设计，加上证明它的 ablations。
